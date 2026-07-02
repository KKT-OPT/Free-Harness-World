from __future__ import annotations

import json
import re
import shutil
from contextlib import redirect_stdout
from collections import Counter, defaultdict
from html import escape
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from rag_candidate.commands import (
    run_build_graph as _run_candidate_build_graph,
    run_enrichment_plan as _run_candidate_enrichment_plan,
    run_health as _run_candidate_health,
    run_ingest as _run_candidate_ingest,
    run_lint as _run_candidate_lint,
    run_promotion_plan as _run_candidate_promotion_plan,
    run_promote_reviewed as _run_candidate_promote_reviewed,
    run_review_package as _run_candidate_review_package,
)
from rag_candidate.common import (
    extract_wikilinks,
    print_json,
    read_text,
    rel,
    safe_run_id,
    scan_sensitive_text,
    timestamp_id,
    today,
    update_status,
    write_text,
)


VAULT_INDEX_FILES = {
    "Home.md",
}

SECONDARY_VAULT_VIEW_FILES = {
    "CandidateEvidenceIndex.md",
    "CandidateReviewPackage.md",
    "CandidateReviewQueue.md",
    "KnowledgeGovernance.md",
    "KnowledgeIndex.md",
    "RawSourceIndex.md",
    "ReviewedKnowledgeIndex.md",
    "ReviewedOverview.md",
}

PIPELINE_SMOKE_CONCEPTS = {
    "AgentHarnessEngineering": (
        "Agent Harness Engineering 是围绕 LLM agent 的执行环境、工具、上下文、生命周期、观测、验证和治理构建可靠控制层的工程 discipline。",
        ["ETCLOVGTaxonomy", "TraceNativeEvaluation", "HarnessCouplingProblem"],
    ),
    "BindingConstraintThesis": (
        "长周期 agent 可靠性可能被 execution harness 约束，而不只由模型能力决定。",
        ["AgentHarnessEngineering", "HarnessCouplingProblem", "TraceNativeEvaluation"],
    ),
    "ETCLOVGTaxonomy": (
        "Execution、Tooling、Context、Lifecycle、Observability、Verification、Governance 七层分类框架。",
        ["AgentHarnessEngineering", "TraceNativeEvaluation", "StandardHandoffProtocol"],
    ),
    "HarnessCouplingProblem": (
        "Harness 层之间存在耦合，局部优化需要按系统变更验证。",
        ["AgentHarnessEngineering", "BindingConstraintThesis", "AdaptiveHarnessOptimization"],
    ),
    "TraceNativeEvaluation": (
        "以执行 trace 作为评价、诊断和回归测试的主要证据对象。",
        ["AgentHarnessEngineering", "ETCLOVGTaxonomy", "StandardHandoffProtocol"],
    ),
    "ContextDrift": (
        "长周期任务中 agent 内部状态逐步偏离真实任务状态或原始目标的 failure mode。",
        ["AgentHarnessEngineering", "TraceNativeEvaluation", "StandardHandoffProtocol"],
    ),
    "StandardHandoffProtocol": (
        "在 agents、tools、humans 之间转移状态和责任时需要明确授权、证据、边界和返回条件。",
        ["AgentHarnessEngineering", "TraceNativeEvaluation", "ContextDrift"],
    ),
    "AdaptiveHarnessOptimization": (
        "随着模型和任务变化，持续重新评估并简化 Harness controls。",
        ["AgentHarnessEngineering", "HarnessCouplingProblem", "TraceNativeEvaluation"],
    ),
}


