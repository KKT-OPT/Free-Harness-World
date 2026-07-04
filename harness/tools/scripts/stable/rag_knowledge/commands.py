from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
from contextlib import redirect_stdout
from collections import Counter, defaultdict
from html import escape
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from rag_candidate.commands import (
    _source_gate as _candidate_source_gate,
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

EXTERNALIZATION_PIPELINE_CONCEPTS = {
    "LLMAgentExternalization": (
        "LLM Agent Externalization 指 durable agent capability 不只存在于模型权重或单次 prompt 中，而是分布在模型调用、memory、skills、protocols、tools 和 harness controls 组成的系统里。",
        ["ExternalizedMemory", "SkillLibrary", "ProtocolMediatedCoordination", "HarnessEngineering"],
    ),
    "ExternalizedMemory": (
        "Externalized Memory 指把 agent state 保存在 prompt 之外，使后续动作可以复用有来源、可治理、可过期和可删除的上下文，而不是只依赖瞬时模型上下文。",
        ["LLMAgentExternalization", "StatePersistence", "HarnessEngineering"],
    ),
    "SkillLibrary": (
        "Skill Library 指把可复用 procedure、tool-use pattern、decision heuristic 和约束封装为可发现、可调用、可审查和可版本化的能力包。",
        ["LLMAgentExternalization", "ToolInterfaceBoundary", "HarnessEngineering"],
    ),
    "ProtocolMediatedCoordination": (
        "Protocol-mediated coordination 指通过 message contract、handoff rule、approval boundary 和 responsibility transfer，把 agent-tool、agent-agent 或 human-agent 协作显式化。",
        ["LLMAgentExternalization", "ToolInterfaceBoundary", "GovernedExternalState"],
    ),
    "HarnessEngineering": (
        "Harness Engineering 是围绕 LLM agent 和外部化能力建立 execution、observation、verification、lifecycle 和 governance 控制层的系统工程。",
        ["LLMAgentExternalization", "ExternalizedMemory", "ProtocolMediatedCoordination"],
    ),
    "StatePersistence": (
        "State Persistence 关注哪些状态应该跨 turn、run、user 或 agent 保留，因此必须同时定义 retention、staleness、provenance 和 deletion 规则。",
        ["ExternalizedMemory", "GovernedExternalState", "HarnessEngineering"],
    ),
    "ToolInterfaceBoundary": (
        "Tool Interface Boundary 定义 agent 可以调用什么工具、工具返回什么证据、允许哪些 side effects、失败如何上报和审计。",
        ["SkillLibrary", "ProtocolMediatedCoordination", "HarnessEngineering"],
    ),
    "GovernedExternalState": (
        "Governed External State 要求把 authoritative knowledge、candidate material、runtime index、memory 和 project facts 分开治理，避免 agent 混用不同证据等级。",
        ["ExternalizedMemory", "StatePersistence", "HarnessEngineering"],
    ),
}

SCHEMA_CONTEXT_TASK_SECTIONS = {
    "ingest": [
        "Directory Rules",
        "Naming Rules",
        "Source Gate Rules",
        "Controlled Tag Vocabulary",
    ],
    "promotion": [
        "Required Reviewed Page Sections",
        "Controlled Tag Vocabulary",
        "Alias Rules",
        "Source Gate Rules",
        "Validation Rules",
    ],
    "query": [
        "Directory Rules",
        "Controlled Tag Vocabulary",
        "Alias Rules",
        "Validation Rules",
    ],
    "validation": [
        "Directory Rules",
        "Naming Rules",
        "Required Reviewed Page Sections",
        "Validation Rules",
        "Controlled Tag Vocabulary",
        "Alias Rules",
        "Source Gate Rules",
    ],
    "cleanup": [
        "Directory Rules",
        "Naming Rules",
        "Validation Rules",
        "Source Gate Rules",
    ],
}

RESIDUAL_GAP_DISPOSITIONS = {
    "CandidateKnowledge": {
        "candidateConcept": "CandidateKnowledgeConcept",
        "disposition": "dedup-to-harness-knowledge-policy",
        "replacement": "Candidate Knowledge（候选知识；见 `harness/governance/KnowledgePromotionPolicy.md` 和 `harness/templates/knowledge/CandidateKnowledgeTemplate.md`）",
        "targets": [
            "harness/governance/KnowledgePromotionPolicy.md",
            "harness/templates/knowledge/CandidateKnowledgeTemplate.md",
        ],
    },
    "StructuredIngestion": {
        "candidateConcept": "StructuredIngestion",
        "disposition": "dedup-to-rag-structured-ingestion-skill",
        "replacement": "Structured Ingestion（结构化摄取；见 `harness/skills/rag-structured-ingestion/SKILL.md` 和 `harness/templates/knowledge/StructuredIngestionManifestTemplate.md`）",
        "targets": [
            "harness/skills/rag-structured-ingestion/SKILL.md",
            "harness/templates/knowledge/StructuredIngestionManifestTemplate.md",
        ],
    },
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
    pages = _reviewed_pages(reviewed, authoritative_only=False)
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
        "authoritativeReviewedPageCount": len([p for p in pages if _is_authoritative_reviewed_page(p)]),
        "evidenceReviewedPageCount": len([p for p in pages if not _is_authoritative_reviewed_page(p)]),
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
            "knowledgeRole": _knowledge_role(text),
            "authoritative": _is_authoritative_reviewed_text(text),
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


def run_govern_reviewed_duplicates(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    report = _resolve_under_root(root, args.report)
    records = [
        _duplicate_reviewed_record(root, vault, page)
        for page in _reviewed_pages(reviewed, authoritative_only=False)
    ]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        for raw_source in record["rawSourceRefs"]:
            topic_keys = [_duplicate_topic_key(record)] + [f"alias:{alias}" for alias in _duplicate_alias_keys(record)]
            for topic_key in _dedupe_preserve_order(topic_keys):
                group_key = (raw_source, topic_key)
                groups[group_key].append(record)
    similarity_candidates = _duplicate_similarity_candidates(records)
    for item in similarity_candidates:
        groups[(item["rawSource"], item["topicKey"])].extend(item["pages"])

    duplicate_groups = []
    blocking_issues = []
    for (raw_source, topic_key), items in sorted(groups.items()):
        if len(items) < 2:
            continue
        authoritative = [item for item in items if item["authoritative"]]
        governed_non_authoritative = [
            item for item in items
            if not item["authoritative"] and _is_governed_duplicate_non_authoritative(item)
        ]
        group_state = "passed" if len(authoritative) == 1 and len(authoritative) + len(governed_non_authoritative) == len(items) else "failed"
        if group_state != "passed":
            blocking_issues.append(
                f"duplicate group raw={raw_source} topic={topic_key} requires exactly one authoritative page and governed non-authoritative duplicates"
            )
        duplicate_groups.append({
            "rawSource": raw_source,
            "topicKey": topic_key,
            "state": group_state,
            "authoritativePages": [item["page"] for item in authoritative],
            "nonAuthoritativePages": [item["page"] for item in items if not item["authoritative"]],
            "pages": items,
        })

    result = {
        "state": "passed" if not blocking_issues else "failed",
        "scope": "reviewed-duplicate-governance",
        "reviewed": rel(root, reviewed),
        "reviewedFileCount": len(records),
        "duplicateGroupCount": len(duplicate_groups),
        "similarityCandidateCount": len(similarity_candidates),
        "blockingIssues": blocking_issues,
        "duplicateGroups": duplicate_groups,
        "similarityCandidates": [
            {
                "rawSource": item["rawSource"],
                "topicKey": item["topicKey"],
                "score": item["score"],
                "pages": [page["page"] for page in item["pages"]],
            }
            for item in similarity_candidates
        ],
        "report": rel(root, report),
        "boundary": "one-authoritative-reviewed-page-per-raw-source-topic-alias-or-similar-body-duplicate",
    }
    write_text(report, _format_duplicate_governance_report(result))
    update_status(root, args.run_id, {"duplicateReviewedGovernance": result})
    print_json(result)
    return result


def run_dispose_residual_gaps(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate_wiki = _resolve_under_root(root, args.candidate_wiki)
    report = _resolve_under_root(root, args.report)

    page_actions = []
    for page in _reviewed_pages(reviewed):
        text = read_text(page)
        new_text = text
        replaced_links = []
        for link, disposition in RESIDUAL_GAP_DISPOSITIONS.items():
            token = f"[[{link}]]"
            if token not in new_text:
                continue
            new_text = new_text.replace(token, disposition["replacement"])
            replaced_links.append({
                "link": link,
                "disposition": disposition["disposition"],
                "replacement": disposition["replacement"],
                "targets": disposition["targets"],
            })
        if new_text != text:
            write_text(page, new_text)
            page_actions.append({
                "page": rel(root, page),
                "replacedLinks": replaced_links,
            })

    candidate_updates = _mark_residual_gap_candidate_pages(root, candidate_wiki)
    residual_gaps = _current_residual_gap_links(vault, reviewed)
    state = "passed" if not residual_gaps else "failed"
    result = {
        "state": state,
        "scope": "residual-reviewed-gap-disposition",
        "reviewed": rel(root, reviewed),
        "candidateWiki": rel(root, candidate_wiki),
        "disposedLinks": sorted(RESIDUAL_GAP_DISPOSITIONS),
        "pageActions": page_actions,
        "candidateUpdates": candidate_updates,
        "remainingResidualGaps": residual_gaps,
        "promotion": "none",
        "boundary": "dedup-or-defer-residual-workflow-gaps-no-reviewed-promotion",
        "report": rel(root, report),
    }
    write_text(report, _format_residual_gap_disposition_report(result))
    update_status(root, args.run_id, {"residualGapDisposition": result})
    if getattr(args, "candidate_run_id", None):
        update_status(root, args.candidate_run_id, {"residualGapDisposition": result})
    print_json(result)
    return result


def run_canonicalize_vault_layout(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate = _resolve_under_root(root, args.candidate)
    raw = _resolve_under_root(root, args.raw)
    registry = _resolve_under_root(root, args.registry)
    report = _resolve_under_root(root, args.report)

    source_domain = safe_run_id(args.source_domain)
    target_domain = safe_run_id(args.target_domain)
    source_id = safe_run_id(args.source_id)
    canonical_page = safe_run_id(args.canonical_page)

    source_raw_dir = raw / source_domain
    target_raw_dir = raw / target_domain
    source_reviewed_dir = reviewed / source_domain
    target_reviewed_dir = reviewed / target_domain
    reviewed_archive_dir = reviewed / "_archive" / "validation-evidence" / target_domain
    source_archive_root = candidate / "_archive"
    target_archive_root = source_archive_root / "by-source" / source_id

    moves: list[dict] = []
    rewrites: list[dict] = []

    _move_path(root, source_raw_dir, target_raw_dir, moves, "raw-domain")
    _move_path(
        root,
        source_reviewed_dir / "llm-wiki-absorption-pdf-smoke.md",
        target_reviewed_dir / f"{canonical_page}.md",
        moves,
        "authoritative-reviewed-page",
    )
    _move_path(
        root,
        source_reviewed_dir / "p5-15-pipeline-smoke.md",
        reviewed_archive_dir / "p5-15-pipeline-smoke.md",
        moves,
        "reviewed-validation-evidence-archive",
    )
    _move_path(root, source_reviewed_dir / "concepts", target_reviewed_dir / "concepts", moves, "reviewed-concepts")
    _move_path(
        root,
        source_reviewed_dir / "index.md",
        target_archive_root / "layout" / f"{source_domain}-index-before-canonicalization.md",
        moves,
        "old-domain-index-evidence",
    )
    _remove_empty_dir(root, source_reviewed_dir, moves, "old-domain-dir")

    _move_path(
        root,
        source_archive_root / "promoted-evidence" / "llm-wiki-absorption-pdf-smoke",
        target_archive_root / "canonical-candidate",
        moves,
        "candidate-canonical-evidence",
    )
    _move_path(
        root,
        source_archive_root / "promoted-evidence" / "p5-15-pipeline-smoke",
        target_archive_root / "validation-evidence" / "p5-15-pipeline-smoke",
        moves,
        "candidate-validation-evidence",
    )
    _move_path(
        root,
        source_archive_root / "promoted-evidence" / "reviewed-gap-concepts",
        target_archive_root / "gap-concepts" / "reviewed-gap-concepts",
        moves,
        "candidate-gap-concepts-evidence",
    )
    _move_path(
        root,
        source_archive_root / "legacy-or-test-candidate" / "agent-harness-engineering-survey-20260614",
        target_archive_root / "legacy" / "agent-harness-engineering-survey-20260614",
        moves,
        "candidate-legacy-evidence",
    )
    _move_path(
        root,
        source_archive_root / "legacy-or-test-candidate" / "agent-harness-engineering-survey-skill-20260616",
        target_archive_root / "legacy" / "agent-harness-engineering-survey-skill-20260616",
        moves,
        "candidate-legacy-evidence",
    )
    _move_path(
        root,
        source_archive_root / "legacy-or-test-candidate" / "h6-boundary-smoke",
        source_archive_root / "by-source" / "harness-rag-boundary-smoke" / "legacy" / "h6-boundary-smoke",
        moves,
        "candidate-legacy-evidence",
    )
    _remove_empty_dir(root, source_archive_root / "promoted-evidence", moves, "old-archive-state-dir")
    _remove_empty_dir(root, source_archive_root / "legacy-or-test-candidate", moves, "old-archive-state-dir")

    replacements = _canonical_layout_replacements(
        source_domain=source_domain,
        target_domain=target_domain,
        source_id=source_id,
        canonical_page=canonical_page,
    )
    rewrites.extend(_rewrite_vault_references(root, vault, registry, replacements))

    canonical_path = target_reviewed_dir / f"{canonical_page}.md"
    evidence_path = reviewed_archive_dir / "p5-15-pipeline-smoke.md"
    if canonical_path.exists():
        _normalize_canonical_authoritative_page(canonical_path, target_domain, canonical_page)
        rewrites.append({"path": rel(root, canonical_path), "reason": "normalized-authoritative-page-metadata"})
    if evidence_path.exists():
        _normalize_validation_evidence_page(evidence_path, target_domain, canonical_path)
        rewrites.append({"path": rel(root, evidence_path), "reason": "archived-validation-evidence-metadata"})

    target_reviewed_dir.mkdir(parents=True, exist_ok=True)
    write_text(target_reviewed_dir / "index.md", _canonical_domain_index_text(root, target_reviewed_dir, target_domain, canonical_page, evidence_path))
    write_text(target_reviewed_dir / "schema.md", _canonical_domain_schema_text(target_domain))
    rewrites.append({"path": rel(root, target_reviewed_dir / "index.md"), "reason": "canonical-domain-index"})
    rewrites.append({"path": rel(root, target_reviewed_dir / "schema.md"), "reason": "canonical-domain-schema"})

    registry_update = _canonicalize_knowledge_registry(root, registry, target_domain)
    if registry_update:
        rewrites.append(registry_update)

    _write_candidate_archive_readme(root, candidate, _archived_candidate_inventory(root, candidate))
    sync = _sync_reviewed_index(root, vault, reviewed)
    candidate_records = _candidate_inventory(root, candidate, reviewed)
    _write_home(
        vault,
        reviewed_records=sync["records"],
        active_candidates=[item for item in candidate_records if item["governanceState"] == "active-review"],
        evidence_candidates=[item for item in candidate_records if item["governanceState"] != "active-review"],
        archived_candidates=_archived_candidate_inventory(root, candidate),
        raw_records=_raw_inventory(root, raw),
    )

    result = {
        "state": "passed",
        "scope": "knowledge-vault-canonical-layout",
        "sourceDomain": source_domain,
        "targetDomain": target_domain,
        "sourceId": source_id,
        "canonicalReviewedPage": rel(root, canonical_path),
        "archivedValidationEvidence": rel(root, evidence_path),
        "moves": moves,
        "rewrites": rewrites,
        "home": rel(root, vault / "Home.md"),
        "sync": {
            "reviewedPageCount": sync["reviewedPageCount"],
            "authoritativeReviewedPageCount": sync["authoritativeReviewedPageCount"],
            "evidenceReviewedPageCount": sync["evidenceReviewedPageCount"],
        },
        "report": rel(root, report),
        "boundary": "source-centered-canonical-vault-layout-no-new-promotion",
    }
    write_text(report, _format_canonical_layout_report(result))
    update_status(root, args.run_id, {"canonicalVaultLayout": result})
    print_json(result)
    return result


def run_validate_knowledge_vault(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate = _resolve_under_root(root, args.candidate)
    raw = _resolve_under_root(root, args.raw)
    registry = _resolve_under_root(root, args.registry)
    graph_dir = _resolve_under_root(root, args.graph)
    graph_json = graph_dir / "graph.json"
    report = _resolve_under_root(root, args.report)

    health = _quiet_call(run_health_reviewed, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        report="var/rag/reviewed-knowledge/evals/health-report.md",
        run_id=args.run_id,
    ))
    graph = _quiet_call(run_build_reviewed_graph, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        graph=rel(root, graph_dir),
        report="var/rag/reviewed-knowledge/evals/graph-report.md",
        run_id=args.run_id,
    ))
    gaps = _quiet_call(run_reviewed_gap_plan, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        graph=rel(root, graph_json),
        report="var/rag/reviewed-knowledge/evals/reviewed-gap-plan.md",
        candidate_wiki="user/knowledge/candidate/reviewed-gap-concepts/wiki",
        write_candidates=False,
        run_id=args.run_id,
    ))
    duplicates = _quiet_call(run_govern_reviewed_duplicates, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        report="var/rag/reviewed-knowledge/evals/duplicate-reviewed-governance.md",
        run_id=args.run_id,
    ))

    registry_check, registry_domains = _validate_knowledge_registry(root, vault, reviewed, candidate, raw, registry)
    checks = [
        registry_check,
        _validate_home_entry(root, vault, registry_domains),
        _validate_domain_layout(root, vault, reviewed, raw, registry_domains),
        _validation_check(
            "reviewed-frontmatter-health",
            health.get("state") == "passed",
            f"reviewed={health.get('reviewedPageCount')}, authoritative={health.get('authoritativeReviewedPageCount')}, evidence={health.get('evidenceReviewedPageCount')}",
            health.get("missingIndexFiles", []) + health.get("missingFrontmatter", []) + health.get("missingReviewMetadata", []) + health.get("sensitiveFindings", []),
            {
                "report": health.get("report"),
                "reviewedPageCount": health.get("reviewedPageCount"),
                "authoritativeReviewedPageCount": health.get("authoritativeReviewedPageCount"),
                "evidenceReviewedPageCount": health.get("evidenceReviewedPageCount"),
            },
        ),
        _validate_source_trace(root, reviewed),
        _validation_check(
            "reviewed-graph-links",
            graph.get("state") == "passed" and graph.get("brokenLinkCount") == 0 and graph.get("orphanCount") == 0,
            f"nodes={graph.get('nodeCount')}, edges={graph.get('edgeCount')}, broken={graph.get('brokenLinkCount')}, orphan={graph.get('orphanCount')}",
            _graph_gate_issues(graph_json, graph),
            {
                "graphJson": graph.get("graphJson"),
                "graphHtml": graph.get("graphHtml"),
                "report": graph.get("report"),
            },
        ),
        _validation_check(
            "reviewed-gap-plan",
            gaps.get("state") == "passed" and gaps.get("gapCount") == 0,
            f"gapCount={gaps.get('gapCount')}",
            [f"{item.get('link')} referenced by {', '.join(item.get('referencedBy', []))}" for item in gaps.get("gaps", [])],
            {"report": gaps.get("report")},
        ),
        _validation_check(
            "duplicate-source-governance",
            duplicates.get("state") == "passed" and not duplicates.get("blockingIssues"),
            f"duplicateGroups={duplicates.get('duplicateGroupCount')}",
            duplicates.get("blockingIssues", []),
            {
                "report": duplicates.get("report"),
                "duplicateGroupCount": duplicates.get("duplicateGroupCount"),
            },
        ),
        _validate_archive_references(root, reviewed, candidate),
        _validate_git_ignore_boundary(root, vault, registry),
        _validate_obsidian_plugin_boundary(root, vault, reviewed),
        _validate_llm_wiki_absorbed_mechanisms(root, vault, reviewed, registry_domains),
    ]

    blocking = [
        f"{check['name']}: {issue}"
        for check in checks
        if check["state"] != "passed"
        for issue in (check.get("issues") or ["failed"])
    ]
    result = {
        "state": "passed" if not blocking else "failed",
        "scope": "knowledge-one-click-validation-gate",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "candidate": rel(root, candidate),
        "raw": rel(root, raw),
        "registry": rel(root, registry),
        "report": rel(root, report),
        "checkCount": len(checks),
        "passedCheckCount": len([item for item in checks if item["state"] == "passed"]),
        "failedCheckCount": len([item for item in checks if item["state"] != "passed"]),
        "blockingIssues": blocking,
        "checks": checks,
        "boundary": "read-only-validation-no-promotion-no-knowledge-mutation",
    }
    write_text(report, _format_knowledge_validation_report(result))
    update_status(root, args.run_id, {"knowledgeValidationGate": result})
    print_json(result)
    if blocking:
        raise RuntimeError("knowledge validation gate failed: " + "; ".join(blocking))
    return result


def run_schema_context(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    registry = _resolve_under_root(root, args.registry)
    report = _resolve_under_root(root, args.report) if args.report else None
    domains = _read_registry_domains(root, registry)
    selected = [item for item in domains if item.get("domainId") == args.domain]
    contexts = [_schema_context_for_domain(root, item, args.task) for item in selected]
    issues = []
    if not selected:
        issues.append(f"domain not found in registry: {args.domain}")
    for context in contexts:
        issues.extend(context.get("issues") or [])
    result = {
        "state": "passed" if not issues else "failed",
        "scope": "reviewed-domain-schema-context",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "registry": rel(root, registry),
        "domain": args.domain,
        "task": args.task,
        "contextCount": len(contexts),
        "contexts": contexts,
        "issues": issues,
        "report": rel(root, report) if report else None,
        "boundary": "read-only-schema-context-no-knowledge-mutation",
    }
    if report:
        write_text(report, _format_schema_context_report(result))
    update_status(root, args.run_id, {"schemaContext": result})
    print_json(result)
    if issues:
        raise RuntimeError("schema context failed: " + "; ".join(issues))
    return result


def run_validate_llm_wiki_mechanisms(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate = _resolve_under_root(root, args.candidate)
    raw = _resolve_under_root(root, args.raw)
    registry = _resolve_under_root(root, args.registry)
    graph_dir = _resolve_under_root(root, args.graph)
    report = _resolve_under_root(root, args.report)

    registry_check, registry_domains = _validate_knowledge_registry(root, vault, reviewed, candidate, raw, registry)
    graph = _quiet_call(run_build_reviewed_graph, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        graph=rel(root, graph_dir),
        report="var/rag/reviewed-knowledge/evals/graph-report.md",
        run_id=args.run_id,
    ))
    duplicates = _quiet_call(run_govern_reviewed_duplicates, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        report="var/rag/reviewed-knowledge/evals/duplicate-reviewed-governance.md",
        run_id=args.run_id,
    ))

    checks = [
        registry_check,
        _validate_schema_context_mechanism(root, registry_domains),
        _validate_source_gate_fixture(root),
        _validate_extraction_granularity_fixture(root),
        _validate_tag_vocabulary_requirement(root, reviewed, registry_domains),
        _validation_check(
            "alias-aware-duplicate-governance",
            duplicates.get("state") == "passed" and not duplicates.get("blockingIssues"),
            f"duplicateGroups={duplicates.get('duplicateGroupCount')}, similarityCandidates={duplicates.get('similarityCandidateCount', 0)}",
            duplicates.get("blockingIssues", []),
            {
                "report": duplicates.get("report"),
                "duplicateGroupCount": duplicates.get("duplicateGroupCount"),
                "similarityCandidateCount": duplicates.get("similarityCandidateCount", 0),
                "boundary": duplicates.get("boundary"),
            },
        ),
        _validate_graph_retrieval_mechanism(root, vault, reviewed, graph_dir / "graph.json", graph),
        _validate_auto_maintenance_boundary(root, vault),
        _validate_llm_wiki_absorbed_mechanisms(root, vault, reviewed, registry_domains),
    ]
    blocking = [
        f"{check['name']}: {issue}"
        for check in checks
        if check["state"] != "passed"
        for issue in (check.get("issues") or ["failed"])
    ]
    result = {
        "state": "passed" if not blocking else "failed",
        "scope": "llm-wiki-mechanism-validation",
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "registry": rel(root, registry),
        "report": rel(root, report),
        "checkCount": len(checks),
        "passedCheckCount": len([item for item in checks if item["state"] == "passed"]),
        "failedCheckCount": len([item for item in checks if item["state"] != "passed"]),
        "blockingIssues": blocking,
        "checks": checks,
        "boundary": "executable-mechanism-validation-no-reviewed-promotion",
    }
    write_text(report, _format_llm_wiki_mechanism_validation_report(result))
    update_status(root, args.run_id, {"llmWikiMechanismValidation": result})
    print_json(result)
    if blocking:
        raise RuntimeError("llm wiki mechanism validation failed: " + "; ".join(blocking))
    return result


def run_candidate_cleanup_plan(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate = _resolve_under_root(root, args.candidate)
    raw = _resolve_under_root(root, args.raw)
    registry = _resolve_under_root(root, args.registry)
    report = _resolve_under_root(root, args.report)

    active_records = _candidate_inventory(root, candidate, reviewed)
    active_entries = []
    for item in active_records:
        candidate_path = (root / item["path"]).resolve()
        wiki_path = (root / item["wiki"]).resolve() if item.get("wiki") != "missing" else candidate_path
        markdown_files = _candidate_markdown_files(wiki_path if wiki_path.exists() else candidate_path)
        active_entries.append({
            "corpusId": item["runId"],
            "path": item["path"],
            "kind": "active-candidate",
            "governanceState": item["governanceState"],
            "markdownCount": len(markdown_files),
            "wikilinkCount": _candidate_wikilink_count(markdown_files),
            "references": _candidate_cleanup_references(root, vault, reviewed, registry, candidate_path),
            "recommendedAction": "keep-active-review-in-candidate-boundary",
            "reason": item["reason"],
        })

    archived_entries = _candidate_archive_cleanup_records(root, vault, reviewed, candidate, registry)
    audit_cleanup_entries = _candidate_audit_cleanup_records(root, vault, reviewed, candidate, registry)
    entries = active_entries + archived_entries + audit_cleanup_entries
    full_corpus_entries = [item for item in entries if item["kind"] == "full-corpus"]
    audit_entries = [item for item in entries if item["kind"] == "lightweight-audit-record"]
    remove_actions = [
        item for item in entries
        if item["recommendedAction"] in {
            "compact-to-audit-record-and-remove-full-corpus-from-vault",
            "rewrite-source-trace-to-audit-record-before-removal",
        }
    ]
    reviewed_reference_count = sum(len(item["references"]["reviewed"]) for item in entries)
    registry_reference_count = sum(len(item["references"]["registry"]) for item in entries)
    home_reference_count = sum(len(item["references"]["home"]) for item in entries)
    result = {
        "state": "passed",
        "scope": "candidate-post-promotion-cleanup-dry-run",
        "dryRun": True,
        "vault": rel(root, vault),
        "reviewed": rel(root, reviewed),
        "candidate": rel(root, candidate),
        "raw": rel(root, raw),
        "registry": rel(root, registry),
        "report": rel(root, report),
        "activeCandidateCount": len(active_entries),
        "archivedCandidateCount": len(archived_entries),
        "fullCorpusCandidateCount": len(full_corpus_entries),
        "lightweightAuditRecordCount": len(audit_entries),
        "candidateMarkdownCount": sum(item["markdownCount"] for item in entries),
        "candidateWikiLinkCount": sum(item["wikilinkCount"] for item in entries),
        "reviewedReferenceCount": reviewed_reference_count,
        "homeReferenceCount": home_reference_count,
        "registryReferenceCount": registry_reference_count,
        "recommendedCleanupActionCount": len(remove_actions),
        "recommendedCleanupActions": [
            {
                "corpusId": item["corpusId"],
                "path": item["path"],
                "action": item["recommendedAction"],
                "reason": item["reason"],
            }
            for item in remove_actions
        ],
        "entries": entries,
        "preconditionsForDestructiveCleanup": [
            "run candidate-cleanup-plan first and review its report",
            "rewrite reviewed source trace to lightweight audit records when reviewedReferenceCount > 0",
            "rewrite Home/archive summary references before removing full corpus markdown",
            "run validate-knowledge-vault after cleanup",
            "require explicit user approval before deleting or moving candidate full corpus out of the vault",
        ],
        "boundary": "dry-run-no-delete-no-move-no-reviewed-promotion",
    }
    write_text(report, _format_candidate_cleanup_plan_report(result))
    update_status(root, args.run_id, {"candidatePostPromotionCleanupPlan": result})
    print_json(result)
    return result


def run_candidate_cleanup_apply(args) -> dict:
    root = Path(args.root).resolve()
    vault = _resolve_under_root(root, args.vault)
    reviewed = _resolve_under_root(root, args.reviewed)
    candidate = _resolve_under_root(root, args.candidate)
    raw = _resolve_under_root(root, args.raw)
    registry = _resolve_under_root(root, args.registry)
    backup_root = _resolve_under_root(root, args.backup_root)
    report = _resolve_under_root(root, args.report)
    reviewer = args.reviewer.strip()
    approval_note = args.approval_note.strip()
    if not reviewer:
        raise ValueError("candidate-cleanup-apply requires reviewer")
    if not approval_note:
        raise ValueError("candidate-cleanup-apply requires approval note")

    plan = _quiet_call(run_candidate_cleanup_plan, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        candidate=rel(root, candidate),
        raw=rel(root, raw),
        registry=rel(root, registry),
        report="var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-plan.md",
        run_id=args.run_id,
    ))
    actions = [
        item for item in plan.get("entries", [])
        if item.get("kind") == "full-corpus"
        and item.get("recommendedAction") in {
            "compact-to-audit-record-and-remove-full-corpus-from-vault",
            "rewrite-source-trace-to-audit-record-before-removal",
        }
    ]

    audit_records = []
    moves = []
    rewrites = []
    for item in actions:
        source = (root / item["path"]).resolve()
        archive_root = (candidate / "_archive").resolve()
        if not source.exists():
            moves.append({"oldPath": item["path"], "state": "source-missing"})
            continue
        _ensure_path_under(source, archive_root, "candidate cleanup source")
        markdown_files = _candidate_markdown_files(source)
        corpus_hash = _candidate_corpus_hash(source, markdown_files)
        audit_path = _candidate_audit_path(root, candidate, item["corpusId"])
        destination = _unique_backup_destination(backup_root / today() / source.relative_to(archive_root))
        _ensure_path_under(destination, backup_root.resolve(), "candidate cleanup backup")

        audit_record = {
            "corpusId": item["corpusId"],
            "sourcePath": rel(root, source),
            "backupPath": rel(root, destination),
            "auditPath": rel(root, audit_path),
            "governanceState": item.get("governanceState"),
            "markdownCount": len(markdown_files),
            "wikilinkCount": item.get("wikilinkCount", 0),
            "corpusHashSha256": corpus_hash,
            "reviewer": reviewer,
            "approvalNote": approval_note,
            "cleanedAt": today(),
            "referencesBeforeCleanup": item.get("references", {}),
            "cleanupAction": item.get("recommendedAction"),
        }
        write_text(audit_path, _format_candidate_audit_record(audit_record))
        rewrites.extend(_rewrite_candidate_references_to_audit(
            root=root,
            vault=vault,
            reviewed=reviewed,
            registry=registry,
            old_root=rel(root, source),
            audit_ref=rel(root, audit_path),
        ))
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        _remove_empty_dirs_up_to(root, source.parent, archive_root)
        moves.append({
            "corpusId": item["corpusId"],
            "oldPath": audit_record["sourcePath"],
            "newPath": audit_record["backupPath"],
            "auditPath": audit_record["auditPath"],
            "state": "moved-out-of-vault",
        })
        audit_records.append(audit_record)

    _write_candidate_archive_readme(root, candidate, _archived_candidate_inventory(root, candidate))
    _write_candidate_audit_index(root, candidate, _candidate_audit_inventory(root, candidate))
    graph_filter = _ensure_obsidian_graph_filter(vault)
    sync = _sync_reviewed_index(root, vault, reviewed)
    reviewed_records = sync["records"]
    candidate_records = _candidate_inventory(root, candidate, reviewed)
    raw_records = _raw_inventory(root, raw)
    _write_home(
        vault,
        reviewed_records=reviewed_records,
        active_candidates=[item for item in candidate_records if item["governanceState"] == "active-review"],
        evidence_candidates=[item for item in candidate_records if item["governanceState"] != "active-review"],
        archived_candidates=_archived_candidate_inventory(root, candidate),
        audit_records=_candidate_audit_inventory(root, candidate),
        raw_records=raw_records,
    )

    post_plan = _quiet_call(run_candidate_cleanup_plan, SimpleNamespace(
        root=str(root),
        vault=rel(root, vault),
        reviewed=rel(root, reviewed),
        candidate=rel(root, candidate),
        raw=rel(root, raw),
        registry=rel(root, registry),
        report="var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-plan.md",
        run_id=args.run_id,
    ))
    result = {
        "state": "passed" if post_plan.get("fullCorpusCandidateCount") == 0 else "partial",
        "scope": "candidate-post-promotion-cleanup-apply",
        "dryRun": False,
        "vault": rel(root, vault),
        "candidate": rel(root, candidate),
        "backupRoot": rel(root, backup_root),
        "reviewer": reviewer,
        "approvalNote": approval_note,
        "movedCorpusCount": len([item for item in moves if item.get("state") == "moved-out-of-vault"]),
        "auditRecordCount": len(_candidate_audit_inventory(root, candidate)),
        "remainingFullCorpusCandidateCount": post_plan.get("fullCorpusCandidateCount"),
        "recommendedCleanupActionCount": post_plan.get("recommendedCleanupActionCount"),
        "rewrittenFileCount": len(rewrites),
        "graphFilter": graph_filter,
        "moves": moves,
        "rewrites": rewrites,
        "auditRecords": audit_records,
        "postCleanupPlanReport": post_plan.get("report"),
        "report": rel(root, report),
        "boundary": "approved-apply-move-full-corpus-out-of-vault-keep-lightweight-audit-records",
    }
    write_text(report, _format_candidate_cleanup_apply_report(result))
    update_status(root, args.run_id, {"candidatePostPromotionCleanupApply": result})
    print_json(result)
    if result["state"] != "passed":
        raise RuntimeError("candidate cleanup apply did not remove all full corpus candidates")
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
    domain = safe_run_id(getattr(args, "domain", None) or "agent")
    target_dir_value = args.target_dir or f"user/knowledge/reviewed/{domain}/concepts"
    target_dir = _resolve_under_root(root, target_dir_value)
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
    audit_records = _candidate_audit_inventory(root, candidate)
    removed_secondary_views = _dedupe_preserve_order(
        sync.get("removedSecondaryViews", []) + _remove_secondary_vault_view_files(root, vault)
    )
    _write_home(
        vault,
        reviewed_records=reviewed_records,
        active_candidates=active_candidates,
        evidence_candidates=evidence_candidates,
        archived_candidates=archived_candidates,
        audit_records=audit_records,
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
        "candidateAuditRecordCount": len(audit_records),
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
    registry = _resolve_under_root(root, getattr(args, "registry", "user/registry/knowledge.local.json"))
    run_id = safe_run_id(args.run_id or timestamp_id().replace("rag-candidate", "raw-to-reviewed-pipeline"))
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
    domain = safe_run_id(getattr(args, "domain", None) or "agent")
    target = _resolve_under_root(root, args.target or f"user/knowledge/reviewed/{domain}/{run_id}.md")
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
        raw_domain=domain,
        copy_raw=bool(args.copy_raw),
        max_chunk_chars=args.max_chunk_chars,
        extraction_granularity=getattr(args, "extraction_granularity", "standard"),
        entity_cap=getattr(args, "entity_cap", None),
        concept_cap=getattr(args, "concept_cap", None),
        batch_strategy=getattr(args, "batch_strategy", "single-pass-local-conversion"),
        tag_vocabulary_mode=getattr(args, "tag_vocabulary_mode", "default"),
        allowed_tags=getattr(args, "allowed_tags", []) or [],
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
    steps["promoteReviewedConcepts"] = _promote_pipeline_concepts(
        root=root,
        reviewed=reviewed,
        domain=domain,
        wiki=candidate_wiki,
        target=target,
        scope=args.scope,
        reviewer=args.reviewer,
        approval_note=args.approval_note,
        review_after=args.review_after,
    )
    steps["ensureReviewedDomain"] = _ensure_reviewed_domain(
        root=root,
        vault=vault,
        reviewed=reviewed,
        raw=raw_root,
        registry=registry,
        domain=domain,
        target=target,
        allowed_tags=getattr(args, "allowed_tags", []) or [],
    )
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
        "scope": "raw-to-reviewed-query-pipeline-smoke",
        "runId": run_id,
        "inputs": [rel(root, path) for path in input_paths],
        "candidateWiki": candidate_wiki_ref,
        "manifest": rel(root, manifest),
        "targetReviewed": target_ref,
        "query": args.question,
        "queryHitsTarget": query_hits_target,
        "archivePromotedCandidate": bool(args.archive_promoted_candidate),
        "extractionGranularity": getattr(args, "extraction_granularity", "standard"),
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


def _pipeline_concept_catalog() -> dict[str, tuple[str, list[str]]]:
    catalog = dict(PIPELINE_SMOKE_CONCEPTS)
    catalog.update(EXTERNALIZATION_PIPELINE_CONCEPTS)
    return catalog


def _promote_pipeline_concepts(
    root: Path,
    reviewed: Path,
    domain: str,
    wiki: Path,
    target: Path,
    scope: str,
    reviewer: str,
    approval_note: str,
    review_after: str,
) -> dict:
    concept_dir = reviewed / domain / "concepts"
    concept_dir.mkdir(parents=True, exist_ok=True)
    source_stem = target.stem
    catalog = _pipeline_concept_catalog()
    promoted = []
    existing = []
    for candidate_page in sorted((wiki / "concepts").glob("*.md")):
        concept = candidate_page.stem
        if concept in {"CandidateKnowledge", "StructuredIngestion"}:
            continue
        definition = _section_by_heading(read_text(candidate_page), "Candidate Definition") or catalog.get(concept, ("", []))[0]
        neighbors = catalog.get(concept, ("", []))[1]
        reviewed_page = concept_dir / f"{concept}.md"
        if reviewed_page.exists():
            existing.append(rel(root, reviewed_page))
            continue
        write_text(reviewed_page, _format_pipeline_reviewed_concept_page(
            root=root,
            concept=concept,
            definition=definition,
            neighbors=neighbors,
            domain=domain,
            source_page=target,
            source_stem=source_stem,
            scope=scope,
            reviewer=reviewer,
            approval_note=approval_note,
            review_after=review_after,
        ))
        promoted.append(rel(root, reviewed_page))
    result = {
        "state": "passed" if promoted or existing else "partial",
        "domain": domain,
        "promotedCount": len(promoted),
        "existingCount": len(existing),
        "promotedPages": promoted,
        "existingPages": existing,
        "boundary": "approved-pipeline-concept-promotion-source-traced-to-reviewed-page",
    }
    update_status(root, source_stem, {"pipelineSmokeConceptPromotion": result})
    return result


def _format_pipeline_reviewed_concept_page(
    root: Path,
    concept: str,
    definition: str,
    neighbors: list[str],
    domain: str,
    source_page: Path,
    source_stem: str,
    scope: str,
    reviewer: str,
    approval_note: str,
    review_after: str,
) -> str:
    tags = _domain_default_tags(domain)
    aliases = _concept_aliases(concept)
    related = _dedupe_preserve_order([source_stem] + [item for item in neighbors if item != concept])
    related_links = "\n".join(f"- [[{item}]]" for item in related)
    doc_name = rel(root, root / "user" / "knowledge" / "reviewed" / domain / "concepts" / f"{concept}.md")
    return f"""---
documentName: {doc_name}
version: v1.0.0-reviewed-concept
updatedAt: {today()}
status: active
knowledgeRole: authoritative
authoritative: true
tags: [{", ".join(tags)}]
aliases:
{chr(10).join(f"  - {json.dumps(item, ensure_ascii=False)}" for item in aliases)}
purpose: 保存从已审核 raw-to-reviewed pipeline 晋升的 reviewed concept：{concept}。
scope:
  - reviewed-knowledge
  - {scope}
  - {domain}
prerequisites:
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - {rel(root, source_page)}
outputTo:
  - {doc_name}
owner: user
reviewAfter: {review_after}
supersededBy:
dependsOn:
  - {rel(root, source_page)}
review:
  reviewedBy: {reviewer}
  reviewedAt: {today()}
  decision: user-approved-pipeline-concept-promotion
---
# {concept}

## 元数据
```yaml
knowledgeId: {concept}
knowledgeRole: authoritative
authoritative: true
scope: {scope}
domain: {domain}
reviewedAt: {today()}
reviewedBy: {reviewer}
sourceRefs:
  - {rel(root, source_page)}
supersedes: []
reviewAfter: {review_after}
sensitiveRisk: low
storageBoundary: user/knowledge/reviewed/{domain}/concepts
approvalNote: {json.dumps(approval_note, ensure_ascii=False)}
```

## Statement

{definition}

## Concept Detail

- 本概念来自 source-level reviewed page `[[{source_stem}]]`，用于帮助 agent 在 reviewed graph 中定位原始材料的核心主题。
- 概念页只保留可独立复用的定义、适用范围、边界和相邻概念；完整论证和上下文应回到 source-level reviewed page 阅读。
- 当本概念与相邻概念共同出现时，应按 source page 的 Source Trace 和 Governance Notes 判断证据等级，不回退读取 raw、candidate 或 runtime chunk 作为事实源。

## Applicability

- 适用于阅读或查询 reviewed source page `[[{source_stem}]]` 时快速定位 `{concept}`。
- 适用于把本 domain 与相邻 reviewed concepts 建立知识图谱关系。
- 适用于在回答前提示 agent 回到 source-level reviewed page 获取更完整上下文。

## Non-Applicability

- 本页不替代 source-level reviewed page，也不覆盖原始材料的全部信息。
- 本页不能作为 reviewed source page 不存在之断言的证据。
- 本页不得把 raw、candidate、runtime artifacts 或插件输出反向当作事实源。

## Source Trace

| Source | Evidence Summary | Notes |
|---|---|---|
| `{rel(root, source_page)}` | 已审核的 source-level authoritative reviewed page。 | Concept source trace 指向 reviewed Knowledge，不指向 candidate 或 runtime chunks。 |

## Related

{related_links}

## Governance Notes

- 本页只在 `pipeline-smoke` 获得明确 approval 后生成。
- Candidate wiki、chunks 和 runtime graph 仍是证据或运行态产物，不是 authoritative facts。
"""


def _ensure_reviewed_domain(
    root: Path,
    vault: Path,
    reviewed: Path,
    raw: Path,
    registry: Path,
    domain: str,
    target: Path,
    allowed_tags: list[str],
) -> dict:
    domain_dir = reviewed / domain
    concepts_dir = domain_dir / "concepts"
    raw_dir = raw / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    concepts_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    tags = _domain_default_tags(domain, allowed_tags)
    schema = domain_dir / "schema.md"
    if not schema.exists():
        write_text(schema, _format_domain_schema(root, domain, tags))
    index = domain_dir / "index.md"
    write_text(index, _format_domain_index(root, domain, target, concepts_dir))
    registry_updated = _upsert_registry_domain(root, registry, domain)
    result = {
        "state": "passed",
        "domain": domain,
        "domainDir": rel(root, domain_dir),
        "rawDir": rel(root, raw_dir),
        "index": rel(root, index),
        "schema": rel(root, schema),
        "concepts": rel(root, concepts_dir),
        "registryUpdated": registry_updated,
        "boundary": "local-registry-and-domain-layout-update-no-public-knowledge-body",
    }
    update_status(root, "reviewed-knowledge", {"pipelineDomainEnsure": result})
    return result


def _domain_default_tags(domain: str, allowed_tags: list[str] | None = None) -> list[str]:
    if allowed_tags:
        return _dedupe_preserve_order([safe_run_id(tag).lower() for tag in allowed_tags])
    if domain == "llm-agent-externalization":
        return ["llm-agent", "externalization", "memory", "skill", "protocol", "harness-engineering", "governance"]
    if domain == "agent-harness-engineering":
        return ["agent-harness", "harness-architecture", "agent-evaluation", "agent-governance", "trace-native", "workflow-evidence", "knowledge-governance"]
    return [domain]


def _concept_aliases(concept: str) -> list[str]:
    aliases = {
        "LLMAgentExternalization": ["LLM agent externalization", "agent externalization", "外部化智能体能力"],
        "ExternalizedMemory": ["externalized memory", "agent memory", "外部化记忆"],
        "SkillLibrary": ["skill library", "skills", "技能库"],
        "ProtocolMediatedCoordination": ["protocol mediated coordination", "agent protocol", "协议化协作"],
        "HarnessEngineering": ["harness engineering", "agent harness engineering", "运行支架工程"],
        "StatePersistence": ["state persistence", "persistent state", "状态持久化"],
        "ToolInterfaceBoundary": ["tool interface boundary", "tool boundary", "工具接口边界"],
        "GovernedExternalState": ["governed external state", "external state governance", "外部状态治理"],
    }
    return aliases.get(concept, [concept])


def _format_domain_schema(root: Path, domain: str, tags: list[str]) -> str:
    domain_title = _domain_title(domain)
    tag_lines = "\n".join(f"- `{tag}`" for tag in tags)
    doc_name = f"user/knowledge/reviewed/{domain}/schema.md"
    return f"""---
documentName: {doc_name}
version: v1.0.0-domain-schema
updatedAt: {today()}
status: active
knowledgeRole: domain-schema
authoritative: true
purpose: Define reviewed Knowledge layout, tags, aliases, source gate, and validation rules for {domain}.
scope:
  - reviewed-knowledge
  - user-private
  - {domain}
prerequisites:
  - user/knowledge/reviewed/{domain}/index.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - harness/governance/KnowledgePromotionPolicy.md
outputTo:
  - {doc_name}
owner: user
reviewAfter: source-updated-or-2026-12-31
supersededBy:
dependsOn:
  - user/knowledge/reviewed/{domain}/index.md
review:
  reviewedBy: user
  reviewedAt: {today()}
  decision: generated-by-approved-pipeline-smoke
---
# {domain_title} Schema

## Directory Rules

- `index.md` is the domain entry page.
- Formal reviewed pages use semantic names and live directly under `reviewed/{domain}/`.
- Reviewed concept pages live under `reviewed/{domain}/concepts/`.
- Raw sources live under `raw/{domain}/`.

## Naming Rules

- Formal reviewed pages must not use smoke, pipeline, stage, or temporary run-id names.
- Concept pages use stable PascalCase concept ids.

## Required Reviewed Page Sections

- Statement
- Applicability
- Non-Applicability
- Key Concepts
- Source Trace
- Staleness
- Governance Notes

## Validation Rules

- Reviewed graph should have no broken links.
- The same raw source and topic should have one active authoritative page.
- Runtime artifacts and candidate pages remain evidence, not fact sources.

## Controlled Tag Vocabulary

{tag_lines}

## Alias Rules

- Each reviewed concept page should maintain aliases, abbreviations, or cross-language names.
- Duplicate governance must use titles, aliases, Key Concepts, wikilinks, source trace, and body similarity as inputs.
- Aliases are governance inputs, not display-only metadata.

## Source Gate Rules

- Empty files, frontmatter-only files, incompatible types, and duplicate body hash sources must be blocked before candidate extraction.
- Source slugs should include path fingerprint and content hash evidence to avoid same-name overwrite.
- Candidate manifest should record extraction granularity, entity cap, concept cap, batch strategy, tag vocabulary, source fingerprint, and body hash.
"""


def _format_domain_index(root: Path, domain: str, target: Path, concepts_dir: Path) -> str:
    domain_title = _domain_title(domain)
    doc_name = f"user/knowledge/reviewed/{domain}/index.md"
    concept_links = []
    for page in sorted(concepts_dir.glob("*.md")):
        concept_links.append(f"- [[{page.stem}]]")
    if not concept_links:
        concept_links.append("- _No reviewed concept pages yet._")
    return f"""---
documentName: {doc_name}
version: v1.0.0-domain-index
updatedAt: {today()}
status: active
knowledgeRole: domain-index
authoritative: true
purpose: Reviewed Knowledge domain entry for {domain}.
scope:
  - reviewed-knowledge
  - user-private
  - {domain}
prerequisites:
  - user/knowledge/reviewed/{domain}/schema.md
relatedDocuments:
  - user/knowledge/reviewed/{domain}/schema.md
  - {rel(root, target)}
outputTo:
  - {doc_name}
owner: user
reviewAfter: source-updated-or-2026-12-31
supersededBy:
dependsOn:
  - user/knowledge/reviewed/{domain}/schema.md
review:
  reviewedBy: user
  reviewedAt: {today()}
  decision: generated-by-approved-pipeline-smoke
---
# {domain_title}

## Reviewed Knowledge

- [[{target.stem}]]

## Reviewed Concepts

{chr(10).join(concept_links)}

## Domain Schema

- [[reviewed/{domain}/schema|schema]]
"""


def _upsert_registry_domain(root: Path, registry: Path, domain: str) -> bool:
    registry.parent.mkdir(parents=True, exist_ok=True)
    if registry.exists():
        try:
            data = json.loads(read_text(registry))
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    data.setdefault("schemaVersion", "harness.knowledgeRegistry.v1")
    data.setdefault("registryKind", "local")
    data["updatedAt"] = today()
    sources = data.setdefault("knowledgeSources", [{
        "knowledgeId": "user-knowledge-vault",
        "root": "user/knowledge",
        "scope": "user-private",
        "status": "active",
        "description": "Local-only user knowledge vault route.",
        "knowledgeRoots": {
            "home": "user/knowledge/Home.md",
            "raw": "user/knowledge/raw",
            "candidate": "user/knowledge/candidate",
            "reviewed": "user/knowledge/reviewed",
        },
        "domains": [],
        "authoritativeBoundary": "reviewed-only",
        "gitBoundary": "ignored-local-only",
        "sensitiveBoundarySummary": [],
        "updatedAt": today(),
    }])
    source = sources[0]
    domains = source.setdefault("domains", [])
    entry = {
        "domainId": domain,
        "raw": f"user/knowledge/raw/{domain}",
        "reviewed": f"user/knowledge/reviewed/{domain}",
        "index": f"user/knowledge/reviewed/{domain}/index.md",
        "schema": f"user/knowledge/reviewed/{domain}/schema.md",
        "concepts": f"user/knowledge/reviewed/{domain}/concepts",
        "status": "active",
    }
    for index, item in enumerate(domains):
        if item.get("domainId") == domain:
            changed = item != entry
            domains[index] = entry
            break
    else:
        changed = True
        domains.append(entry)
    source["updatedAt"] = today()
    write_text(registry, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return changed


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
    catalog = _pipeline_concept_catalog()
    for concept in sorted(concept_names):
        definition, neighbors = catalog[concept]
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
    externalization_terms = ["externalization", "externalized", "memory", "skills", "protocols"]
    if any(term in haystack for term in externalization_terms) and "agent" in haystack:
        return list(EXTERNALIZATION_PIPELINE_CONCEPTS.keys())
    if "agent harness" in haystack or "harness engineering" in haystack:
        return list(PIPELINE_SMOKE_CONCEPTS.keys())
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
    if "LLMAgentExternalization" in concepts:
        return "\n".join([
            "- LLM agent capability should be understood as a combination of model calls and externalized system components such as memory, skills, protocols, tools, and harness controls.",
            "- [[ExternalizedMemory]] and [[StatePersistence]] need provenance, retention, staleness, and deletion governance rather than ad hoc prompt carryover.",
            "- [[SkillLibrary]] and [[ToolInterfaceBoundary]] separate reusable agent procedures from the base model and therefore need explicit review, versioning, and side-effect boundaries.",
            "- [[ProtocolMediatedCoordination]] makes handoff and coordination contracts auditable across agents, tools, and humans.",
            "- [[HarnessEngineering]] and [[GovernedExternalState]] connect this material to the existing reviewed Harness knowledge base.",
        ])
    if "AgentHarnessEngineering" in concepts:
        return "\n".join([
            "- Agent Harness Engineering 应作为独立系统工程层处理，而不是 prompt 或模型能力的附属细节。",
            "- 长周期 agent 任务可靠性受 execution harness、tool boundary、context、observability、verification 和 governance 共同约束。",
            "- [[ETCLOVGTaxonomy]] 可作为分析 agent harness 的七层框架。",
            "- [[TraceNativeEvaluation]]、[[StandardHandoffProtocol]]、[[AdaptiveHarnessOptimization]] 和 [[ContextDrift]] 是后续 Harness 建设需要持续处理的 reviewed concepts。",
        ])
    return "- 本材料已被转换为 source-grounded candidate page；具体 claims 需要人工审核补充。"


def _pipeline_entities(concepts: list[str]) -> str:
    if "LLMAgentExternalization" in concepts:
        return "\n".join([
            "- `LLM Agent`: the runtime actor whose durable capability depends on external memory, skills, protocols, tools, and harness controls.",
            "- `Memory`: external state that must carry provenance, lifecycle, and staleness metadata.",
            "- `Skill`: reusable procedure or tool-use package governed separately from the base model.",
            "- `Protocol`: coordination contract for tool, human, or multi-agent interaction.",
            "- `Harness`: execution and governance layer that controls externalized state and side effects.",
        ])
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
        if stripped.startswith("#") or any(term in stripped.lower() for term in ["agent harness", "harness engineering", "observability", "verification", "governance", "externalization", "memory", "skills", "protocols"]):
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
            "inputCount",
            "blockedInputCount",
            "nodeCount",
            "edgeCount",
            "matchCount",
            "reviewedPageCount",
            "readyForHumanReviewCount",
            "promotedCount",
            "existingCount",
            "archiveActionCount",
            "registryUpdated",
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
        ("smokeCandidateEnrichment", "passed"),
        ("candidateHealth", "passed"),
        ("candidateLint", "passed"),
        ("candidateGraph", "passed"),
        ("enrichmentPlan", "passed"),
        ("reviewPackage", "ready-for-human-review"),
        ("promoteReviewed", "promoted"),
        ("promoteReviewedConcepts", "passed"),
        ("ensureReviewedDomain", "passed"),
        ("vaultGovernance", "passed"),
        ("reviewedHealth", "passed"),
        ("reviewedGraph", "passed"),
        ("reviewedQuery", "passed"),
    ]
    blocking = []
    ingest = steps.get("ingest", {})
    if ingest.get("state") not in {"passed", "partial"}:
        blocking.append(f"ingest expected passed or partial, got {ingest.get('state')}")
    if ingest.get("inputCount", 0) < 1:
        blocking.append("ingest accepted no sources")
    if ingest.get("blockedInputCount", 0):
        blocking.append(f"ingest blocked inputs: {ingest.get('blockedInputCount')}")
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
        f"# Raw To Reviewed Pipeline Smoke Report - {today()}",
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
    pages = _reviewed_pages(reviewed, authoritative_only=False)
    records = [_page_record(root, vault, p) for p in pages]
    records.sort(key=lambda item: item["title"].lower())
    _write_home(
        vault,
        reviewed_records=records,
        audit_records=_candidate_audit_inventory(root, vault / "candidate"),
        raw_records=_raw_inventory(root, vault / "raw"),
    )
    removed = _remove_secondary_vault_view_files(root, vault)
    authoritative_count = len([item for item in records if item["authoritative"]])
    evidence_count = len(records) - authoritative_count
    return {
        "reviewedPageCount": len(records),
        "authoritativeReviewedPageCount": authoritative_count,
        "evidenceReviewedPageCount": evidence_count,
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
    audit_records: list[dict] | None = None,
    raw_records: list[dict] | None = None,
) -> None:
    reviewed_records = reviewed_records or []
    active_candidates = active_candidates or []
    evidence_candidates = evidence_candidates or []
    archived_candidates = archived_candidates or []
    audit_records = audit_records or []
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
        "这是 Obsidian vault 的单一入口。默认事实源只看 `reviewed/` 中的 authoritative pages；用户审核候选时只看本页的 Candidate Review Queue。",
        "",
    ]

    domain_records = _domain_records(reviewed_records, raw_records)
    if domain_records:
        lines.extend([
            "## Reviewed Domains",
            "",
            "| Domain | Reviewed Root | Raw Root |",
            "|---|---|---|",
        ])
        for item in domain_records:
            lines.append(
                f"| [[{item['indexStem']}|{item['title']}]] | "
                f"`{item['reviewedRoot']}` | `{item['rawRoot']}` |"
            )
        lines.append("")

    knowledge_records = [
        item for item in reviewed_records
        if item.get("authoritative", True)
        and item.get("status") not in {"archived", "superseded", "deprecated"}
        and not item["vaultPath"].replace("\\", "/").endswith("/index.md")
        and not item["vaultPath"].replace("\\", "/").endswith("/schema.md")
        and "/concepts/" not in item["vaultPath"].replace("\\", "/")
    ]
    concept_records = [
        item for item in reviewed_records
        if item.get("authoritative", True)
        and item.get("status") not in {"archived", "superseded", "deprecated"}
        and "/concepts/" in item["vaultPath"].replace("\\", "/")
    ]
    validation_evidence_records = [
        item for item in reviewed_records
        if not item.get("authoritative", True)
        and item.get("status") not in {"archived", "superseded", "deprecated"}
    ]
    lines.extend([
        "## Reviewed Knowledge",
        "",
        "| Title | Scope | Review |",
        "|---|---|---|",
    ])
    if knowledge_records:
        for item in knowledge_records:
            lines.append(
                f"| [[{item['vaultStem']}|{item['title']}]] | `{item['scope']}` | "
                f"{item.get('reviewedBy') or 'unknown'} / {item.get('reviewedAt') or 'unknown'} |"
            )
    else:
        lines.append("| _No reviewed Knowledge yet._ |  |  |")

    if concept_records:
        lines.extend([
            "",
            "## Reviewed Concepts",
            "",
            "| Concept | Domain | Review |",
            "|---|---|---|",
        ])
        for item in concept_records:
            parts = item["vaultPath"].replace("\\", "/").split("/")
            domain = parts[1] if len(parts) > 2 else "unknown"
            lines.append(
                f"| [[{item['vaultStem']}|{item['title']}]] | `{domain}` | "
                f"{item.get('reviewedBy') or 'unknown'} / {item.get('reviewedAt') or 'unknown'} |"
            )

    if validation_evidence_records:
        lines.extend([
            "",
            "## Reviewed Validation Evidence",
            "",
            "| Title | Role | Authoritative Page |",
            "|---|---|---|",
        ])
        for item in validation_evidence_records:
            authoritative_page = item.get("authoritativePage") or "none"
            if authoritative_page.startswith("user/knowledge/"):
                authoritative_page = authoritative_page.removeprefix("user/knowledge/").removesuffix(".md")
            lines.append(
                f"| [[{item['vaultStem']}|{item['title']}]] | `{item['knowledgeRole']}` | "
                f"`{authoritative_page}` |"
            )

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
        "## Candidate Audit Records",
        "",
        "| Corpus | State | Audit Record | Backup Path |",
        "|---|---|---|---|",
    ])
    if audit_records:
        for item in audit_records:
            lines.append(
                f"| `{item['runId']}` | `{item['governanceState']}` | "
                f"`{item['path']}` | `{item.get('backupPath') or 'unknown'}` |"
            )
    else:
        lines.append("| _No post-promotion candidate cleanup audit records._ |  |  |  |")

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


