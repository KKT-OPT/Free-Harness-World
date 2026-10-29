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
    normalization_ref = getattr(args, "normalization_manifest", None)
    normalized_sources = {}
    if normalization_ref:
        from .pdf_normalize import under
        normalization_file = under(root, normalization_ref)
        normalization = json.loads(read_text(normalization_file))
        for item in normalization.get("sources", []):
            normalized = under(root, item["normalizedMarkdown"], root / "user/knowledge/raw")
            original = under(root, item["sourceRef"], root / "user/knowledge/raw")
            if not item.get("candidateAllowed"):
                raise ValueError("normalization still requires OCR; candidate ingest blocked")
            if sha256_file(normalized) != item["normalizedHashSha256"] or sha256_file(original) != item["sourceHashSha256"]:
                raise ValueError("normalization provenance hash changed")
            normalized_sources[normalized] = item
        if not normalized_sources:
            raise ValueError("normalization manifest has no sources")
        if args.copy_raw:
            raise ValueError("normalized inputs are already in raw; do not use --copy-raw")
    input_files = collect_inputs([str(root / p) if not Path(p).is_absolute() else p for p in args.inputs]) if args.inputs else list(normalized_sources)
    if not input_files:
        raise ValueError("ingest requires inputs or a normalization manifest")
    if normalized_sources and any(p.resolve() not in normalized_sources for p in input_files):
        raise ValueError("input is not covered by normalization manifest")

    raw_domain = getattr(args, "raw_domain", None) or run_id
    if Path(raw_domain).name != raw_domain or raw_domain.startswith("."):
        raise ValueError("raw domain must be a single domain name")
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
            if raw_target.exists() and sha256_file(raw_target) != sha256_file(source):
                raw_target = raw_out / source_gate["sourceFingerprint"] / source.name
            raw_target.parent.mkdir(parents=True, exist_ok=True)
            if raw_target.resolve() != source.resolve():
                shutil.copy2(source, raw_target)
            source_ref = rel(root, raw_target)
        else:
            source_ref = rel(root, source)

        title = title_from_markdown(markdown, source.stem.replace("-", " ").title())
        extracted_path = extracted_out / f"{slug}.md"
        write_text(extracted_path, markdown)
        runtime_extracted_ref = rel(root, extracted_path)
        normalized_record = normalized_sources.get(source)
        if normalized_record:
            normalized_path = source
            extracted_ref = rel(root, source)
            source_ref = normalized_record["sourceRef"]
            converter = "page-preserving-normalized-pdf"
        elif args.copy_raw:
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
        log_entries.append(f"## [{today()}] ingest | {title}\n\nSource ID: `{slug}`. Scaffolded candidate page from `{source_ref}`.")

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
            "sourceHashSha256": normalized_record["sourceHashSha256"] if normalized_record else sha256_file(source),
            "sourceFingerprint": source_gate["sourceFingerprint"],
            "sourceGate": source_gate,
            "extractedMarkdown": extracted_ref,
            "runtimeExtractedMarkdown": runtime_extracted_ref,
            "normalizedMarkdown": rel(root, normalized_path) if normalized_path else None,
            "normalizedHashSha256": sha256_file(normalized_path) if normalized_path else None,
            "normalizationManifest": rel(root, normalization_file) if normalized_record else None,
            "normalizationManifestHashSha256": sha256_file(normalization_file) if normalized_record else None,
            "qualityState": normalized_record.get("qualityState") if normalized_record else None,
            "pageCount": normalized_record.get("pageCount", 0) if normalized_record else 0,
            "pages": normalized_record.get("pages", []) if normalized_record else [],
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
    from .promotion import bindings_from_args, review_snapshot, source_issues, validate_draft
    root = Path(args.root).resolve()
    manifest_path = _resolve_under_root(root, args.manifest)
    wiki = _resolve_under_root(root, args.wiki)
    manifest = json.loads(read_text(manifest_path))
    run_id = args.run_id or manifest.get("manifestId") or infer_run_id_from_wiki(wiki)
    report = _optional_path(root, args.report) or _default_eval_report(root, run_id, "review-package.md")
    # Refresh structural checks on the bytes being reviewed, rather than trust a
    # status JSON from an earlier candidate revision.
    health_wiki(root, wiki, _default_eval_report(root, run_id, "health-report.md"), run_id=run_id)
    lint_wiki(root, wiki, _default_eval_report(root, run_id, "lint-report.md"), run_id=run_id)
    build_graph(wiki, root / "var/rag" / run_id / "graph", _default_eval_report(root, run_id, "graph-report.md"), root=root, run_id=run_id)
    status = _load_status(root, run_id)
    inventory = _wiki_inventory(root, wiki)
    gates = _review_gates(manifest, status, inventory)

    gates["blockingIssues"].extend(source_issues(root, manifest))
    for source in manifest.get("sources", []):
        candidate = _resolve_under_root(root, source.get("candidatePage", "missing"))
        content = read_text(candidate) if candidate.is_file() else ""
        for name in ("Candidate Summary", "Key Claims", "Entities", "Concepts", "Contradictions", "Applicability", "Review Checklist"):
            if not _section(content, name):
                gates["blockingIssues"].append(f"{source['id']} missing candidate section: {name}")
        if "Agent review required" in content:
            gates["blockingIssues"].append(f"{source['id']} still contains scaffold text")
    bindings = bindings_from_args(root, manifest, args)
    by_id = {source["id"]: source for source in manifest.get("sources", [])}
    for item in bindings:
        try:
            validate_draft(root, by_id[item["sourceId"]], _resolve_under_root(root, item["target"]), read_text(_resolve_under_root(root, item["draft"])))
        except (ValueError, OSError) as exc:
            gates["blockingIssues"].append(f"draft {item['sourceId']}: {exc}")

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
        "bindings": bindings,
        "reviewInputHashSha256": review_snapshot(root, manifest_path, wiki, bindings),
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
    from .promotion import promote
    return promote(args)


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
        blocking.append("graph 检查未通过或缺失")
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
