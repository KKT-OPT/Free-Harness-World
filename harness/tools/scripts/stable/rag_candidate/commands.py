from __future__ import annotations

import json
import shutil
import re
from pathlib import Path

from .common import (
    infer_run_id_from_wiki,
    package_version,
    print_json,
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
from .wiki_ops import build_graph, concept_page, health_wiki, lint_wiki, source_page, title_from_markdown


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
    terms = [t.lower() for t in re.findall(r"[\w-]{3,}", args.question)]
    scored = []
    for page in sorted(wiki.rglob("*.md")):
        if page.name in {"index.md", "log.md"}:
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        score = sum(text.lower().count(term) for term in terms)
        if score:
            scored.append({"page": rel(wiki, page), "score": score})
    scored.sort(key=lambda item: item["score"], reverse=True)
    result = {
        "question": args.question,
        "matches": scored[: args.limit],
        "state": "passed",
        "note": "keyword candidate lookup only; agent synthesis must cite pages it reads",
    }
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