def _domain_records(reviewed_records: list[dict], raw_records: list[dict]) -> list[dict]:
    domains: dict[str, dict] = {}
    for item in reviewed_records:
        parts = item["vaultPath"].replace("\\", "/").split("/")
        if len(parts) < 3 or parts[0] != "reviewed":
            continue
        domain = parts[1]
        if domain.startswith("_"):
            continue
        domains.setdefault(domain, {
            "domain": domain,
            "title": _domain_title(domain),
            "reviewedRoot": f"reviewed/{domain}/",
            "rawRoot": f"raw/{domain}/",
            "indexStem": f"reviewed/{domain}/index",
        })
    for item in raw_records:
        parts = item["path"].replace("\\", "/").split("/")
        if len(parts) < 4 or parts[:2] != ["user", "knowledge"] or parts[2] != "raw":
            continue
        domain = parts[3]
        domains.setdefault(domain, {
            "domain": domain,
            "title": _domain_title(domain),
            "reviewedRoot": f"reviewed/{domain}/",
            "rawRoot": f"raw/{domain}/",
            "indexStem": f"reviewed/{domain}/index",
        })
    return [domains[key] for key in sorted(domains)]


def _domain_title(domain: str) -> str:
    words = [part for part in re.split(r"[-_\s]+", domain) if part]
    return " ".join(word[:1].upper() + word[1:] for word in words) or domain


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
        f"- Authoritative reviewed pages: {result['authoritativeReviewedPageCount']}",
        f"- Evidence reviewed pages: {result['evidenceReviewedPageCount']}",
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


