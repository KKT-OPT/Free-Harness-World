from __future__ import annotations

import json
import re
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

    raw_domain = safe_run_id(getattr(args, "raw_domain", None) or run_id)
    raw_out = root / "user" / "knowledge" / "raw" / raw_domain
    extracted_out = root / "var" / "rag" / run_id / "extracted"
    candidate_wiki = root / "user" / "knowledge" / "candidate" / run_id / "wiki"
    eval_out = root / "var" / "rag" / run_id / "evals"
    graph_out = root / "var" / "rag" / run_id / "graph"
    status_out = root / "var" / "logs" / f"{run_id}.json"

    normalized_out = raw_out / "normalized"

    for path in [extracted_out, candidate_wiki, eval_out, graph_out, status_out.parent]:
        path.mkdir(parents=True, exist_ok=True)

    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = lambda value, **_: value  # type: ignore

    source_records = []
    blocked_sources = []
    seen_body_hashes: dict[str, str] = {}
    chunk_lines = []
    source_entries = []
    log_entries = []
    extraction_config = _effective_extraction_config(args)
    tag_vocabulary = {
        "mode": getattr(args, "tag_vocabulary_mode", "default"),
        "allowedTags": sorted(set(getattr(args, "allowed_tags", []) or [])),
    }

    for source in tqdm(input_files, desc="Converting raw"):
        source = source.resolve()
        try:
            markdown, converter = convert_file(source)
        except Exception as exc:
            blocked_sources.append(_source_gate_block(source, "incompatible-type", str(exc)))
            continue

        source_gate = _source_gate(source, markdown, seen_body_hashes)
        if source_gate["state"] != "accepted":
            blocked_sources.append(source_gate)
            continue

        slug = _unique_slug(source_records, f"{source.stem}-{source_gate['sourceFingerprint']}")
        if args.copy_raw:
            raw_target = raw_out / source.name
            raw_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, raw_target)
            source_ref = rel(root, raw_target)
        else:
            source_ref = rel(root, source)

        title = title_from_markdown(markdown, source.stem.replace("-", " ").title())
        extracted_path = extracted_out / f"{slug}.md"
        write_text(extracted_path, markdown)
        runtime_extracted_ref = rel(root, extracted_path)
        if args.copy_raw:
            normalized_out.mkdir(parents=True, exist_ok=True)
            normalized_path = normalized_out / f"{slug}.md"
            write_text(normalized_path, markdown)
            extracted_ref = rel(root, normalized_path)
        else:
            normalized_path = None
            extracted_ref = runtime_extracted_ref

        preview = _candidate_preview(markdown, extraction_config)
        source_wiki_path = candidate_wiki / "sources" / f"{slug}.md"
        write_text(source_wiki_path, source_page(title, source_ref, extracted_ref, preview))
        source_entries.append(f"- [{title}](sources/{slug}.md) - candidate source page")
        log_entries.append(f"## [{today()}] ingest | {title}\n\nScaffolded candidate page from `{source_ref}`.")

        chunks = split_chunks(markdown, extraction_config["effectiveMaxChunkChars"])
        batch_ids = _chunk_batch_ids(len(chunks), extraction_config["batchStrategy"], extraction_config["extractionGranularity"])
        for index, chunk in enumerate(chunks, 1):
            chunk_lines.append(json.dumps({
                "chunkId": f"{slug}:{index:03d}",
                "sourceId": slug,
                "batchId": batch_ids[index - 1],
                "text": chunk,
                "provenance": {
                    "sourceRef": source_ref,
                    "extractedPath": extracted_ref,
                    "runtimeExtractedPath": runtime_extracted_ref,
                    "tool": converter,
                },
            }, ensure_ascii=False))

        source_records.append({
            "id": slug,
            "sourceRef": source_ref,
            "sourceHashSha256": sha256_file(source),
            "sourceFingerprint": source_gate["sourceFingerprint"],
            "sourceGate": source_gate,
            "extractedMarkdown": extracted_ref,
            "runtimeExtractedMarkdown": runtime_extracted_ref,
            "normalizedMarkdown": rel(root, normalized_path) if normalized_path else None,
            "outputHashSha256": sha256_text(markdown),
            "bodyHashSha256": source_gate["bodyHashSha256"],
            "converter": converter,
            "candidatePage": rel(root, source_wiki_path),
            "extraction": extraction_config,
            "tagVocabulary": tag_vocabulary,
            "chunkCount": len(chunks),
            "batchCount": len(set(batch_ids)),
        })

    if not source_records:
        write_text(extracted_out / "blocked-sources.json", json.dumps(blocked_sources, indent=2, ensure_ascii=False))
        raise ValueError("all sources were blocked by source gate: " + "; ".join(f"{item['sourceRef']}={item['reason']}" for item in blocked_sources))

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
        "blockedSources": blocked_sources,
        "extraction": extraction_config,
        "tagVocabulary": tag_vocabulary,
        "sourceGate": {
            "blockedSourceCount": len(blocked_sources),
            "acceptedSourceCount": len(source_records),
            "rules": [
                "empty-file",
                "frontmatter-only",
                "incompatible-type",
                "duplicate-body-hash",
            ],
        },
        "outputs": {
            "rawCopy": rel(root, raw_out) if args.copy_raw else None,
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
        "blockedInputCount": len(blocked_sources),
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


def _effective_extraction_config(args) -> dict:
    granularity = (getattr(args, "extraction_granularity", "standard") or "standard").strip().lower()
    if granularity not in {"fine", "standard", "coarse", "minimal", "custom"}:
        granularity = "standard"

    profiles = {
        "fine": {"maxChunkChars": 2000, "entityCap": 40, "conceptCap": 24, "previewLineLimit": 32, "previewCharLimit": 2400},
        "standard": {"maxChunkChars": 4000, "entityCap": 24, "conceptCap": 16, "previewLineLimit": 18, "previewCharLimit": 1400},
        "coarse": {"maxChunkChars": 8000, "entityCap": 12, "conceptCap": 8, "previewLineLimit": 12, "previewCharLimit": 1000},
        "minimal": {"maxChunkChars": 12000, "entityCap": 5, "conceptCap": 4, "previewLineLimit": 8, "previewCharLimit": 700},
        "custom": {"maxChunkChars": getattr(args, "max_chunk_chars", 4000), "entityCap": None, "conceptCap": None, "previewLineLimit": 18, "previewCharLimit": 1400},
    }
    profile = dict(profiles[granularity])
    explicit_max = int(getattr(args, "max_chunk_chars", profile["maxChunkChars"]) or profile["maxChunkChars"])
    if granularity == "custom" or explicit_max != 4000:
        profile["maxChunkChars"] = max(500, explicit_max)
    explicit_entity_cap = getattr(args, "entity_cap", None)
    explicit_concept_cap = getattr(args, "concept_cap", None)
    if explicit_entity_cap is not None:
        profile["entityCap"] = int(explicit_entity_cap)
    if explicit_concept_cap is not None:
        profile["conceptCap"] = int(explicit_concept_cap)
    batch_strategy = (getattr(args, "batch_strategy", "single-pass-local-conversion") or "single-pass-local-conversion").strip()
    return {
        "extractionGranularity": granularity,
        "entityCap": profile["entityCap"],
        "conceptCap": profile["conceptCap"],
        "batchStrategy": batch_strategy,
        "effectiveMaxChunkChars": int(profile["maxChunkChars"]),
        "previewLineLimit": int(profile["previewLineLimit"]),
        "previewCharLimit": int(profile["previewCharLimit"]),
    }


def _candidate_preview(markdown: str, extraction_config: dict) -> str:
    line_limit = int(extraction_config.get("previewLineLimit") or 18)
    char_limit = int(extraction_config.get("previewCharLimit") or 1400)
    preview = "\n".join(markdown.strip().splitlines()[:line_limit]).strip()
    if len(preview) > char_limit:
        clipped = preview[:char_limit]
        preview = clipped.rsplit(" ", 1)[0] if " " in clipped else clipped
        preview = preview.rstrip() + "..."
    return preview


def _chunk_batch_ids(chunk_count: int, batch_strategy: str, granularity: str) -> list[str]:
    if chunk_count <= 0:
        return []
    normalized = (batch_strategy or "").strip().lower()
    if normalized in {"source-per-batch", "single-source"}:
        return ["batch-001" for _ in range(chunk_count)]
    if normalized in {"balanced-batches", "balanced"}:
        target_batches = {"fine": 4, "standard": 3, "coarse": 2, "minimal": 1, "custom": 3}.get(granularity, 3)
        batch_count = max(1, min(target_batches, chunk_count))
        return [f"batch-{((index * batch_count) // chunk_count) + 1:03d}" for index in range(chunk_count)]
    return [f"batch-{index:03d}" for index in range(1, chunk_count + 1)]


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


def _source_gate(source: Path, markdown: str, seen_body_hashes: dict[str, str]) -> dict:
    fingerprint = sha256_text(source.as_posix().lower())[:12]
    body = _strip_markdown_frontmatter(markdown).strip()
    body_hash = sha256_text(re.sub(r"\s+", "\n", body).strip())
    source_ref = source.as_posix()
    if not markdown.strip():
        return _source_gate_block(source, "empty-file", "converted markdown is empty", fingerprint=fingerprint, body_hash=body_hash)
    if not body:
        return _source_gate_block(source, "frontmatter-only", "converted markdown has no body after frontmatter", fingerprint=fingerprint, body_hash=body_hash)
    duplicate_of = seen_body_hashes.get(body_hash)
    if duplicate_of:
        return _source_gate_block(
            source,
            "duplicate-body-hash",
            f"same body hash as {duplicate_of}",
            fingerprint=fingerprint,
            body_hash=body_hash,
            duplicate_of=duplicate_of,
        )
    seen_body_hashes[body_hash] = source_ref
    return {
        "state": "accepted",
        "sourceRef": source_ref,
        "reason": "accepted",
        "sourceFingerprint": fingerprint,
        "bodyHashSha256": body_hash,
        "duplicateBodyHashOf": None,
    }


def _source_gate_block(
    source: Path,
    reason: str,
    detail: str,
    *,
    fingerprint: str | None = None,
    body_hash: str | None = None,
    duplicate_of: str | None = None,
) -> dict:
    return {
        "state": "blocked",
        "sourceRef": source.as_posix(),
        "reason": reason,
        "detail": detail,
        "sourceFingerprint": fingerprint or sha256_text(source.as_posix().lower())[:12],
        "bodyHashSha256": body_hash,
        "duplicateBodyHashOf": duplicate_of,
    }


def _strip_markdown_frontmatter(markdown: str) -> str:
    return re.sub(r"(?s)^---\s*\n.*?\n---\s*", "", markdown).strip()


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
    runtime_extracted_ref = source.get("runtimeExtractedMarkdown", "")
    domain = _reviewed_domain_from_target(root, target)
    tags = _reviewed_domain_tags(domain)
    page_title = _reviewed_page_title(title, domain)

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
knowledgeRole: authoritative
authoritative: true
tags: [{", ".join(tags)}]
purpose: {_reviewed_purpose(title, domain)}
scope:
  - reviewed-knowledge
  - {scope}
  - {domain}
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
# {page_title}

## 元数据

```yaml
knowledgeId: {Path(target).stem}
knowledgeRole: authoritative
authoritative: true
scope: {scope}
domain: {domain}
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
storageBoundary: user/knowledge/reviewed/{domain}
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
| `{extracted_ref}` | 原始材料转换后的 normalized Markdown。 | 长期保存在 raw domain，作为原始材料的可读派生版本；不是 reviewed 结论本身。 |
| `{source_page_ref}` | candidate source page，包含 summary、key claims、concepts、entities、contradictions 和 applicability。 | 已通过 health / lint / graph / enrichment 检查。 |
| `{rel(root, wiki)}` | candidate wiki。 | 晋升后仍保留为候选证据。 |
{f"| `{runtime_extracted_ref}` | 运行态抽取副本。 | 仅用于复现本次 pipeline；不得作为长期 Source Trace。 |" if runtime_extracted_ref and runtime_extracted_ref != extracted_ref else ""}

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


def _reviewed_domain_from_target(root: Path, target: Path) -> str:
    try:
        relative = target.resolve().relative_to((root / "user" / "knowledge" / "reviewed").resolve())
        if relative.parts:
            return safe_run_id(relative.parts[0])
    except ValueError:
        pass
    return "reviewed-knowledge"


def _reviewed_domain_tags(domain: str) -> list[str]:
    if domain == "llm-agent-externalization":
        return ["llm-agent", "externalization", "memory", "skill", "protocol", "harness-engineering", "governance"]
    if domain == "agent-harness-engineering":
        return ["agent-harness", "harness-architecture", "agent-evaluation", "agent-governance", "trace-native", "workflow-evidence", "knowledge-governance"]
    return [domain]


def _reviewed_page_title(title: str, domain: str) -> str:
    if domain == "llm-agent-externalization":
        return "LLM Agent 外部化综述 Reviewed Knowledge"
    if domain == "agent-harness-engineering":
        return "Agent Harness Engineering 综述 Reviewed Knowledge"
    return f"{title} Reviewed Knowledge"


def _reviewed_purpose(title: str, domain: str) -> str:
    if domain == "llm-agent-externalization":
        return "保存 Externalization in LLM Agents 相关原始材料晋升后的 reviewed Knowledge。"
    if domain == "agent-harness-engineering":
        return "保存 Agent Harness Engineering A Survey 晋升后的 reviewed Knowledge。"
    return f"保存从 candidate wiki 晋升而来的 reviewed Knowledge：{title}。"


def _reviewed_statement_for_source(title: str) -> str:
    if any(term in title.lower() for term in ["externalization", "memory", "skills", "protocols"]):
        return """本 reviewed Knowledge 确认：LLM agent 的长期能力正在从“模型内部能力”转向“模型 + 外部认知基础设施”的系统能力。论文使用 externalization 视角解释这一变化：memory 外部化跨时间状态，skills 外部化程序性专长，protocols 外部化交互结构，harness engineering 则把这些外部化能力组织为可执行、可观测、可验证、可治理的系统。

核心结论包括：

- 评价 LLM agent 不能只看单次模型输出质量，还要看 memory、skill、protocol、tool interface 和 harness control 共同构成的系统可靠性。
- Memory 的价值不只是“保存更多上下文”，而是把 agent state 从易丢失的 prompt context 转成可追踪、可检索、可过期、可删除、可治理的外部状态。
- Skill 的价值不只是“提示词模板”，而是把 procedure、decision heuristic、tool-use pattern 和 normative constraint 包装成可发现、可调用、可复用、可版本化的能力单元。
- Protocol 的价值是把 agent-tool、agent-agent、human-agent 交互从隐式对话变成显式 message contract、handoff rule、approval boundary 和 responsibility transfer。
- Harness engineering 是 memory、skills 和 protocols 的统一执行层，负责 agent loop、sandbox、tool binding、human oversight、state transition、trace、evaluation、deployment feedback 和 governance。
- 这份材料应与既有 [[agent-harness-engineering-survey|AgentHarnessEngineering]] 知识关联：前者强调外部化机制，后者强调 harness taxonomy、trace-native evaluation 和 governance boundary。

## Source Overview

原始材料是一篇关于 LLM agent externalization 的综述。它解释 agent engineering 为什么从 model weights、prompt/context engineering，进一步走向 memory、skills、protocols 和 harness infrastructure。论文把这些机制统一为 external cognitive infrastructure：把模型难以稳定内部完成的状态保持、程序执行、交互协调和治理约束，转移到外部结构中管理。

## Core Framework

| 层级 | 外部化对象 | 主要作用 | 治理关注点 |
|---|---|---|---|
| Memory | state across time | 保存任务状态、历史证据、环境变化和长期上下文 | provenance、retention、staleness、privacy、deletion |
| Skills | procedural expertise | 封装可复用步骤、工具使用模式、决策启发式和规范性约束 | versioning、review、side effect、capability boundary |
| Protocols | interaction structure | 规范 agent 与工具、用户、其他 agent 的消息、授权、移交和反馈 | message contract、handoff、approval、accountability |
| Harness | governed execution | 编排 memory、skills、protocols、tools 和 agent loop | trace、verification、lifecycle、policy、rollback |

## Knowledge Implications

- Reviewed Knowledge 应表达原材料主线、概念、方法和边界，而不是只支持关键词命中。
- normalized Markdown 应作为 raw source derivative 长期保存在 `raw/<domain>/normalized/`；`var/rag` 只能保存可清理的运行态副本。
- Concept page 是知识图谱节点，不能替代 source-level reviewed page；复杂问题应优先阅读 source-level reviewed page。"""
    if "Agent Harness Engineering" in title:
        return """本 reviewed Knowledge 确认：Agent Harness Engineering，中文可理解为智能体运行支架工程，应被视为独立的系统工程层，而不是 prompt 或模型能力的附属细节。

核心结论包括：

- 长周期 agent 任务的可靠性不仅由模型决定，也由 execution harness 决定；这对应 [[BindingConstraintThesis]]。
- Harness engineering 是 prompt engineering 和 context engineering 之后更高层的工程面，覆盖 execution、tooling、context、lifecycle、observability、verification 和 governance。
- [[ETCLOVGTaxonomy]] 可以作为分析 agent harness 的七层框架：Execution、Tooling、Context、Lifecycle、Observability、Verification、Governance。
- Observability 和 Governance 应作为一等层，而不是 lifecycle hooks 的副作用。
- Harness 的局部优化可能产生系统级副作用；prompt、tool schema、sandbox、memory policy、verifier 和 monitor 都需要按系统变更评估，这对应 [[HarnessCouplingProblem]]。
- 未来 Harness 需要加强 [[TraceNativeEvaluation]]、[[StandardHandoffProtocol]]、[[AdaptiveHarnessOptimization]] 和对 [[ContextDrift]] 的控制。

## Source Overview

原始材料是一篇关于 Agent Harness Engineering 的综述。其核心判断是：生产环境中 LLM agent 的可靠性往往被包裹模型的 execution harness 所约束，而不仅由基础模型能力决定。论文把这一判断展开为三条主线：agent harness 是独立系统层；ETCLOVG 七层 taxonomy 能描述 harness 的关键组成；开源项目生态和生产实践显示 observability、verification 和 governance 已经成为 harness 工程不可缺少的显式能力。

## Core Framework

| 层级 | 关注对象 | 关键问题 |
|---|---|---|
| Execution | runtime、sandbox、deployment | agent 在什么环境中执行，如何隔离和限制副作用 |
| Tooling | tool interface、protocol、selection | agent 能调用什么工具，工具描述和返回证据如何被治理 |
| Context | prompt、memory、session state | agent 如何维护短期、中期、长期上下文，如何控制 context drift |
| Lifecycle | loop、orchestration、handoff | agent 任务如何启动、推进、暂停、交接、结束和回滚 |
| Observability | trace、monitoring、feedback | agent 行为如何被记录、解释、诊断和复盘 |
| Verification | eval、regression、judgement | agent 结果如何被验证，失败如何归因 |
| Governance | permission、policy、audit、review | agent 能力如何被授权、审计、约束和持续治理 |

## Knowledge Implications

- Workflow Evidence、Report、Skill、Knowledge、Memory 和 RAG Index 不能混为一类资产；它们承担不同治理职责。
- Trace-native evaluation 应成为真实项目验证和回归测试的主要证据对象，而不是只保存一段运行日志。
- Standard handoff protocol 应明确任务状态、授权边界、证据链、下一步责任和回退条件。
- Harness coupling problem 表明局部优化可能改变整体系统行为，因此工具、Skill、Memory、Knowledge、Governance 的改动都需要门禁和回归验证。
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
        "LLMAgentExternalization": ("LLM agent 的 durable capability 分布在 model calls、memory、skills、protocols、tools 和 harness controls 组成的系统中。", "LLM agent externalization, agent externalization"),
        "ExternalizedMemory": ("将 agent state 保存到 prompt 之外，使后续动作能使用有来源、可治理、可过期的上下文。", "agent memory, external memory"),
        "SkillLibrary": ("将可复用 procedure、tool-use pattern、decision heuristic 和约束封装为可调用能力包。", "skills, reusable procedures"),
        "ProtocolMediatedCoordination": ("通过协议让 tool、human 或 multi-agent handoff 显式化、可审计。", "agent protocol, handoff protocol"),
        "HarnessEngineering": ("为 agents 和外部化能力提供 execution、observation、verification、lifecycle 和 governance 控制层。", "agent harness engineering, runtime harness"),
        "StatePersistence": ("定义哪些状态应跨 turn、run、user 或 agent 保留，以及如何过期、删除和追踪。", "persistent state, durable state"),
        "ToolInterfaceBoundary": ("治理 agent 可调用工具、返回证据、副作用、失败处理和审计边界。", "tool boundary, tool contract"),
        "GovernedExternalState": ("将 authoritative knowledge、candidate material、runtime indexes、memory 和 project facts 分开治理。", "external state governance, governed state"),
    }
    existing_pages = {p.stem: p for p in all_wiki_pages(wiki) if "concepts" in p.parts}
    existing = set(existing_pages)
    concepts = []
    for name, item in preferred.items():
        if name in existing:
            concepts.append((name, item[0], item[1]))
    for name, page in sorted(existing_pages.items()):
        if name in preferred or name in {"CandidateKnowledge", "StructuredIngestion"}:
            continue
        text = read_text(page)
        definition = _section(text, "Candidate Definition") or _first_non_heading_line(text) or "Candidate concept promoted after review."
        concepts.append((name, definition, name))
    return concepts


def _first_non_heading_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", "---")) and ":" not in stripped[:24]:
            return stripped
    return ""


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
