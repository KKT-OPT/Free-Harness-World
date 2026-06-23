from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

from .common import (
    all_wiki_pages,
    extract_wikilinks,
    infer_run_id_from_wiki,
    read_text,
    rel,
    scan_sensitive_text,
    today,
    update_status,
    write_text,
    yaml_string,
)


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()[:120] or fallback
    return fallback


def source_page(title: str, source_ref: str, extracted_ref: str, preview: str) -> str:
    return f"""---
title: {yaml_string(title)}
type: source
tags: [candidate, ingestion]
date: {today()}
source_file: {yaml_string(source_ref)}
extracted_file: {yaml_string(extracted_ref)}
---

# {title}

## Candidate Summary

Agent review required. Summarize only source-grounded claims before any user review.

## Extracted Preview

{preview}

## Candidate Notes

- Related workflow: [[StructuredIngestion]].
- Knowledge state: [[CandidateKnowledge]].
- Add key claims, entities, concepts, contradictions, applicability, and non-applicability during agent review.

## Review Checklist

- Source provenance checked.
- Sensitive content checked.
- Usage rights checked.
- Contradictions checked against existing candidate/reviewed material.
- No reviewed knowledge written by this raw-to-candidate workflow.
"""


def concept_page(name: str, body: str) -> str:
    return f"""---
title: {yaml_string(name)}
type: concept
tags: [harness, knowledge]
sources: []
last_updated: {today()}
---

# {name}

{body}
"""


def health_wiki(root: Path, wiki_dir: Path, report_path: Path | None = None, run_id: str | None = None) -> dict:
    pages = all_wiki_pages(wiki_dir)
    index_path = wiki_dir / "index.md"
    log_path = wiki_dir / "log.md"
    index = read_text(index_path) if index_path.exists() else ""
    log = read_text(log_path) if log_path.exists() else ""

    empty_pages = []
    for page in pages:
        content = re.sub(r"(?s)^---.*?---", "", read_text(page)).strip()
        if len(content) < 40:
            empty_pages.append(rel(wiki_dir, page))

    index_links = set(re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", index))
    disk_links = {rel(wiki_dir, p) for p in pages}
    missing_from_index = sorted(disk_links - index_links)
    stale_index_entries = sorted(index_links - disk_links - {"overview.md"})
    source_pages = [p for p in pages if "sources" in p.parts]
    missing_log = [
        rel(wiki_dir, p) for p in source_pages
        if p.stem.lower().replace("-", " ") not in log.lower() and p.stem.lower() not in log.lower()
    ]
    sensitive_findings = scan_sensitive_text(root, pages + [p for p in [index_path, log_path] if p.exists()])

    result = {
        "pageCount": len(pages),
        "emptyPages": empty_pages,
        "missingFromIndex": missing_from_index,
        "staleIndexEntries": stale_index_entries,
        "missingLogEntries": missing_log,
        "sensitiveFindings": sensitive_findings,
        "state": "passed" if not empty_pages and not missing_from_index and not stale_index_entries and not missing_log and not sensitive_findings else "partial",
    }

    if report_path:
        write_text(report_path, _report("Candidate Wiki Health Report", result, pages=len(pages)))
    update_status(root, run_id or infer_run_id_from_wiki(wiki_dir), {"health": result})
    return result


def lint_wiki(root: Path, wiki_dir: Path, report_path: Path | None = None, run_id: str | None = None) -> dict:
    pages = all_wiki_pages(wiki_dir)
    stems = {p.stem.lower(): p for p in pages}
    broken: list[dict[str, str]] = []
    inbound = {p: 0 for p in pages}
    sparse_pages: list[str] = []

    for page in pages:
        links = extract_wikilinks(read_text(page))
        outbound = 0
        for link in links:
            target = stems.get(Path(link).stem.lower())
            if target:
                inbound[target] += 1
                outbound += 1
            else:
                broken.append({"page": rel(wiki_dir, page), "link": link})
        if page.name != "overview.md" and outbound < 1:
            sparse_pages.append(rel(wiki_dir, page))

    orphans = sorted(rel(wiki_dir, p) for p, count in inbound.items() if count == 0 and p.name != "overview.md")
    result = {
        "pageCount": len(pages),
        "brokenLinks": broken,
        "orphans": orphans,
        "sparsePages": sorted(sparse_pages),
        "semanticChecks": "agent-required-for-contradictions-and-gaps",
        "state": "passed" if not broken and not orphans else "partial",
    }
    if report_path:
        write_text(report_path, _report("Candidate Wiki Lint Report", result, pages=len(pages)))
    update_status(root, run_id or infer_run_id_from_wiki(wiki_dir), {"lint": result})
    return result


def build_graph(wiki_dir: Path, graph_dir: Path, report_path: Path | None = None, root: Path | None = None, run_id: str | None = None) -> dict:
    pages = all_wiki_pages(wiki_dir)
    stems = {p.stem.lower(): p for p in pages}
    nodes = []
    edges = []
    seen_edges: set[tuple[str, str]] = set()

    for page in pages:
        content = read_text(page)
        node_id = rel(wiki_dir, page).removesuffix(".md")
        node_type = "unknown"
        type_match = re.search(r"^type:\s*([^\s]+)", content, re.MULTILINE)
        if type_match:
            node_type = type_match.group(1).strip("\"'")
        title = page.stem
        title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip().strip("\"'")
        nodes.append({"id": node_id, "label": title, "type": node_type, "path": rel(wiki_dir, page)})
        for link in extract_wikilinks(content):
            target_page = stems.get(Path(link).stem.lower())
            if not target_page:
                continue
            target_id = rel(wiki_dir, target_page).removesuffix(".md")
            if target_id == node_id:
                continue
            key = (node_id, target_id)
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append({"from": node_id, "to": target_id, "type": "EXPLICIT_WIKILINK", "confidence": 1.0})

    graph_dir.mkdir(parents=True, exist_ok=True)
    graph = {"built": today(), "nodes": nodes, "edges": edges}
    graph_json = graph_dir / "graph.json"
    graph_html = graph_dir / "graph.html"
    write_text(graph_json, json.dumps(graph, indent=2, ensure_ascii=False))
    html = "<!doctype html><meta charset='utf-8'><title>Candidate Knowledge Graph</title>"
    html += "<h1>Candidate Knowledge Graph</h1><pre>"
    html += escape(json.dumps(graph, indent=2, ensure_ascii=False))
    html += "</pre>"
    write_text(graph_html, html)

    root_for_rel = root or wiki_dir
    result = {
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "state": "passed",
        "graphJson": rel(root_for_rel, graph_json),
        "graphHtml": rel(root_for_rel, graph_html),
    }
    if report_path:
        write_text(
            report_path,
            f"# Candidate Graph Report - {today()}\n\n"
            f"- Nodes: {len(nodes)}\n"
            f"- Edges: {len(edges)}\n"
            f"- Graph JSON: `{result['graphJson']}`\n"
            f"- Graph HTML: `{result['graphHtml']}`\n",
        )
    if root:
        update_status(root, run_id or infer_run_id_from_wiki(wiki_dir), {"graphSummary": result})
    return result


def _report(title: str, result: dict, pages: int) -> str:
    return "\n".join([
        f"# {title} - {today()}",
        "",
        f"- Pages: {pages}",
        f"- State: {result['state']}",
        "",
        "## Details",
        "",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