def _format_duplicate_governance_report(result: dict) -> str:
    lines = [
        f"# Duplicate Reviewed Knowledge Governance - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Reviewed files: {result['reviewedFileCount']}",
        f"- Duplicate groups: {result['duplicateGroupCount']}",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## 规则",
        "",
        "- 同一 raw source 和同一 topic 的 reviewed pages 只能保留一个 authoritative page。",
        "- 其余重复页必须标记为 validation evidence、superseded、archived 或 deprecated。",
        "- Non-authoritative evidence 可以进入 graph 作为导航节点，但不得被 reviewed query 或 gap plan 当作事实源。",
        "",
        "## Blocking Issues",
        "",
    ]
    lines.extend(f"- {item}" for item in result["blockingIssues"] or ["无"])
    lines.extend([
        "",
        "## Duplicate Groups",
        "",
    ])
    if not result["duplicateGroups"]:
        lines.append("- 未发现同 raw source / topic 的重复 reviewed pages。")
    for group in result["duplicateGroups"]:
        lines.extend([
            f"### {group['topicKey']}",
            "",
            f"- Raw source: `{group['rawSource']}`",
            f"- State: `{group['state']}`",
            f"- Authoritative pages: {', '.join(f'`{page}`' for page in group['authoritativePages']) or '`none`'}",
            f"- Non-authoritative pages: {', '.join(f'`{page}`' for page in group['nonAuthoritativePages']) or '`none`'}",
            "",
            "| Page | Role | Authoritative | Disposition | Reviewed |",
            "|---|---|---|---|---|",
        ])
        for page in group["pages"]:
            lines.append(
                f"| `{page['page']}` | `{page['knowledgeRole']}` | `{str(page['authoritative']).lower()}` | "
                f"`{page['duplicateDisposition'] or page['status']}` | {page['reviewedBy']} / {page['reviewedAt']} |"
            )
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