def run_init_obsidian_vault(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    vault.mkdir(parents=True, exist_ok=True)
    reviewed.mkdir(parents=True, exist_ok=True)

    obsidian = vault / ".obsidian"
    obsidian.mkdir(parents=True, exist_ok=True)
    files = {
        obsidian / "app.json": {
            "alwaysUpdateLinks": True,
            "newFileLocation": "folder",
            "newFileFolderPath": "reviewed",
            "promptDelete": True,
        },
        obsidian / "appearance.json": {
            "accentColor": "#2563eb",
            "baseFontSize": 16,
            "showViewHeader": True,
        },
        obsidian / "graph.json": {
            "collapse-filter": False,
            "search": "-path:raw -path:candidate -path:.obsidian",
            "showTags": True,
            "showAttachments": False,
            "hideUnresolved": False,
        },
    }
    written = []
    for path, payload in files.items():
        write_text(path, json.dumps(payload, indent=2, ensure_ascii=False))
        written.append(rel(root, path))

    sync = _sync_reviewed_index(root, vault, reviewed)

    result = {
        "state": "passed",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "obsidianConfig": rel(root, obsidian),
        "written": written + sync["written"],
        "reviewedPageCount": sync["reviewedPageCount"],
        "openWithObsidian": rel(root, vault),
        "note": "Open the vault path in Obsidian. Generated vault files are local-only user knowledge views.",
    }
    update_status(root, args.run_id, {"obsidianVault": result})
    print_json(result)
    return result


def run_sync_reviewed_index(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    result = _sync_reviewed_index(root, vault, reviewed)
    result["state"] = "passed"
    result["vault"] = rel(root, vault)
    result["reviewed"] = rel(root, reviewed)
    update_status(root, args.run_id, {"reviewedIndex": result})
    print_json(result)
    return result


def run_health_reviewed(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    report = _resolve_under_root(root, args.report)
    pages = _reviewed_pages(reviewed)
    index_files = [vault / name for name in VAULT_INDEX_FILES]
    missing_index_files = [rel(root, p) for p in index_files if not p.exists()]
    missing_frontmatter = [rel(root, p) for p in pages if not read_text(p).lstrip().startswith("---")]
    missing_review = [
        rel(root, p) for p in pages
        if "review:" not in read_text(p) and "reviewedBy:" not in read_text(p)
    ]
    sensitive = scan_sensitive_text(root, pages + [p for p in index_files if p.exists()])

    result = {
        "state": "passed" if not missing_index_files and not missing_frontmatter and not missing_review and not sensitive else "partial",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "reviewedPageCount": len(pages),
        "missingIndexFiles": missing_index_files,
        "missingFrontmatter": missing_frontmatter,
        "missingReviewMetadata": missing_review,
        "sensitiveFindings": sensitive,
        "report": rel(root, report),
    }
    write_text(report, _format_health_report(result))
    update_status(root, args.run_id, {"reviewedHealth": result})
    print_json(result)
    return result


def run_build_reviewed_graph(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    graph_dir = _resolve_under_root(root, args.graph)
    report = _resolve_under_root(root, args.report)
    pages = _graph_pages(vault, reviewed)
    lookup = _page_lookup(vault, pages)
    nodes = []
    edges = []
    seen_edges: set[tuple[str, str]] = set()
    broken_refs: dict[str, list[str]] = defaultdict(list)

    for page in pages:
        text = read_text(page)
        node_id = rel(vault, page).removesuffix(".md")
        nodes.append({
            "id": node_id,
            "label": _page_title(text, page.stem),
            "type": _frontmatter_value(text, "type") or _node_type(vault, reviewed, page),
            "path": rel(root, page),
            "vaultPath": rel(vault, page),
            "contentChars": len(_strip_frontmatter(text)),
        })
        for link in extract_wikilinks(text):
            target = _resolve_wikilink(link, lookup)
            if not target:
                broken_refs[link].append(rel(vault, page))
                continue
            target_id = rel(vault, target).removesuffix(".md")
            if target_id == node_id:
                continue
            edge_key = (node_id, target_id)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            edges.append({
                "from": node_id,
                "to": target_id,
                "type": "EXPLICIT_WIKILINK",
                "confidence": 1.0,
            })

    health = _graph_health(nodes, edges, broken_refs)
    graph = {
        "built": today(),
        "scope": "reviewed-knowledge",
        "nodes": nodes,
        "edges": edges,
        "health": health,
    }
    graph_json = graph_dir / "graph.json"
    graph_html = graph_dir / "graph.html"
    write_text(graph_json, json.dumps(graph, indent=2, ensure_ascii=False))
    write_text(graph_html, _render_graph_html(graph))

    result = {
        "state": "passed",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "brokenLinkCount": sum(len(v) for v in broken_refs.values()),
        "orphanCount": len(health["orphanNodes"]),
        "graphJson": rel(root, graph_json),
        "graphHtml": rel(root, graph_html),
        "report": rel(root, report),
    }
    write_text(report, _format_graph_report(result, health))
    update_status(root, args.run_id, {"reviewedGraph": result})
    print_json(result)
    return result


def run_query_reviewed(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    graph = _resolve_under_root(root, args.graph)
    report = _resolve_under_root(root, args.report) if args.report else None
    result = _query_reviewed(root, vault, reviewed, graph, args.question, args.limit)
    if report:
        result["report"] = rel(root, report)
        write_text(report, _format_query_report(result))
    update_status(root, args.run_id, {"lastReviewedQuery": result})
    print_json(result)
    return result


def run_reviewed_gap_plan(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    graph = _resolve_under_root(root, args.graph)
    report = _resolve_under_root(root, args.report)
    candidate_wiki = _resolve_under_root(root, args.candidate_wiki)
    pages = _reviewed_pages(reviewed)
    lookup = _page_lookup(vault, _graph_pages(vault, reviewed))
    gaps_by_link: dict[str, set[str]] = defaultdict(set)

    for page in pages:
        for link in extract_wikilinks(read_text(page)):
            if _resolve_wikilink(link, lookup):
                continue
            gaps_by_link[link].add(rel(vault, page))

    gaps = _gap_records(root, candidate_wiki, gaps_by_link)
    written = []
    if args.write_candidates and gaps:
        written = _write_gap_candidate_wiki(root, candidate_wiki, gaps)

    result = {
        "state": "needs-candidate-enrichment" if gaps else "passed",
        "scope": "reviewed-knowledge",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "reviewedPageCount": len(pages),
        "graph": rel(root, graph),
        "gapCount": len(gaps),
        "gaps": gaps,
        "candidateWiki": rel(root, candidate_wiki),
        "candidateWritten": bool(written),
        "written": written,
        "boundary": "candidate-only-no-promotion",
        "report": rel(root, report),
    }
    write_text(report, _format_gap_plan_report(result))
    update_status(root, args.run_id, {"reviewedGapPlan": result})
    print_json(result)
    return result


def run_enrich_gap_candidates(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate_wiki = _resolve_under_root(root, args.candidate_wiki)
    report = _resolve_under_root(root, args.report)
    if not candidate_wiki.exists():
        raise FileNotFoundError(f"candidate wiki not found: {rel(root, candidate_wiki)}")

    reviewed_records = _reviewed_records(root, vault, reviewed)
    concept_index = _reviewed_concept_index(reviewed_records)
    concept_pages = [
        page for page in sorted((candidate_wiki / "concepts").glob("*.md"))
        if page.stem not in {"CandidateKnowledge", "ReviewedKnowledgeGap"}
    ]
    enriched = []
    for page in concept_pages:
        original_link = _original_gap_link(page)
        concept = _concept_evidence(original_link, concept_index)
        snippets = _reviewed_snippets_for_link(original_link, reviewed_records)
        result_item = {
            "page": rel(root, page),
            "candidateConcept": page.stem,
            "originalLink": original_link,
            "definitionStatus": concept["status"],
            "sourcePages": sorted({item["page"] for item in snippets}),
            "evidenceCount": len(snippets),
            "promotionHint": _promotion_hint(original_link, concept),
        }
        write_text(page, _format_enriched_gap_candidate_page(page.stem, original_link, concept, snippets))
        enriched.append(result_item)

    _write_gap_enriched_overview(candidate_wiki, enriched)
    _append_gap_enrichment_log(candidate_wiki, enriched)

    result = {
        "state": "passed" if enriched else "partial",
        "scope": "reviewed-gap-candidate-enrichment",
        "reviewed": rel(root, reviewed),
        "candidateWiki": rel(root, candidate_wiki),
        "enrichedPageCount": len(enriched),
        "enriched": enriched,
        "boundary": "candidate-only-no-promotion",
        "report": rel(root, report),
    }
    write_text(report, _format_gap_enrichment_report(result))
    update_status(root, args.run_id, {"gapCandidateEnrichment": result})
    print_json(result)
    return result


def run_gap_review_package(args) -> dict:
    root = Path(args.root).resolve()
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate_wiki = _resolve_under_root(root, args.candidate_wiki)
    report = _resolve_under_root(root, args.report)
    if not candidate_wiki.exists():
        raise FileNotFoundError(f"candidate wiki not found: {rel(root, candidate_wiki)}")

    status = _load_status(root, args.run_id)
    items = _gap_review_items(root, candidate_wiki)
    gates = _gap_review_gates(status, items)
    ready_items = [item for item in items if item["recommendation"] == "approve-for-human-review"]
    dedup_items = [item for item in items if item["recommendation"] == "dedup-before-promotion"]
    revise_items = [item for item in items if item["recommendation"] == "revise-before-review"]

    result = {
        "state": "ready-for-human-review" if not gates["blockingIssues"] else "needs-repair-before-human-review",
        "scope": "reviewed-gap-candidate-review-package",
        "reviewed": rel(root, reviewed),
        "candidateWiki": rel(root, candidate_wiki),
        "candidateConceptCount": len(items),
        "readyForHumanReviewCount": len(ready_items),
        "dedupBeforePromotionCount": len(dedup_items),
        "reviseBeforeReviewCount": len(revise_items),
        "reviewGates": gates,
        "items": items,
        "boundary": "candidate-only-no-promotion",
        "report": rel(root, report),
        "nextAction": "human-review-decides-approve-defer-reject-dedup-no-reviewed-write-by-this-command",
    }
    write_text(report, _format_gap_review_package(result))
    update_status(root, args.run_id, {"gapReviewPackage": result})
    print_json(result)
    return result


def run_promote_gap_candidates(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate_wiki = _resolve_under_root(root, args.candidate_wiki)
    target_dir = _resolve_under_root(root, args.target_dir)
    report = _resolve_under_root(root, args.report)
    if not candidate_wiki.exists():
        raise FileNotFoundError(f"candidate wiki not found: {rel(root, candidate_wiki)}")
    if not args.reviewer.strip():
        raise ValueError("promote-gap-candidates requires reviewer")
    if not args.approval_note.strip():
        raise ValueError("promote-gap-candidates requires approval note")

    status = _load_status(root, args.run_id)
    items = _gap_review_items(root, candidate_wiki)
    gates = _gap_review_gates(status, items)
    if gates["blockingIssues"]:
        raise ValueError("gap promotion blocked: " + "; ".join(gates["blockingIssues"]))
    package = status.get("gapReviewPackage", {})
    if package.get("state") != "ready-for-human-review":
        raise ValueError("gap promotion requires ready-for-human-review gapReviewPackage")

    approved = [
        item for item in items
        if item["recommendation"] == "approve-for-human-review"
        and item["definitionStatus"] == "reviewed-key-concept"
    ]
    deferred = [item for item in items if item not in approved]
    target_dir.mkdir(parents=True, exist_ok=True)

    promoted = []
    skipped = []
    for item in approved:
        concept = item["candidateConcept"]
        target = target_dir / f"{concept}.md"
        page_text = _format_reviewed_concept_page(
            root=root,
            vault=vault,
            reviewed=reviewed,
            candidate_wiki=candidate_wiki,
            item=item,
            target=target,
            reviewer=args.reviewer,
            approval_note=args.approval_note,
            review_after=args.review_after,
            scope=args.scope,
        )
        if target.exists() and not args.overwrite:
            skipped.append({
                "concept": concept,
                "target": rel(root, target),
                "reason": "target-exists-use-overwrite-to-regenerate",
            })
            continue
        write_text(target, page_text)
        promoted.append({
            "concept": concept,
            "target": rel(root, target),
            "sourceCandidatePage": item["page"],
            "sourcePages": item["sourcePages"],
            "evidenceCount": item["evidenceCount"],
        })

    sync = _sync_reviewed_index(root, vault, reviewed)
    result = {
        "state": "passed" if promoted or skipped else "partial",
        "scope": "reviewed-gap-candidate-promotion",
        "runId": args.run_id,
        "reviewed": rel(root, reviewed),
        "targetDir": rel(root, target_dir),
        "candidateWiki": rel(root, candidate_wiki),
        "reviewer": args.reviewer,
        "reviewedAt": today(),
        "approvalNote": args.approval_note,
        "reviewAfter": args.review_after,
        "approvedCandidateCount": len(approved),
        "promotedCount": len(promoted),
        "skippedExistingCount": len(skipped),
        "deferredCount": len(deferred),
        "promoted": promoted,
        "skipped": skipped,
        "deferred": [
            {
                "concept": item["candidateConcept"],
                "recommendation": item["recommendation"],
                "definitionStatus": item["definitionStatus"],
                "reason": "deferred-for-dedup-or-revise",
            }
            for item in deferred
        ],
        "reviewGates": gates,
        "homeSync": {
            "reviewedPageCount": sync["reviewedPageCount"],
            "written": sync["written"],
        },
        "boundary": "reviewed-concept-promotion-with-explicit-user-approval-no-memory-or-project-facts",
        "report": rel(root, report),
    }
    write_text(report, _format_gap_promotion_report(result))
    update_status(root, args.run_id, {"gapConceptPromotion": result})
    print_json(result)
    return result


def run_govern_vault(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate = _resolve_under_root(root, args.candidate)
    raw = _resolve_under_root(root, args.raw)
    report = _resolve_under_root(root, args.report)

    sync = _sync_reviewed_index(root, vault, reviewed)
    reviewed_records = sync["records"]
    candidate_records = _candidate_inventory(root, candidate, reviewed)
    archive_actions = []
    reviewed_rewrites = []
    if getattr(args, "archive_inactive_candidates", False):
        archive_actions = _archive_inactive_candidates(root, candidate, candidate_records)
        reviewed_rewrites = _rewrite_reviewed_source_traces(root, reviewed, archive_actions)
        candidate_records = _candidate_inventory(root, candidate, reviewed)
    raw_records = _raw_inventory(root, raw)
    active_candidates = [item for item in candidate_records if item["governanceState"] == "active-review"]
    evidence_candidates = [item for item in candidate_records if item["governanceState"] != "active-review"]
    archived_candidates = _archived_candidate_inventory(root, candidate)
    removed_secondary_views = _dedupe_preserve_order(
        sync.get("removedSecondaryViews", []) + _remove_secondary_vault_view_files(root, vault)
    )
    _write_home(
        vault,
        reviewed_records=reviewed_records,
        active_candidates=active_candidates,
        evidence_candidates=evidence_candidates,
        archived_candidates=archived_candidates,
        raw_records=raw_records,
    )

    result = {
        "state": "passed",
        "vault": rel(root, vault),
        "reviewedPageCount": len(reviewed_records),
        "candidateCorpusCount": len(candidate_records),
        "activeReviewCount": len(active_candidates),
        "evidenceOnlyCandidateCount": len(evidence_candidates),
        "archivedCandidateCount": len(archived_candidates),
        "archiveActionCount": len(archive_actions),
        "rawSourceCount": len(raw_records),
        "primaryEntry": rel(root, vault / "Home.md"),
        "removedSecondaryViews": removed_secondary_views,
        "archiveActions": archive_actions,
        "reviewedSourceTraceRewrites": reviewed_rewrites,
        "report": rel(root, report),
        "boundary": "non-destructive-archive-no-reviewed-promotion-single-entry",
    }
    write_text(report, _format_vault_governance_report(result, candidate_records, raw_records, archived_candidates))
    update_status(root, args.run_id, {"knowledgeVaultGovernance": result})
    print_json(result)
    return result


def run_pipeline_smoke(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate_root = _resolve_under_root(root, args.candidate)
    raw_root = _resolve_under_root(root, args.raw)
    run_id = safe_run_id(args.run_id or timestamp_id().replace("rag-candidate", "p5-15-pipeline-smoke"))
    if not getattr(args, "inputs", None):
        raise ValueError("pipeline-smoke requires at least one input")
    if not args.reviewer.strip():
        raise ValueError("pipeline-smoke requires reviewer")
    if not args.approval_note.strip():
        raise ValueError("pipeline-smoke requires approval note")
    if not args.question.strip():
        raise ValueError("pipeline-smoke requires question")

    input_paths = [_resolve_under_root(root, value) for value in args.inputs]
    candidate_wiki = candidate_root / run_id / "wiki"
    run_var = root / "var" / "rag" / run_id
    eval_dir = run_var / "evals"
    graph_dir = run_var / "graph"
    manifest = run_var / "extracted" / "metadata-manifest.json"
    target = _resolve_under_root(root, args.target or f"user/knowledge/reviewed/{run_id}.md")
    report = _resolve_under_root(root, args.report or f"var/rag/{run_id}/evals/pipeline-smoke.md")

    _prepare_pipeline_smoke_run(
        root=root,
        run_id=run_id,
        candidate_run_dir=candidate_root / run_id,
        run_var=run_var,
        target=target,
        overwrite=bool(args.overwrite),
    )

    steps: dict[str, dict] = {}
    steps["ingest"] = _quiet_call(_run_candidate_ingest, SimpleNamespace(
        root=str(root),
        inputs=[str(path) for path in input_paths],
        run_id=run_id,
        copy_raw=bool(args.copy_raw),
        max_chunk_chars=args.max_chunk_chars,
    ))
    steps["smokeCandidateEnrichment"] = _enrich_pipeline_smoke_candidate(
        root=root,
        run_id=run_id,
        manifest_path=manifest,
        wiki=candidate_wiki,
    )
    steps["candidateHealth"] = _quiet_call(_run_candidate_health, SimpleNamespace(
        root=str(root),
        wiki=str(candidate_wiki),
        report=str(eval_dir / "health-report.md"),
        run_id=run_id,
    ))
    steps["candidateLint"] = _quiet_call(_run_candidate_lint, SimpleNamespace(
        root=str(root),
        wiki=str(candidate_wiki),
        report=str(eval_dir / "lint-report.md"),
        run_id=run_id,
    ))
    steps["candidateGraph"] = _quiet_call(_run_candidate_build_graph, SimpleNamespace(
        root=str(root),
        wiki=str(candidate_wiki),
        graph=str(graph_dir),
        report=str(eval_dir / "graph-report.md"),
        run_id=run_id,
    ))
    steps["enrichmentPlan"] = _quiet_call(_run_candidate_enrichment_plan, SimpleNamespace(
        root=str(root),
        manifest=str(manifest),
        wiki=str(candidate_wiki),
        report=str(eval_dir / "enrichment-plan.md"),
        run_id=run_id,
    ))
    steps["reviewPackage"] = _quiet_call(_run_candidate_review_package, SimpleNamespace(
        root=str(root),
        manifest=str(manifest),
        wiki=str(candidate_wiki),
        report=str(eval_dir / "review-package.md"),
        run_id=run_id,
    ))
    steps["promotionPlan"] = _quiet_call(_run_candidate_promotion_plan, SimpleNamespace(
        root=str(root),
        manifest=str(manifest),
        wiki=str(candidate_wiki),
        scope=args.scope,
        target=rel(root, target),
        report=str(eval_dir / "promotion-plan.md"),
        run_id=run_id,
    ))
    steps["promoteReviewed"] = _quiet_call(_run_candidate_promote_reviewed, SimpleNamespace(
        root=str(root),
        manifest=str(manifest),
        wiki=str(candidate_wiki),
        scope=args.scope,
        target=rel(root, target),
        reviewer=args.reviewer,
        approval_note=args.approval_note,
        review_after=args.review_after,
        report=str(eval_dir / "promotion-result.md"),
        run_id=run_id,
        overwrite=bool(args.overwrite),
    ))
    steps["vaultGovernance"] = _quiet_call(run_govern_vault, SimpleNamespace(
        root=str(root),
        vault=str(vault),
        reviewed=str(reviewed),
        candidate=str(candidate_root),
        raw=str(raw_root),
        report=str(root / "var" / "rag" / "reviewed-knowledge" / "evals" / "knowledge-vault-governance.md"),
        archive_inactive_candidates=bool(args.archive_promoted_candidate),
        run_id="reviewed-knowledge",
    ))
    steps["reviewedHealth"] = _quiet_call(run_health_reviewed, SimpleNamespace(
        root=str(root),
        vault=str(vault),
        reviewed=str(reviewed),
        report=str(root / "var" / "rag" / "reviewed-knowledge" / "evals" / "health-report.md"),
        run_id="reviewed-knowledge",
    ))
    steps["reviewedGraph"] = _quiet_call(run_build_reviewed_graph, SimpleNamespace(
        root=str(root),
        vault=str(vault),
        reviewed=str(reviewed),
        graph=str(root / "var" / "rag" / "reviewed-knowledge" / "graph"),
        report=str(root / "var" / "rag" / "reviewed-knowledge" / "evals" / "graph-report.md"),
        run_id="reviewed-knowledge",
    ))
    steps["reviewedQuery"] = _quiet_call(run_query_reviewed, SimpleNamespace(
        root=str(root),
        vault=str(vault),
        reviewed=str(reviewed),
        graph=str(root / "var" / "rag" / "reviewed-knowledge" / "graph" / "graph.json"),
        report=str(eval_dir / "reviewed-query-smoke.md"),
        question=args.question,
        limit=args.limit,
        run_id="reviewed-knowledge",
    ))

    target_ref = rel(root, target)
    candidate_wiki_ref = _pipeline_candidate_wiki_ref_after_governance(root, candidate_wiki, run_id, steps["vaultGovernance"])
    query_hits_target = any(match.get("page") == target_ref for match in steps["reviewedQuery"].get("matches", []))
    blocking = _pipeline_smoke_blocking_issues(steps, query_hits_target)
    result = {
        "state": "passed" if not blocking else "failed",
        "scope": "p5-15-raw-to-reviewed-query-pipeline-smoke",
        "runId": run_id,
        "inputs": [rel(root, path) for path in input_paths],
        "candidateWiki": candidate_wiki_ref,
        "manifest": rel(root, manifest),
        "targetReviewed": target_ref,
        "query": args.question,
        "queryHitsTarget": query_hits_target,
        "archivePromotedCandidate": bool(args.archive_promoted_candidate),
        "steps": _pipeline_step_summary(steps),
        "blockingIssues": blocking,
        "report": rel(root, report),
        "boundary": "stable-command-smoke-with-explicit-approval-no-memory-or-project-facts",
    }
    write_text(report, _format_pipeline_smoke_report(result, steps))
    update_status(root, run_id, {"pipelineSmoke": result})
    print_json(result)
    if blocking:
        raise RuntimeError("pipeline smoke failed: " + "; ".join(blocking))
    return result


def _quiet_call(func, args) -> dict:
    buffer = StringIO()
    with redirect_stdout(buffer):
        return func(args)


def _prepare_pipeline_smoke_run(
    root: Path,
    run_id: str,
    candidate_run_dir: Path,
    run_var: Path,
    target: Path,
    overwrite: bool,
) -> None:
    status = root / "var" / "logs" / f"{run_id}.json"
    existing = [path for path in [candidate_run_dir, run_var, status, target] if path.exists()]
    if existing and not overwrite:
        refs = ", ".join(rel(root, path) for path in existing)
        raise FileExistsError(f"pipeline-smoke run already has outputs; pass -Overwrite or use a new -RunId: {refs}")
    if not overwrite:
        return
    _remove_path_under(root, candidate_run_dir, [root / "user" / "knowledge" / "candidate"])
    _remove_path_under(root, run_var, [root / "var" / "rag"])
    _remove_path_under(root, status, [root / "var" / "logs"])


def _remove_path_under(root: Path, path: Path, allowed_roots: list[Path]) -> None:
    if not path.exists():
        return
    resolved = path.resolve()
    allowed = [item.resolve() for item in allowed_roots]
    if not any(resolved == base or base in resolved.parents for base in allowed):
        raise ValueError(f"refusing to remove path outside allowed runtime boundary: {rel(root, path)}")
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _enrich_pipeline_smoke_candidate(root: Path, run_id: str, manifest_path: Path, wiki: Path) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {rel(root, manifest_path)}")
    manifest = json.loads(read_text(manifest_path))
    sources = manifest.get("sources", [])
    enriched_sources = []
    concept_names: set[str] = set()
    for source in sources:
        candidate_page = _resolve_under_root(root, source.get("candidatePage", ""))
        extracted_path = _resolve_under_root(root, source.get("extractedMarkdown", ""))
        source_text = read_text(candidate_page) if candidate_page.exists() else ""
        extracted = read_text(extracted_path) if extracted_path.exists() else ""
        title = _page_title(source_text, Path(source.get("sourceRef", "source")).stem)
        selected = _pipeline_concepts_for_source(title, extracted)
        concept_names.update(selected)
        write_text(candidate_page, _format_pipeline_source_page(
            existing=source_text,
            title=title,
            run_id=run_id,
            source_ref=source.get("sourceRef", ""),
            extracted_ref=source.get("extractedMarkdown", ""),
            extracted=extracted,
            concepts=selected,
        ))
        enriched_sources.append({
            "sourceId": source.get("id"),
            "candidatePage": rel(root, candidate_page),
            "extractedMarkdown": source.get("extractedMarkdown"),
            "conceptCount": len(selected),
        })

    concept_refs = []
    source_stems = [Path(item.get("candidatePage", "source")).stem for item in sources]
    for concept in sorted(concept_names):
        definition, neighbors = PIPELINE_SMOKE_CONCEPTS[concept]
        page = wiki / "concepts" / f"{concept}.md"
        write_text(page, _format_pipeline_concept_page(
            concept=concept,
            definition=definition,
            neighbors=neighbors,
            source_stems=source_stems,
            run_id=run_id,
        ))
        concept_refs.append(rel(root, page))

    _write_pipeline_candidate_index(root, wiki)
    _append_pipeline_enrichment_log(wiki, run_id, enriched_sources, sorted(concept_names))
    result = {
        "state": "passed" if enriched_sources else "partial",
        "runId": run_id,
        "wiki": rel(root, wiki),
        "sourceCount": len(enriched_sources),
        "conceptCount": len(concept_refs),
        "enrichedSources": enriched_sources,
        "conceptPages": concept_refs,
        "boundary": "candidate-only-smoke-enrichment-no-reviewed-write",
    }
    update_status(root, run_id, {"pipelineSmokeCandidateEnrichment": result})
    return result


def _pipeline_concepts_for_source(title: str, extracted: str) -> list[str]:
    haystack = f"{title}\n{extracted}".lower()
    if "agent harness" not in haystack and "harness engineering" not in haystack:
        return []
    return list(PIPELINE_SMOKE_CONCEPTS.keys())


def _format_pipeline_source_page(
    existing: str,
    title: str,
    run_id: str,
    source_ref: str,
    extracted_ref: str,
    extracted: str,
    concepts: list[str],
) -> str:
    frontmatter = _frontmatter_block(existing) or "\n".join([
        "---",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        "type: source",
        "tags: [candidate, ingestion, pipeline-smoke]",
        f"date: {today()}",
        f"source_file: {json.dumps(source_ref, ensure_ascii=False)}",
        f"extracted_file: {json.dumps(extracted_ref, ensure_ascii=False)}",
        "---",
    ])
    concept_links = ", ".join(f"[[{name}]]" for name in concepts) or "[[StructuredIngestion]], [[CandidateKnowledge]]"
    evidence = _pipeline_evidence_lines(extracted)
    claims = _pipeline_key_claims(concepts)
    entities = _pipeline_entities(concepts)
    return f"""{frontmatter}

# {title}

## Candidate Summary

本页是 P5-15 pipeline smoke 生成的 candidate source page。它基于 `{source_ref}` 的抽取文本 `{extracted_ref}` 生成结构化候选知识，用于验证 raw -> candidate -> approved promotion -> reviewed vault -> query 的稳定命令闭环。

## Key Claims

{claims}

## Entities

{entities}

## Concepts

- 本候选页关联的核心概念：{concept_links}。
- Workflow 概念：[[StructuredIngestion]]、[[CandidateKnowledge]]。

## Contradictions

- 本 smoke enrichment 未发现源内明确矛盾；该结论只表示 deterministic candidate 检查结果，最终仍以 human review 或用户明确批准为准。
- 使用权利（usage rights）和 copyright risk 仍属于审核判断，不由本命令自动定性为通用事实。

## Applicability

- 适用于验证 Harness RAG/Knowledge pipeline 的稳定命令闭环。
- 适用于将 source-grounded candidate 晋升为 user-private reviewed Knowledge 的 smoke case。
- 适用于后续 agent 通过 reviewed-only query 检索并阅读 reviewed Knowledge。

## Non-Applicability

- 不替代 Harness architecture authority。
- 不把 raw PDF、extracted chunks、candidate wiki 或 graph JSON 当作 authoritative knowledge。
- 不作为自动泛化到其他 raw 材料的内容质量评估。

## Source Evidence

{evidence}

## Candidate Notes

- Related workflow: [[StructuredIngestion]].
- Knowledge state: [[CandidateKnowledge]].
- Candidate concepts: {concept_links}.

## Review Checklist

- Source provenance checked.
- Sensitive content checked.
- Usage rights checked.
- Contradictions checked against existing candidate/reviewed material.
- No reviewed knowledge written by candidate enrichment.
"""


def _pipeline_key_claims(concepts: list[str]) -> str:
    if "AgentHarnessEngineering" in concepts:
        return "\n".join([
            "- Agent Harness Engineering 应作为独立系统工程层处理，而不是 prompt 或模型能力的附属细节。",
            "- 长周期 agent 任务可靠性受 execution harness、tool boundary、context、observability、verification 和 governance 共同约束。",
            "- [[ETCLOVGTaxonomy]] 可作为分析 agent harness 的七层框架。",
            "- [[TraceNativeEvaluation]]、[[StandardHandoffProtocol]]、[[AdaptiveHarnessOptimization]] 和 [[ContextDrift]] 是后续 Harness 建设需要持续处理的 reviewed concepts。",
        ])
    return "- 本材料已被转换为 source-grounded candidate page；具体 claims 需要人工审核补充。"


def _pipeline_entities(concepts: list[str]) -> str:
    if "AgentHarnessEngineering" in concepts:
        return "\n".join([
            "- `Agent Harness Engineering`：source material 的核心主题。",
            "- `Harness`：agent 执行、工具、上下文、生命周期、观测、验证和治理的控制层。",
            "- `Agent Runtime`：执行 agent 任务并与 harness 交互的外部主体。",
        ])
    return "- `Source Material`：本轮 pipeline smoke 的输入材料。"


def _pipeline_evidence_lines(extracted: str) -> str:
    lines = []
    for line in extracted.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or any(term in stripped.lower() for term in ["agent harness", "harness engineering", "observability", "verification", "governance"]):
            lines.append(stripped)
        if len(lines) >= 8:
            break
    if not lines:
        lines = [line.strip() for line in extracted.splitlines() if line.strip()][:5]
    return "\n".join(f"- {line[:240]}" for line in lines) if lines else "- No extracted evidence available."


def _format_pipeline_concept_page(
    concept: str,
    definition: str,
    neighbors: list[str],
    source_stems: list[str],
    run_id: str,
) -> str:
    related = ["StructuredIngestion", "CandidateKnowledge"] + neighbors + source_stems
    related_links = ", ".join(f"[[{item}]]" for item in _dedupe_preserve_order(related))
    return f"""---
title: "{concept}"
type: concept
tags: [candidate, pipeline-smoke]
sources: []
last_updated: {today()}
---

# {concept}

## Candidate Definition

{definition}

## Source-Grounded Role

- 本概念页由 P5-15 pipeline smoke 为 `{run_id}` 生成，用于让 candidate wiki 在晋升前具备可检查的 wikilink graph。
- 本页仍属于 candidate Knowledge，不是 reviewed Knowledge。

## Related

{related_links}
"""


def _write_pipeline_candidate_index(root: Path, wiki: Path) -> None:
    source_pages = sorted((wiki / "sources").glob("*.md"))
    concept_pages = sorted((wiki / "concepts").glob("*.md"))
    lines = [
        "# Candidate Wiki Index",
        "",
        "## Overview",
        "- [Overview](overview.md) - candidate corpus synthesis",
        "",
        "## Sources",
    ]
    if source_pages:
        for page in source_pages:
            title = _page_title(read_text(page), page.stem)
            lines.append(f"- [{title}]({rel(wiki, page)}) - candidate source page")
    else:
        lines.append("- _No source pages._")
    lines.extend(["", "## Concepts"])
    if concept_pages:
        for page in concept_pages:
            title = _page_title(read_text(page), page.stem)
            lines.append(f"- [{title}]({rel(wiki, page)}) - candidate concept page")
    else:
        lines.append("- _No concept pages._")
    write_text(wiki / "index.md", "\n".join(lines) + "\n")


def _append_pipeline_enrichment_log(wiki: Path, run_id: str, sources: list[dict], concepts: list[str]) -> None:
    log = read_text(wiki / "log.md") if (wiki / "log.md").exists() else "# Candidate Wiki Log\n"
    lines = [log.rstrip(), "", f"## [{today()}] pipeline-smoke-enrichment | {run_id}", ""]
    for source in sources:
        page_stem = Path(source["candidatePage"]).stem
        lines.append(f"- Enriched source page `{page_stem}` with required review sections.")
    lines.append(f"- Added concept pages: {', '.join(concepts) if concepts else 'none'}.")
    write_text(wiki / "log.md", "\n".join(lines) + "\n")


def _frontmatter_block(text: str) -> str | None:
    match = re.match(r"(?s)^---\n.*?\n---", text.lstrip())
    return match.group(0) if match else None


def _pipeline_step_summary(steps: dict[str, dict]) -> dict[str, dict]:
    summary = {}
    for name, value in steps.items():
        item = {"state": value.get("state", "unknown")}
        for key in [
            "pageCount",
            "nodeCount",
            "edgeCount",
            "matchCount",
            "reviewedPageCount",
            "readyForHumanReviewCount",
            "promotedCount",
            "archiveActionCount",
        ]:
            if key in value:
                item[key] = value[key]
        summary[name] = item
    return summary


def _pipeline_candidate_wiki_ref_after_governance(root: Path, candidate_wiki: Path, run_id: str, governance: dict) -> str:
    for action in governance.get("archiveActions", []):
        if action.get("runId") == run_id and action.get("newPath"):
            return f"{action['newPath'].rstrip('/')}/wiki"
    return rel(root, candidate_wiki)


def _pipeline_smoke_blocking_issues(steps: dict[str, dict], query_hits_target: bool) -> list[str]:
    checks = [
        ("ingest", "passed"),
        ("smokeCandidateEnrichment", "passed"),
        ("candidateHealth", "passed"),
        ("candidateLint", "passed"),
        ("candidateGraph", "passed"),
        ("enrichmentPlan", "passed"),
        ("reviewPackage", "ready-for-human-review"),
        ("promoteReviewed", "promoted"),
        ("vaultGovernance", "passed"),
        ("reviewedHealth", "passed"),
        ("reviewedGraph", "passed"),
        ("reviewedQuery", "passed"),
    ]
    blocking = []
    for name, expected in checks:
        actual = steps.get(name, {}).get("state")
        if actual != expected:
            blocking.append(f"{name} expected {expected}, got {actual}")
    if not steps.get("promotionPlan", {}).get("candidateReady"):
        blocking.append("promotionPlan candidateReady is false")
    if steps.get("reviewedQuery", {}).get("matchCount", 0) < 1:
        blocking.append("reviewedQuery returned no matches")
    if not query_hits_target:
        blocking.append("reviewedQuery did not include the newly promoted reviewed target")
    return blocking


def _format_pipeline_smoke_report(result: dict, steps: dict[str, dict]) -> str:
    lines = [
        f"# P5-15 Pipeline Smoke Report - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Run ID: `{result['runId']}`",
        f"- 输入（Inputs）: {', '.join(f'`{item}`' for item in result['inputs'])}",
        f"- Candidate Wiki: `{result['candidateWiki']}`",
        f"- Reviewed Target: `{result['targetReviewed']}`",
        f"- Query: {result['query']}",
        f"- Query hits target: `{_yes_no(result['queryHitsTarget'])}`",
        f"- Archive promoted candidate: `{_yes_no(result['archivePromotedCandidate'])}`",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## Step Summary",
        "",
        "| Step | State | Key Counts |",
        "|---|---|---|",
    ]
    for name, summary in result["steps"].items():
        counts = ", ".join(f"{key}={value}" for key, value in summary.items() if key != "state") or "-"
        lines.append(f"| `{name}` | `{summary.get('state')}` | {counts} |")
    lines.extend(["", "## Blocking Issues", ""])
    lines.extend(f"- {item}" for item in result["blockingIssues"] or ["无"])
    lines.extend([
        "",
        "## Reviewed Query Matches",
        "",
    ])
    for match in steps.get("reviewedQuery", {}).get("matches", []):
        lines.append(f"- `{match.get('page')}` - {match.get('title')} (score={match.get('score')})")
    lines.extend([
        "",
        "## Governance Boundary",
        "",
        "- 本 smoke 使用 explicit approval 参数执行 reviewed promotion。",
        "- Candidate wiki、chunks、graph、eval reports 和 status JSON 仍是证据或运行态产物，不是 authoritative knowledge。",
        "- 本命令不写入 Memory、Project Facts 或 Harness architecture authority。",
        "",
    ])
    return "\n".join(lines)


def _sync_reviewed_index(root: Path, vault: Path, reviewed: Path) -> dict:
    vault.mkdir(parents=True, exist_ok=True)
    reviewed.mkdir(parents=True, exist_ok=True)
    pages = _reviewed_pages(reviewed)
    records = [_page_record(root, vault, p) for p in pages]
    records.sort(key=lambda item: item["title"].lower())
    _write_home(vault, reviewed_records=records)
    removed = _remove_secondary_vault_view_files(root, vault)
    return {
        "reviewedPageCount": len(records),
        "written": [
            rel(root, vault / "Home.md"),
        ],
        "removedSecondaryViews": removed,
        "records": records,
    }


def _query_reviewed(root: Path, vault: Path, reviewed: Path, graph_path: Path, question: str, limit: int) -> dict:
    pages = _reviewed_pages(reviewed)
    terms = _query_terms(question)
    scored: dict[Path, dict] = {}
    for page in pages:
        text = read_text(page)
        title = _page_title(text, page.stem)
        haystacks = {
            "title": title,
            "path": rel(vault, page),
            "body": text,
        }
        score = 0.0
        reasons = []
        for term in terms:
            term_lower = term.lower()
            for field, value in haystacks.items():
                hits = value.lower().count(term_lower)
                if not hits:
                    continue
                weight = 5 if field == "title" else 2 if field == "path" else 1
                score += hits * weight
                reasons.append(f"{field}:{term}")
        if score > 0:
            scored[page] = {
                "page": rel(root, page),
                "vaultPath": rel(vault, page),
                "title": title,
                "score": round(score, 3),
                "reason": sorted(set(reasons)),
                "reviewedAt": _frontmatter_value(text, "reviewedAt") or _nested_reviewed_at(text),
                "reviewedBy": _frontmatter_value(text, "reviewedBy") or _nested_reviewed_by(text),
                "matchedSections": _matched_sections(text, terms),
                "wikilinks": sorted(set(extract_wikilinks(text)))[:20],
            }

    _expand_query_from_graph(root, vault, graph_path, scored)
    matches = sorted(scored.values(), key=lambda item: (-item["score"], item["vaultPath"]))[:limit]
    return {
        "state": "passed",
        "scope": "reviewed-knowledge",
        "question": question,
        "terms": terms,
        "matchCount": len(matches),
        "matches": matches,
        "answerInstruction": "Agent must read matched reviewed pages before answering. Do not cite raw/candidate/chunks as facts.",
    }


def _write_home(
    vault: Path,
    reviewed_records: list[dict] | None = None,
    active_candidates: list[dict] | None = None,
    evidence_candidates: list[dict] | None = None,
    archived_candidates: list[dict] | None = None,
    raw_records: list[dict] | None = None,
) -> None:
    reviewed_records = reviewed_records or []
    active_candidates = active_candidates or []
    evidence_candidates = evidence_candidates or []
    archived_candidates = archived_candidates or []
    raw_records = raw_records or []

    lines = [
        "---",
        "title: Harness Knowledge Vault Home",
        "type: vault-index",
        f"last_updated: {today()}",
        "entry_policy: single-entry",
        "---",
        "# Harness Knowledge Vault",
        "",
        "这是 Obsidian vault 的单一入口。默认事实源只看 `reviewed/`；用户审核候选时只看本页的 Candidate Review Queue。",
        "",
        "## Reviewed Knowledge",
        "",
        "| Title | Scope | Review |",
        "|---|---|---|",
    ]
    if reviewed_records:
        for item in reviewed_records:
            lines.append(
                f"| [[{item['vaultStem']}|{item['title']}]] | `{item['scope']}` | "
                f"{item.get('reviewedBy') or 'unknown'} / {item.get('reviewedAt') or 'unknown'} |"
            )
    else:
        lines.append("| _No reviewed Knowledge yet._ |  |  |")

    lines.extend([
        "",
        "## Candidate Review Queue",
        "",
        "| Corpus | State | Pages | Review Package | Decision Summary | Entry |",
        "|---|---|---:|---|---|---|",
    ])
    if active_candidates:
        for item in active_candidates:
            package = item["reviewPackage"] or "missing"
            lines.append(
                f"| `{item['runId']}` | `{item['governanceState']}` | {item['markdownCount']} | "
                f"`{package}` | {item['decisionSummary']} | {_candidate_entry_link(item)} |"
            )
    else:
        lines.append("| _No active candidate for human review._ |  |  |  |  |  |")

    package_items = _active_candidate_package_items(active_candidates)
    if package_items:
        lines.extend([
            "",
            "### Current Candidate Items",
            "",
            "| Concept | Recommendation | Definition Status | Evidence | Page |",
            "|---|---|---|---:|---|",
        ])
        for item in package_items:
            lines.append(
                f"| `{item['candidateConcept']}` | `{item['recommendation']}` | "
                f"`{item['definitionStatus']}` | {item['evidenceCount']} | "
                f"{_vault_markdown_link(item['candidateConcept'], item['page'])} |"
            )

    lines.extend([
        "",
        "## Archived Candidate Evidence",
        "",
        "| Corpus | State | Pages | Archive Path |",
        "|---|---|---:|---|",
    ])
    inactive_records = archived_candidates or evidence_candidates
    if inactive_records:
        for item in inactive_records:
            lines.append(
                f"| `{item['runId']}` | `{item['governanceState']}` | "
                f"{item['markdownCount']} | `{item['path']}` |"
            )
    else:
        lines.append("| _No archived or inactive candidate corpus._ |  |  |  |")

    lines.extend([
        "",
        "## Raw Sources",
        "",
        "| Source | Size | Modified |",
        "|---|---:|---|",
    ])
    if raw_records:
        for item in raw_records:
            lines.append(f"| `{item['path']}` | {item['size']} | {item['modified']} |")
    else:
        lines.append("| _No raw sources._ |  |  |")

    lines.extend([
        "",
        "## Governance Rules",
        "",
        "- `reviewed/` 是默认 authoritative knowledge source。",
        "- `raw/` 只作为 provenance 使用。",
        "- `candidate/` 根目录只保留当前 active-review candidate；历史候选归档到 `candidate/_archive/`。",
        "- Candidate review package 不是 promotion approval；candidate -> reviewed 必须有用户审核或明确批准。",
        "- `var/rag/`、graph、chunks、eval reports 和 status JSON 都是可重建运行态产物，不是事实源。",
        "- `README.md` 是文件系统边界说明，不作为 Obsidian 日常入口。",
        "",
    ])
    write_text(vault / "Home.md", "\n".join(lines))


def _format_knowledge_index(records: list[dict]) -> str:
    return "\n".join([
        "---",
        "title: Knowledge Index",
        "type: vault-index",
        f"last_updated: {today()}",
        "---",
        "# Knowledge Index",
        "",
        "本文件是 vault 总索引。日常阅读从 `Home.md` 进入；事实回答优先使用 reviewed Knowledge。",
        "",
        "## Reviewed Knowledge",
        "",
        "- [[ReviewedKnowledgeIndex]] - reviewed Knowledge 列表。",
        "- [[ReviewedOverview]] - reviewed Knowledge 概览。",
        "",
        "## Human Review",
        "",
        "- [Candidate Review Queue](CandidateReviewQueue.md) - 当前待审核候选。",
        "- [Candidate Review Package](CandidateReviewPackage.md) - 当前审核包。",
        "- [Candidate Evidence Index](CandidateEvidenceIndex.md) - 历史候选、已晋升证据、测试候选。",
        "",
        "## Provenance And Rules",
        "",
        "- [Raw Source Index](RawSourceIndex.md) - raw source provenance。",
        "- [Knowledge Governance](KnowledgeGovernance.md) - Obsidian 阅读和治理规则。",
        "- [Boundary README](README.md) - 本地知识边界说明。",
        "",
        f"Reviewed Knowledge count: {len(records)}",
        "",
    ])


def _format_reviewed_index(records: list[dict]) -> str:
    lines = [
        "---",
        "title: Reviewed Knowledge Index",
        "type: reviewed-index",
        f"last_updated: {today()}",
        "---",
        "# Reviewed Knowledge Index",
        "",
        "本索引由 stable tool 生成，用于 Obsidian 阅读和 agent reviewed query。事实源仍是 `reviewed/` 下的 reviewed Knowledge 文档。",
        "",
        "| Title | Scope | Reviewed | Source Trace |",
        "|---|---|---|---|",
    ]
    for record in records:
        link = f"[[{record['vaultStem']}|{record['title']}]]"
        lines.append(f"| {link} | `{record['scope']}` | {record['reviewedBy']} / {record['reviewedAt']} | {record['sourceTrace']} |")
    if not records:
        lines.append("| _No reviewed knowledge yet._ |  |  |  |")
    lines.append("")
    return "\n".join(lines)


def _format_reviewed_overview(records: list[dict]) -> str:
    by_scope = Counter(record["scope"] for record in records)
    lines = [
        "---",
        "title: Reviewed Knowledge Overview",
        "type: reviewed-overview",
        f"last_updated: {today()}",
        "---",
        "# Reviewed Knowledge Overview",
        "",
        f"Reviewed Knowledge documents: {len(records)}",
        "",
        "## Scope Summary",
        "",
    ]
    if by_scope:
        for scope, count in sorted(by_scope.items()):
            lines.append(f"- `{scope}`: {count}")
    else:
        lines.append("- No reviewed knowledge yet.")
    lines.extend(["", "## Documents", ""])
    for record in records:
        lines.append(f"- [[{record['vaultStem']}|{record['title']}]] - {record['purpose']}")
    lines.append("")
    return "\n".join(lines)


def _format_health_report(result: dict) -> str:
    return "\n".join([
        f"# Reviewed Knowledge Health Report - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Reviewed pages: {result['reviewedPageCount']}",
        f"- Missing index files: {len(result['missingIndexFiles'])}",
        f"- Missing frontmatter: {len(result['missingFrontmatter'])}",
        f"- Missing review metadata: {len(result['missingReviewMetadata'])}",
        f"- Sensitive findings: {len(result['sensitiveFindings'])}",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])


def _format_graph_report(result: dict, health: dict) -> str:
    return "\n".join([
        f"# Reviewed Knowledge Graph Report - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Nodes: {result['nodeCount']}",
        f"- Edges: {result['edgeCount']}",
        f"- Orphans: {result['orphanCount']}",
        f"- Broken link refs: {result['brokenLinkCount']}",
        "",
        "## Health",
        "",
        "```json",
        json.dumps(health, indent=2, ensure_ascii=False),
        "```",
        "",
    ])


def _format_query_report(result: dict) -> str:
    lines = [
        f"# Reviewed Knowledge Query Report - {today()}",
        "",
        f"- Question: {result['question']}",
        f"- Match count: {result['matchCount']}",
        "",
    ]
    for match in result["matches"]:
        lines.extend([
            f"## {match['title']}",
            "",
            f"- Page: `{match['page']}`",
            f"- Score: `{match['score']}`",
            f"- Reasons: {', '.join(match['reason'])}",
            "",
        ])
        for section in match["matchedSections"]:
            lines.append(f"- `{section['heading']}`: {section['excerpt']}")
        lines.append("")
    return "\n".join(lines)


def _format_gap_plan_report(result: dict) -> str:
    lines = [
        f"# Reviewed Knowledge Gap Plan - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Reviewed pages: {result['reviewedPageCount']}",
        f"- Gap count: {result['gapCount']}",
        f"- Candidate wiki: `{result['candidateWiki']}`",
        f"- Candidate written: `{_yes_no(result['candidateWritten'])}`",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## 处理规则",
        "",
        "- 本报告只把 reviewed Knowledge 中尚未落地的 wikilinks 转为 candidate enrichment 任务。",
        "- Candidate concept pages 不是 reviewed Knowledge，不能作为事实源回答用户问题。",
        "- 后续若要晋升概念页，必须重新走 candidate review 和 explicit approval。",
        "",
        "## Gap Items",
        "",
    ]
    if not result["gaps"]:
        lines.append("- 未发现 unresolved reviewed wikilinks。")
    for gap in result["gaps"]:
        lines.extend([
            f"### {gap['link']}",
            "",
            f"- Candidate concept: `[[{gap['candidateConcept']}]]`",
            f"- Suggested page: `{gap['suggestedCandidatePage']}`",
            f"- Action: `{gap['action']}`",
            "- Referenced by:",
        ])
        lines.extend(f"  - `{item}`" for item in gap["referencedBy"])
        lines.append("")
    lines.extend([
        "## JSON",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    return "\n".join(lines)


def _format_gap_enrichment_report(result: dict) -> str:
    lines = [
        f"# Gap Candidate Enrichment Report - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Candidate wiki: `{result['candidateWiki']}`",
        f"- Enriched pages: {result['enrichedPageCount']}",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## 处理规则",
        "",
        "- 本命令只补强 candidate gap pages，不写入 reviewed Knowledge。",
        "- 定义只来自 reviewed Knowledge 的 Key Concepts 或明确引用行；没有 reviewed 定义时标记为 dedup / workflow-boundary 待审。",
        "- 后续 promotion 必须重新走 human review 和 explicit approval。",
        "",
        "## Enriched Pages",
        "",
    ]
    for item in result["enriched"]:
        lines.extend([
            f"### {item['candidateConcept']}",
            "",
            f"- Page: `{item['page']}`",
            f"- Original link: `[[{item['originalLink']}]]`",
            f"- Definition status: `{item['definitionStatus']}`",
            f"- Evidence count: {item['evidenceCount']}",
            f"- Promotion hint: `{item['promotionHint']}`",
            "",
        ])
    lines.extend([
        "## JSON",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    return "\n".join(lines)


def _format_gap_review_package(result: dict) -> str:
    gates = result["reviewGates"]
    lines = [
        f"# Gap Candidate Review Package - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Candidate wiki: `{result['candidateWiki']}`",
        f"- Candidate concepts: {result['candidateConceptCount']}",
        f"- Ready for human review: {result['readyForHumanReviewCount']}",
        f"- Dedup before promotion: {result['dedupBeforePromotionCount']}",
        f"- Revise before review: {result['reviseBeforeReviewCount']}",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## 审核门禁（Review Gates）",
        "",
        f"- Health: `{gates['health']}`",
        f"- Lint: `{gates['lint']}`",
        f"- Graph: `{gates['graph']}`",
        f"- Enrichment: `{gates['enrichment']}`",
        f"- Required fields: `{gates['requiredFields']}`",
        f"- Human approval: `{gates['humanApproval']}`",
        "",
        "### Blocking Issues",
        "",
    ]
    lines.extend(f"- {item}" for item in gates["blockingIssues"] or ["无"])
    lines.extend([
        "",
        "## Candidate Decisions",
        "",
        "| Concept | Definition Status | Evidence | Recommendation | Promotion Hint |",
        "|---|---|---:|---|---|",
    ])
    for item in result["items"]:
        lines.append(
            f"| `[[{item['candidateConcept']}]]` | `{item['definitionStatus']}` | "
            f"{item['evidenceCount']} | `{item['recommendation']}` | `{item['promotionHint']}` |"
        )

    lines.extend([
        "",
        "## Detail",
        "",
    ])
    for item in result["items"]:
        lines.extend([
            f"### {item['candidateConcept']}",
            "",
            f"- Page: `{item['page']}`",
            f"- Original link: `[[{item['originalLink']}]]`",
            f"- Definition status: `{item['definitionStatus']}`",
            f"- Recommendation: `{item['recommendation']}`",
            f"- Promotion hint: `{item['promotionHint']}`",
            f"- Source pages: {', '.join(f'`{source}`' for source in item['sourcePages']) if item['sourcePages'] else '`missing`'}",
            "",
            "Candidate definition:",
            "",
            item["definition"] or "_No definition extracted._",
            "",
            "Review notes:",
        ])
        lines.extend(f"- {note}" for note in item["reviewNotes"])
        lines.append("")

    lines.extend([
        "## Reviewer Decision Template",
        "",
        "```yaml",
        "reviewPackage: gap-candidate-review-package",
        f"candidateWiki: {result['candidateWiki']}",
        "reviewer: null",
        "reviewedAt: null",
        "overallDecision: approve-selected | defer | reject | revise",
        "conceptDecisions:",
    ])
    for item in result["items"]:
        default_decision = "dedup" if item["recommendation"] == "dedup-before-promotion" else "approve-for-promotion" if item["recommendation"] == "approve-for-human-review" else "revise"
        lines.extend([
            f"  {item['candidateConcept']}:",
            f"    decision: {default_decision} # approve-for-promotion | dedup | defer | reject | revise",
            "    reason: null",
            "    targetReviewedPath: null",
        ])
    lines.extend([
        "```",
        "",
        "## Governance Boundary",
        "",
        "- 本 review package 不写入 reviewed Knowledge。",
        "- 即使 reviewer 在模板中填写 approve，仍需后续独立 promotion command 或人工写入流程。",
        "- Candidate pages、report、graph 和 status JSON 仍是候选证据或运行态产物，不是 authoritative knowledge。",
        "",
    ])
    return "\n".join(lines)


def _format_candidate_review_queue(records: list[dict]) -> str:
    lines = [
        "---",
        "title: Candidate Review Queue",
        "type: candidate-review-queue",
        f"last_updated: {today()}",
        "review_state: active-review-only",
        "---",
        "# Candidate Review Queue",
        "",
        "本页只列当前应由用户审核的 candidate corpus。历史候选、重复候选、测试候选和已晋升证据不在本页审核。",
        "",
        "| Corpus | State | Pages | Review Package | Runtime Report | Decision Summary |",
        "|---|---|---:|---|---|---|",
    ]
    if not records:
        lines.append("| _No active candidate review queue._ |  |  |  |  |  |")
    for item in records:
        review_package = "[CandidateReviewPackage](CandidateReviewPackage.md)"
        runtime_report = item.get("reviewPackage") or "missing"
        summary = item.get("decisionSummary") or "pending"
        lines.append(
            f"| `{item['runId']}` | `{item['governanceState']}` | {item['markdownCount']} | "
            f"{review_package} | `{runtime_report}` | {summary} |"
        )
    lines.extend([
        "",
        "## 审核规则",
        "",
        "- 本页是人类审核入口，不是事实源。",
        "- 审核时先看 review package，再打开 candidate pages。",
        "- 审核通过后仍需独立 promotion 流程；本页不写 reviewed Knowledge。",
        "",
    ])
    return "\n".join(lines)


def _format_current_candidate_review_package(records: list[dict]) -> str:
    lines = [
        "---",
        "title: Candidate Review Package",
        "type: candidate-review-package",
        f"last_updated: {today()}",
        "review_state: active-review",
        "---",
        "# Candidate Review Package",
        "",
        "本页是当前 candidate review package 的 Obsidian 镜像，便于用户审核。事实源仍是 reviewed Knowledge；本页不代表 promotion approval。",
        "",
    ]
    if not records:
        lines.extend([
            "当前没有 active candidate review package。",
            "",
        ])
        return "\n".join(lines)

    for record in records:
        package = record.get("reviewPackageData") or {}
        lines.extend([
            f"## Corpus: `{record['runId']}`",
            "",
            f"- Runtime report: `{record.get('reviewPackage') or 'missing'}`",
            f"- State: `{package.get('state', 'missing')}`",
            f"- Ready: {package.get('readyForHumanReviewCount', 0)}",
            f"- Dedup: {package.get('dedupBeforePromotionCount', 0)}",
            f"- Revise: {package.get('reviseBeforeReviewCount', 0)}",
            f"- Boundary: `{package.get('boundary', 'candidate-only-no-promotion')}`",
            "",
            "### Decisions",
            "",
            "| Concept | Recommendation | Definition Status | Evidence | Candidate Page |",
            "|---|---|---|---:|---|",
        ])
        for item in package.get("items", []):
            page = _vault_relative_candidate_page(item.get("page", ""))
            page_link = f"[{item.get('candidateConcept')}](<{page}>)" if page else item.get("candidateConcept")
            lines.append(
                f"| `{item.get('candidateConcept')}` | `{item.get('recommendation')}` | "
                f"`{item.get('definitionStatus')}` | {item.get('evidenceCount', 0)} | {page_link} |"
            )
        lines.extend([
            "",
            "### Reviewer Decision Template",
            "",
            "```yaml",
            f"corpus: {record['runId']}",
            "reviewer: null",
            "reviewedAt: null",
            "overallDecision: approve-selected | defer | reject | revise",
            "conceptDecisions:",
        ])
        for item in package.get("items", []):
            default_decision = "dedup" if item.get("recommendation") == "dedup-before-promotion" else "approve-for-promotion" if item.get("recommendation") == "approve-for-human-review" else "revise"
            lines.extend([
                f"  {item.get('candidateConcept')}:",
                f"    decision: {default_decision}",
                "    reason: null",
                "    targetReviewedPath: null",
            ])
        lines.extend([
            "```",
            "",
        ])
    lines.extend([
        "## Boundary",
        "",
        "- 本页不是 reviewed Knowledge。",
        "- 审核通过后仍需独立 promotion command 或人工晋升记录。",
        "- `dedup-before-promotion` 项不应直接晋升；应先合并或确认已有 workflow/概念页。",
        "",
    ])
    return "\n".join(lines)


def _format_reviewed_concept_page(
    root: Path,
    vault: Path,
    reviewed: Path,
    candidate_wiki: Path,
    item: dict,
    target: Path,
    reviewer: str,
    approval_note: str,
    review_after: str,
    scope: str,
) -> str:
    concept = item["candidateConcept"]
    candidate_page = root / item["page"]
    candidate_text = read_text(candidate_page) if candidate_page.exists() else ""
    definition = item.get("definition") or _candidate_definition(candidate_text)
    aliases = _candidate_aliases(candidate_text)
    reviewed_evidence = _section_by_heading(candidate_text, "Reviewed Evidence")
    source_pages = item.get("sourcePages") or _frontmatter_sources(candidate_text)
    source_refs = _dedupe_preserve_order(
        source_pages + [
            rel(root, candidate_page),
            rel(root, candidate_wiki),
        ]
    )
    evidence_rows = _reviewed_evidence_rows(reviewed_evidence, source_pages)
    source_ref_lines = "\n".join(f"  - {source}" for source in source_refs) or "  []"
    related_lines = "\n".join(f"  - {source}" for source in source_pages) or "  []"
    target_rel = rel(root, target)
    reviewed_rel = rel(root, reviewed)
    vault_path = rel(vault, target)

    return f"""---
documentName: {target_rel}
version: v1.0.0-reviewed-gap-concept
updatedAt: {today()} 00:00:00.000 +08:00
status: active
purpose: 保存经过用户批准的 reviewed gap concept：{concept}。
scope:
  - reviewed-knowledge
  - user-private
  - agent-harness-engineering
prerequisites:
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
{related_lines}
  - {rel(root, candidate_page)}
outputTo:
  - {target_rel}
owner: user
reviewAfter: {review_after}
supersededBy:
dependsOn:
{source_ref_lines}
review:
  reviewedBy: {reviewer}
  reviewedAt: {today()}
  decision: user-approved-gap-concept-promotion
---
# {concept}

## 元数据

```yaml
knowledgeId: reviewed-gap-concept-{concept}
conceptId: {concept}
scope: {scope}
domain: agent-harness-engineering
projectId: null
reviewedAt: {today()}
reviewedBy: {reviewer}
sourceRefs:
{source_ref_lines}
supersedes: []
reviewAfter: {review_after}
sensitiveRisk: low
storageBoundary: {reviewed_rel}
vaultPath: {vault_path}
approvalNote: {json.dumps(approval_note, ensure_ascii=False)}
```

## Statement

{definition}

## Applicability

- 适用于讨论 Agent Harness Engineering 中与 `{concept}` 相关的设计判断、边界或验证任务。
- 适用于解释 reviewed Knowledge 中对 `[[{concept}]]` 的概念引用。
- 可作为 agent 查询 reviewed Knowledge 时的独立概念页。

## Non-Applicability

- 本页不是原始论文或 raw source 的替代物。
- 本页不覆盖 Harness architecture authority；如与架构权威冲突，应进入 governance review。
- 本页不写入 Memory、Project Facts 或 RAG Index。

## Key Concepts

| Concept | Definition | Aliases |
|---|---|---|
| `{concept}` | {definition} | {aliases} |

## Source Trace

| Source | Evidence Summary | Notes |
|---|---|---|
{evidence_rows}

## Staleness

- 默认复审条件：`{review_after}`。
- 如果 source reviewed Knowledge 被更新、候选证据被废弃，或本概念与后续 Harness governance 文档冲突，应重新 review。

## Governance Notes

- 本页由 `promote-gap-candidates` 在用户明确批准后生成。
- Candidate page 和 runtime reports 只作为 source trace，不反向成为 authoritative knowledge。
- 该晋升不修改 Memory、Project Facts 或 Harness architecture authority。
"""


def _candidate_aliases(candidate_text: str) -> str:
    match = re.search(r"^Aliases:\s*`([^`]+)`", candidate_text, re.MULTILINE)
    return match.group(1).strip() if match else "none"


def _reviewed_evidence_rows(reviewed_evidence: str, source_pages: list[str]) -> str:
    rows = []
    for line in reviewed_evidence.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- `"):
            continue
        match = re.match(r"- `([^`]+)` / `([^`]+)`: (.+)", stripped)
        if match:
            source, heading, excerpt = match.groups()
            rows.append(
                f"| `{_markdown_table_cell(source)}` | "
                f"{_markdown_table_cell(excerpt)} | "
                f"Section `{_markdown_table_cell(heading)}`. |"
            )
        else:
            rows.append(
                f"| reviewed evidence | {_markdown_table_cell(stripped.lstrip('- ').strip())} | "
                "Candidate evidence excerpt. |"
            )
    if rows:
        return "\n".join(rows)
    if source_pages:
        return "\n".join(
            f"| `{_markdown_table_cell(source)}` | Reviewed source page. | Source page listed by candidate evidence. |"
            for source in source_pages
        )
    return "| reviewed source | Evidence missing from candidate page. | Requires re-review if reused. |"


def _markdown_table_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def _format_gap_promotion_report(result: dict) -> str:
    lines = [
        f"# Reviewed Gap Concept Promotion Report - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Run ID: `{result['runId']}`",
        f"- Candidate wiki: `{result['candidateWiki']}`",
        f"- Target dir: `{result['targetDir']}`",
        f"- Reviewer: `{result['reviewer']}`",
        f"- Reviewed at: `{result['reviewedAt']}`",
        f"- Approval note: {result['approvalNote']}",
        f"- Approved candidate count: {result['approvedCandidateCount']}",
        f"- Promoted count: {result['promotedCount']}",
        f"- Skipped existing count: {result['skippedExistingCount']}",
        f"- Deferred count: {result['deferredCount']}",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Promoted Concepts",
        "",
        "| Concept | Target | Evidence |",
        "|---|---|---:|",
    ]
    if result["promoted"]:
        for item in result["promoted"]:
            lines.append(f"| `{item['concept']}` | `{item['target']}` | {item['evidenceCount']} |")
    else:
        lines.append("| _No concepts promoted in this run._ |  |  |")
    lines.extend([
        "",
        "## Skipped Existing",
        "",
    ])
    if result["skipped"]:
        lines.extend(f"- `{item['concept']}` -> `{item['target']}`: {item['reason']}" for item in result["skipped"])
    else:
        lines.append("- No existing targets skipped.")
    lines.extend([
        "",
        "## Deferred Items",
        "",
        "| Concept | Recommendation | Definition Status | Reason |",
        "|---|---|---|---|",
    ])
    if result["deferred"]:
        for item in result["deferred"]:
            lines.append(
                f"| `{item['concept']}` | `{item['recommendation']}` | "
                f"`{item['definitionStatus']}` | {item['reason']} |"
            )
    else:
        lines.append("| _No deferred items._ |  |  |  |")
    lines.extend([
        "",
        "## Review Gates",
        "",
        "```json",
        json.dumps(result["reviewGates"], indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    return "\n".join(lines)


def _format_candidate_evidence_index(records: list[dict]) -> str:
    lines = [
        "---",
        "title: Candidate Evidence Index",
        "type: candidate-evidence-index",
        f"last_updated: {today()}",
        "review_state: evidence-only",
        "---",
        "# Candidate Evidence Index",
        "",
        "本页列出不属于当前审核队列的 candidate corpus。它们可能是已晋升证据、历史重复候选或测试烟囱，不应要求用户逐一审核。",
        "",
        "| Corpus | Governance State | Reason | Pages | Wiki |",
        "|---|---|---|---:|---|",
    ]
    if not records:
        lines.append("| _No evidence-only candidates._ |  |  |  |  |")
    for item in records:
        lines.append(
            f"| `{item['runId']}` | `{item['governanceState']}` | {item['reason']} | "
            f"{item['markdownCount']} | `{item['wiki']}` |"
        )
    lines.extend([
        "",
        "## 使用规则",
        "",
        "- `promoted-evidence` 只作为 reviewed Knowledge 的 source trace 证据保留。",
        "- `legacy-or-test-candidate` 不进入当前用户审核；如要复用，需重新生成 review package。",
        "- 不要从本页直接回答事实问题。",
        "",
    ])
    return "\n".join(lines)


def _format_raw_source_index(records: list[dict]) -> str:
    lines = [
        "---",
        "title: Raw Source Index",
        "type: raw-source-index",
        f"last_updated: {today()}",
        "---",
        "# Raw Source Index",
        "",
        "Raw source 只作为 provenance，不是 reviewed Knowledge。Agent 回答事实问题时不直接引用 raw，除非任务明确要求重新摄取或复核来源。",
        "",
        "| Source | Size | Modified |",
        "|---|---:|---|",
    ]
    if not records:
        lines.append("| _No raw sources._ |  |  |")
    for item in records:
        lines.append(f"| `{item['path']}` | {item['size']} | {item['modified']} |")
    lines.append("")
    return "\n".join(lines)


def _format_knowledge_governance() -> str:
    return "\n".join([
        "---",
        "title: Knowledge Governance",
        "type: knowledge-governance",
        f"last_updated: {today()}",
        "---",
        "# Knowledge Governance",
        "",
        "## Obsidian 阅读规则",
        "",
        "- 日常阅读从 [Home](Home.md) 进入。",
        "- Agent 回答事实问题时默认只使用 `reviewed/` 下的 reviewed Knowledge。",
        "- 用户审核候选时只看 [Candidate Review Queue](CandidateReviewQueue.md)。",
        "- [Candidate Evidence Index](CandidateEvidenceIndex.md) 中的历史候选和已晋升证据不属于当前审核队列。",
        "- [Raw Source Index](RawSourceIndex.md) 只用于 provenance 和重新摄取。",
        "",
        "## Index 规则",
        "",
        "- `Home.md` 是唯一主入口。",
        "- `KnowledgeIndex.md` 是总索引，供 Obsidian 导航。",
        "- `ReviewedKnowledgeIndex.md` 和 `ReviewedOverview.md` 是 reviewed collection view，可由 stable tool 重建。",
        "- `README.md` 是文件系统边界说明，不作为日常 Obsidian 入口。",
        "",
        "## Promotion 规则",
        "",
        "- candidate -> reviewed 必须有人类审核或用户明确批准。",
        "- review package 不是 promotion approval。",
        "- RAG graph、chunks、eval reports 和 status JSON 都是可重建产物，不是事实源。",
        "",
    ])


def _remove_secondary_vault_view_files(root: Path, vault: Path) -> list[str]:
    removed = []
    for name in sorted(SECONDARY_VAULT_VIEW_FILES):
        path = vault / name
        if path.exists() and path.is_file():
            path.unlink()
            removed.append(rel(root, path))
    return removed


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _candidate_entry_link(item: dict) -> str:
    wiki = item.get("wiki") or "missing"
    if wiki == "missing":
        return "`missing`"
    return _vault_markdown_link("wiki", f"{wiki}/index.md")


def _active_candidate_package_items(active_candidates: list[dict]) -> list[dict]:
    items = []
    for candidate in active_candidates:
        package = candidate.get("reviewPackageData") or {}
        for item in package.get("items", []):
            items.append({
                "candidateConcept": item.get("candidateConcept", "unknown"),
                "recommendation": item.get("recommendation", "unknown"),
                "definitionStatus": item.get("definitionStatus", "unknown"),
                "evidenceCount": item.get("evidenceCount", 0),
                "page": item.get("page", ""),
            })
    return items


def _vault_markdown_link(label: str, path: str) -> str:
    vault_path = _vault_relative_candidate_page(path)
    return f"[{label}](<{vault_path}>)"


def _format_vault_governance_report(
    result: dict,
    candidate_records: list[dict],
    raw_records: list[dict],
    archived_candidates: list[dict],
) -> str:
    lines = [
        f"# Knowledge Vault Governance Report - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Vault: `{result['vault']}`",
        f"- Reviewed pages: {result['reviewedPageCount']}",
        f"- Candidate corpus count: {result['candidateCorpusCount']}",
        f"- Active review count: {result['activeReviewCount']}",
        f"- Evidence-only candidate count: {result['evidenceOnlyCandidateCount']}",
        f"- Archived candidate count: {result['archivedCandidateCount']}",
        f"- Archive actions: {result['archiveActionCount']}",
        f"- Raw source count: {result['rawSourceCount']}",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Candidate Classification",
        "",
        "| Corpus | State | Reason |",
        "|---|---|---|",
    ]
    for item in candidate_records:
        lines.append(f"| `{item['runId']}` | `{item['governanceState']}` | {item['reason']} |")
    lines.extend([
        "",
        "## Archived Candidates",
        "",
        "| Corpus | State | Archive Path |",
        "|---|---|---|",
    ])
    if archived_candidates:
        for item in archived_candidates:
            lines.append(f"| `{item['runId']}` | `{item['governanceState']}` | `{item['path']}` |")
    else:
        lines.append("| _No archived candidates._ |  |  |")
    lines.extend([
        "",
        "## Archive Actions",
        "",
    ])
    if result.get("archiveActions"):
        lines.extend(
            f"- `{item['oldPath']}` -> `{item['newPath']}` ({item['governanceState']})"
            for item in result["archiveActions"]
        )
    else:
        lines.append("- No candidate directories moved in this run.")
    lines.extend([
        "",
        "## Reviewed Source Trace Rewrites",
        "",
    ])
    if result.get("reviewedSourceTraceRewrites"):
        lines.extend(f"- `{item}`" for item in result["reviewedSourceTraceRewrites"])
    else:
        lines.append("- No reviewed source trace rewrites in this run.")
    lines.extend([
        "",
        "## Removed Secondary Vault Views",
        "",
    ])
    if result.get("removedSecondaryViews"):
        lines.extend(f"- `{item}`" for item in result["removedSecondaryViews"])
    else:
        lines.append("- No secondary vault views removed in this run.")
    lines.extend([
        "",
        "## Raw Sources",
        "",
    ])
    if raw_records:
        lines.extend(f"- `{item['path']}`" for item in raw_records)
    else:
        lines.append("- No raw sources.")
    lines.extend([
        "",
        "## Result",
        "",
        "- 已建立单一主入口 `Home.md`。",
        "- 当前用户审核只应进入 `Home.md` 中的 Candidate Review Queue。",
        "- 历史候选和已晋升证据已非破坏性归档；reviewed source trace 按需同步。",
        "",
    ])
    return "\n".join(lines)


def _page_record(root: Path, vault: Path, page: Path) -> dict:
    text = read_text(page)
    scope = _scope_from_text(text)
    return {
        "title": _page_title(text, page.stem),
        "path": rel(root, page),
        "vaultPath": rel(vault, page),
        "vaultStem": rel(vault, page).removesuffix(".md"),
        "scope": scope,
        "purpose": _frontmatter_value(text, "purpose") or _first_sentence(_strip_frontmatter(text)),
        "reviewedBy": _frontmatter_value(text, "reviewedBy") or _nested_reviewed_by(text) or "unknown",
        "reviewedAt": _frontmatter_value(text, "reviewedAt") or _nested_reviewed_at(text) or "unknown",
        "sourceTrace": "yes" if "## Source Trace" in text else "missing",
    }


def _reviewed_pages(reviewed: Path) -> list[Path]:
    if not reviewed.exists():
        return []
    return [
        p for p in sorted(reviewed.rglob("*.md"))
        if p.is_file() and p.name not in VAULT_INDEX_FILES
    ]


def _graph_pages(vault: Path, reviewed: Path) -> list[Path]:
    pages = [vault / name for name in VAULT_INDEX_FILES if (vault / name).exists()]
    pages.extend(_reviewed_pages(reviewed))
    return sorted({p.resolve(): p for p in pages}.values())


def _gap_records(root: Path, candidate_wiki: Path, gaps_by_link: dict[str, set[str]]) -> list[dict]:
    used_names: set[str] = {"candidateknowledge", "reviewedknowledgegap"}
    records = []
    for link, refs in sorted(gaps_by_link.items(), key=lambda item: item[0].lower()):
        name = _unique_gap_name(_candidate_concept_name(link), used_names)
        candidate_page = candidate_wiki / "concepts" / f"{name}.md"
        records.append({
            "link": link,
            "candidateConcept": name,
            "referencedBy": sorted(refs),
            "action": "create-candidate-concept-page",
            "suggestedCandidatePage": rel(root, candidate_page),
        })
    return records


def _write_gap_candidate_wiki(root: Path, candidate_wiki: Path, gaps: list[dict]) -> list[str]:
    candidate_wiki.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    first_concept = gaps[0]["candidateConcept"] if gaps else "ReviewedKnowledgeGap"
    files = {
        candidate_wiki / "overview.md": _format_gap_candidate_overview(gaps),
        candidate_wiki / "index.md": _format_gap_candidate_index(gaps),
        candidate_wiki / "log.md": _format_gap_candidate_log(gaps),
        candidate_wiki / "concepts" / "CandidateKnowledge.md": _gap_support_page(
            "CandidateKnowledge",
            "Candidate Knowledge，中文解释是候选知识，表示尚未完成 reviewed promotion 的本地语料。",
            ["ReviewedKnowledgeGap", first_concept],
        ),
        candidate_wiki / "concepts" / "ReviewedKnowledgeGap.md": _gap_support_page(
            "ReviewedKnowledgeGap",
            "Reviewed Knowledge Gap，中文解释是已审核知识中的未落地概念链接，需要进入 candidate enrichment，而不是直接补写 reviewed Knowledge。",
            ["CandidateKnowledge", first_concept],
        ),
    }
    for gap in gaps:
        files[candidate_wiki / "concepts" / f"{gap['candidateConcept']}.md"] = _format_gap_candidate_page(gap)

    for path, content in files.items():
        write_text(path, content)
        written.append(rel(root, path))
    return sorted(written)


def _write_gap_enriched_overview(candidate_wiki: Path, enriched: list[dict]) -> None:
    lines = [
        "---",
        "title: Reviewed Gap Candidate Overview",
        "type: synthesis",
        "tags: [candidate, reviewed-gap, enriched]",
        "sources: []",
        f"last_updated: {today()}",
        "---",
        "# Reviewed Gap Candidate Overview",
        "",
        "本 candidate wiki 由 reviewed Knowledge 的 unresolved wikilinks 生成，并已用 reviewed source evidence 做候选补强。它不是 reviewed Knowledge。",
        "",
        "## Enrichment Summary",
        "",
        f"- Enriched concept pages: {len(enriched)}",
        "- Boundary: candidate-only-no-promotion",
        "",
        "## Gap Concepts",
        "",
    ]
    for item in enriched:
        lines.append(
            f"- [[{item['candidateConcept']}]]：来自 `[[{item['originalLink']}]]`，"
            f"definition status = `{item['definitionStatus']}`，"
            f"promotion hint = `{item['promotionHint']}`。"
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "- [[CandidateKnowledge]] 不能作为 authoritative knowledge。",
        "- [[ReviewedKnowledgeGap]] 只能触发 candidate enrichment，不触发 reviewed promotion。",
        "- 每个概念页需要人类审核后，才能决定是否进入正式 promotion。",
        "",
    ])
    write_text(candidate_wiki / "overview.md", "\n".join(lines))


def _append_gap_enrichment_log(candidate_wiki: Path, enriched: list[dict]) -> None:
    log_path = candidate_wiki / "log.md"
    existing = read_text(log_path) if log_path.exists() else "# Reviewed Gap Candidate Log\n"
    lines = [
        existing.rstrip(),
        "",
        f"## [{today()}] enrich-gap-candidates",
        "",
        f"Enriched {len(enriched)} candidate concept pages from reviewed Knowledge evidence.",
        "",
    ]
    for item in enriched:
        lines.append(f"- `[[{item['originalLink']}]]` -> `concepts/{item['candidateConcept']}.md` ({item['definitionStatus']})")
    lines.append("")
    write_text(log_path, "\n".join(lines))


def _format_gap_candidate_index(gaps: list[dict]) -> str:
    lines = [
        "# Reviewed Gap Candidate Wiki Index",
        "",
        "## Overview",
        "- [Overview](overview.md) - reviewed wikilink gap synthesis",
        "",
        "## Concepts",
        "- [Candidate Knowledge](concepts/CandidateKnowledge.md) - candidate knowledge boundary",
        "- [Reviewed Knowledge Gap](concepts/ReviewedKnowledgeGap.md) - unresolved reviewed link boundary",
    ]
    for gap in gaps:
        lines.append(f"- [{gap['candidateConcept']}](concepts/{gap['candidateConcept']}.md) - unresolved link `[[{gap['link']}]]`")
    lines.append("")
    return "\n".join(lines)


def _format_gap_candidate_overview(gaps: list[dict]) -> str:
    lines = [
        "---",
        "title: Reviewed Gap Candidate Overview",
        "type: synthesis",
        "tags: [candidate, reviewed-gap]",
        "sources: []",
        f"last_updated: {today()}",
        "---",
        "# Reviewed Gap Candidate Overview",
        "",
        "本 candidate wiki 由 reviewed Knowledge 的 unresolved wikilinks 生成，用于后续 agent enrichment 和人类审核。它不是 reviewed Knowledge。",
        "",
        "## Gap Concepts",
        "",
    ]
    for gap in gaps:
        refs = ", ".join(f"`{ref}`" for ref in gap["referencedBy"])
        lines.append(f"- [[{gap['candidateConcept']}]]：来自 `[[{gap['link']}]]`，引用位置：{refs}。")
    lines.extend([
        "",
        "## Boundary",
        "",
        "- [[CandidateKnowledge]] 不能作为 authoritative knowledge。",
        "- [[ReviewedKnowledgeGap]] 只能触发 candidate enrichment，不触发 reviewed promotion。",
        "- 每个概念页需要补充来源证据、定义、适用范围和冲突检查后，才能进入审核。",
        "",
    ])
    return "\n".join(lines)


def _format_gap_candidate_log(gaps: list[dict]) -> str:
    lines = [
        "# Reviewed Gap Candidate Log",
        "",
        f"## [{today()}] reviewed-gap-plan",
        "",
        f"Generated {len(gaps)} candidate concept placeholders from unresolved reviewed wikilinks.",
        "",
    ]
    for gap in gaps:
        lines.append(f"- `[[{gap['link']}]]` -> `concepts/{gap['candidateConcept']}.md`")
    lines.append("")
    return "\n".join(lines)


def _gap_support_page(title: str, summary: str, links: list[str]) -> str:
    related = "\n".join(f"- [[{link}]]" for link in links if link != title)
    return f"""---
title: "{title}"
type: concept
tags: [candidate, reviewed-gap]
sources: []
last_updated: {today()}
---

# {title}

## Candidate Summary

{summary}

## Connections

{related}

## Review Boundary

- 本页是 candidate support page，不是 reviewed Knowledge。
- 任何正式知识晋升都需要单独 review 和 explicit approval。
"""


def _format_gap_candidate_page(gap: dict) -> str:
    refs = "\n".join(f"- `{ref}`" for ref in gap["referencedBy"])
    return f"""---
title: "{gap['candidateConcept']}"
type: concept
tags: [candidate, reviewed-gap]
sources: []
last_updated: {today()}
---

# {gap['candidateConcept']}

## Candidate Summary

`[[{gap['candidateConcept']}]]` 是由 reviewed Knowledge 中的 unresolved wikilink `[[{gap['link']}]]` 生成的候选概念页。当前页面只记录补强任务，不声明该概念的正式定义。

## Evidence To Review

{refs}

## Required Enrichment

- 阅读引用它的 reviewed Knowledge 文档，确认该概念是否值得独立晋升。
- 从已审核来源或新的 raw-to-candidate workflow 中补充定义、适用范围、非适用范围和冲突检查。
- 补齐 source provenance 后重新运行 candidate `health`、`lint` 和 `build-graph`。

## Connections

- [[ReviewedKnowledgeGap]]
- [[CandidateKnowledge]]

## Review Boundary

- 本页是 candidate placeholder，不是 authoritative knowledge。
- 不得在未审核时用本页回答用户事实问题。
"""


def _format_enriched_gap_candidate_page(concept_name: str, original_link: str, concept: dict, snippets: list[dict]) -> str:
    evidence_lines = []
    for item in snippets:
        evidence_lines.append(f"- `{item['page']}` / `{item['heading']}`: {item['excerpt']}")
    if not evidence_lines:
        evidence_lines.append("- 未在 reviewed Knowledge 中找到足够引用段落；需要人工确认是否保留。")

    aliases = concept.get("aliases") or "none"
    definition = concept.get("definition") or _fallback_gap_definition(original_link)
    source_status = concept.get("status", "missing-reviewed-definition")
    readiness = _promotion_hint(original_link, concept)
    return f"""---
title: "{concept_name}"
type: concept
tags: [candidate, reviewed-gap, enriched]
sources:
{_yaml_source_lines(snippets)}
last_updated: {today()}
original_link: "{original_link}"
definition_status: "{source_status}"
promotion_hint: "{readiness}"
---

# {concept_name}

## Candidate Summary

`[[{concept_name}]]` 是由 reviewed Knowledge 中的 unresolved wikilink `[[{original_link}]]` 生成的候选概念页。当前页面已根据 reviewed Knowledge evidence 补强，但仍不是 authoritative knowledge。

## Candidate Definition

{definition}

Definition status: `{source_status}`.

Aliases: `{aliases}`.

## Reviewed Evidence

{chr(10).join(evidence_lines)}

## Applicability

- 可用于讨论 reviewed Knowledge 中与 `[[{original_link}]]` 相关的 Harness 概念、边界或后续补强任务。
- 只能作为 candidate enrichment material；回答用户事实问题时仍应引用 reviewed Knowledge 文档本身。

## Non-Applicability

- 不直接替代 `user/knowledge/reviewed/` 下的 reviewed Knowledge。
- 不代表该概念已经通过独立 human review。
- 不应绕过 review 被写入 Memory、Project Facts 或 Harness architecture authority。

## Conflict And Dedup Check

- 与 [[CandidateKnowledge]] 的关系：本页仍处于 candidate state。
- 与 [[ReviewedKnowledgeGap]] 的关系：本页来源是 reviewed wikilink gap。
- Promotion hint: `{readiness}`.

## Review Checklist

- Source evidence 已核对。
- Definition status 已标记。
- Scope、applicability 和 non-applicability 已填写。
- 后续 promotion 需要 human review 和 explicit approval。
"""


def _candidate_concept_name(link: str) -> str:
    target = link.split("|", 1)[0].split("#", 1)[0].strip()
    parts = re.findall(r"[A-Za-z0-9]+|[\u3400-\u9fff]+", target)
    if not parts:
        return "GapConcept"
    if all(re.fullmatch(r"[A-Za-z0-9]+", part) for part in parts):
        return "".join(part[:1].upper() + part[1:] for part in parts)
    return "".join(parts)


def _unique_gap_name(base: str, used: set[str]) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\u3400-\u9fff]+", "", base) or "GapConcept"
    if cleaned.lower() in used:
        cleaned = f"{cleaned}Concept"
    candidate = cleaned
    counter = 2
    while candidate.lower() in used:
        candidate = f"{cleaned}{counter}"
        counter += 1
    used.add(candidate.lower())
    return candidate


def _reviewed_records(root: Path, vault: Path, reviewed: Path) -> list[dict]:
    records = []
    for page in _reviewed_pages(reviewed):
        text = read_text(page)
        records.append({
            "page": rel(root, page),
            "vaultPath": rel(vault, page),
            "title": _page_title(text, page.stem),
            "text": text,
        })
    return records


def _reviewed_concept_index(records: list[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for record in records:
        for concept in _reviewed_key_concepts(record["text"]):
            key = _link_key(concept["name"])
            current = index.setdefault(key, {
                "name": concept["name"],
                "definition": concept["definition"],
                "aliases": concept["aliases"],
                "sources": [],
                "status": "reviewed-key-concept",
            })
            current["sources"].append(record["page"])
    return index


def _reviewed_key_concepts(text: str) -> list[dict]:
    block = _section_by_heading(text, "Key Concepts")
    concepts = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "Concept" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        name = cells[0].strip("` ")
        if not name:
            continue
        concepts.append({
            "name": name,
            "definition": cells[1].strip(),
            "aliases": cells[2].strip(),
        })
    return concepts


def _concept_evidence(original_link: str, concept_index: dict[str, dict]) -> dict:
    found = concept_index.get(_link_key(original_link))
    if found:
        return found
    workflow_links = {
        "candidateknowledge": "reviewed-workflow-link",
        "structuredingestion": "reviewed-workflow-link",
    }
    status = workflow_links.get(_link_key(original_link), "missing-reviewed-definition")
    return {
        "name": original_link,
        "definition": "",
        "aliases": "none",
        "sources": [],
        "status": status,
    }


def _reviewed_snippets_for_link(original_link: str, records: list[dict]) -> list[dict]:
    snippets = []
    link_pattern = f"[[{original_link}]]"
    concept_pattern = f"`{original_link}`"
    for record in records:
        for heading, body in _sections(record["text"]):
            for line in body.splitlines():
                compact = re.sub(r"\s+", " ", line.strip())
                if not compact:
                    continue
                if link_pattern in compact or concept_pattern in compact or _link_key(original_link) in _link_key(compact):
                    snippets.append({
                        "page": record["page"],
                        "heading": heading,
                        "excerpt": _limit_text(compact, 360),
                    })
    return snippets[:8]


def _original_gap_link(page: Path) -> str:
    text = read_text(page)
    frontmatter = _frontmatter_value(text, "original_link")
    if frontmatter:
        return frontmatter
    match = re.search(r"unresolved wikilink `\[\[([^\]]+)\]\]`", text)
    if match:
        return match.group(1).strip()
    return page.stem


def _fallback_gap_definition(original_link: str) -> str:
    if _link_key(original_link) == "candidateknowledge":
        return "Reviewed Knowledge 中仅把该链接作为 candidate workflow boundary 引用；当前没有独立 reviewed 概念定义。建议优先与已有 [[CandidateKnowledge]] 支撑页去重，而不是直接晋升。"
    if _link_key(original_link) == "structuredingestion":
        return "Reviewed Knowledge 中仅把该链接作为 structured ingestion workflow 引用；当前没有独立 reviewed 概念定义。建议优先与 raw-to-candidate Skill 和既有 ingestion workflow 去重。"
    return "Reviewed Knowledge 中尚未提供独立定义；需要进一步 source-grounded enrichment 或人工决定是否保留。"


def _promotion_hint(original_link: str, concept: dict) -> str:
    if concept.get("status") == "reviewed-key-concept":
        return "candidate-ready-for-human-review"
    if _link_key(original_link) in {"candidateknowledge", "structuredingestion"}:
        return "dedup-with-existing-workflow-before-promotion"
    return "needs-source-grounded-definition-before-review"


def _yaml_source_lines(snippets: list[dict]) -> str:
    pages = sorted({item["page"] for item in snippets})
    if not pages:
        return "  []"
    return "\n".join(f"  - {page}" for page in pages)


def _section_by_heading(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def _limit_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0] + "..."


def _gap_review_items(root: Path, candidate_wiki: Path) -> list[dict]:
    concept_dir = candidate_wiki / "concepts"
    pages = [
        page for page in sorted(concept_dir.glob("*.md"))
        if page.stem not in {"CandidateKnowledge", "ReviewedKnowledgeGap"}
    ]
    items = []
    for page in pages:
        text = read_text(page)
        definition_status = _frontmatter_value(text, "definition_status") or "missing"
        promotion_hint = _frontmatter_value(text, "promotion_hint") or "missing"
        original_link = _frontmatter_value(text, "original_link") or page.stem
        evidence = _section_by_heading(text, "Reviewed Evidence")
        evidence_count = len([line for line in evidence.splitlines() if line.strip().startswith("- `")])
        sources = _frontmatter_sources(text)
        definition = _candidate_definition(text)
        recommendation = _gap_review_recommendation(definition_status, promotion_hint, evidence_count)
        items.append({
            "page": rel(root, page),
            "candidateConcept": page.stem,
            "originalLink": original_link,
            "definitionStatus": definition_status,
            "promotionHint": promotion_hint,
            "sourcePages": sources,
            "evidenceCount": evidence_count,
            "definition": definition,
            "recommendation": recommendation,
            "reviewNotes": _gap_review_notes(definition_status, promotion_hint, evidence_count, sources),
        })
    return items


def _gap_review_gates(status: dict, items: list[dict]) -> dict:
    health = status.get("health", {}).get("state", "missing")
    lint = status.get("lint", {}).get("state", "missing")
    graph = status.get("graphSummary", {}).get("state", "missing")
    enrichment = status.get("gapCandidateEnrichment", {}).get("state", "missing")
    missing_required = [
        item["candidateConcept"]
        for item in items
        if item["definitionStatus"] == "missing"
        or item["promotionHint"] == "missing"
        or item["evidenceCount"] == 0
        or not item["sourcePages"]
    ]
    blocking = []
    if health != "passed":
        blocking.append("candidate health 未通过或缺失")
    if lint != "passed":
        blocking.append("candidate lint 未通过或缺失")
    if graph != "passed":
        blocking.append("candidate graph 未通过或缺失")
    if enrichment != "passed":
        blocking.append("gap candidate enrichment 未通过或缺失")
    if missing_required:
        blocking.append("以下概念缺少 required fields: " + ", ".join(missing_required))
    if not items:
        blocking.append("candidate wiki 中没有可审核概念页")
    return {
        "health": health,
        "lint": lint,
        "graph": graph,
        "enrichment": enrichment,
        "requiredFields": "passed" if not missing_required and items else "failed",
        "missingRequiredFields": missing_required,
        "humanApproval": "required-for-any-promotion",
        "blockingIssues": blocking,
    }


def _gap_review_recommendation(definition_status: str, promotion_hint: str, evidence_count: int) -> str:
    if promotion_hint == "dedup-with-existing-workflow-before-promotion":
        return "dedup-before-promotion"
    if definition_status == "reviewed-key-concept" and evidence_count > 0:
        return "approve-for-human-review"
    return "revise-before-review"


def _gap_review_notes(definition_status: str, promotion_hint: str, evidence_count: int, sources: list[str]) -> list[str]:
    notes = []
    if definition_status == "reviewed-key-concept":
        notes.append("定义来自 reviewed Knowledge 的 Key Concepts，可进入人工审核。")
    elif definition_status == "reviewed-workflow-link":
        notes.append("该链接更像 workflow / existing concept reference，晋升前应先去重。")
    else:
        notes.append("缺少 reviewed definition，需补充 source-grounded evidence。")
    if evidence_count == 0:
        notes.append("缺少 Reviewed Evidence 引用行。")
    if not sources:
        notes.append("缺少 sources frontmatter。")
    if promotion_hint == "dedup-with-existing-workflow-before-promotion":
        notes.append("建议 reviewer 选择 dedup 或 defer，而不是直接 promotion。")
    return notes


def _frontmatter_sources(text: str) -> list[str]:
    match = re.search(r"(?m)^sources:\s*\n((?:\s+- [^\n]+\n)+|\s+\[\]\n?)", text)
    if not match:
        return []
    block = match.group(1)
    return [
        line.split("-", 1)[1].strip()
        for line in block.splitlines()
        if "-" in line
    ]


def _candidate_definition(text: str) -> str:
    block = _section_by_heading(text, "Candidate Definition")
    lines = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            if lines:
                break
            continue
        if stripped.startswith("Definition status:") or stripped.startswith("Aliases:"):
            break
        lines.append(stripped)
    return "\n".join(lines).strip()


def _load_status(root: Path, run_id: str | None) -> dict:
    if not run_id:
        return {}
    status_path = root / "var" / "logs" / f"{run_id}.json"
    if not status_path.exists():
        return {}
    try:
        return json.loads(read_text(status_path))
    except json.JSONDecodeError:
        return {"statusError": "invalid-json"}


def _candidate_inventory(root: Path, candidate_dir: Path, reviewed: Path) -> list[dict]:
    reviewed_text = "\n".join(read_text(page) for page in _reviewed_pages(reviewed))
    records = []
    if not candidate_dir.exists():
        return records
    current_run_dirs = [
        path for path in candidate_dir.iterdir()
        if path.is_dir() and not path.name.startswith("_") and not path.name.startswith(".")
    ]
    for run_dir in sorted(current_run_dirs, key=lambda p: p.name.lower()):
        run_id = run_dir.name
        wiki = run_dir / "wiki"
        status = _load_status(root, run_id)
        markdown_count = len(list(wiki.rglob("*.md"))) if wiki.exists() else 0
        state, reason = _candidate_governance_state(root, run_id, run_dir, reviewed_text, status)
        review_package = _status_report_path(status, "gapReviewPackage") or _status_report_path(status, "reviewPackage")
        records.append({
            "runId": run_id,
            "path": rel(root, run_dir),
            "wiki": rel(root, wiki) if wiki.exists() else "missing",
            "markdownCount": markdown_count,
            "governanceState": state,
            "reason": reason,
            "reviewPackage": review_package,
            "reviewPackageData": status.get("gapReviewPackage") or status.get("reviewPackage") or {},
            "decisionSummary": _candidate_decision_summary(status),
        })
    return records


def _archive_inactive_candidates(root: Path, candidate_dir: Path, records: list[dict]) -> list[dict]:
    archive_actions = []
    archive_root = candidate_dir / "_archive"
    for item in records:
        if item["governanceState"] == "active-review":
            continue
        source = (root / item["path"]).resolve()
        if not source.exists() or not source.is_dir():
            continue
        if archive_root.resolve() in source.parents or source == archive_root.resolve():
            continue
        if candidate_dir.resolve() not in source.parents:
            raise ValueError(f"candidate archive source escapes candidate dir: {source}")
        state = re.sub(r"[^a-zA-Z0-9._-]+", "-", item["governanceState"]).strip(".-") or "inactive"
        destination = _unique_archive_destination(archive_root / state / item["runId"])
        if candidate_dir.resolve() not in destination.resolve().parents:
            raise ValueError(f"candidate archive destination escapes candidate dir: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        old_path = rel(root, source)
        shutil.move(str(source), str(destination))
        new_path = rel(root, destination)
        archive_actions.append({
            "runId": item["runId"],
            "governanceState": item["governanceState"],
            "reason": item["reason"],
            "oldPath": old_path,
            "newPath": new_path,
            "markdownCount": item["markdownCount"],
        })
    if archive_actions:
        _write_candidate_archive_readme(root, candidate_dir, _archived_candidate_inventory(root, candidate_dir))
    return archive_actions


def _unique_archive_destination(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.name}-{index:03d}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"unable to allocate archive destination: {path}")


def _archived_candidate_inventory(root: Path, candidate_dir: Path) -> list[dict]:
    archive_root = candidate_dir / "_archive"
    if not archive_root.exists():
        return []
    records = []
    for run_dir in sorted([path for path in archive_root.glob("*/*") if path.is_dir()], key=lambda p: rel(root, p).lower()):
        wiki = run_dir / "wiki"
        records.append({
            "runId": run_dir.name,
            "path": rel(root, run_dir),
            "wiki": rel(root, wiki) if wiki.exists() else "missing",
            "markdownCount": len(list(wiki.rglob("*.md"))) if wiki.exists() else 0,
            "governanceState": run_dir.parent.name,
            "reason": "archived inactive candidate corpus",
        })
    return records


def _write_candidate_archive_readme(root: Path, candidate_dir: Path, archived_records: list[dict]) -> None:
    archive_root = candidate_dir / "_archive"
    lines = [
        "---",
        "title: Candidate Archive",
        "type: candidate-archive-index",
        f"last_updated: {today()}",
        "---",
        "# Candidate Archive",
        "",
        "本目录保存已从 active candidate root 移出的历史候选或已晋升证据。它们不属于当前用户审核队列。",
        "",
        "| Corpus | State | Pages | Path |",
        "|---|---|---:|---|",
    ]
    if archived_records:
        for item in archived_records:
            lines.append(
                f"| `{item['runId']}` | `{item['governanceState']}` | "
                f"{item['markdownCount']} | `{item['path']}` |"
            )
    else:
        lines.append("| _No archived candidates._ |  |  |  |")
    lines.extend([
        "",
        "归档是非破坏性的：目录被移动但不删除；已晋升证据的 reviewed source trace 会同步到新路径。",
        "",
    ])
    write_text(archive_root / "ARCHIVE.md", "\n".join(lines))


def _rewrite_reviewed_source_traces(root: Path, reviewed: Path, archive_actions: list[dict]) -> list[str]:
    if not archive_actions:
        return []
    rewritten = []
    replacements = []
    for item in archive_actions:
        replacements.append((item["oldPath"], item["newPath"]))
        replacements.append((item["oldPath"].replace("/", "\\"), item["newPath"].replace("/", "\\")))
    for page in _reviewed_pages(reviewed):
        text = read_text(page)
        new_text = text
        for old, new in replacements:
            new_text = new_text.replace(old, new)
        if new_text != text:
            write_text(page, new_text)
            rewritten.append(rel(root, page))
    return rewritten


def _candidate_governance_state(root: Path, run_id: str, run_dir: Path, reviewed_text: str, status: dict) -> tuple[str, str]:
    run_ref = rel(root, run_dir)
    if status.get("gapReviewPackage", {}).get("state") == "ready-for-human-review":
        return "active-review", "gap review package ready; user decision pending"
    if status.get("state") == "promoted" or status.get("promotionResult", {}).get("state") == "promoted":
        return "promoted-evidence", "promotion result exists; keep as source trace evidence"
    if run_ref in reviewed_text or f"{run_ref}/" in reviewed_text:
        return "promoted-evidence", "referenced by reviewed Knowledge source trace"
    if run_id in {"h6-boundary-smoke"}:
        return "legacy-or-test-candidate", "historical boundary smoke candidate, not user review queue"
    return "legacy-or-test-candidate", "older duplicate or exploratory candidate; not current review queue"


def _candidate_decision_summary(status: dict) -> str:
    promotion = status.get("gapConceptPromotion", {})
    if promotion:
        return (
            f"promoted={promotion.get('promotedCount', 0)}, "
            f"deferred={promotion.get('deferredCount', 0)}, "
            f"skipped={promotion.get('skippedExistingCount', 0)}"
        )
    review = status.get("gapReviewPackage", {})
    if review:
        return (
            f"ready={review.get('readyForHumanReviewCount', 0)}, "
            f"dedup={review.get('dedupBeforePromotionCount', 0)}, "
            f"revise={review.get('reviseBeforeReviewCount', 0)}"
        )
    if status.get("promotionResult"):
        return "promoted"
    if status.get("reviewPackage"):
        return status["reviewPackage"].get("state", "review-package-exists")
    return "not-current-review"


def _status_report_path(status: dict, key: str) -> str | None:
    value = status.get(key, {})
    if isinstance(value, dict):
        return value.get("report")
    return None


def _raw_inventory(root: Path, raw: Path) -> list[dict]:
    if not raw.exists():
        return []
    records = []
    for path in sorted([item for item in raw.rglob("*") if item.is_file()]):
        records.append({
            "path": rel(root, path),
            "size": path.stat().st_size,
            "modified": path.stat().st_mtime,
        })
    for item in records:
        item["modified"] = _format_file_time(item["modified"])
    return records


def _format_file_time(timestamp: float) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def _vault_relative_candidate_page(path: str) -> str:
    marker = "user/knowledge/"
    if marker in path:
        return path.split(marker, 1)[1]
    return path


def _resolve_under_root(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    if root.resolve() not in resolved.parents and resolved != root.resolve():
        raise ValueError(f"path escapes root: {value}")
    return resolved


def _page_title(text: str, fallback: str) -> str:
    return _frontmatter_value(text, "title") or _first_heading(text) or fallback


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip().strip("\"'")
    return value or None


def _scope_from_text(text: str) -> str:
    scope_block = re.search(r"(?ms)^scope:\s*\n((?:\s+- .+\n)+)", text)
    if scope_block:
        scopes = [line.split("-", 1)[1].strip() for line in scope_block.group(1).splitlines() if "-" in line]
        for scope in scopes:
            if scope != "reviewed-knowledge":
                return scope
    return _frontmatter_value(text, "scope") or "unknown"


def _nested_reviewed_by(text: str) -> str | None:
    match = re.search(r"(?ms)^review:\s*\n(?:\s+.+\n)*?\s+reviewedBy:\s*(.+)$", text)
    return match.group(1).strip().strip("\"'") if match else None


def _nested_reviewed_at(text: str) -> str | None:
    match = re.search(r"(?ms)^review:\s*\n(?:\s+.+\n)*?\s+reviewedAt:\s*(.+)$", text)
    return match.group(1).strip().strip("\"'") if match else None


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"(?s)^---.*?---", "", text).strip()


def _first_sentence(text: str) -> str:
    stripped = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#"))
    return stripped[:160] or "reviewed Knowledge document"


def _node_type(vault: Path, reviewed: Path, page: Path) -> str:
    if page in [vault / name for name in VAULT_INDEX_FILES]:
        return "vault-index"
    try:
        page.relative_to(reviewed)
        return "reviewed-knowledge"
    except ValueError:
        return "unknown"


def _query_terms(question: str) -> list[str]:
    terms: list[str] = []
    terms.extend(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}", question.lower()))
    for sequence in re.findall(r"[\u3400-\u9fff]{2,}", question):
        if len(sequence) <= 16:
            terms.append(sequence)
        terms.extend(sequence[i:i + 2] for i in range(0, max(0, len(sequence) - 1)))
    seen = set()
    result = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            result.append(term)
    return result[:40]


def _matched_sections(text: str, terms: list[str]) -> list[dict]:
    sections = _sections(text)
    matches = []
    for heading, body in sections:
        lowered = (heading + "\n" + body).lower()
        if any(term.lower() in lowered for term in terms):
            matches.append({
                "heading": heading,
                "excerpt": _excerpt(body, terms),
            })
    if not matches:
        matches.append({"heading": "document", "excerpt": _excerpt(_strip_frontmatter(text), terms)})
    return matches[:5]


def _sections(text: str) -> list[tuple[str, str]]:
    body = _strip_frontmatter(text)
    result = []
    current_heading = "document"
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines:
                result.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        result.append((current_heading, "\n".join(current_lines).strip()))
    return result


def _excerpt(body: str, terms: list[str], limit: int = 280) -> str:
    compact = re.sub(r"\s+", " ", body).strip()
    if not compact:
        return ""
    lowered = compact.lower()
    positions = [lowered.find(term.lower()) for term in terms if lowered.find(term.lower()) >= 0]
    start = max(0, min(positions) - 80) if positions else 0
    excerpt = compact[start:start + limit]
    if start > 0:
        excerpt = "..." + excerpt
    if start + limit < len(compact):
        excerpt += "..."
    return excerpt


def _page_lookup(vault: Path, pages: list[Path]) -> dict[str, Path]:
    lookup: dict[str, Path] = {}
    for page in pages:
        keys = [
            page.stem,
            page.name,
            rel(vault, page),
            rel(vault, page).removesuffix(".md"),
        ]
        for key in keys:
            lookup[_link_key(key)] = page
    return lookup


def _resolve_wikilink(link: str, lookup: dict[str, Path]) -> Path | None:
    candidates = [link, Path(link).stem, Path(link).name, link.replace(" ", ""), link.replace(" ", "-")]
    for candidate in candidates:
        found = lookup.get(_link_key(candidate))
        if found:
            return found
    return None


def _link_key(value: str) -> str:
    target = value.split("|", 1)[0].split("#", 1)[0].strip()
    target = target.removesuffix(".md").replace("\\", "/")
    target = Path(target).stem if "/" in target else target
    return re.sub(r"[\s_-]+", "", target).lower()


def _yes_no(value: object) -> str:
    return "是" if bool(value) else "否"


def _graph_health(nodes: list[dict], edges: list[dict], broken_refs: dict[str, list[str]]) -> dict:
    degree = Counter()
    node_ids = {node["id"] for node in nodes}
    for edge in edges:
        degree[edge["from"]] += 1
        degree[edge["to"]] += 1
    return {
        "orphanNodes": sorted(node_id for node_id in node_ids if degree[node_id] == 0),
        "hubNodes": sorted([
            {"node": node_id, "degree": count}
            for node_id, count in degree.items()
            if count >= 5
        ], key=lambda item: (-item["degree"], item["node"])),
        "brokenLinks": [
            {"link": link, "referencedBy": sorted(refs)}
            for link, refs in sorted(broken_refs.items())
        ],
    }


def _expand_query_from_graph(root: Path, vault: Path, graph_path: Path, scored: dict[Path, dict]) -> None:
    if not graph_path.exists() or not scored:
        return
    try:
        graph = json.loads(read_text(graph_path))
    except json.JSONDecodeError:
        return
    id_to_path = {node["id"]: vault / f"{node['id']}.md" for node in graph.get("nodes", [])}
    path_to_id = {path.resolve(): node_id for node_id, path in id_to_path.items()}
    seed_ids = {
        path_to_id.get(page.resolve()): item["score"]
        for page, item in scored.items()
        if path_to_id.get(page.resolve())
    }
    for edge in graph.get("edges", []):
        endpoints = [edge.get("from"), edge.get("to")]
        for index, endpoint in enumerate(endpoints):
            if endpoint not in seed_ids:
                continue
            neighbor_id = endpoints[1 - index]
            neighbor = id_to_path.get(neighbor_id)
            if not neighbor or not neighbor.exists() or neighbor in scored:
                continue
            if not rel(vault, neighbor).startswith("reviewed/"):
                continue
            bonus = max(0.1, seed_ids[endpoint] * 0.25)
            text = read_text(neighbor)
            scored[neighbor] = {
                "page": rel(root, neighbor),
                "vaultPath": rel(vault, neighbor),
                "title": _page_title(text, neighbor.stem),
                "score": round(bonus, 3),
                "reason": ["graph-neighbor"],
                "reviewedAt": _frontmatter_value(text, "reviewedAt") or _nested_reviewed_at(text),
                "reviewedBy": _frontmatter_value(text, "reviewedBy") or _nested_reviewed_by(text),
                "matchedSections": _matched_sections(text, []),
                "wikilinks": sorted(set(extract_wikilinks(text)))[:20],
            }


def _render_graph_html(graph: dict) -> str:
    nodes = json.dumps(graph["nodes"], ensure_ascii=False)
    edges = json.dumps(graph["edges"], ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Reviewed Knowledge Graph</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 0; }}
header {{ padding: 12px 16px; border-bottom: 1px solid #ddd; }}
#graph {{ width: 100vw; height: calc(100vh - 58px); }}
.node {{ position: absolute; padding: 6px 8px; border: 1px solid #2563eb; border-radius: 6px; background: #eff6ff; max-width: 220px; }}
svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
</style>
</head>
<body>
<header><strong>Reviewed Knowledge Graph</strong> built {escape(graph["built"])} · {len(graph["nodes"])} nodes · {len(graph["edges"])} edges</header>
<div id="graph"><svg id="edges"></svg></div>
<script>
const nodes = {nodes};
const edges = {edges};
const root = document.getElementById("graph");
const svg = document.getElementById("edges");
const cx = window.innerWidth / 2;
const cy = (window.innerHeight - 58) / 2;
const radius = Math.max(120, Math.min(cx, cy) - 80);
const positions = {{}};
nodes.forEach((node, i) => {{
  const angle = (Math.PI * 2 * i) / Math.max(nodes.length, 1);
  const x = cx + Math.cos(angle) * radius;
  const y = cy + Math.sin(angle) * radius;
  positions[node.id] = {{x, y}};
  const div = document.createElement("div");
  div.className = "node";
  div.style.left = `${{x - 80}}px`;
  div.style.top = `${{y - 20}}px`;
  div.title = node.path;
  div.textContent = node.label;
  root.appendChild(div);
}});
edges.forEach(edge => {{
  const a = positions[edge.from];
  const b = positions[edge.to];
  if (!a || !b) return;
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", a.x);
  line.setAttribute("y1", a.y);
  line.setAttribute("x2", b.x);
  line.setAttribute("y2", b.y);
  line.setAttribute("stroke", "#64748b");
  line.setAttribute("stroke-width", "1.5");
  svg.appendChild(line);
}});
</script>
</body>
</html>
"""
