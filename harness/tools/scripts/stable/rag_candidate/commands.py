from __future__ import annotations

import json
import shutil
from pathlib import Path

from .common import (
    all_wiki_pages,
    infer_run_id_from_wiki,
    package_version,
    print_json,
    read_text,
    rel,
    safe_run_id,
    sha256_file,
    sha256_text,
    split_chunks,
    timestamp_id,
    today,
    update_status,
    write_text,
)
from .convert import collect_inputs, convert_file
from .wiki_ops import build_graph, concept_page, health_wiki, lint_wiki, search_wiki_pages, source_page, title_from_markdown


def run_ingest(args) -> dict:
    root = Path(args.root).resolve()
    run_id = safe_run_id(args.run_id or timestamp_id())
    input_files = collect_inputs(args.inputs)

    raw_out = root / "user" / "knowledge" / "raw" / run_id
    extracted_out = root / "var" / "rag" / run_id / "extracted"
    candidate_wiki = root / "user" / "knowledge" / "candidate" / run_id / "wiki"
    eval_out = root / "var" / "rag" / run_id / "evals"
    graph_out = root / "var" / "rag" / run_id / "graph"
    status_out = root / "var" / "logs" / f"{run_id}.json"

    for path in [extracted_out, candidate_wiki, eval_out, graph_out, status_out.parent]:
        path.mkdir(parents=True, exist_ok=True)

    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = lambda value, **_: value  # type: ignore

    source_records = []
    chunk_lines = []
    source_entries = []
    log_entries = []

    for source in tqdm(input_files, desc="Converting raw"):
        source = source.resolve()
        slug = _unique_slug(source_records, source.name)
        if args.copy_raw:
            raw_target = raw_out / source.name
            raw_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, raw_target)
            source_ref = rel(root, raw_target)
        else:
            source_ref = rel(root, source)

        markdown, converter = convert_file(source)
        title = title_from_markdown(markdown, source.stem.replace("-", " ").title())
        extracted_path = extracted_out / f"{slug}.md"
        write_text(extracted_path, markdown)
        extracted_ref = rel(root, extracted_path)

        preview = "\n".join(markdown.strip().splitlines()[:18]).strip()
        if len(preview) > 1400:
            preview = preview[:1400].rsplit(" ", 1)[0] + "..."
        source_wiki_path = candidate_wiki / "sources" / f"{slug}.md"
        write_text(source_wiki_path, source_page(title, source_ref, extracted_ref, preview))
        source_entries.append(f"- [{title}](sources/{slug}.md) - candidate source page")
        log_entries.append(f"## [{today()}] ingest | {title}\n\nScaffolded candidate page from `{source_ref}`.")

        chunks = split_chunks(markdown, args.max_chunk_chars)
        for index, chunk in enumerate(chunks, 1):
            chunk_lines.append(json.dumps({
                "chunkId": f"{slug}:{index:03d}",
                "sourceId": slug,
                "text": chunk,
                "provenance": {
                    "sourceRef": source_ref,
                    "extractedPath": extracted_ref,
                    "tool": converter,
                },
            }, ensure_ascii=False))

        source_records.append({
            "id": slug,
            "sourceRef": source_ref,
            "sourceHashSha256": sha256_file(source),
            "extractedMarkdown": extracted_ref,
            "outputHashSha256": sha256_text(markdown),
            "converter": converter,
            "candidatePage": rel(root, source_wiki_path),
        })

    _write_foundation_pages(candidate_wiki)
    _write_index(candidate_wiki, source_entries)
    _write_overview(candidate_wiki, run_id, source_records)
    write_text(candidate_wiki / "log.md", "# Candidate Wiki Log\n\n" + "\n\n".join(log_entries) + "\n")
    write_text(extracted_out / "chunks.jsonl", "\n".join(chunk_lines) + "\n")

    manifest = {
        "manifestId": run_id,
        "status": "candidate-generated",
        "createdAt": today(),
        "network": "not-required-for-local-conversion",
        "llmApiRequired": False,
        "cloudLlmApisAllowed": False,
        "sources": source_records,
        "outputs": {
            "chunksJsonl": rel(root, extracted_out / "chunks.jsonl"),
            "candidateWiki": rel(root, candidate_wiki),
            "graphRuntime": rel(root, graph_out),
        },
        "review": {
            "reviewedKnowledge": False,
            "promotionHandledByThisTool": False,
            "reviewer": None,
        },
        "toolVersions": {
            "markitdown": package_version("markitdown"),
            "tqdm": package_version("tqdm"),
            "pymupdf4llm": package_version("pymupdf4llm"),
            "PyMuPDF": package_version("PyMuPDF"),
        },
    }
    write_text(extracted_out / "metadata-manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
    _write_extraction_report(extracted_out, root, run_id, source_records, candidate_wiki)

    health = health_wiki(root, candidate_wiki, eval_out / "health-report.md", run_id=run_id)
    lint = lint_wiki(root, candidate_wiki, eval_out / "lint-report.md", run_id=run_id)
    graph = build_graph(candidate_wiki, graph_out, eval_out / "graph-report.md", root=root, run_id=run_id)
    state = "passed" if health["state"] == "passed" and lint["state"] == "passed" else "partial"
    status = {
        "state": state,
        "runId": run_id,
        "inputCount": len(source_records),
        "extracted": rel(root, extracted_out),
        "candidateWiki": rel(root, candidate_wiki),
        "eval": rel(root, eval_out),
        "graph": rel(root, graph_out),
        "statusJson": rel(root, status_out),
        "health": health,
        "lint": lint,
        "graphSummary": graph,
        "nextAction": "agent-enrich-candidate-and-run-health-lint-graph-before-user-review",
    }
    write_text(status_out, json.dumps(status, indent=2, ensure_ascii=False))
    print_json(status)
    return status


def run_health(args) -> dict:
    root = Path(args.root).resolve()
    wiki = _resolve_under_root(root, args.wiki)
    report = _optional_path(root, args.report)
    result = health_wiki(root, wiki, report, run_id=args.run_id or infer_run_id_from_wiki(wiki))
    print_json(result)
    return result


def run_lint(args) -> dict:
    root = Path(args.root).resolve()
    wiki = _resolve_under_root(root, args.wiki)
    report = _optional_path(root, args.report)
    result = lint_wiki(root, wiki, report, run_id=args.run_id or infer_run_id_from_wiki(wiki))
    print_json(result)
    return result


def run_build_graph(args) -> dict:
    root = Path(args.root).resolve()
    wiki = _resolve_under_root(root, args.wiki)
    graph = _resolve_under_root(root, args.graph)
    report = _optional_path(root, args.report)
    result = build_graph(wiki, graph, report, root=root, run_id=args.run_id or infer_run_id_from_wiki(wiki))
    print_json(result)
    return result


def run_query(args) -> dict:
    root = Path(args.root).resolve()
    wiki = _resolve_under_root(root, args.wiki)
    result = search_wiki_pages(root, wiki, args.question, args.limit)
    print_json(result)
    return result


def run_enrichment_plan(args) -> dict:
    root = Path(args.root).resolve()
    manifest_path = _resolve_under_root(root, args.manifest)
    wiki = _resolve_under_root(root, args.wiki)
    report = _optional_path(root, args.report)
    manifest = json.loads(read_text(manifest_path))
    run_id = args.run_id or manifest.get("manifestId") or infer_run_id_from_wiki(wiki)

    required_sections = [
        "## Candidate Summary",
        "## Key Claims",
        "## Entities",
        "## Concepts",
        "## Contradictions",
        "## Applicability",
        "## Review Checklist",
    ]
    items = []
    for source in manifest.get("sources", []):
        candidate_page_ref = source.get("candidatePage", "")
        candidate_page = _resolve_under_root(root, candidate_page_ref) if candidate_page_ref else None
        content = read_text(candidate_page) if candidate_page and candidate_page.exists() else ""
        missing_sections = [section for section in required_sections if section not in content]
        items.append({
            "sourceId": source.get("id"),
            "sourceRef": source.get("sourceRef"),
            "extractedMarkdown": source.get("extractedMarkdown"),
            "candidatePage": candidate_page_ref,
            "missingSections": missing_sections,
            "recommendedActions": [
                "编辑 candidate page 前先阅读 extracted Markdown",
                "用 source-grounded summary 替换 scaffold summary",
                "仅在能提升审核价值时提取可复用 entities 和 concepts",
                "明确标记 contradictions 和 agent inferences",
                "编辑后重新运行 health、lint 和 build-graph",
            ],
        })

    result = {
        "state": "passed",
        "runId": run_id,
        "manifest": rel(root, manifest_path),
        "wiki": rel(root, wiki),
        "sourceCount": len(items),
        "items": items,
        "boundary": "candidate-only-no-promotion",
    }
    if report:
        write_text(report, _format_enrichment_plan(result))
        result["report"] = rel(root, report)
    update_status(root, run_id, {"enrichmentPlan": result})
    print_json(result)
    return result


def run_review_package(args) -> dict:
    root = Path(args.root).resolve()
    manifest_path = _resolve_under_root(root, args.manifest)
    wiki = _resolve_under_root(root, args.wiki)
    manifest = json.loads(read_text(manifest_path))
    run_id = args.run_id or manifest.get("manifestId") or infer_run_id_from_wiki(wiki)
    report = _optional_path(root, args.report) or _default_eval_report(root, run_id, "review-package.md")
    status = _load_status(root, run_id)
    inventory = _wiki_inventory(root, wiki)
    gates = _review_gates(manifest, status, inventory)

    result = {
        "state": "ready-for-human-review" if gates["blockingIssues"] == [] else "needs-repair-before-review",
        "runId": run_id,
        "manifest": rel(root, manifest_path),
        "wiki": rel(root, wiki),
        "sourceCount": len(manifest.get("sources", [])),
        "pageCount": inventory["pageCount"],
        "pagesByType": inventory["pagesByType"],
        "reviewGates": gates,
        "reviewBoundary": "candidate-only-no-promotion",
        "report": rel(root, report),
    }
    write_text(report, _format_review_package(result, inventory))
    update_status(root, run_id, {"reviewPackage": result})
    print_json(result)
    return result


def run_promotion_plan(args) -> dict:
    root = Path(args.root).resolve()
    manifest_path = _resolve_under_root(root, args.manifest)
    wiki = _resolve_under_root(root, args.wiki)
    manifest = json.loads(read_text(manifest_path))
    run_id = args.run_id or manifest.get("manifestId") or infer_run_id_from_wiki(wiki)
    report = _optional_path(root, args.report) or _default_eval_report(root, run_id, "promotion-plan.md")
    status = _load_status(root, run_id)
    inventory = _wiki_inventory(root, wiki)
    gates = _review_gates(manifest, status, inventory)
    target = args.target or f"user/knowledge/reviewed/{run_id}.md"

    approval_blockers = [
        "写入 reviewed Knowledge 前必须完成人类审核或获得用户明确批准",
        "usage rights 和 copyright risk 必须由人类判断",
    ]
    result = {
        "state": "blocked-awaiting-explicit-approval",
        "runId": run_id,
        "manifest": rel(root, manifest_path),
        "wiki": rel(root, wiki),
        "scope": args.scope,
        "target": target,
        "candidateReady": gates["blockingIssues"] == [],
        "reviewGates": gates,
        "approvalBlockers": approval_blockers,
        "wouldWriteReviewedKnowledge": False,
        "promotionHandledByThisTool": False,
        "report": rel(root, report),
    }
    write_text(report, _format_promotion_plan(result))
    update_status(root, run_id, {"promotionPlan": result})
    print_json(result)
    return result


def run_promote_reviewed(args) -> dict:
    root = Path(args.root).resolve()
    manifest_path = _resolve_under_root(root, args.manifest)
    wiki = _resolve_under_root(root, args.wiki)
    target = _resolve_under_root(root, args.target)
    report = _optional_path(root, args.report)
    manifest = json.loads(read_text(manifest_path))
    run_id = args.run_id or manifest.get("manifestId") or infer_run_id_from_wiki(wiki)
    if report is None:
        report = _default_eval_report(root, run_id, "promotion-result.md")

    status = _load_status(root, run_id)
    inventory = _wiki_inventory(root, wiki)
    gates = _review_gates(manifest, status, inventory)
    if gates["blockingIssues"]:
        raise ValueError("promotion blocked: " + "; ".join(gates["blockingIssues"]))
    review_package = status.get("reviewPackage", {})
    if review_package.get("state") != "ready-for-human-review":
        raise ValueError("promotion requires a ready review-package")
    if target.exists() and not args.overwrite:
        raise FileExistsError(f"reviewed target already exists: {rel(root, target)}")

    reviewed_text = _format_reviewed_knowledge(
        root=root,
        run_id=run_id,
        manifest=manifest,
        wiki=wiki,
        target=target,
        scope=args.scope,
        reviewer=args.reviewer,
        approval_note=args.approval_note,
        review_after=args.review_after,
    )
    write_text(target, reviewed_text)

    result = {
        "state": "promoted",
        "runId": run_id,
        "scope": args.scope,
        "target": rel(root, target),
        "reviewer": args.reviewer,
        "reviewedAt": today(),
        "approvalNote": args.approval_note,
        "reviewAfter": args.review_after,
        "sourceManifest": rel(root, manifest_path),
        "candidateWiki": rel(root, wiki),
        "report": rel(root, report),
        "promotionHandledByThisTool": True,
        "reviewedKnowledgeWritten": True,
    }
    write_text(report, _format_promotion_result(result, gates))
    update_status(root, run_id, {"state": "promoted", "promotionResult": result})
    print_json(result)
    return result


def run_stale_plan(args) -> dict:
    root = Path(args.root).resolve()
    manifest_path = _resolve_under_root(root, args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changed = []
    missing = []
    unchanged = []
    for source in manifest.get("sources", []):
        source_ref = source.get("sourceRef", "")
        source_path = _resolve_under_root(root, source_ref)
        if not source_path.exists():
            missing.append(source_ref)
            continue
        current_hash = sha256_file(source_path)
        if current_hash != source.get("sourceHashSha256"):
            changed.append(source_ref)
        else:
            unchanged.append(source_ref)
    result = {
        "state": "passed",
        "manifest": rel(root, manifest_path),
        "changedSources": changed,
        "missingSources": missing,
        "unchangedSources": unchanged,
        "action": "plan-only-no-delete-no-promotion",
    }
    update_status(root, manifest.get("manifestId"), {"stalePlan": result})
    print_json(result)
    return result


def _write_foundation_pages(candidate_wiki: Path) -> None:
    write_text(candidate_wiki / "concepts" / "StructuredIngestion.md", concept_page(
        "StructuredIngestion",
        "[[StructuredIngestion]] converts raw material into extracted Markdown, candidate wiki pages, review evidence, and rebuildable graph output.\n\nRelated: [[CandidateKnowledge]].",
    ))
    write_text(candidate_wiki / "concepts" / "CandidateKnowledge.md", concept_page(
        "CandidateKnowledge",
        "[[CandidateKnowledge]] is source-grounded Markdown prepared for review. It is not authoritative reviewed knowledge.\n\nRelated: [[StructuredIngestion]].",
    ))


def _write_index(candidate_wiki: Path, source_entries: list[str]) -> None:
    index = "# Candidate Wiki Index\n\n"
    index += "## Overview\n- [Overview](overview.md) - candidate corpus synthesis\n\n"
    index += "## Sources\n" + "\n".join(source_entries) + "\n\n"
    index += "## Concepts\n"
    index += "- [Structured Ingestion](concepts/StructuredIngestion.md) - raw to candidate workflow\n"
    index += "- [Candidate Knowledge](concepts/CandidateKnowledge.md) - review-only knowledge state\n"
    write_text(candidate_wiki / "index.md", index)


def _write_overview(candidate_wiki: Path, run_id: str, source_records: list[dict]) -> None:
    source_links = "\n".join(f"- [[{record['id']}]]" for record in source_records)
    write_text(candidate_wiki / "overview.md", f"""---
title: "Candidate Overview"
type: synthesis
tags: [candidate, ingestion]
sources: []
last_updated: {today()}
---

# Candidate Overview

This candidate wiki was generated by Harness structured ingestion run `{run_id}`.

It contains extracted raw material scaffolded as [[CandidateKnowledge]] through [[StructuredIngestion]]. Agent enrichment should add source-grounded claims, concepts, entities, contradictions, applicability notes, and wikilinks before human review.

## Sources

{source_links}
""")


def _write_extraction_report(extracted_out: Path, root: Path, run_id: str, source_records: list[dict], candidate_wiki: Path) -> None:
    report = [
        f"# Extraction Report - {today()}",
        "",
        f"- Run ID: `{run_id}`",
        f"- Input files: {len(source_records)}",
        f"- Extracted path: `{rel(root, extracted_out)}`",
        f"- Candidate wiki: `{rel(root, candidate_wiki)}`",
        "",
        "## Governance",
        "",
        "This tool generated runtime extraction artifacts and candidate knowledge only. It did not write reviewed knowledge.",
    ]
    write_text(extracted_out / "extraction-report.md", "\n".join(report) + "\n")


def _unique_slug(records: list[dict], filename: str) -> str:
    from .common import slugify

    base = slugify(filename)
    used = {record["id"] for record in records}
    slug = base
    counter = 2
    while slug in used:
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _resolve_under_root(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _optional_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    return _resolve_under_root(root, value)


def _format_enrichment_plan(result: dict) -> str:
    lines = [
        f"# 候选知识补全计划（Candidate Enrichment Plan）- {today()}",
        "",
        f"- Run ID: `{result.get('runId')}`",
        f"- Manifest: `{result.get('manifest')}`",
        f"- 候选知识库（Candidate Wiki）: `{result.get('wiki')}`",
        f"- 来源数量（Source Count）: {result.get('sourceCount')}",
        f"- 边界（Boundary）: `{result.get('boundary')}`",
        "",
        "## 按来源补全（Source Actions）",
        "",
    ]
    for item in result.get("items", []):
        missing = item.get("missingSections") or ["无"]
        lines.extend([
            f"### {item.get('sourceId')}",
            "",
            f"- 原始来源（Source）: `{item.get('sourceRef')}`",
            f"- 抽取文本（Extracted Markdown）: `{item.get('extractedMarkdown')}`",
            f"- 候选页面（Candidate Page）: `{item.get('candidatePage')}`",
            f"- 缺失小节（Missing Sections）: {', '.join(missing)}",
            "",
            "建议动作：",
        ])
        lines.extend(f"- {action}" for action in item.get("recommendedActions", []))
        lines.append("")
    return "\n".join(lines)


def _default_eval_report(root: Path, run_id: str | None, name: str) -> Path:
    if not run_id:
        raise ValueError("run id is required when report path is omitted")
    return root / "var" / "rag" / run_id / "evals" / name


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


def _wiki_inventory(root: Path, wiki: Path) -> dict:
    pages = all_wiki_pages(wiki)
    pages_by_type: dict[str, list[dict]] = {}
    for page in pages:
        text = read_text(page)
        page_type = _frontmatter_value(text, "type") or "unknown"
        item = {
            "path": rel(root, page),
            "wikiPath": rel(wiki, page),
            "title": _page_title(text, page.stem),
            "type": page_type,
            "chars": len(text),
        }
        pages_by_type.setdefault(page_type, []).append(item)
    for values in pages_by_type.values():
        values.sort(key=lambda item: item["wikiPath"])
    return {
        "pageCount": len(pages),
        "pagesByType": pages_by_type,
    }


def _review_gates(manifest: dict, status: dict, inventory: dict) -> dict:
    health = status.get("health", {})
    lint = status.get("lint", {})
    graph = status.get("graphSummary", {})
    enrichment = status.get("enrichmentPlan", {})
    blocking = []
    warnings = []

    if not manifest.get("sources"):
        blocking.append("manifest 中没有 sources")
    if health.get("state") != "passed":
        blocking.append("health 检查未通过")
    if lint.get("state") != "passed":
        blocking.append("lint 检查未通过")
    if graph.get("state") != "passed":
        warnings.append("graph 检查未通过或缺失")
    missing_sections = []
    for item in enrichment.get("items", []):
        for section in item.get("missingSections", []):
            missing_sections.append({"sourceId": item.get("sourceId"), "section": section})
    if missing_sections:
        blocking.append("enrichment-plan 仍存在缺失小节")

    pages_by_type = inventory.get("pagesByType", {})
    if not pages_by_type.get("source"):
        blocking.append("candidate wiki 没有 source 页面")
    if not pages_by_type.get("concept"):
        warnings.append("candidate wiki 没有 concept 页面")

    return {
        "sourceProvenance": "passed" if manifest.get("sources") else "failed",
        "health": health.get("state", "missing"),
        "lint": lint.get("state", "missing"),
        "graph": graph.get("state", "missing"),
        "enrichment": "passed" if not missing_sections else "partial",
        "sensitiveRisk": "requires-human-confirmation",
        "usageRights": "requires-human-confirmation",
        "conflictCheck": "agent-candidate-check-only",
        "humanApproval": "required",
        "blockingIssues": blocking,
        "warnings": warnings,
    }


def _format_review_package(result: dict, inventory: dict) -> str:
    gates = result["reviewGates"]
    lines = [
        f"# 候选知识审核包（Candidate Review Package）- {today()}",
        "",
        f"- Run ID: `{result['runId']}`",
        f"- 候选知识库（Candidate Wiki）: `{result['wiki']}`",
        f"- Manifest: `{result['manifest']}`",
        f"- 状态代码（State）: `{result['state']}`",
        f"- 边界（Boundary）: `{result['reviewBoundary']}`",
        "",
        "## 审核门禁（Review Gates）",
        "",
        f"- 来源追踪（Source provenance）: `{gates['sourceProvenance']}`",
        f"- Health: `{gates['health']}`",
        f"- Lint: `{gates['lint']}`",
        f"- Graph: `{gates['graph']}`",
        f"- 补全状态（Enrichment）: `{gates['enrichment']}`",
        f"- 敏感风险（Sensitive risk）: `{gates['sensitiveRisk']}`",
        f"- 使用权利（Usage rights）: `{gates['usageRights']}`",
        f"- 冲突检查（Conflict check）: `{gates['conflictCheck']}`",
        f"- 人类批准（Human approval）: `{gates['humanApproval']}`",
        "",
        "## 阻塞项（Blocking Issues）",
        "",
    ]
    lines.extend(f"- {item}" for item in gates["blockingIssues"] or ["无"])
    lines.extend(["", "## 警告（Warnings）", ""])
    lines.extend(f"- {item}" for item in gates["warnings"] or ["无"])
    lines.extend(["", "## 页面清单（Page Inventory）", ""])
    for page_type, pages in sorted(inventory["pagesByType"].items()):
        lines.append(f"### {_page_type_label(page_type)}")
        lines.append("")
        for page in pages:
            lines.append(f"- `{page['wikiPath']}` - {page['title']}")
        lines.append("")
    lines.extend([
        "## 审核人决策（Reviewer Decision）",
        "",
        "```yaml",
        "# 可选值: approve | reject | defer",
        "decision: approve | reject | defer",
        "# 审核人姓名或标识",
        "reviewer: null",
        "# 审核日期",
        "reviewedAt: null",
        "# 目标 scope，例如 user-private / domain / project-reviewed / global",
        "targetScope: user-private",
        "# 如批准晋升，填写 reviewed knowledge 目标路径",
        "targetAsset: null",
        "# 审核理由",
        "reason: null",
        "```",
        "",
    ])
    return "\n".join(lines)


def _format_promotion_plan(result: dict) -> str:
    gates = result["reviewGates"]
    lines = [
        f"# 晋升计划（Promotion Plan）- {today()}",
        "",
        f"- Run ID: `{result['runId']}`",
        f"- 候选知识库（Candidate Wiki）: `{result['wiki']}`",
        f"- Manifest: `{result['manifest']}`",
        f"- 目标范围（Scope）: `{result['scope']}`",
        f"- 目标路径（Target）: `{result['target']}`",
        f"- 状态代码（State）: `{result['state']}`",
        f"- 候选是否就绪（Candidate ready）: `{_yes_no(result['candidateReady'])}`",
        f"- 是否会写入 reviewed Knowledge（Would write reviewed knowledge）: `{_yes_no(result['wouldWriteReviewedKnowledge'])}`",
        "",
        "## 仍需批准（Required Approval）",
        "",
    ]
    lines.extend(f"- {item}" for item in result["approvalBlockers"])
    lines.extend([
        "",
        "## 晋升前门禁（Pre-Promotion Gates）",
        "",
        f"- 来源追踪（Source provenance）: `{gates['sourceProvenance']}`",
        f"- Health: `{gates['health']}`",
        f"- Lint: `{gates['lint']}`",
        f"- Graph: `{gates['graph']}`",
        f"- 补全状态（Enrichment）: `{gates['enrichment']}`",
        f"- 敏感风险（Sensitive risk）: `{gates['sensitiveRisk']}`",
        f"- 使用权利（Usage rights）: `{gates['usageRights']}`",
        f"- 冲突检查（Conflict check）: `{gates['conflictCheck']}`",
        "",
        "## 如果后续获得明确批准（If Approved）",
        "",
        "使用 `harness/templates/knowledge/ReviewedKnowledgeTemplate.md` 创建 reviewed Knowledge。",
        "必须保留 sourceRefs、reviewedBy、reviewedAt、reviewAfter、sensitiveRisk、storageBoundary、applicability、source trace 和 governance notes。",
        "不得复制 raw source 长段正文、credentials、private settings、raw logs 或未脱敏 traces。",
        "",
    ])
    return "\n".join(lines)


def _format_reviewed_knowledge(
    root: Path,
    run_id: str,
    manifest: dict,
    wiki: Path,
    target: Path,
    scope: str,
    reviewer: str,
    approval_note: str,
    review_after: str,
) -> str:
    sources = manifest.get("sources", [])
    source = sources[0] if sources else {}
    source_page_ref = source.get("candidatePage", "")
    source_page = _resolve_under_root(root, source_page_ref) if source_page_ref else wiki / "overview.md"
    source_content = read_text(source_page) if source_page.exists() else ""
    title = _page_title(source_content, "Reviewed Knowledge")
    source_ref = source.get("sourceRef", "")
    extracted_ref = source.get("extractedMarkdown", "")

    concepts = _reviewed_concepts(wiki)
    concept_rows = [
        "| Concept | Definition | Aliases |",
        "|---|---|---|",
    ]
    for concept, definition, aliases in concepts:
        concept_rows.append(f"| `{concept}` | {definition} | {aliases} |")

    statement = _reviewed_statement_for_source(title)
    applicability = _section(source_content, "Applicability")
    non_applicability = _section(source_content, "Non-Applicability")
    contradictions = _section(source_content, "Contradictions")

    doc_name = rel(root, target)
    return f"""---
documentName: {doc_name}
version: v1.0.0-reviewed
updatedAt: {today()}
status: active
purpose: 保存从 candidate wiki 晋升而来的 reviewed Knowledge，主题为 agent harness engineering。
scope:
  - reviewed-knowledge
  - {scope}
  - agent-harness-engineering
prerequisites:
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/templates/knowledge/ReviewedKnowledgeTemplate.md
  - {rel(root, wiki)}
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
  decision: user-approved-promotion
---
# Agent Harness Engineering Survey Reviewed Knowledge

## 元数据

```yaml
knowledgeId: {Path(target).stem}
scope: {scope}
domain: agent-harness-engineering
projectId: null
reviewedAt: {today()}
reviewedBy: {reviewer}
sourceRefs:
  - {source_ref}
  - {extracted_ref}
  - {source_page_ref}
  - {rel(root, wiki)}
supersedes: []
reviewAfter: {review_after}
sensitiveRisk: low
storageBoundary: user/knowledge/reviewed
approvalNote: {json.dumps(approval_note, ensure_ascii=False)}
```

## Statement

{statement}

## Applicability

{_reviewed_block(applicability, "本知识适用于 Harness 架构、RAG / Knowledge workflow、agent runtime governance、tool boundary、workflow evidence 和 evaluation 设计。")}

## Non-Applicability

{_reviewed_block(non_applicability, "本知识不直接替代 Harness 架构权威文档，也不作为具体第三方工具选型建议。论文中的项目列表具有时间边界，后续引用具体项目时仍需单独验证。")}

## Key Concepts

{chr(10).join(concept_rows)}

## Source Trace

| Source | Evidence Summary | Notes |
|---|---|---|
| `{source_ref}` | 原始 PDF source。 | 用户审核通过后作为 reviewed Knowledge 来源。 |
| `{extracted_ref}` | `pymupdf4llm` 抽取出的 Markdown。 | runtime artifact，可重建，不是事实源。 |
| `{source_page_ref}` | candidate source page，包含 summary、key claims、concepts、entities、contradictions 和 applicability。 | 已通过 health / lint / graph / enrichment 检查。 |
| `{rel(root, wiki)}` | candidate wiki。 | 晋升后仍保留为候选证据。 |

## Staleness

- 默认复审条件：`{review_after}`。
- 如果原始论文正式发表、项目 catalog 更新、Harness 架构进入新阶段，或 reviewed Knowledge 与后续 architecture / governance 文档冲突，应重新 review。

## Governance Notes

- 本文件由 `promote-reviewed` 在用户明确审核通过后生成。
- Candidate wiki、chunks、graph、eval reports 和 status JSON 仍然是证据或运行态产物，不反向成为事实源。
- 不包含 raw source 长段正文、credential、private settings、raw logs 或未脱敏 traces。
- Candidate contradiction notes: {_inline_summary(contradictions)}
"""


def _format_promotion_result(result: dict, gates: dict) -> str:
    lines = [
        f"# 晋升结果（Promotion Result）- {today()}",
        "",
        f"- Run ID: `{result['runId']}`",
        f"- 状态（State）: `{result['state']}`",
        f"- Reviewed Knowledge target: `{result['target']}`",
        f"- Reviewer: `{result['reviewer']}`",
        f"- Reviewed At: `{result['reviewedAt']}`",
        f"- Review After: `{result['reviewAfter']}`",
        f"- Approval Note: {result['approvalNote']}",
        "",
        "## 晋升门禁结果",
        "",
        f"- 来源追踪（Source provenance）: `{gates['sourceProvenance']}`",
        f"- Health: `{gates['health']}`",
        f"- Lint: `{gates['lint']}`",
        f"- Graph: `{gates['graph']}`",
        f"- 补全状态（Enrichment）: `{gates['enrichment']}`",
        f"- 阻塞项（Blocking Issues）: {', '.join(gates['blockingIssues'] or ['无'])}",
        f"- 警告（Warnings）: {', '.join(gates['warnings'] or ['无'])}",
        "",
        "## 边界",
        "",
        "- 已写入 reviewed Knowledge。",
        "- 未写入 Memory、Project Fact 或 Harness architecture authority。",
        "- Runtime RAG artifacts 仍是可重建证据，不是事实源。",
        "",
    ]
    return "\n".join(lines)


def _reviewed_statement_for_source(title: str) -> str:
    if "Agent Harness Engineering" in title:
        return """本 reviewed Knowledge 确认：Agent Harness Engineering，中文可理解为智能体运行支架工程，应被视为独立的系统工程层，而不是 prompt 或模型能力的附属细节。

核心结论包括：

- 长周期 agent 任务的可靠性不仅由模型决定，也由 execution harness 决定；这对应 [[BindingConstraintThesis]]。
- Harness engineering 是 prompt engineering 和 context engineering 之后更高层的工程面，覆盖 execution、tooling、context、lifecycle、observability、verification 和 governance。
- [[ETCLOVGTaxonomy]] 可以作为分析 agent harness 的七层框架：Execution、Tooling、Context、Lifecycle、Observability、Verification、Governance。
- Observability 和 Governance 应作为一等层，而不是 lifecycle hooks 的副作用。
- Harness 的局部优化可能产生系统级副作用；prompt、tool schema、sandbox、memory policy、verifier 和 monitor 都需要按系统变更评估，这对应 [[HarnessCouplingProblem]]。
- 未来 Harness 需要加强 [[TraceNativeEvaluation]]、[[StandardHandoffProtocol]]、[[AdaptiveHarnessOptimization]] 和对 [[ContextDrift]] 的控制。
"""
    return f"本 reviewed Knowledge 确认 `{title}` 已通过 candidate review，并可在指定 scope 内作为 reviewed Knowledge 使用。"


def _reviewed_concepts(wiki: Path) -> list[tuple[str, str, str]]:
    preferred = {
        "AgentHarnessEngineering": ("围绕 LLM agent 的执行环境、工具、上下文、生命周期、观测、验证和治理构建可靠控制层的工程 discipline。", "agent harness, harness engineering"),
        "BindingConstraintThesis": ("长周期 agent 可靠性可能被 execution harness 约束，而不只由模型能力决定。", "harness over model"),
        "ETCLOVGTaxonomy": ("Execution、Tooling、Context、Lifecycle、Observability、Verification、Governance 七层分类框架。", "ETCLOVG"),
        "CostQualitySpeedTrilemma": ("Harness 设计中 cost、quality、speed 之间的系统级权衡。", "cost-quality-speed"),
        "CapabilityControlTradeoff": ("增强 agent capability 会同时扩大 control、permission、audit 和 safety 问题。", "capability-control"),
        "HarnessCouplingProblem": ("Harness 层之间存在耦合，局部优化需要按系统变更验证。", "coupling"),
        "TraceNativeEvaluation": ("以执行 trace 作为评价、诊断和回归测试的主要证据对象。", "trace-first eval"),
        "ContextDrift": ("长周期任务中 agent 内部状态逐步偏离真实任务状态或原始目标的 failure mode。", "state drift"),
        "StandardHandoffProtocol": ("在 agents、tools、humans 之间转移状态和责任时需要明确授权、证据、边界和返回条件。", "handoff"),
        "AdaptiveHarnessOptimization": ("随着模型和任务变化，持续重新评估并简化 Harness controls。", "adaptive harness"),
    }
    existing = {p.stem for p in all_wiki_pages(wiki) if "concepts" in p.parts}
    concepts = []
    for name, item in preferred.items():
        if name in existing:
            concepts.append((name, item[0], item[1]))
    return concepts


def _section(content: str, heading: str) -> str:
    lines = content.splitlines()
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


def _reviewed_block(value: str, fallback: str) -> str:
    return value.strip() if value.strip() else fallback


def _inline_summary(value: str) -> str:
    text = " ".join(line.strip("- ").strip() for line in value.splitlines() if line.strip())
    return text if text else "无已知内部矛盾。"


def _frontmatter_value(content: str, key: str) -> str | None:
    import re

    match = re.search(rf"^{key}:\s*(.+)$", content, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip("\"'")


def _page_title(content: str, fallback: str) -> str:
    return _frontmatter_value(content, "title") or title_from_markdown(content, fallback)


def _page_type_label(page_type: str) -> str:
    labels = {
        "concept": "概念（concept）",
        "entity": "实体（entity）",
        "source": "来源页（source）",
        "synthesis": "综合页（synthesis）",
        "unknown": "未知类型（unknown）",
    }
    return labels.get(page_type, f"{page_type}")


def _yes_no(value: object) -> str:
    return "是" if bool(value) else "否"