def _validation_check(name: str, passed: bool, summary: str, issues: list | None = None, details: dict | None = None) -> dict:
    normalized_issues = [str(item) for item in (issues or []) if str(item)]
    return {
        "name": name,
        "state": "passed" if passed and not normalized_issues else "failed",
        "summary": summary,
        "issues": normalized_issues,
        "details": details or {},
    }


def _validate_knowledge_registry(
    root: Path,
    vault: Path,
    reviewed: Path,
    candidate: Path,
    raw: Path,
    registry: Path,
) -> tuple[dict, list[dict]]:
    issues: list[str] = []
    domains: list[dict] = []
    details: dict = {"registry": rel(root, registry)}
    if not registry.exists():
        return _validation_check("local-registry", False, "registry missing", [f"missing {rel(root, registry)}"], details), domains

    text = read_text(registry)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return _validation_check("local-registry", False, "registry invalid json", [str(exc)], details), domains

    if data.get("schemaVersion") != "harness.knowledgeRegistry.v1":
        issues.append("schemaVersion must be harness.knowledgeRegistry.v1")
    if data.get("registryKind") != "local":
        issues.append("registryKind must be local")
    if _contains_absolute_path_or_url(text):
        issues.append("registry must not contain absolute paths or URLs")
    if re.search(r"(?i)(api[_-]?key|token|password|secret|settings\.xml)", text):
        issues.append("registry must not contain credential-like keys")

    sources = data.get("knowledgeSources") or []
    if not sources:
        issues.append("knowledgeSources must not be empty")
    source = sources[0] if sources else {}
    roots = source.get("knowledgeRoots") or {}
    expected_roots = {
        "home": vault / "Home.md",
        "raw": raw,
        "candidate": candidate,
        "reviewed": reviewed,
    }
    for key, expected in expected_roots.items():
        value = roots.get(key)
        if not value:
            issues.append(f"knowledgeRoots.{key} missing")
            continue
        if _is_absolute_or_url(value):
            issues.append(f"knowledgeRoots.{key} must be relative: {value}")
            continue
        path = (root / value).resolve()
        if path != expected.resolve():
            issues.append(f"knowledgeRoots.{key} expected {rel(root, expected)}, got {value}")
        if not path.exists():
            issues.append(f"knowledgeRoots.{key} target missing: {value}")

    domains = source.get("domains") or []
    if not domains:
        issues.append("registry domains must not be empty")
    for item in domains:
        domain_id = item.get("domainId")
        if not domain_id:
            issues.append("domainId missing")
            continue
        for key in ["raw", "reviewed", "index", "schema"]:
            value = item.get(key)
            if not value:
                issues.append(f"domain {domain_id} {key} missing")
                continue
            if _is_absolute_or_url(value):
                issues.append(f"domain {domain_id} {key} must be relative: {value}")
                continue
            if not (root / value).exists():
                issues.append(f"domain {domain_id} {key} target missing: {value}")
        concepts = item.get("concepts")
        if concepts and not (root / concepts).exists():
            issues.append(f"domain {domain_id} concepts target missing: {concepts}")

    ignored = _git_check_ignored(root, registry)
    if not ignored["ignored"]:
        issues.append(f"registry must be ignored by Git: {rel(root, registry)}")

    details.update({
        "schemaVersion": data.get("schemaVersion"),
        "registryKind": data.get("registryKind"),
        "domainCount": len(domains),
        "gitIgnore": ignored,
    })
    return _validation_check("local-registry", not issues, f"domains={len(domains)}", issues, details), domains


def _validate_home_entry(root: Path, vault: Path, domains: list[dict]) -> dict:
    home = vault / "Home.md"
    issues: list[str] = []
    details = {"home": rel(root, home)}
    if not home.exists():
        return _validation_check("home-single-entry", False, "Home.md missing", [f"missing {rel(root, home)}"], details)
    text = read_text(home)
    if not text.lstrip().startswith("---"):
        issues.append("Home.md missing frontmatter")
    if _frontmatter_value(text, "entry_policy") != "single-entry":
        issues.append("Home.md entry_policy must be single-entry")
    for section in [
        "## Reviewed Domains",
        "## Reviewed Knowledge",
        "## Candidate Review Queue",
        "## Archived Candidate Evidence",
        "## Candidate Audit Records",
        "## Raw Sources",
        "## Governance Rules",
    ]:
        if section not in text:
            issues.append(f"Home.md missing section {section}")
    for item in domains:
        domain_id = item.get("domainId")
        if domain_id and f"reviewed/{domain_id}/index" not in text:
            issues.append(f"Home.md missing domain index link for {domain_id}")
    old_patterns = ["reviewed/agent/", "raw/agent/", "[[llm-wiki-absorption-pdf-smoke]]"]
    for pattern in old_patterns:
        if pattern in text:
            issues.append(f"Home.md contains old layout reference: {pattern}")
    secondary = [rel(root, vault / name) for name in SECONDARY_VAULT_VIEW_FILES if (vault / name).exists()]
    if secondary:
        issues.append("secondary vault view files must not exist: " + ", ".join(secondary))

    lookup = _page_lookup(vault, _graph_pages(vault, vault / "reviewed"))
    unresolved = []
    for link in extract_wikilinks(text):
        if not _resolve_wikilink(link, lookup):
            unresolved.append(link)
    if unresolved:
        issues.append("Home.md has unresolved wikilinks: " + ", ".join(sorted(set(unresolved))))

    details.update({"secondaryViews": secondary, "wikilinkCount": len(extract_wikilinks(text))})
    return _validation_check("home-single-entry", not issues, "Home.md single-entry view checked", issues, details)


def _validate_domain_layout(root: Path, vault: Path, reviewed: Path, raw: Path, domains: list[dict]) -> dict:
    issues: list[str] = []
    expected = {item.get("domainId") for item in domains if item.get("domainId")}
    reviewed_domains = {
        path.name for path in reviewed.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    } if reviewed.exists() else set()
    raw_domains = {
        path.name for path in raw.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    } if raw.exists() else set()

    if expected and reviewed_domains != expected:
        issues.append(f"reviewed domains mismatch: expected {sorted(expected)}, got {sorted(reviewed_domains)}")
    if expected and raw_domains - expected:
        issues.append(f"raw contains unregistered domains: {sorted(raw_domains - expected)}")
    root_reviewed_pages = [rel(root, path) for path in reviewed.glob("*.md")] if reviewed.exists() else []
    if root_reviewed_pages:
        issues.append("reviewed root must not contain markdown pages: " + ", ".join(root_reviewed_pages))

    for item in domains:
        domain_id = item.get("domainId")
        if not domain_id:
            continue
        domain_dir = root / item.get("reviewed", "")
        index = root / item.get("index", "")
        schema = root / item.get("schema", "")
        raw_dir = root / item.get("raw", "")
        concepts = root / item.get("concepts", "") if item.get("concepts") else None
        for label, path in [("reviewed", domain_dir), ("index", index), ("schema", schema), ("raw", raw_dir)]:
            if not path.exists():
                issues.append(f"domain {domain_id} {label} missing: {rel(root, path)}")
        if concepts and not concepts.exists():
            issues.append(f"domain {domain_id} concepts missing: {rel(root, concepts)}")
        for label, path, role in [("index", index, "domain-index"), ("schema", schema, "domain-schema")]:
            if not path.exists():
                continue
            text = read_text(path)
            if not text.lstrip().startswith("---"):
                issues.append(f"domain {domain_id} {label} missing frontmatter")
            if _knowledge_role(text) != role:
                issues.append(f"domain {domain_id} {label} knowledgeRole must be {role}")
        for page in sorted(domain_dir.rglob("*.md")) if domain_dir.exists() else []:
            name = page.stem.lower()
            role = _knowledge_role(read_text(page))
            if role in {"domain-index", "domain-schema"}:
                continue
            if re.search(r"(smoke|pipeline|^p\d+-|^h\d+-)", name):
                issues.append(f"formal reviewed page must use semantic name: {rel(root, page)}")

    details = {
        "registeredDomains": sorted(expected),
        "reviewedDomains": sorted(reviewed_domains),
        "rawDomains": sorted(raw_domains),
    }
    return _validation_check("domain-layout-and-schema", not issues, f"domains={len(expected)}", issues, details)


def _validate_source_trace(root: Path, reviewed: Path) -> dict:
    issues: list[str] = []
    checked_pages = 0
    for page in _reviewed_pages(reviewed, authoritative_only=False):
        text = read_text(page)
        role = _knowledge_role(text)
        if role in {"domain-index", "domain-schema"}:
            continue
        checked_pages += 1
        page_ref = rel(root, page)
        refs = _metadata_list_values(text, "sourceRefs")
        if not refs:
            issues.append(f"{page_ref} missing sourceRefs")
        if "## Source Trace" not in text:
            issues.append(f"{page_ref} missing Source Trace section")
        for source_ref in refs:
            if _is_absolute_or_url(source_ref):
                issues.append(f"{page_ref} sourceRef must be relative local route: {source_ref}")
                continue
            if source_ref.startswith("var/"):
                continue
            target = root / source_ref
            if not target.exists():
                issues.append(f"{page_ref} sourceRef target missing: {source_ref}")
        vault_path = page_ref.replace("\\", "/")
        is_concept = "/concepts/" in vault_path
        authoritative = _is_authoritative_reviewed_page(page)
        if authoritative and not is_concept:
            raw_refs = [item for item in refs if item.startswith("user/knowledge/raw/") and (root / item).exists()]
            if not raw_refs:
                issues.append(f"{page_ref} authoritative page must trace to an existing raw source")
            runtime_extracted_refs = [
                item for item in refs
                if item.replace("\\", "/").startswith("var/rag/") and "/extracted/" in item.replace("\\", "/")
            ]
            if runtime_extracted_refs:
                issues.append(
                    f"{page_ref} extracted markdown sourceRefs must be normalized under user/knowledge/raw/<domain>/normalized, not runtime var/rag: {', '.join(runtime_extracted_refs)}"
                )
            if "## Source Overview" not in text:
                issues.append(f"{page_ref} source-level authoritative page missing Source Overview")
            if "## Core Framework" not in text:
                issues.append(f"{page_ref} source-level authoritative page missing Core Framework")
        if authoritative and is_concept:
            reviewed_refs = [item for item in refs if item.startswith("user/knowledge/reviewed/") and (root / item).exists()]
            if not reviewed_refs:
                issues.append(f"{page_ref} concept page must trace to an existing authoritative reviewed page")
        if not authoritative:
            authoritative_page = _frontmatter_value(text, "authoritativePage")
            if not authoritative_page or _is_absolute_or_url(authoritative_page) or not (root / authoritative_page).exists():
                issues.append(f"{page_ref} non-authoritative page must reference existing authoritativePage")

    return _validation_check("source-trace", not issues, f"checkedPages={checked_pages}", issues, {"checkedPages": checked_pages})


def _graph_gate_issues(graph_json: Path, graph_result: dict) -> list[str]:
    issues: list[str] = []
    if graph_result.get("brokenLinkCount"):
        try:
            graph = json.loads(read_text(graph_json))
            broken = graph.get("health", {}).get("brokenLinks", [])
            issues.extend(f"broken link {item.get('link')} referenced by {', '.join(item.get('referencedBy', []))}" for item in broken)
        except Exception:
            issues.append(f"brokenLinkCount={graph_result.get('brokenLinkCount')}")
    if graph_result.get("orphanCount"):
        try:
            graph = json.loads(read_text(graph_json))
            issues.extend(f"orphan node {item}" for item in graph.get("health", {}).get("orphanNodes", []))
        except Exception:
            issues.append(f"orphanCount={graph_result.get('orphanCount')}")
    return issues


def _validate_archive_references(root: Path, reviewed: Path, candidate: Path) -> dict:
    issues: list[str] = []
    active_candidates = _candidate_inventory(root, candidate, reviewed)
    if active_candidates:
        issues.append("candidate root must not contain active candidate corpora: " + ", ".join(item["runId"] for item in active_candidates))

    archive_root = candidate / "_archive"
    if not archive_root.exists():
        issues.append(f"candidate archive missing: {rel(root, archive_root)}")
    archive_index = archive_root / "ARCHIVE.md"
    if not archive_index.exists():
        issues.append(f"candidate archive index missing: {rel(root, archive_index)}")
    archived = _archived_candidate_inventory(root, candidate)
    audit_records = _candidate_audit_inventory(root, candidate)
    if not archived and not audit_records:
        issues.append("candidate archive inventory and post-promotion audit inventory are both empty")
    for item in archived:
        path = root / item["path"]
        wiki = root / item["wiki"]
        if not path.exists():
            issues.append(f"archived candidate path missing: {item['path']}")
        if not wiki.exists():
            issues.append(f"archived candidate wiki missing: {item['wiki']}")
        if "/candidate/_archive/by-source/" not in item["path"].replace("\\", "/"):
            issues.append(f"archived candidate must use source-centered by-source path: {item['path']}")
    for item in audit_records:
        path = root / item["path"]
        if not path.exists():
            issues.append(f"candidate audit record missing: {item['path']}")
        backup = item.get("backupPath")
        if backup and not (root / backup).exists():
            issues.append(f"candidate audit backup path missing: {backup}")

    home = reviewed.parent / "Home.md"
    if home.exists():
        archive_refs = sorted(set(re.findall(r"user/knowledge/candidate/_archive/[A-Za-z0-9_./-]+", read_text(home))))
        for archive_ref in archive_refs:
            if not (root / archive_ref).exists():
                issues.append(f"Home archive reference missing: {archive_ref}")

    reviewed_archive = reviewed / "_archive"
    reviewed_archive_pages = sorted(reviewed_archive.rglob("*.md")) if reviewed_archive.exists() else []
    for page in reviewed_archive_pages:
        text = read_text(page)
        page_ref = rel(root, page)
        if _is_authoritative_reviewed_page(page):
            issues.append(f"reviewed archive page must not be authoritative: {page_ref}")
        status = (_frontmatter_value(text, "status") or "").lower()
        if status not in {"archived", "superseded", "deprecated"}:
            issues.append(f"reviewed archive page must have archived/superseded/deprecated status: {page_ref}")
        authoritative_page = _frontmatter_value(text, "authoritativePage")
        if authoritative_page and not (root / authoritative_page).exists():
            issues.append(f"reviewed archive authoritativePage target missing: {authoritative_page}")

    for page in _reviewed_pages(reviewed, authoritative_only=False):
        refs = _metadata_list_values(read_text(page), "sourceRefs")
        for source_ref in refs:
            if "user/knowledge/candidate/_archive/" in source_ref and not (root / source_ref).exists():
                issues.append(f"{rel(root, page)} archived sourceRef target missing: {source_ref}")
            if "user/knowledge/candidate/_audit/" in source_ref and not (root / source_ref).exists():
                issues.append(f"{rel(root, page)} audit sourceRef target missing: {source_ref}")

    details = {
        "activeCandidateCount": len(active_candidates),
        "archivedCandidateCount": len(archived),
        "candidateAuditRecordCount": len(audit_records),
        "reviewedArchivePageCount": len(reviewed_archive_pages),
    }
    return _validation_check(
        "archive-references",
        not issues,
        f"archivedCandidates={len(archived)}, candidateAuditRecords={len(audit_records)}, reviewedArchivePages={len(reviewed_archive_pages)}",
        issues,
        details,
    )


def _validate_git_ignore_boundary(root: Path, vault: Path, registry: Path) -> dict:
    issues: list[str] = []
    checked_paths = [
        vault / "Home.md",
        vault / "reviewed",
        vault / "candidate",
        vault / "raw",
        vault / ".obsidian",
        registry,
    ]
    ignore_details = []
    for path in checked_paths:
        if not path.exists():
            issues.append(f"git boundary target missing: {rel(root, path)}")
            continue
        ignored = _git_check_ignored(root, path)
        ignore_details.append(ignored)
        if not ignored["ignored"]:
            issues.append(f"path must be ignored by Git: {rel(root, path)}")

    tracked_knowledge = _git_ls_files(root, "user/knowledge")
    unexpected_tracked_knowledge = [item for item in tracked_knowledge if item != "user/knowledge/README.md"]
    if unexpected_tracked_knowledge:
        issues.append("unexpected tracked user knowledge files: " + ", ".join(unexpected_tracked_knowledge))
    tracked_registry = [item for item in _git_ls_files(root, "user/registry") if item.endswith(".local.json")]
    if tracked_registry:
        issues.append("local registry files must not be tracked: " + ", ".join(tracked_registry))

    details = {
        "ignoreChecks": ignore_details,
        "trackedKnowledge": tracked_knowledge,
        "trackedRegistry": tracked_registry,
    }
    return _validation_check("git-ignore-boundary", not issues, f"checked={len(checked_paths)}", issues, details)


def _validate_obsidian_plugin_boundary(root: Path, vault: Path, reviewed: Path) -> dict:
    issues: list[str] = []
    obsidian = vault / ".obsidian"
    plugins = obsidian / "plugins"
    karpathy = plugins / "karpathywiki"
    if not obsidian.exists():
        issues.append(f"Obsidian config missing: {rel(root, obsidian)}")
    if not plugins.exists():
        issues.append(f"Obsidian plugins dir missing: {rel(root, plugins)}")
    enabled_plugins = []
    community = obsidian / "community-plugins.json"
    if community.exists():
        try:
            enabled_plugins = json.loads(read_text(community))
        except json.JSONDecodeError as exc:
            issues.append(f"community-plugins.json invalid: {exc}")
    else:
        issues.append(f"community plugins config missing: {rel(root, community)}")
    if "karpathywiki" not in enabled_plugins:
        issues.append("karpathywiki plugin must be explicitly listed in community-plugins.json for boundary validation")
    if not karpathy.exists():
        issues.append(f"karpathywiki plugin dir missing: {rel(root, karpathy)}")
    else:
        manifest = karpathy / "manifest.json"
        if not manifest.exists():
            issues.append(f"karpathywiki manifest missing: {rel(root, manifest)}")
        else:
            try:
                manifest_data = json.loads(read_text(manifest))
                if manifest_data.get("id") != "karpathywiki":
                    issues.append("karpathywiki manifest id mismatch")
            except json.JSONDecodeError as exc:
                issues.append(f"karpathywiki manifest invalid: {exc}")
        data_file = karpathy / "data.json"
        if data_file.exists():
            try:
                data = json.loads(read_text(data_file))
                issues.extend(_sensitive_plugin_config_issues(data, "karpathywiki.data"))
            except json.JSONDecodeError as exc:
                issues.append(f"karpathywiki data.json invalid: {exc}")
        ignored = _git_check_ignored(root, karpathy)
        if not ignored["ignored"]:
            issues.append(f"karpathywiki plugin dir must be ignored by Git: {rel(root, karpathy)}")

    plugin_ref_pages = []
    for page in _reviewed_pages(reviewed, authoritative_only=False):
        refs = _metadata_list_values(read_text(page), "sourceRefs")
        if any(".obsidian/" in item or "karpathywiki" in item for item in refs):
            plugin_ref_pages.append(rel(root, page))
    if plugin_ref_pages:
        issues.append("reviewed sourceRefs must not point to Obsidian plugin runtime: " + ", ".join(plugin_ref_pages))

    graph_json = obsidian / "graph.json"
    graph_search = ""
    if graph_json.exists():
        try:
            graph_search = str(json.loads(read_text(graph_json)).get("search") or "")
        except json.JSONDecodeError as exc:
            issues.append(f"graph.json invalid: {exc}")
    else:
        issues.append(f"Obsidian graph config missing: {rel(root, graph_json)}")
    for token in ["-path:candidate", "-path:raw"]:
        if token not in graph_search.split():
            issues.append(f"Obsidian graph search must exclude {token}")

    details = {
        "enabledPlugins": enabled_plugins,
        "karpathywiki": rel(root, karpathy),
        "graphSearch": graph_search,
    }
    return _validation_check("obsidian-plugin-boundary", not issues, f"enabledPlugins={len(enabled_plugins)}", issues, details)


def _validate_llm_wiki_absorbed_mechanisms(root: Path, vault: Path, reviewed: Path, domains: list[dict]) -> dict:
    issues: list[str] = []
    domain_details = []
    repair_order = [
        "structure-pollution",
        "aliases",
        "duplicate-merge",
        "dead-links",
        "orphans",
        "empty-pages",
        "retag",
    ]
    for domain in domains:
        domain_id = domain.get("domainId") or "unknown"
        schema_ref = domain.get("schema")
        if not schema_ref:
            issues.append(f"domain {domain_id} schema missing in registry")
            continue
        schema = root / schema_ref
        if not schema.exists():
            issues.append(f"domain {domain_id} schema target missing: {schema_ref}")
            continue
        schema_text = read_text(schema)
        required_sections = [
            "Controlled Tag Vocabulary",
            "Alias Rules",
            "Source Gate Rules",
        ]
        for section in required_sections:
            if not _section_by_heading(schema_text, section):
                issues.append(f"domain {domain_id} schema missing section: {section}")
        allowed_tags = _controlled_tag_vocabulary(schema_text)
        if not allowed_tags:
            issues.append(f"domain {domain_id} controlled tag vocabulary is empty")
        domain_root = root / (domain.get("reviewed") or "")
        pages = [page for page in _reviewed_pages(domain_root, authoritative_only=False)] if domain_root.exists() else []
        tag_violations = []
        missing_tags = []
        concept_alias_missing = []
        for page in pages:
            text = read_text(page)
            role = _knowledge_role(text)
            tags = _reviewed_tags(text)
            if role not in {"domain-index", "domain-schema"} and _is_authoritative_reviewed_text(text) and not tags:
                missing_tags.append(rel(root, page))
            for tag in _reviewed_tags(text):
                if allowed_tags and tag not in allowed_tags:
                    tag_violations.append(f"{rel(root, page)} uses tag outside vocabulary: {tag}")
            if "/concepts/" in rel(root, page).replace("\\", "/") and not _reviewed_aliases(text):
                concept_alias_missing.append(rel(root, page))
        issues.extend(tag_violations)
        if missing_tags:
            issues.append("authoritative pages missing controlled tags: " + ", ".join(missing_tags))
        if concept_alias_missing:
            issues.append("concept pages missing aliases: " + ", ".join(concept_alias_missing))
        schema_contexts = [_schema_context_for_domain(root, domain, task) for task in SCHEMA_CONTEXT_TASK_SECTIONS]
        for context in schema_contexts:
            issues.extend(context.get("issues") or [])
        domain_details.append({
            "domainId": domain_id,
            "schema": schema_ref,
            "controlledTagCount": len(allowed_tags),
            "checkedReviewedPages": len(pages),
            "tagViolationCount": len(tag_violations),
            "missingTagCount": len(missing_tags),
            "conceptAliasMissingCount": len(concept_alias_missing),
            "schemaContextTasks": [item["task"] for item in schema_contexts],
        })

    details = {
        "domains": domain_details,
        "repairPlanOrder": repair_order,
        "sourceGate": "raw-to-candidate ingest blocks empty, frontmatter-only, incompatible, and duplicate body hash sources",
        "graphRetrieval": "query-reviewed scans authoritative reviewed graph only and applies lexical plus graph PPR expansion",
        "autoMaintenanceBoundary": "no watcher writes reviewed Knowledge; only dry-run, candidate-only, or explicit approval commands may mutate",
    }
    return _validation_check(
        "llm-wiki-mechanism-absorption",
        not issues,
        f"domains={len(domains)}, repairOrder={len(repair_order)}",
        issues,
        details,
    )


def _read_registry_domains(root: Path, registry: Path) -> list[dict]:
    if not registry.exists():
        return []
    try:
        data = json.loads(read_text(registry))
    except json.JSONDecodeError:
        return []
    sources = data.get("knowledgeSources") or []
    if not sources:
        return []
    return list(sources[0].get("domains") or [])


def _schema_context_for_domain(root: Path, domain: dict, task: str) -> dict:
    domain_id = domain.get("domainId") or "unknown"
    schema_ref = domain.get("schema") or ""
    schema = root / schema_ref if schema_ref else root / "__missing_schema__"
    issues = []
    if not schema_ref:
        issues.append(f"domain {domain_id} schema missing in registry")
        return {"domainId": domain_id, "task": task, "schema": schema_ref, "sections": [], "contextMarkdown": "", "issues": issues}
    if not schema.exists():
        issues.append(f"domain {domain_id} schema target missing: {schema_ref}")
        return {"domainId": domain_id, "task": task, "schema": schema_ref, "sections": [], "contextMarkdown": "", "issues": issues}

    schema_text = read_text(schema)
    all_sections = _schema_markdown_sections(schema_text)
    if task == "all":
        required = list(all_sections)
    else:
        required = SCHEMA_CONTEXT_TASK_SECTIONS.get(task, SCHEMA_CONTEXT_TASK_SECTIONS["validation"])
    selected = []
    context_lines = [f"# Schema Context: {domain_id} / {task}", ""]
    for heading in required:
        body = all_sections.get(heading, "").strip()
        if not body:
            issues.append(f"domain {domain_id} schema context missing section for task {task}: {heading}")
            continue
        selected.append({
            "heading": heading,
            "chars": len(body),
            "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        })
        context_lines.extend([f"## {heading}", "", body, ""])
    return {
        "domainId": domain_id,
        "task": task,
        "schema": schema_ref,
        "selectedSectionCount": len(selected),
        "sections": selected,
        "contextMarkdown": "\n".join(context_lines).strip() + "\n",
        "issues": issues,
    }


def _schema_markdown_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[heading] = text[start:end].strip()
    return sections


def _validate_schema_context_mechanism(root: Path, domains: list[dict]) -> dict:
    issues = []
    task_details = []
    for domain in domains:
        for task in SCHEMA_CONTEXT_TASK_SECTIONS:
            context = _schema_context_for_domain(root, domain, task)
            issues.extend(context.get("issues") or [])
            task_details.append({
                "domainId": context["domainId"],
                "task": task,
                "selectedSectionCount": context.get("selectedSectionCount", 0),
            })
    return _validation_check(
        "schema-context-task-sections",
        not issues and bool(task_details),
        f"tasks={len(task_details)}",
        issues or ([] if task_details else ["no schema context tasks were produced"]),
        {"tasks": task_details, "taskSectionMap": SCHEMA_CONTEXT_TASK_SECTIONS},
    )


def _validate_source_gate_fixture(root: Path) -> dict:
    seen: dict[str, str] = {}
    empty = _candidate_source_gate(root / "empty.md", "", seen)
    frontmatter_only = _candidate_source_gate(root / "frontmatter-only.md", "---\ntitle: Only\n---\n", seen)
    accepted = _candidate_source_gate(root / "accepted.md", "# Accepted\n\nReusable body text for source gate fixture.\n", seen)
    duplicate = _candidate_source_gate(root / "duplicate.md", "# Accepted\n\nReusable body text for source gate fixture.\n", seen)
    expected = {
        "empty-file": empty.get("reason"),
        "frontmatter-only": frontmatter_only.get("reason"),
        "accepted": accepted.get("state"),
        "duplicate-body-hash": duplicate.get("reason"),
    }
    issues = []
    if expected["empty-file"] != "empty-file":
        issues.append(f"empty fixture expected empty-file, got {expected['empty-file']}")
    if expected["frontmatter-only"] != "frontmatter-only":
        issues.append(f"frontmatter fixture expected frontmatter-only, got {expected['frontmatter-only']}")
    if expected["accepted"] != "accepted":
        issues.append(f"accepted fixture expected accepted, got {expected['accepted']}")
    if expected["duplicate-body-hash"] != "duplicate-body-hash":
        issues.append(f"duplicate fixture expected duplicate-body-hash, got {expected['duplicate-body-hash']}")
    return _validation_check(
        "source-gate-fixture",
        not issues,
        "empty/frontmatter-only/duplicate accepted fixture checked",
        issues,
        {"fixtureResults": [empty, frontmatter_only, accepted, duplicate]},
    )


def _validate_extraction_granularity_fixture(root: Path) -> dict:
    fixture_dir = root / "var" / "rag" / "reviewed-knowledge" / "mechanism-fixtures"
    fixture = fixture_dir / "granularity-source.md"
    body = "\n\n".join(
        f"## Section {index}\n\nExternalized memory, skill libraries, protocols, and harness engineering need source-traceable governance and validation evidence."
        for index in range(1, 80)
    )
    write_text(fixture, "# Granularity Fixture\n\n" + body + "\n")
    run_ids = {
        "fine": "llm-wiki-mechanism-fine",
        "minimal": "llm-wiki-mechanism-minimal",
    }
    details = {}
    issues = []
    try:
        for granularity, run_id in run_ids.items():
            _cleanup_mechanism_fixture_run(root, run_id)
            result = _quiet_call(_run_candidate_ingest, SimpleNamespace(
                root=str(root),
                inputs=[str(fixture)],
                run_id=run_id,
                raw_domain="mechanism-fixtures",
                copy_raw=False,
                max_chunk_chars=4000,
                extraction_granularity=granularity,
                entity_cap=None,
                concept_cap=None,
                batch_strategy="balanced-batches",
                tag_vocabulary_mode="custom",
                allowed_tags=["mechanism-fixture"],
            ))
            manifest = json.loads(read_text(root / "var" / "rag" / run_id / "extracted" / "metadata-manifest.json"))
            chunk_count = len([line for line in read_text(root / "var" / "rag" / run_id / "extracted" / "chunks.jsonl").splitlines() if line.strip()])
            details[granularity] = {
                "state": result.get("state"),
                "effectiveMaxChunkChars": manifest.get("extraction", {}).get("effectiveMaxChunkChars"),
                "entityCap": manifest.get("extraction", {}).get("entityCap"),
                "conceptCap": manifest.get("extraction", {}).get("conceptCap"),
                "batchStrategy": manifest.get("extraction", {}).get("batchStrategy"),
                "chunkCount": chunk_count,
                "sourceRecordCount": len(manifest.get("sources", [])),
            }
        if details["fine"]["effectiveMaxChunkChars"] >= details["minimal"]["effectiveMaxChunkChars"]:
            issues.append("fine granularity should use smaller effective chunks than minimal")
        if details["fine"]["chunkCount"] <= details["minimal"]["chunkCount"]:
            issues.append("fine granularity should produce more chunks than minimal on the same fixture")
        if details["fine"]["entityCap"] <= details["minimal"]["entityCap"]:
            issues.append("fine granularity should allow a larger entity cap than minimal")
    finally:
        for run_id in run_ids.values():
            _cleanup_mechanism_fixture_run(root, run_id)
    return _validation_check(
        "extraction-granularity-fixture",
        not issues,
        f"fineChunks={details.get('fine', {}).get('chunkCount')}, minimalChunks={details.get('minimal', {}).get('chunkCount')}",
        issues,
        {"granularityRuns": details},
    )


def _cleanup_mechanism_fixture_run(root: Path, run_id: str) -> None:
    _remove_path_under(root, root / "user" / "knowledge" / "candidate" / run_id, [root / "user" / "knowledge" / "candidate"])
    _remove_path_under(root, root / "var" / "rag" / run_id, [root / "var" / "rag"])
    _remove_path_under(root, root / "var" / "logs" / f"{run_id}.json", [root / "var" / "logs"])


def _validate_tag_vocabulary_requirement(root: Path, reviewed: Path, domains: list[dict]) -> dict:
    issues = []
    checked = 0
    for domain in domains:
        schema_ref = domain.get("schema")
        domain_root = root / (domain.get("reviewed") or "")
        if not schema_ref or not domain_root.exists():
            continue
        allowed_tags = _controlled_tag_vocabulary(read_text(root / schema_ref)) if (root / schema_ref).exists() else set()
        for page in _reviewed_pages(domain_root, authoritative_only=False):
            text = read_text(page)
            role = _knowledge_role(text)
            if role in {"domain-index", "domain-schema"} or not _is_authoritative_reviewed_text(text):
                continue
            checked += 1
            tags = _reviewed_tags(text)
            if not tags:
                issues.append(f"{rel(root, page)} missing tags")
                continue
            for tag in tags:
                if allowed_tags and tag not in allowed_tags:
                    issues.append(f"{rel(root, page)} tag outside vocabulary: {tag}")
    return _validation_check(
        "tag-vocabulary-required-on-authoritative-pages",
        not issues,
        f"checkedAuthoritativePages={checked}",
        issues,
        {"checkedAuthoritativePages": checked},
    )


def _validate_graph_retrieval_mechanism(root: Path, vault: Path, reviewed: Path, graph_json: Path, graph_result: dict) -> dict:
    result = _query_reviewed(root, vault, reviewed, graph_json, "BindingConstraintThesis", 20)
    matches = result.get("matches", [])
    ppr_matches = [item for item in matches if "graph-ppr" in item.get("reason", [])]
    non_reviewed = [item.get("page") for item in matches if not item.get("vaultPath", "").startswith("reviewed/")]
    non_authoritative = [
        item.get("page") for item in matches
        if item.get("page") and not _is_authoritative_reviewed_page(root / item["page"])
    ]
    issues = []
    if graph_result.get("state") != "passed":
        issues.append(f"reviewed graph build state is {graph_result.get('state')}")
    if not matches:
        issues.append("reviewed query returned no matches")
    if not ppr_matches:
        issues.append("reviewed query did not return any graph-ppr expansion match")
    if non_reviewed:
        issues.append("query returned non-reviewed pages: " + ", ".join(non_reviewed))
    if non_authoritative:
        issues.append("query returned non-authoritative pages: " + ", ".join(non_authoritative))
    return _validation_check(
        "reviewed-graph-ppr-retrieval",
        not issues,
        f"matches={len(matches)}, graphPprMatches={len(ppr_matches)}",
        issues,
        {
            "query": result.get("question"),
            "matchCount": len(matches),
            "graphPprMatchCount": len(ppr_matches),
            "graphJson": rel(root, graph_json),
        },
    )


def _validate_auto_maintenance_boundary(root: Path, vault: Path) -> dict:
    issues = []
    details = {"pluginConfig": "missing", "dangerousTrueSettings": []}
    data_file = vault / ".obsidian" / "plugins" / "karpathywiki" / "data.json"
    if data_file.exists():
        details["pluginConfig"] = rel(root, data_file)
        try:
            data = json.loads(read_text(data_file))
        except json.JSONDecodeError as exc:
            issues.append(f"plugin data.json invalid: {exc}")
            data = {}
        dangerous = []
        _collect_true_auto_settings(data, "", dangerous)
        details["dangerousTrueSettings"] = dangerous
        if dangerous:
            issues.append("plugin auto maintenance settings must not be enabled for reviewed writes: " + ", ".join(dangerous))
    graph_json = vault / ".obsidian" / "graph.json"
    if graph_json.exists():
        try:
            search = str(json.loads(read_text(graph_json)).get("search") or "")
        except json.JSONDecodeError as exc:
            search = ""
            issues.append(f"graph.json invalid: {exc}")
        details["graphSearch"] = search
        for token in ["-path:candidate", "-path:raw", "-path:.obsidian"]:
            if token not in search.split():
                issues.append(f"Obsidian graph search must exclude {token}")
    return _validation_check(
        "auto-maintenance-boundary",
        not issues,
        "no background reviewed writes; only dry-run/candidate-only/explicit approval commands",
        issues,
        details,
    )


def _collect_true_auto_settings(value, prefix: str, output: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            _collect_true_auto_settings(child, next_prefix, output)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _collect_true_auto_settings(child, f"{prefix}[{index}]", output)
        return
    lowered = prefix.lower()
    if value is True and any(term in lowered for term in ["watch", "auto", "smartfix", "smart_fix", "write"]):
        output.append(prefix)


def _format_schema_context_report(result: dict) -> str:
    lines = [
        f"# Reviewed Domain Schema Context - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Domain: `{result['domain']}`",
        f"- Task: `{result['task']}`",
        f"- Boundary: `{result['boundary']}`",
        "",
    ]
    for context in result["contexts"]:
        lines.extend([
            f"## {context['domainId']} / {context['task']}",
            "",
            f"- Schema: `{context['schema']}`",
            f"- Selected sections: {context.get('selectedSectionCount', 0)}",
            "",
            "```markdown",
            context.get("contextMarkdown", "").rstrip(),
            "```",
            "",
        ])
    if result["issues"]:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {item}" for item in result["issues"])
    return "\n".join(lines)


def _format_llm_wiki_mechanism_validation_report(result: dict) -> str:
    lines = [
        f"# LLM Wiki Mechanism Validation - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Checks: {result['passedCheckCount']} / {result['checkCount']} passed",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Check Summary",
        "",
        "| Check | State | Summary | Issues |",
        "|---|---|---|---|",
    ]
    for check in result["checks"]:
        issues = "<br>".join(escape(str(item)) for item in check.get("issues", [])) or "none"
        lines.append(f"| `{check['name']}` | `{check['state']}` | {check.get('summary')} | {issues} |")
    lines.extend(["", "## Blocking Issues", ""])
    lines.extend(f"- {item}" for item in result["blockingIssues"] or ["none"])
    lines.extend([
        "",
        "## Boundary",
        "",
        "- This validation writes runtime reports and temporary fixtures only.",
        "- Temporary candidate fixture corpora are removed after the granularity check.",
        "- Reviewed Knowledge mutation still requires human review or explicit user approval.",
        "",
    ])
    return "\n".join(lines)


def _format_knowledge_validation_report(result: dict) -> str:
    lines = [
        f"# Knowledge One-Click Validation Gate - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Vault: `{result['vault']}`",
        f"- Reviewed: `{result['reviewed']}`",
        f"- Candidate: `{result['candidate']}`",
        f"- Raw: `{result['raw']}`",
        f"- Registry: `{result['registry']}`",
        f"- Checks: {result['passedCheckCount']} / {result['checkCount']} passed",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## Check Summary",
        "",
        "| Check | State | Summary | Issues |",
        "|---|---|---|---|",
    ]
    for check in result["checks"]:
        issues = "<br>".join(escape(str(item)) for item in check.get("issues", [])) or "无"
        lines.append(f"| `{check['name']}` | `{check['state']}` | {check['summary']} | {issues} |")
    lines.extend([
        "",
        "## Blocking Issues",
        "",
    ])
    if result["blockingIssues"]:
        lines.extend(f"- {item}" for item in result["blockingIssues"])
    else:
        lines.append("- 无")
    lines.extend([
        "",
        "## Gate Boundary",
        "",
        "- 本门禁只写入 runtime report 和 status JSON，不执行 reviewed promotion。",
        "- `raw/`、`candidate/`、Obsidian `.obsidian/` 和 local registry 必须保持 local-only / Git ignored。",
        "- Query、graph、chunks 和 eval reports 是可重建运行态产物，不是事实源。",
        "- Obsidian LLM Wiki plugin 可以作为人类阅读和 candidate generation 工具，但不得成为 reviewed Knowledge 的直接写入源。",
        "",
        "## JSON",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    return "\n".join(lines)


def _format_candidate_cleanup_plan_report(result: dict) -> str:
    lines = [
        f"# Candidate Post-Promotion Cleanup Plan - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Scope: `{result['scope']}`",
        f"- Dry run: `{str(result['dryRun']).lower()}`",
        f"- Candidate root: `{result['candidate']}`",
        f"- Active candidates: {result['activeCandidateCount']}",
        f"- Archived candidates: {result['archivedCandidateCount']}",
        f"- Full corpus candidates: {result['fullCorpusCandidateCount']}",
        f"- Lightweight audit records: {result['lightweightAuditRecordCount']}",
        f"- Candidate markdown pages: {result['candidateMarkdownCount']}",
        f"- Candidate wikilinks: {result['candidateWikiLinkCount']}",
        f"- Reviewed references: {result['reviewedReferenceCount']}",
        f"- Home references: {result['homeReferenceCount']}",
        f"- Registry references: {result['registryReferenceCount']}",
        f"- Recommended cleanup actions: {result['recommendedCleanupActionCount']}",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Policy",
        "",
        "1. Active review candidate 可以暂时留在 `candidate/`，但不得作为 reviewed Knowledge 事实源。",
        "2. Candidate 被晋升、拒绝或归档后，full corpus 默认应移出 Obsidian 默认图谱或删除，只保留轻量审计记录。",
        "3. 轻量审计记录只保存 run id、source fingerprint、hash、review decision、target reviewed page 和必要 provenance；不保留完整 candidate wiki 正文。",
        "4. 如果 reviewed source trace、registry 或 Home 仍引用 full corpus 路径，必须先改写到轻量审计记录，再执行实际删除或移出 vault。",
        "5. 实际删除或移动必须先有本 dry-run report、用户明确批准和 `validate-knowledge-vault` 回归通过。",
        "",
        "## Inventory",
        "",
        "| Corpus | Kind | Pages | Wikilinks | Reviewed refs | Home refs | Registry refs | Recommended action |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in result["entries"]:
        references = item["references"]
        lines.append(
            f"| `{item['path']}` | `{item['kind']}` | {item['markdownCount']} | {item['wikilinkCount']} | "
            f"{len(references['reviewed'])} | {len(references['home'])} | {len(references['registry'])} | "
            f"`{item['recommendedAction']}` |"
        )
    if not result["entries"]:
        lines.append("| _No candidate corpus found._ |  |  |  |  |  |  |  |")
    lines.extend([
        "",
        "## Recommended Cleanup Actions",
        "",
    ])
    if result["recommendedCleanupActions"]:
        for item in result["recommendedCleanupActions"]:
            lines.append(f"- `{item['path']}` -> `{item['action']}`: {item['reason']}")
    else:
        lines.append("- No full candidate corpus cleanup action recommended.")
    lines.extend([
        "",
        "## Preconditions For Destructive Cleanup",
        "",
    ])
    lines.extend(f"- {item}" for item in result["preconditionsForDestructiveCleanup"])
    lines.extend([
        "",
        "## Reference Details",
        "",
    ])
    for item in result["entries"]:
        refs = item["references"]
        if not refs["reviewed"] and not refs["home"] and not refs["registry"]:
            continue
        lines.extend([
            f"### {item['corpusId']}",
            "",
            f"- Reviewed: {', '.join(f'`{ref}`' for ref in refs['reviewed']) or '`none`'}",
            f"- Home: {', '.join(f'`{ref}`' for ref in refs['home']) or '`none`'}",
            f"- Registry: {', '.join(f'`{ref}`' for ref in refs['registry']) or '`none`'}",
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


def _format_candidate_cleanup_apply_report(result: dict) -> str:
    lines = [
        f"# Candidate Post-Promotion Cleanup Apply - {today()}",
        "",
        f"- State: `{result['state']}`",
        f"- Scope: `{result['scope']}`",
        f"- Dry run: `{str(result['dryRun']).lower()}`",
        f"- Candidate root: `{result['candidate']}`",
        f"- Backup root: `{result['backupRoot']}`",
        f"- Reviewer: `{result['reviewer']}`",
        f"- Approval note: `{result['approvalNote']}`",
        f"- Moved corpus: {result['movedCorpusCount']}",
        f"- Audit records: {result['auditRecordCount']}",
        f"- Remaining full corpus candidates: {result['remainingFullCorpusCandidateCount']}",
        f"- Remaining cleanup actions: {result['recommendedCleanupActionCount']}",
        f"- Rewritten files: {result['rewrittenFileCount']}",
        f"- Graph filter: `{result['graphFilter'].get('search', '')}`",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Moves",
        "",
    ]
    if result["moves"]:
        for item in result["moves"]:
            lines.append(
                f"- `{item.get('oldPath')}` -> `{item.get('newPath', '')}` "
                f"({item.get('state')}; audit `{item.get('auditPath', '')}`)"
            )
    else:
        lines.append("- No candidate full corpus needed moving.")
    lines.extend([
        "",
        "## Rewrites",
        "",
    ])
    if result["rewrites"]:
        for item in result["rewrites"]:
            lines.append(f"- `{item['path']}`: {item['replacementCount']} reference rewrite(s)")
    else:
        lines.append("- No reference rewrites were needed.")
    lines.extend([
        "",
        "## JSON",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    return "\n".join(lines)


def _candidate_audit_path(root: Path, candidate_dir: Path, corpus_id: str) -> Path:
    digest = hashlib.sha256(corpus_id.encode("utf-8")).hexdigest()[:10]
    base = safe_run_id(corpus_id.replace("/", "-"))[:80]
    return candidate_dir / "_audit" / "post-promotion" / f"{base}-{digest}.md"


def _format_candidate_audit_record(record: dict) -> str:
    references = record.get("referencesBeforeCleanup", {})
    lines = [
        "---",
        f"documentName: {record['auditPath']}",
        "version: v1.0.0-candidate-post-promotion-audit",
        f"updatedAt: {record['cleanedAt']}",
        "status: active",
        "knowledgeRole: candidate-audit-record",
        "authoritative: false",
        "purpose: 记录晋升后 candidate full corpus 清理的轻量审计信息，不保存候选正文。",
        "scope:",
        "  - candidate-governance",
        "  - user-private",
        "prerequisites:",
        "  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md",
        "relatedDocuments:",
        "  - harness/architecture/HarnessEngineering.md",
        "  - harness/rag/RAGIndex.md",
        "  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md",
        "outputTo:",
        f"  - {record['auditPath']}",
        "owner: user",
        "reviewAfter: source-updated-or-2026-12-31",
        "supersededBy:",
        "dependsOn:",
        f"  - {record['backupPath']}",
        "review:",
        f"  reviewedBy: {record['reviewer']}",
        f"  reviewedAt: {record['cleanedAt']}",
        "  decision: approved-candidate-full-corpus-cleanup",
        "---",
        f"# Candidate Cleanup Audit - {record['corpusId']}",
        "",
        "## Summary",
        "",
        f"- Corpus ID: `{record['corpusId']}`",
        f"- Source path before cleanup: `{record['sourcePath']}`",
        f"- Backup path outside vault graph: `{record['backupPath']}`",
        f"- Corpus hash: `{record['corpusHashSha256']}`",
        f"- Markdown pages: {record['markdownCount']}",
        f"- Wikilinks: {record['wikilinkCount']}",
        f"- Cleanup action: `{record['cleanupAction']}`",
        f"- Approval note: `{record['approvalNote']}`",
        "",
        "## References Before Cleanup",
        "",
    ]
    for key in ["reviewed", "home", "registry"]:
        values = references.get(key) or []
        lines.append(f"- {key}: {', '.join(f'`{item}`' for item in values) if values else '`none`'}")
    lines.extend([
        "",
        "## Boundary",
        "",
        "- This file is a lightweight audit record only.",
        "- It must not be used as authoritative reviewed Knowledge.",
        "- It intentionally does not preserve full candidate page bodies.",
        "",
    ])
    return "\n".join(lines)


def _candidate_corpus_hash(corpus_root: Path, markdown_files: list[Path]) -> str:
    digest = hashlib.sha256()
    for page in markdown_files:
        digest.update(page.relative_to(corpus_root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(page.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _rewrite_candidate_references_to_audit(
    root: Path,
    vault: Path,
    reviewed: Path,
    registry: Path,
    old_root: str,
    audit_ref: str,
) -> list[dict]:
    files = [page for page in _reviewed_pages(reviewed, authoritative_only=False)]
    home = vault / "Home.md"
    if home.exists():
        files.append(home)
    if registry.exists():
        files.append(registry)
    rewrites = []
    for path in sorted({p.resolve(): p for p in files}.values(), key=lambda p: rel(root, p)):
        text = read_text(path)
        new_text, count = _rewrite_candidate_text_to_audit(text, old_root, audit_ref)
        if new_text == text:
            continue
        write_text(path, new_text)
        rewrites.append({"path": rel(root, path), "replacementCount": count})
    return rewrites


def _rewrite_candidate_text_to_audit(text: str, old_root: str, audit_ref: str) -> tuple[str, int]:
    old_root = old_root.replace("\\", "/").rstrip("/")
    path_pattern = re.compile(re.escape(old_root) + r"(?:/[A-Za-z0-9._~%#@+=:-]+)*")
    count = 0
    lines = []
    for line in text.splitlines():
        normalized = line.replace("\\", "/")
        if old_root not in normalized:
            lines.append(line)
            continue
        list_match = re.match(r"^(\s*-\s+).*$", line)
        if list_match:
            replacement = f"{list_match.group(1)}{audit_ref}"
        else:
            replacement = path_pattern.sub(audit_ref, line)
        count += 1
        lines.append(replacement)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), count


def _candidate_audit_inventory(root: Path, candidate_dir: Path) -> list[dict]:
    audit_root = candidate_dir / "_audit" / "post-promotion"
    if not audit_root.exists():
        return []
    records = []
    for page in sorted(audit_root.glob("*.md"), key=lambda p: p.name.lower()):
        if page.name.upper() == "INDEX.MD":
            continue
        text = read_text(page)
        corpus_id = _heading_title(text) or page.stem
        if corpus_id.startswith("Candidate Cleanup Audit - "):
            corpus_id = corpus_id.removeprefix("Candidate Cleanup Audit - ")
        records.append({
            "runId": corpus_id,
            "path": rel(root, page),
            "wiki": "none",
            "markdownCount": 1,
            "governanceState": "post-promotion-audit",
            "reason": "lightweight audit record retained after full corpus moved out of vault",
            "backupPath": _audit_field(text, "Backup path outside vault graph"),
            "corpusHashSha256": _audit_field(text, "Corpus hash"),
        })
    return records


def _candidate_audit_cleanup_records(
    root: Path,
    vault: Path,
    reviewed: Path,
    candidate_dir: Path,
    registry: Path,
) -> list[dict]:
    records = []
    for item in _candidate_audit_inventory(root, candidate_dir):
        path = (root / item["path"]).resolve()
        references = _candidate_cleanup_references(root, vault, reviewed, registry, path)
        records.append({
            "corpusId": item["runId"],
            "path": item["path"],
            "kind": "lightweight-audit-record",
            "governanceState": item["governanceState"],
            "markdownCount": 1,
            "wikilinkCount": _candidate_wikilink_count([path]) if path.exists() else 0,
            "references": references,
            "recommendedAction": "keep-lightweight-audit-record",
            "reason": item["reason"],
        })
    return records


def _write_candidate_audit_index(root: Path, candidate_dir: Path, audit_records: list[dict]) -> None:
    audit_root = candidate_dir / "_audit" / "post-promotion"
    lines = [
        "---",
        "title: Candidate Post-Promotion Audit Index",
        "type: candidate-audit-index",
        f"last_updated: {today()}",
        "---",
        "# Candidate Post-Promotion Audit Index",
        "",
        "This directory keeps lightweight audit records for candidate full corpus cleanup. It does not keep full candidate page bodies.",
        "",
        "| Corpus | Audit Record | Backup Path | Hash |",
        "|---|---|---|---|",
    ]
    if audit_records:
        for item in audit_records:
            lines.append(
                f"| `{item['runId']}` | `{item['path']}` | "
                f"`{item.get('backupPath') or 'unknown'}` | `{item.get('corpusHashSha256') or 'unknown'}` |"
            )
    else:
        lines.append("| _No post-promotion audit records._ |  |  |  |")
    write_text(audit_root / "INDEX.md", "\n".join(lines) + "\n")


def _audit_field(text: str, label: str) -> str:
    match = re.search(rf"(?m)^-\s+{re.escape(label)}:\s+`([^`]+)`", text)
    return match.group(1) if match else ""


def _heading_title(text: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def _ensure_obsidian_graph_filter(vault: Path) -> dict:
    graph_json = vault / ".obsidian" / "graph.json"
    data = {}
    if graph_json.exists():
        try:
            data = json.loads(read_text(graph_json))
        except json.JSONDecodeError:
            data = {}
    search = str(data.get("search") or "")
    tokens = [token for token in search.split() if token]
    for token in ["-path:candidate", "-path:raw", "-path:.obsidian"]:
        if token not in tokens:
            tokens.append(token)
    data["search"] = " ".join(tokens)
    write_text(graph_json, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return {"path": rel(vault.parent, graph_json), "search": data["search"]}


def _unique_backup_destination(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.name}-{index:03d}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"unable to allocate backup destination: {path}")


def _ensure_path_under(path: Path, parent: Path, label: str) -> None:
    path = path.resolve()
    parent = parent.resolve()
    if path != parent and parent not in path.parents:
        raise ValueError(f"{label} escapes expected parent: {path}")


def _remove_empty_dirs_up_to(root: Path, directory: Path, stop: Path) -> None:
    directory = directory.resolve()
    stop = stop.resolve()
    while directory != stop and stop in directory.parents:
        if not directory.exists() or any(directory.iterdir()):
            return
        directory.rmdir()
        directory = directory.parent


def _format_residual_gap_disposition_report(result: dict) -> str:
    lines = [
        f"# Residual Reviewed Gap Disposition - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Candidate wiki: `{result['candidateWiki']}`",
        f"- Promotion: `{result['promotion']}`",
        f"- Remaining residual gaps: {len(result['remainingResidualGaps'])}",
        f"- 边界（Boundary）: `{result['boundary']}`",
        "",
        "## 处置规则",
        "",
        "- `CandidateKnowledge` 和 `StructuredIngestion` 是 Harness workflow / mechanism concepts。",
        "- 它们不从当前 raw PDF 派生候选中直接晋升为 reviewed Knowledge。",
        "- 处置方式是 dedup 到已有 Harness policy、template 或 Skill，并移除 authoritative reviewed page 中的 unresolved wikilink。",
        "",
        "## Page Actions",
        "",
    ]
    if result["pageActions"]:
        for action in result["pageActions"]:
            lines.extend([
                f"### {action['page']}",
                "",
            ])
            for item in action["replacedLinks"]:
                lines.extend([
                    f"- Link: `[[{item['link']}]]`",
                    f"- Disposition: `{item['disposition']}`",
                    f"- Replacement: {item['replacement']}",
                    "- Targets:",
                ])
                lines.extend(f"  - `{target}`" for target in item["targets"])
                lines.append("")
    else:
        lines.append("- No reviewed page rewrites were needed.")

    lines.extend([
        "",
        "## Candidate Updates",
        "",
    ])
    if result["candidateUpdates"]:
        for item in result["candidateUpdates"]:
            lines.append(f"- `{item['page']}` -> `{item['disposition']}`")
    else:
        lines.append("- No candidate pages updated.")

    lines.extend([
        "",
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

## Concept Detail

- 本概念来自已审核 source reviewed Knowledge，用于把原始材料中的核心主题拆分为可导航、可复用的概念节点。
- 概念页只承载定义、适用边界、相邻关系和 Source Trace；如果需要理解原始材料的完整论证，应回到 source reviewed Knowledge 阅读。
- 回答问题时，本页可以作为入口，但不能替代 source reviewed Knowledge、原始材料或后续 governance review。

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
        f"- Candidate audit record count: {result.get('candidateAuditRecordCount', 0)}",
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
    knowledge_role = _knowledge_role(text)
    authoritative = _is_authoritative_reviewed_text(text)
    return {
        "title": _page_title(text, page.stem),
        "path": rel(root, page),
        "vaultPath": rel(vault, page),
        "vaultStem": rel(vault, page).removesuffix(".md"),
        "scope": scope,
        "status": _frontmatter_value(text, "status") or "unknown",
        "knowledgeRole": knowledge_role,
        "authoritative": authoritative,
        "authoritativePage": _frontmatter_value(text, "authoritativePage") or "",
        "duplicateDisposition": _frontmatter_value(text, "duplicateDisposition") or "",
        "purpose": _frontmatter_value(text, "purpose") or _first_sentence(_strip_frontmatter(text)),
        "reviewedBy": _frontmatter_value(text, "reviewedBy") or _nested_reviewed_by(text) or "unknown",
        "reviewedAt": _frontmatter_value(text, "reviewedAt") or _nested_reviewed_at(text) or "unknown",
        "sourceTrace": "yes" if "## Source Trace" in text else "missing",
    }


def _reviewed_pages(reviewed: Path, authoritative_only: bool = True) -> list[Path]:
    if not reviewed.exists():
        return []
    pages = [
        p for p in sorted(reviewed.rglob("*.md"))
        if p.is_file() and p.name not in VAULT_INDEX_FILES
    ]
    if authoritative_only:
        pages = [p for p in pages if _is_authoritative_reviewed_page(p)]
    return pages


def _is_authoritative_reviewed_page(page: Path) -> bool:
    return _is_authoritative_reviewed_text(read_text(page))


def _is_authoritative_reviewed_text(text: str) -> bool:
    status = (_frontmatter_value(text, "status") or "active").strip().lower()
    if status in {"archived", "superseded", "deprecated"}:
        return False
    authoritative = (_frontmatter_value(text, "authoritative") or "").strip().lower()
    if authoritative in {"false", "no", "0"}:
        return False
    if authoritative in {"true", "yes", "1"}:
        return True
    role = _knowledge_role(text)
    if role in {"validation-evidence", "pipeline-smoke-evidence", "evidence-only", "superseded-evidence"}:
        return False
    return True


def _knowledge_role(text: str) -> str:
    return (_frontmatter_value(text, "knowledgeRole") or _frontmatter_value(text, "type") or "authoritative").strip()


def _graph_pages(vault: Path, reviewed: Path) -> list[Path]:
    pages = [vault / name for name in VAULT_INDEX_FILES if (vault / name).exists()]
    pages.extend(_reviewed_pages(reviewed, authoritative_only=False))
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
    for page in _reviewed_pages(reviewed, authoritative_only=False):
        text = read_text(page)
        records.append({
            "page": rel(root, page),
            "vaultPath": rel(vault, page),
            "title": _page_title(text, page.stem),
            "text": text,
        })
    return records


def _duplicate_reviewed_record(root: Path, vault: Path, page: Path) -> dict:
    text = read_text(page)
    return {
        "page": rel(root, page),
        "vaultPath": rel(vault, page),
        "title": _page_title(text, page.stem),
        "status": _frontmatter_value(text, "status") or "unknown",
        "knowledgeRole": _knowledge_role(text),
        "authoritative": _is_authoritative_reviewed_text(text),
        "authoritativePage": _frontmatter_value(text, "authoritativePage") or "",
        "duplicateDisposition": _frontmatter_value(text, "duplicateDisposition") or "",
        "domain": _metadata_value(text, "domain") or _scope_from_text(text),
        "rawSourceRefs": _metadata_list_values(text, "sourceRefs", prefix="user/knowledge/raw/"),
        "aliases": _reviewed_aliases(text),
        "bodyWordSet": sorted(_reviewed_body_word_set(text)),
        "reviewedAt": _frontmatter_value(text, "reviewedAt") or _nested_reviewed_at(text) or "unknown",
        "reviewedBy": _frontmatter_value(text, "reviewedBy") or _nested_reviewed_by(text) or "unknown",
    }


def _duplicate_topic_key(record: dict) -> str:
    domain = record.get("domain") or ""
    if domain and domain != "unknown":
        return domain.lower()
    return re.sub(r"[^a-z0-9]+", "-", record["title"].lower()).strip("-") or "unknown-topic"


def _duplicate_alias_keys(record: dict) -> list[str]:
    values = [record.get("title") or ""]
    values.extend(record.get("aliases") or [])
    keys = []
    for value in values:
        key = re.sub(r"[^a-z0-9\u3400-\u9fff]+", "-", value.lower()).strip("-")
        if key and key not in {"none", "unknown"}:
            keys.append(key)
    return _dedupe_preserve_order(keys)


def _duplicate_similarity_candidates(records: list[dict]) -> list[dict]:
    by_raw: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        for raw_source in record.get("rawSourceRefs") or []:
            by_raw[raw_source].append(record)
    candidates = []
    for raw_source, items in by_raw.items():
        for left_index, left in enumerate(items):
            for right in items[left_index + 1:]:
                left_words = set(left.get("bodyWordSet") or [])
                right_words = set(right.get("bodyWordSet") or [])
                score = _jaccard(left_words, right_words)
                alias_overlap = set(_duplicate_alias_keys(left)) & set(_duplicate_alias_keys(right))
                if score < 0.72 and not alias_overlap:
                    continue
                pair_id = hashlib.sha256(f"{left['page']}|{right['page']}".encode("utf-8")).hexdigest()[:10]
                candidates.append({
                    "rawSource": raw_source,
                    "topicKey": f"similarity:{pair_id}",
                    "score": round(score, 3),
                    "pages": [left, right],
                })
    return candidates


def _reviewed_body_word_set(text: str) -> set[str]:
    body = _strip_frontmatter(text).lower()
    stopwords = {
        "with", "this", "that", "from", "into", "reviewed", "knowledge", "source",
        "trace", "scope", "user", "private", "notes", "governance", "applicability",
    }
    words = set()
    for token in re.findall(r"[a-z][a-z0-9_-]{3,}", body):
        normalized = token.strip("-_")
        if normalized and normalized not in stopwords:
            words.add(normalized)
    return words


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _is_governed_duplicate_non_authoritative(record: dict) -> bool:
    status = (record.get("status") or "").lower()
    if status in {"archived", "superseded", "deprecated"}:
        return True
    role = (record.get("knowledgeRole") or "").lower()
    disposition = (record.get("duplicateDisposition") or "").lower()
    if role in {"validation-evidence", "pipeline-smoke-evidence", "evidence-only", "superseded-evidence"}:
        return True
    if disposition in {"evidence-only", "superseded", "archived"}:
        return True
    return False


def _mark_residual_gap_candidate_pages(root: Path, candidate_wiki: Path) -> list[dict]:
    updates = []
    for link, disposition in RESIDUAL_GAP_DISPOSITIONS.items():
        page = candidate_wiki / "concepts" / f"{disposition['candidateConcept']}.md"
        if not page.exists():
            continue
        text = read_text(page)
        if "## P5-19 Disposition" in text:
            updates.append({
                "page": rel(root, page),
                "disposition": disposition["disposition"],
                "state": "already-present",
            })
            continue
        section = [
            "",
            "## P5-19 Disposition",
            "",
            f"- Disposition: `{disposition['disposition']}`.",
            "- Decision: dedup / defer; do not promote from the current PDF-derived candidate.",
            "- Targets:",
        ]
        section.extend(f"  - `{target}`" for target in disposition["targets"])
        section.extend([
            "- Boundary: this page remains candidate evidence only and is not authoritative reviewed Knowledge.",
            "",
        ])
        write_text(page, text.rstrip() + "\n" + "\n".join(section))
        updates.append({
            "page": rel(root, page),
            "disposition": disposition["disposition"],
            "state": "updated",
        })
    return updates


def _current_residual_gap_links(vault: Path, reviewed: Path) -> list[dict]:
    lookup = _page_lookup(vault, _graph_pages(vault, reviewed))
    residual = []
    for page in _reviewed_pages(reviewed):
        for link in extract_wikilinks(read_text(page)):
            if link not in RESIDUAL_GAP_DISPOSITIONS:
                continue
            if _resolve_wikilink(link, lookup):
                continue
            residual.append({
                "link": link,
                "referencedBy": rel(vault, page),
            })
    return residual


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


def _controlled_tag_vocabulary(schema_text: str) -> set[str]:
    block = _section_by_heading(schema_text, "Controlled Tag Vocabulary")
    tags = set()
    for line in block.splitlines():
        match = re.match(r"\s*-\s+`?([A-Za-z0-9_.-]+)`?", line.strip())
        if match:
            tags.add(match.group(1))
    return tags


def _reviewed_tags(text: str) -> list[str]:
    tags = []
    inline = _frontmatter_value(text, "tags")
    if inline and inline.startswith("[") and inline.endswith("]"):
        tags.extend(item.strip().strip("\"'`") for item in inline.strip("[]").split(",") if item.strip())
    tags.extend(_metadata_list_values(text, "tags"))
    return _dedupe_preserve_order([tag for tag in tags if tag])


def _reviewed_aliases(text: str) -> list[str]:
    aliases = _metadata_list_values(text, "aliases")
    for concept in _reviewed_key_concepts(text):
        aliases.extend(_split_aliases(concept.get("aliases") or ""))
    return _dedupe_preserve_order([item for item in aliases if item and item.lower() not in {"none", "n/a", "null"}])


def _split_aliases(value: str) -> list[str]:
    cleaned = value.strip().strip("`")
    if not cleaned or cleaned.lower() in {"none", "n/a", "null"}:
        return []
    parts = re.split(r"[,;，；、/]+", cleaned)
    return [part.strip().strip("`") for part in parts if part.strip().strip("`")]


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
    run_dirs = {wiki.parent for wiki in archive_root.rglob("wiki") if wiki.is_dir()}
    run_dirs.update(path for path in archive_root.glob("*/*") if path.is_dir() and (path / "wiki").exists())
    for run_dir in sorted(run_dirs, key=lambda p: rel(root, p).lower()):
        wiki = run_dir / "wiki"
        archive_parts = run_dir.relative_to(archive_root).parts
        governance_state = _archive_governance_state(archive_parts)
        records.append({
            "runId": run_dir.name,
            "path": rel(root, run_dir),
            "wiki": rel(root, wiki) if wiki.exists() else "missing",
            "markdownCount": len(list(wiki.rglob("*.md"))) if wiki.exists() else 0,
            "governanceState": governance_state,
            "reason": "archived inactive candidate corpus",
        })
    return records


def _candidate_archive_cleanup_records(
    root: Path,
    vault: Path,
    reviewed: Path,
    candidate_dir: Path,
    registry: Path,
) -> list[dict]:
    records = []
    for corpus_root in _candidate_archive_cleanup_roots(candidate_dir):
        markdown_files = _candidate_markdown_files(corpus_root)
        if not markdown_files:
            continue
        kind = _candidate_archive_kind(candidate_dir, corpus_root)
        references = _candidate_cleanup_references(root, vault, reviewed, registry, corpus_root)
        recommended_action, reason = _candidate_cleanup_recommendation(kind, references)
        records.append({
            "corpusId": _candidate_archive_corpus_id(candidate_dir, corpus_root),
            "path": rel(root, corpus_root),
            "kind": kind,
            "governanceState": _archive_governance_state(corpus_root.relative_to(candidate_dir / "_archive").parts),
            "markdownCount": len(markdown_files),
            "wikilinkCount": _candidate_wikilink_count(markdown_files),
            "references": references,
            "recommendedAction": recommended_action,
            "reason": reason,
        })
    return records


def _candidate_archive_cleanup_roots(candidate_dir: Path) -> list[Path]:
    archive_root = candidate_dir / "_archive"
    if not archive_root.exists():
        return []
    roots: list[Path] = []
    by_source = archive_root / "by-source"
    if by_source.exists():
        for source_dir in sorted([p for p in by_source.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
            for bucket in sorted([p for p in source_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
                nested = sorted([p for p in bucket.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
                if bucket.name in {"gap-concepts", "legacy", "validation-evidence"} and nested:
                    roots.extend(nested)
                else:
                    roots.append(bucket)
    for child in sorted([p for p in archive_root.iterdir() if p.is_dir() and p.name != "by-source"], key=lambda p: p.name.lower()):
        nested_wiki_roots = sorted({wiki.parent for wiki in child.rglob("wiki") if wiki.is_dir()}, key=lambda p: str(p).lower())
        roots.extend(nested_wiki_roots or [child])
    unique: dict[str, Path] = {}
    for root_path in roots:
        unique[str(root_path.resolve()).lower()] = root_path
    return sorted(unique.values(), key=lambda p: str(p).lower())


def _candidate_archive_kind(candidate_dir: Path, corpus_root: Path) -> str:
    parts = corpus_root.relative_to(candidate_dir / "_archive").parts
    if "layout" in parts or corpus_root.name in {"layout"}:
        return "lightweight-audit-record"
    return "full-corpus"


def _candidate_archive_corpus_id(candidate_dir: Path, corpus_root: Path) -> str:
    parts = corpus_root.relative_to(candidate_dir / "_archive").parts
    if parts and parts[0] == "by-source":
        return "/".join(parts[1:])
    return "/".join(parts)


def _candidate_markdown_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path] if path.suffix.lower() == ".md" else []
    return sorted([p for p in path.rglob("*.md") if p.is_file()], key=lambda p: str(p).lower())


def _candidate_wikilink_count(markdown_files: list[Path]) -> int:
    total = 0
    for page in markdown_files:
        total += len(extract_wikilinks(read_text(page)))
    return total


def _candidate_cleanup_references(
    root: Path,
    vault: Path,
    reviewed: Path,
    registry: Path,
    corpus_root: Path,
) -> dict:
    reviewed_pages = _reviewed_pages(reviewed, authoritative_only=False)
    home_pages = [vault / "Home.md"] if (vault / "Home.md").exists() else []
    registry_pages = [registry] if registry.exists() else []
    return {
        "reviewed": _candidate_path_references(root, vault, reviewed_pages, corpus_root),
        "home": _candidate_path_references(root, vault, home_pages, corpus_root),
        "registry": _candidate_path_references(root, vault, registry_pages, corpus_root),
    }


def _candidate_path_references(root: Path, vault: Path, pages: list[Path], target: Path) -> list[str]:
    needles = _candidate_reference_needles(root, vault, target)
    refs = []
    for page in pages:
        text = read_text(page).replace("\\", "/")
        if any(needle and needle in text for needle in needles):
            refs.append(rel(root, page))
    return refs


def _candidate_reference_needles(root: Path, vault: Path, target: Path) -> list[str]:
    needles = [rel(root, target).replace("\\", "/")]
    try:
        needles.append(rel(vault, target).replace("\\", "/"))
    except ValueError:
        pass
    try:
        needles.append(str(target.relative_to(vault)).replace("\\", "/"))
    except ValueError:
        pass
    return _dedupe_preserve_order([item for item in needles if item])


def _candidate_cleanup_recommendation(kind: str, references: dict) -> tuple[str, str]:
    if kind == "lightweight-audit-record":
        return "keep-lightweight-audit-record", "lightweight audit evidence may remain outside the full candidate corpus cleanup"
    if references.get("reviewed") or references.get("registry"):
        return (
            "rewrite-source-trace-to-audit-record-before-removal",
            "reviewed or registry references exist; rewrite provenance to a compact audit record first",
        )
    return (
        "compact-to-audit-record-and-remove-full-corpus-from-vault",
        "post-promotion full candidate corpus should leave the default Obsidian graph after audit summary is retained",
    )


def _archive_governance_state(parts: tuple[str, ...]) -> str:
    if not parts:
        return "archived"
    if parts[0] == "by-source":
        if len(parts) >= 3:
            return f"by-source/{parts[1]}/{parts[2]}"
        if len(parts) >= 2:
            return f"by-source/{parts[1]}"
    if len(parts) >= 2:
        return parts[0]
    return "archived"


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
    if status.get("residualGapDisposition", {}).get("state") == "passed" and status.get("gapConceptPromotion", {}):
        return "promoted-evidence", "approved concepts promoted; residual workflow gaps disposed"
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


def _move_path(root: Path, source: Path, destination: Path, moves: list[dict], kind: str) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if not source.exists():
        moves.append({
            "kind": kind,
            "oldPath": rel(root, source),
            "newPath": rel(root, destination),
            "state": "source-missing",
        })
        return
    if destination.exists():
        moves.append({
            "kind": kind,
            "oldPath": rel(root, source),
            "newPath": rel(root, destination),
            "state": "destination-present",
        })
        return
    if root.resolve() not in source.parents and source != root.resolve():
        raise ValueError(f"move source escapes root: {source}")
    if root.resolve() not in destination.parents and destination != root.resolve():
        raise ValueError(f"move destination escapes root: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    moves.append({
        "kind": kind,
        "oldPath": rel(root, source),
        "newPath": rel(root, destination),
        "state": "moved",
    })


def _remove_empty_dir(root: Path, directory: Path, moves: list[dict], kind: str) -> None:
    directory = directory.resolve()
    if not directory.exists() or not directory.is_dir():
        return
    if root.resolve() not in directory.parents and directory != root.resolve():
        raise ValueError(f"empty directory cleanup escapes root: {directory}")
    try:
        next(directory.iterdir())
    except StopIteration:
        directory.rmdir()
        moves.append({
            "kind": kind,
            "oldPath": rel(root, directory),
            "newPath": "",
            "state": "removed-empty-dir",
        })


def _canonical_layout_replacements(source_domain: str, target_domain: str, source_id: str, canonical_page: str) -> dict[str, str]:
    return {
        f"user/knowledge/raw/{source_domain}/Agent Harness Engineering A Survey.pdf": f"user/knowledge/raw/{target_domain}/Agent Harness Engineering A Survey.pdf",
        "user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md": f"user/knowledge/reviewed/{target_domain}/{canonical_page}.md",
        "user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md": f"user/knowledge/reviewed/_archive/validation-evidence/{target_domain}/p5-15-pipeline-smoke.md",
        "user/knowledge/reviewed/agent/concepts": f"user/knowledge/reviewed/{target_domain}/concepts",
        "reviewed/agent/llm-wiki-absorption-pdf-smoke": f"reviewed/{target_domain}/{canonical_page}",
        "reviewed/agent/p5-15-pipeline-smoke": f"reviewed/_archive/validation-evidence/{target_domain}/p5-15-pipeline-smoke",
        "reviewed/agent/concepts": f"reviewed/{target_domain}/concepts",
        "reviewed/agent/index": f"reviewed/{target_domain}/index",
        "reviewed/agent/": f"reviewed/{target_domain}/",
        "raw/agent/": f"raw/{target_domain}/",
        "[[llm-wiki-absorption-pdf-smoke]]": f"[[{canonical_page}]]",
        "[[reviewed/agent/index|Agent]]": f"[[reviewed/{target_domain}/index|Agent Harness Engineering]]",
        "user/knowledge/candidate/_archive/promoted-evidence/llm-wiki-absorption-pdf-smoke/wiki": f"user/knowledge/candidate/_archive/by-source/{source_id}/canonical-candidate/wiki",
        "user/knowledge/candidate/_archive/promoted-evidence/p5-15-pipeline-smoke/wiki": f"user/knowledge/candidate/_archive/by-source/{source_id}/validation-evidence/p5-15-pipeline-smoke/wiki",
        "user/knowledge/candidate/_archive/promoted-evidence/reviewed-gap-concepts/wiki": f"user/knowledge/candidate/_archive/by-source/{source_id}/gap-concepts/reviewed-gap-concepts/wiki",
    }


def _rewrite_vault_references(root: Path, vault: Path, registry: Path, replacements: dict[str, str]) -> list[dict]:
    files = [p for p in vault.rglob("*.md") if p.is_file()]
    if registry.exists():
        files.append(registry)
    rewrites = []
    for path in sorted(set(files), key=lambda p: rel(root, p)):
        text = read_text(path)
        new_text = text
        applied = []
        for old, new in replacements.items():
            if old in new_text:
                new_text = new_text.replace(old, new)
                applied.append(old)
        if new_text != text:
            write_text(path, new_text)
            rewrites.append({
                "path": rel(root, path),
                "replacementCount": len(applied),
            })
    return rewrites


def _normalize_canonical_authoritative_page(page: Path, target_domain: str, canonical_page: str) -> None:
    text = read_text(page)
    replacements = {
        "documentName: user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md": f"documentName: user/knowledge/reviewed/{target_domain}/{canonical_page}.md",
        "version: v1.0.0-reviewed": "version: v1.1.0-canonical-layout",
        "purpose: 保存从 candidate wiki 晋升而来的 reviewed Knowledge，主题为 agent harness engineering。": "purpose: 保存 Agent Harness Engineering A Survey 的正式 reviewed Knowledge。",
        "outputTo:\n  - user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md": f"outputTo:\n  - user/knowledge/reviewed/{target_domain}/{canonical_page}.md",
        "# Agent Harness Engineering Survey Reviewed Knowledge": "# Agent Harness Engineering Survey",
        "knowledgeId: llm-wiki-absorption-pdf-smoke": f"knowledgeId: {canonical_page}",
        "storageBoundary: user/knowledge/reviewed": f"storageBoundary: user/knowledge/reviewed/{target_domain}",
        "`llm-wiki-absorption-pdf-smoke.md` 是 authoritative page": f"`{canonical_page}.md` 是 authoritative page",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    write_text(page, text)


def _normalize_validation_evidence_page(page: Path, target_domain: str, canonical_path: Path) -> None:
    text = read_text(page)
    text = re.sub(r"(?m)^status:\s*active$", "status: archived", text, count=1)
    replacements = {
        "version: v1.1.0-validation-evidence": "version: v1.2.0-archived-validation-evidence",
        "authoritativePage: user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md": f"authoritativePage: user/knowledge/reviewed/{target_domain}/agent-harness-engineering-survey.md",
        "purpose: 保存 P5-15 pipeline smoke 的 reviewed promotion 验证证据；不作为 authoritative reviewed Knowledge。": "purpose: 归档 P5-15 pipeline smoke 的 reviewed promotion 验证证据；不作为 authoritative reviewed Knowledge。",
        "outputTo:\n  - user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md": f"outputTo:\n  - user/knowledge/reviewed/_archive/validation-evidence/{target_domain}/p5-15-pipeline-smoke.md",
        "[[llm-wiki-absorption-pdf-smoke]]": "[[agent-harness-engineering-survey]]",
        "P5-18 duplicate reviewed governance 确认：本页与 [[agent-harness-engineering-survey]] 来自同一 raw source": "P5-18 duplicate reviewed governance 确认：本页与 [[agent-harness-engineering-survey]] 来自同一 raw source",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("本页保留为 validation evidence，不作为 authoritative reviewed Knowledge；事实回答应优先使用 [[agent-harness-engineering-survey]]。", "本页已归档为 validation evidence，不作为 authoritative reviewed Knowledge；事实回答应优先使用 [[agent-harness-engineering-survey]]。")
    write_text(page, text)


def _canonical_domain_index_text(root: Path, domain_dir: Path, target_domain: str, canonical_page: str, evidence_path: Path) -> str:
    concept_dir = domain_dir / "concepts"
    concept_pages = sorted(concept_dir.glob("*.md")) if concept_dir.exists() else []
    lines = [
        "---",
        f"documentName: user/knowledge/reviewed/{target_domain}/index.md",
        "version: v1.1.0-canonical-layout",
        f"updatedAt: {today()}",
        "status: active",
        "knowledgeRole: domain-index",
        "authoritative: true",
        "purpose: 作为 agent-harness-engineering domain reviewed Knowledge 的领域入口。",
        "scope:",
        "  - reviewed-knowledge",
        "  - user-private",
        f"  - {target_domain}",
        "prerequisites:",
        "  - user/knowledge/Home.md",
        "relatedDocuments:",
        f"  - user/knowledge/reviewed/{target_domain}/{canonical_page}.md",
        f"  - user/knowledge/reviewed/{target_domain}/schema.md",
        "outputTo:",
        f"  - user/knowledge/reviewed/{target_domain}/index.md",
        "owner: user",
        "reviewAfter: source-updated-or-2026-12-31",
        "supersededBy:",
        "dependsOn:",
        f"  - user/knowledge/raw/{target_domain}/Agent Harness Engineering A Survey.pdf",
        "review:",
        "  reviewedBy: user",
        f"  reviewedAt: {today()}",
        "  decision: p5-20-pre-canonical-vault-layout",
        "---",
        "# Agent Harness Engineering Domain",
        "",
        "## Knowledge Pages",
        "",
        "| Page | Role | Review |",
        "|---|---|---|",
        f"| [[{canonical_page}|Agent Harness Engineering Survey]] | authoritative content baseline | user / 2026-06-30 |",
        "",
        "## Concepts",
        "",
        "| Concept | Page |",
        "|---|---|",
    ]
    if concept_pages:
        for page in concept_pages:
            lines.append(f"| {page.stem} | [[concepts/{page.stem}]] |")
    else:
        lines.append("| _No concepts yet._ |  |")
    lines.extend([
        "",
        "## Schema",
        "",
        f"- [[schema|{_domain_title(target_domain)} Schema]]",
        "",
        "## Archived Validation Evidence",
        "",
        "| Page | Role | Authoritative Page |",
        "|---|---|---|",
        f"| [[{evidence_path.stem}|Agent Harness Engineering Survey Pipeline Smoke Evidence]] | archived pipeline smoke evidence | [[{canonical_page}]] |",
        "",
        "## Raw Sources",
        "",
        "| Source | Boundary |",
        "|---|---|",
        f"| `user/knowledge/raw/{target_domain}/Agent Harness Engineering A Survey.pdf` | local-only raw provenance |",
        "",
        "## Governance Notes",
        "",
        "- 本领域入口只路由 reviewed Knowledge，不替代 `Home.md` 全局入口。",
        "- 正式 reviewed Knowledge 使用语义文件名，不使用 smoke、pipeline 或阶段编号命名。",
        "- Pipeline smoke 和 gap candidate 只作为 evidence 保留，不与 authoritative page 并列。",
        "- 一份 raw source 对应一个 canonical candidate evidence、一个 authoritative reviewed page，以及可选多个 reviewed concept pages。",
        "",
    ])
    return "\n".join(lines)


def _canonical_domain_schema_text(target_domain: str) -> str:
    return "\n".join([
        "---",
        f"documentName: user/knowledge/reviewed/{target_domain}/schema.md",
        "version: v1.0.0-domain-schema",
        f"updatedAt: {today()}",
        "status: active",
        "knowledgeRole: domain-schema",
        "authoritative: true",
        "purpose: 定义 agent-harness-engineering reviewed Knowledge 的目录、命名、frontmatter 和治理规则。",
        "scope:",
        "  - reviewed-knowledge",
        "  - user-private",
        f"  - {target_domain}",
        "prerequisites:",
        f"  - user/knowledge/reviewed/{target_domain}/index.md",
        "relatedDocuments:",
        "  - harness/architecture/HarnessEngineering.md",
        "  - harness/rag/RAGIndex.md",
        "  - harness/governance/KnowledgePromotionPolicy.md",
        "outputTo:",
        f"  - user/knowledge/reviewed/{target_domain}/schema.md",
        "owner: user",
        "reviewAfter: source-updated-or-2026-12-31",
        "supersededBy:",
        "dependsOn:",
        f"  - user/knowledge/reviewed/{target_domain}/index.md",
        "review:",
        "  reviewedBy: user",
        f"  reviewedAt: {today()}",
        "  decision: p5-20-pre-domain-schema-added",
        "---",
        "# Agent Harness Engineering Schema",
        "",
        "## Directory Rules",
        "",
        "- `index.md` 是本领域入口。",
        "- `agent-harness-engineering-survey.md` 是当前 raw source 的唯一 authoritative reviewed page。",
        "- `concepts/` 保存从 authoritative page 拆分出的 reviewed concept pages。",
        "- validation evidence 进入 `reviewed/_archive/validation-evidence/agent-harness-engineering/`。",
        "- raw source 保存在 `raw/agent-harness-engineering/`。",
        "",
        "## Naming Rules",
        "",
        "- 正式 reviewed page 使用语义名称，不使用 `smoke`、`pipeline`、阶段编号或工具 run id。",
        "- candidate archive 可以保留 run id，但必须按 source-centered 目录归档。",
        "- concept page 使用稳定 PascalCase concept id。",
        "",
        "## Required Reviewed Page Sections",
        "",
        "- Statement",
        "- Applicability",
        "- Non-Applicability",
        "- Key Concepts",
        "- Source Trace",
        "- Staleness",
        "- Governance Notes",
        "",
        "## Validation Rules",
        "",
        "- reviewed graph 不应有 broken links。",
        "- 同一 raw source 和同一 topic 只能有一个 active authoritative page。",
        "- archived validation evidence 不作为事实回答来源。",
        "- source trace 可以引用 candidate archive 和 runtime artifacts，但它们不反向成为事实源。",
        "",
    ])


def _canonicalize_knowledge_registry(root: Path, registry: Path, target_domain: str) -> dict | None:
    if not registry.exists():
        return None
    try:
        data = json.loads(read_text(registry))
    except json.JSONDecodeError:
        return {"path": rel(root, registry), "reason": "registry-invalid-json"}
    for source in data.get("knowledgeSources", []):
        if source.get("knowledgeId") != "user-knowledge-vault":
            continue
        source["updatedAt"] = today()
        source["domains"] = [
            {
                "domainId": target_domain,
                "raw": f"user/knowledge/raw/{target_domain}",
                "reviewed": f"user/knowledge/reviewed/{target_domain}",
                "index": f"user/knowledge/reviewed/{target_domain}/index.md",
                "schema": f"user/knowledge/reviewed/{target_domain}/schema.md",
                "concepts": f"user/knowledge/reviewed/{target_domain}/concepts",
                "status": "active",
            }
        ]
    write_text(registry, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return {"path": rel(root, registry), "reason": "canonical-domain-registry"}


def _format_canonical_layout_report(result: dict) -> str:
    lines = [
        f"# Canonical Knowledge Vault Layout - {today()}",
        "",
        f"- 状态（State）: `{result['state']}`",
        f"- Source domain: `{result['sourceDomain']}`",
        f"- Target domain: `{result['targetDomain']}`",
        f"- Source ID: `{result['sourceId']}`",
        f"- Canonical reviewed page: `{result['canonicalReviewedPage']}`",
        f"- Archived validation evidence: `{result['archivedValidationEvidence']}`",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Moves",
        "",
    ]
    if result["moves"]:
        lines.extend(
            f"- `{item['kind']}`: `{item['oldPath']}` -> `{item['newPath']}` ({item['state']})"
            for item in result["moves"]
        )
    else:
        lines.append("- No moves.")
    lines.extend(["", "## Rewrites", ""])
    if result["rewrites"]:
        for item in result["rewrites"]:
            detail = f", replacements = {item['replacementCount']}" if "replacementCount" in item else ""
            lines.append(f"- `{item['path']}` ({item.get('reason', 'text-rewrite')}{detail})")
    else:
        lines.append("- No rewrites.")
    lines.extend([
        "",
        "## Sync",
        "",
        f"- Reviewed pages: {result['sync']['reviewedPageCount']}",
        f"- Authoritative reviewed pages: {result['sync']['authoritativeReviewedPageCount']}",
        f"- Evidence reviewed pages: {result['sync']['evidenceReviewedPageCount']}",
        "",
        "## JSON",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    return "\n".join(lines)


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


def _is_absolute_or_url(value: str) -> bool:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", value):
        return True
    return Path(value).is_absolute()


def _contains_absolute_path_or_url(text: str) -> bool:
    return bool(re.search(r"(?i)([A-Z]:\\|file://|https?://|/Users/|/home/)", text))


def _git_check_ignored(root: Path, path: Path) -> dict:
    path_ref = rel(root, path)
    try:
        completed = subprocess.run(
            ["git", "check-ignore", "-v", "--", path_ref],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        return {"path": path_ref, "ignored": False, "error": str(exc)}
    return {
        "path": path_ref,
        "ignored": completed.returncode == 0,
        "rule": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _git_ls_files(root: Path, path: str) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--", path],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def _sensitive_plugin_config_issues(value: object, path: str) -> list[str]:
    issues: list[str] = []
    sensitive_keys = {"apikey", "api_key", "token", "secret", "password", "auth", "authorization"}
    if isinstance(value, dict):
        for key, item in value.items():
            key_norm = re.sub(r"[^a-z0-9]+", "", key.lower())
            item_path = f"{path}.{key}"
            if key_norm in {re.sub(r'[^a-z0-9]+', '', name) for name in sensitive_keys}:
                if isinstance(item, str) and item.strip():
                    issues.append(f"{item_path} must be empty in local plugin config")
                elif item not in ("", None, False):
                    issues.append(f"{item_path} must not contain credential-like value")
            issues.extend(_sensitive_plugin_config_issues(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            issues.extend(_sensitive_plugin_config_issues(item, f"{path}[{index}]"))
    return issues


def _page_title(text: str, fallback: str) -> str:
    return _frontmatter_value(text, "title") or _first_heading(text) or fallback


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _frontmatter_value(text: str, key: str) -> str | None:
    frontmatter = _frontmatter_block(text)
    if not frontmatter:
        return None
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip().strip("\"'")
    return value or None


def _metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", text)
    if not match:
        return None
    value = match.group(1).strip().strip("\"'")
    return value or None


def _metadata_list_values(text: str, key: str, prefix: str | None = None) -> list[str]:
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t\r]*$", text)
    if not match:
        return []
    values = []
    for line in text[match.end():].lstrip("\r\n").splitlines():
        item = re.match(r"^[ \t]+-\s+(.+)$", line)
        if item:
            value = item.group(1).strip().strip("\"'")
            if prefix and not value.startswith(prefix):
                continue
            values.append(value)
            continue
        if line.startswith((" ", "\t")) and line.strip():
            continue
        break
    return _dedupe_preserve_order(values)


def _scope_from_text(text: str) -> str:
    scope_block = re.search(r"(?ms)^scope:\s*\n((?:\s+- .+\n)+)", text)
    if scope_block:
        scopes = [line.split("-", 1)[1].strip() for line in scope_block.group(1).splitlines() if "-" in line]
        for scope in scopes:
            if scope != "reviewed-knowledge":
                return scope
    return _frontmatter_value(text, "scope") or "unknown"


def _nested_reviewed_by(text: str) -> str | None:
    return _nested_frontmatter_value(text, "review", "reviewedBy")


def _nested_reviewed_at(text: str) -> str | None:
    return _nested_frontmatter_value(text, "review", "reviewedAt")


def _nested_frontmatter_value(text: str, section: str, key: str) -> str | None:
    frontmatter = _frontmatter_block(text)
    if not frontmatter:
        return None
    in_section = False
    for line in frontmatter.splitlines():
        if re.fullmatch(rf"{re.escape(section)}:\s*", line):
            in_section = True
            continue
        if not in_section:
            continue
        if line and not line.startswith((" ", "\t")):
            break
        match = re.match(rf"\s+{re.escape(key)}:\s*(.*)$", line)
        if match:
            value = match.group(1).strip().strip("\"'")
            return value or None
    return None


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
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph.get("edges", []):
        endpoints = [edge.get("from"), edge.get("to")]
        if endpoints[0] and endpoints[1]:
            adjacency[endpoints[0]].add(endpoints[1])
            adjacency[endpoints[1]].add(endpoints[0])
    if not seed_ids:
        return
    total_seed_score = sum(max(score, 0.1) for score in seed_ids.values())
    seed_probs = {node_id: max(score, 0.1) / total_seed_score for node_id, score in seed_ids.items()}
    ppr = dict(seed_probs)
    damping = 0.85
    for _ in range(20):
        next_scores = {node_id: (1 - damping) * prob for node_id, prob in seed_probs.items()}
        for node_id, score in ppr.items():
            neighbors = adjacency.get(node_id)
            if not neighbors:
                next_scores[node_id] = next_scores.get(node_id, 0.0) + damping * score
                continue
            share = damping * score / len(neighbors)
            for neighbor_id in neighbors:
                next_scores[neighbor_id] = next_scores.get(neighbor_id, 0.0) + share
        ppr = next_scores
    max_seed_score = max(seed_ids.values())
    for neighbor_id, ppr_score in sorted(ppr.items(), key=lambda item: item[1], reverse=True):
        if neighbor_id in seed_ids:
            continue
        neighbor = id_to_path.get(neighbor_id)
        if not neighbor or not neighbor.exists() or neighbor in scored:
            continue
        if not rel(vault, neighbor).startswith("reviewed/"):
            continue
        if not _is_authoritative_reviewed_page(neighbor):
            continue
        bonus = max(0.1, ppr_score * max_seed_score * 1.5)
        text = read_text(neighbor)
        scored[neighbor] = {
            "page": rel(root, neighbor),
            "vaultPath": rel(vault, neighbor),
            "title": _page_title(text, neighbor.stem),
            "score": round(bonus, 3),
            "reason": ["graph-ppr"],
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
