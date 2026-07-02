from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from html import escape
from math import cos, pi, sin
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


def search_wiki_pages(root: Path, wiki_dir: Path, question: str, limit: int = 10) -> dict:
    pages = all_wiki_pages(wiki_dir)
    terms = _query_terms(question)
    scored: dict[Path, dict] = {}

    for page in pages:
        text = read_text(page)
        title = _page_title(text, page.stem)
        title_lower = title.lower()
        path_lower = rel(wiki_dir, page).lower()
        text_lower = text.lower()
        score = 0.0
        reasons: list[str] = []
        for term in terms:
            term_lower = term.lower()
            title_hits = title_lower.count(term_lower)
            path_hits = path_lower.count(term_lower)
            body_hits = text_lower.count(term_lower)
            if title_hits:
                score += title_hits * 5
                reasons.append(f"title:{term}")
            if path_hits:
                score += path_hits * 2
                reasons.append(f"path:{term}")
            if body_hits:
                score += body_hits
                reasons.append(f"body:{term}")
        if score > 0:
            scored[page] = {
                "page": rel(wiki_dir, page),
                "title": title,
                "score": round(score, 3),
                "reason": sorted(set(reasons)),
            }

    _expand_matches_from_graph(root, wiki_dir, scored)
    matches = sorted(scored.values(), key=lambda item: (-item["score"], item["page"]))[:limit]
    return {
        "question": question,
        "terms": terms,
        "matches": matches,
        "state": "passed",
        "note": "candidate lookup only; agent synthesis must read and cite matched pages",
    }


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
    lookup = _page_lookup(pages)
    broken: list[dict[str, str]] = []
    inbound = {p: 0 for p in pages}
    sparse_pages: list[str] = []
    broken_link_refs: dict[str, list[str]] = defaultdict(list)

    for page in pages:
        links = extract_wikilinks(read_text(page))
        outbound = 0
        for link in links:
            target = _resolve_wikilink(link, lookup)
            if target:
                inbound[target] += 1
                outbound += 1
            else:
                page_ref = rel(wiki_dir, page)
                broken.append({"page": page_ref, "link": link})
                broken_link_refs[link].append(page_ref)
        if page.name != "overview.md" and outbound < 2:
            sparse_pages.append(rel(wiki_dir, page))

    orphans = sorted(rel(wiki_dir, p) for p, count in inbound.items() if count == 0 and p.name != "overview.md")
    phantom_hubs = [
        {"link": link, "count": len(refs), "referencedBy": sorted(refs)}
        for link, refs in sorted(broken_link_refs.items(), key=lambda item: (-len(item[1]), item[0].lower()))
        if len(refs) >= 2
    ]
    missing_entity_signals = [
        item for item in phantom_hubs
        if re.search(r"(^[A-Z][A-Za-z0-9]+)|([\u4e00-\u9fff]{2,})", item["link"])
    ]
    duplicate_titles = _duplicate_titles(wiki_dir, pages)
    result = {
        "pageCount": len(pages),
        "brokenLinks": broken,
        "orphans": orphans,
        "sparsePages": sorted(sparse_pages),
        "phantomHubs": phantom_hubs,
        "missingEntitySignals": missing_entity_signals,
        "duplicateTitles": duplicate_titles,
        "semanticChecks": "agent-required-for-contradictions-and-gaps",
        "state": "passed" if not broken and not orphans and not duplicate_titles else "partial",
    }
    if report_path:
        write_text(report_path, _report("Candidate Wiki Lint Report", result, pages=len(pages)))
    update_status(root, run_id or infer_run_id_from_wiki(wiki_dir), {"lint": result})
    return result


def build_graph(wiki_dir: Path, graph_dir: Path, report_path: Path | None = None, root: Path | None = None, run_id: str | None = None) -> dict:
    pages = all_wiki_pages(wiki_dir)
    lookup = _page_lookup(pages)
    nodes = []
    edges = []
    seen_edges: set[tuple[str, str]] = set()
    broken_link_refs: dict[str, list[str]] = defaultdict(list)

    for page in pages:
        content = read_text(page)
        node_id = _page_id(wiki_dir, page)
        node_type = _frontmatter_value(content, "type") or "unknown"
        title = _page_title(content, page.stem)
        nodes.append({
            "id": node_id,
            "label": title,
            "type": node_type,
            "path": rel(wiki_dir, page),
            "contentChars": len(_strip_frontmatter(content)),
        })
        for link in extract_wikilinks(content):
            target_page = _resolve_wikilink(link, lookup)
            if not target_page:
                broken_link_refs[link].append(rel(wiki_dir, page))
                continue
            target_id = _page_id(wiki_dir, target_page)
            if target_id == node_id:
                continue
            key = (node_id, target_id)
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append({"from": node_id, "to": target_id, "type": "EXPLICIT_WIKILINK", "confidence": 1.0})

    graph_dir.mkdir(parents=True, exist_ok=True)
    graph_health = _graph_health(nodes, edges, broken_link_refs)
    for node in nodes:
        node["community"] = graph_health["communities"].get(node["id"], 0)
    graph = {"built": today(), "nodes": nodes, "edges": edges, "health": graph_health}
    graph_json = graph_dir / "graph.json"
    graph_html = graph_dir / "graph.html"
    write_text(graph_json, json.dumps(graph, indent=2, ensure_ascii=False))
    write_text(graph_html, _render_graph_html(graph))

    root_for_rel = root or wiki_dir
    result = {
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "orphanCount": len(graph_health["orphanNodes"]),
        "hubCount": len(graph_health["hubNodes"]),
        "phantomHubCount": len(graph_health["phantomHubs"]),
        "fragileBridgeCount": len(graph_health["fragileBridges"]),
        "state": "passed",
        "graphJson": rel(root_for_rel, graph_json),
        "graphHtml": rel(root_for_rel, graph_html),
    }
    if report_path:
        write_text(report_path, _graph_report(result, graph_health))
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


def _query_terms(question: str) -> list[str]:
    terms: list[str] = []
    terms.extend(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}", question.lower()))
    for sequence in re.findall(r"[\u3400-\u9fff]{2,}", question):
        if len(sequence) <= 16:
            terms.append(sequence)
        terms.extend(sequence[i:i + 2] for i in range(0, max(0, len(sequence) - 1)))
    if not terms:
        terms.extend(part.lower() for part in question.split() if len(part) >= 2)
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            unique.append(term)
    return unique[:32]


def _expand_matches_from_graph(root: Path, wiki_dir: Path, scored: dict[Path, dict]) -> None:
    run_id = infer_run_id_from_wiki(wiki_dir)
    graph_json = root / "var" / "rag" / run_id / "graph" / "graph.json" if run_id else None
    if not graph_json or not graph_json.exists() or not scored:
        return
    try:
        graph = json.loads(read_text(graph_json))
    except json.JSONDecodeError:
        return
    id_to_page = {rel(wiki_dir, page).removesuffix(".md"): page for page in all_wiki_pages(wiki_dir)}
    page_to_id = {page: page_id for page_id, page in id_to_page.items()}
    seeds = sorted(scored.items(), key=lambda item: -item[1]["score"])[:5]
    seed_ids = {page_to_id.get(page): item["score"] for page, item in seeds if page_to_id.get(page)}
    for edge in graph.get("edges", []):
        endpoints = (edge.get("from"), edge.get("to"))
        for index, endpoint in enumerate(endpoints):
            if endpoint not in seed_ids:
                continue
            neighbor_id = endpoints[1 - index]
            neighbor_page = id_to_page.get(neighbor_id)
            if not neighbor_page:
                continue
            bonus = max(0.1, seed_ids[endpoint] * 0.35)
            if neighbor_page in scored:
                scored[neighbor_page]["score"] = round(scored[neighbor_page]["score"] + bonus, 3)
                scored[neighbor_page]["reason"] = sorted(set(scored[neighbor_page]["reason"] + ["graph-neighbor"]))
            else:
                text = read_text(neighbor_page)
                scored[neighbor_page] = {
                    "page": rel(wiki_dir, neighbor_page),
                    "title": _page_title(text, neighbor_page.stem),
                    "score": round(bonus, 3),
                    "reason": ["graph-neighbor"],
                }


def _page_lookup(pages: list[Path]) -> dict[str, Path]:
    lookup: dict[str, Path] = {}
    for page in pages:
        lookup[_link_key(page.stem)] = page
        lookup[_link_key(page.name)] = page
        lookup[_link_key(page.as_posix())] = page
    return lookup


def _resolve_wikilink(link: str, lookup: dict[str, Path]) -> Path | None:
    candidates = [
        link,
        Path(link).stem,
        Path(link).name,
        link.replace(" ", ""),
        link.replace(" ", "-"),
    ]
    for candidate in candidates:
        found = lookup.get(_link_key(candidate))
        if found:
            return found
    return None


def _link_key(value: str) -> str:
    target = value.split("|", 1)[0].split("#", 1)[0].strip()
    target = target.removesuffix(".md")
    target = target.replace("\\", "/")
    target = Path(target).stem if "/" in target else target
    return re.sub(r"[\s_-]+", "", target).lower()


def _frontmatter_value(content: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", content, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip("\"'")


def _page_title(content: str, fallback: str) -> str:
    return _frontmatter_value(content, "title") or title_from_markdown(content, fallback)


def _strip_frontmatter(content: str) -> str:
    return re.sub(r"(?s)^---.*?---", "", content).strip()


def _page_id(wiki_dir: Path, page: Path) -> str:
    return rel(wiki_dir, page).removesuffix(".md")


def _duplicate_titles(wiki_dir: Path, pages: list[Path]) -> list[dict[str, object]]:
    by_title: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        title = _page_title(read_text(page), page.stem)
        by_title[title.lower()].append(rel(wiki_dir, page))
    return [
        {"title": title, "pages": sorted(paths)}
        for title, paths in sorted(by_title.items())
        if len(paths) > 1
    ]


def _graph_health(nodes: list[dict], edges: list[dict], broken_link_refs: dict[str, list[str]]) -> dict:
    node_ids = {node["id"] for node in nodes}
    degree = Counter()
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        degree[src] += 1
        degree[dst] += 1
        adjacency.setdefault(src, set()).add(dst)
        adjacency.setdefault(dst, set()).add(src)

    orphan_nodes = sorted(node_id for node_id in node_ids if degree[node_id] == 0)
    hub_nodes = _hub_nodes(degree)
    communities = _connected_components(adjacency)
    fragile_bridges = _fragile_bridges(adjacency, edges)
    phantom_hubs = [
        {"link": link, "count": len(refs), "referencedBy": sorted(refs)}
        for link, refs in sorted(broken_link_refs.items(), key=lambda item: (-len(item[1]), item[0].lower()))
        if len(refs) >= 2
    ]
    return {
        "orphanNodes": orphan_nodes,
        "hubNodes": hub_nodes,
        "communities": communities,
        "communityCount": len(set(communities.values())) if communities else 0,
        "fragileBridges": fragile_bridges,
        "phantomHubs": phantom_hubs,
    }


def _hub_nodes(degree: Counter) -> list[dict[str, object]]:
    if not degree:
        return []
    values = list(degree.values())
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    threshold = max(3, mean + variance ** 0.5 * 2)
    return [
        {"id": node_id, "degree": count}
        for node_id, count in sorted(degree.items(), key=lambda item: (-item[1], item[0]))
        if count >= threshold
    ]


def _connected_components(adjacency: dict[str, set[str]]) -> dict[str, int]:
    communities: dict[str, int] = {}
    community_id = 0
    for node in sorted(adjacency):
        if node in communities:
            continue
        stack = [node]
        while stack:
            current = stack.pop()
            if current in communities:
                continue
            communities[current] = community_id
            stack.extend(sorted(adjacency.get(current, set()) - communities.keys()))
        community_id += 1
    return communities


def _fragile_bridges(adjacency: dict[str, set[str]], edges: list[dict]) -> list[dict[str, str]]:
    if len(edges) > 1000:
        return []
    baseline = len(set(_connected_components(adjacency).values()))
    bridges: list[dict[str, str]] = []
    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        reduced = {node: set(neighbors) for node, neighbors in adjacency.items()}
        reduced.get(src, set()).discard(dst)
        reduced.get(dst, set()).discard(src)
        if len(set(_connected_components(reduced).values())) > baseline:
            bridges.append({"from": src, "to": dst})
    return bridges


def _render_graph_html(graph: dict) -> str:
    nodes = graph.get("nodes", [])
    radius = 240
    center = 300
    positions = {}
    for index, node in enumerate(nodes):
        angle = 2 * pi * index / max(1, len(nodes))
        positions[node["id"]] = {
            "x": round(center + radius * cos(angle), 2),
            "y": round(center + radius * sin(angle), 2),
        }
    data = json.dumps({"graph": graph, "positions": positions}, ensure_ascii=False)
    escaped_data = escape(data)
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Candidate Knowledge Graph</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 24px; color: #172033; }}
.layout {{ display: grid; grid-template-columns: minmax(360px, 660px) 1fr; gap: 24px; align-items: start; }}
svg {{ width: 100%; max-width: 660px; border: 1px solid #d8dee9; background: #fbfcfe; }}
.node {{ fill: #f8fafc; stroke: #3b82f6; stroke-width: 2; }}
.edge {{ stroke: #94a3b8; stroke-width: 1.5; }}
.label {{ font-size: 12px; fill: #172033; }}
pre {{ white-space: pre-wrap; background: #f6f8fa; padding: 12px; overflow: auto; }}
input {{ width: 100%; padding: 8px; margin-bottom: 12px; }}
li {{ margin: 6px 0; }}
</style>
<body>
<h1>Candidate Knowledge Graph</h1>
<p>Nodes: {len(nodes)}. Edges: {len(graph.get("edges", []))}. Built: {escape(str(graph.get("built", "")))}.</p>
<div class="layout">
<svg id="graph" viewBox="0 0 600 600" role="img" aria-label="Candidate knowledge graph"></svg>
<section>
<input id="filter" placeholder="Filter nodes">
<ul id="nodes"></ul>
<h2>Health</h2>
<pre>{escape(json.dumps(graph.get("health", {}), indent=2, ensure_ascii=False))}</pre>
</section>
</div>
<script type="application/json" id="graph-data">{escaped_data}</script>
<script>
const data = JSON.parse(document.getElementById('graph-data').textContent);
const graph = data.graph;
const positions = data.positions;
const svg = document.getElementById('graph');
function draw(filter = '') {{
  svg.innerHTML = '';
  const visible = new Set(graph.nodes.filter(n => n.label.toLowerCase().includes(filter.toLowerCase()) || n.id.toLowerCase().includes(filter.toLowerCase())).map(n => n.id));
  for (const edge of graph.edges) {{
    if (!visible.has(edge.from) || !visible.has(edge.to)) continue;
    const a = positions[edge.from], b = positions[edge.to];
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', a.x); line.setAttribute('y1', a.y); line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
    line.setAttribute('class', 'edge'); svg.appendChild(line);
  }}
  for (const node of graph.nodes) {{
    if (!visible.has(node.id)) continue;
    const p = positions[node.id];
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y); circle.setAttribute('r', 12);
    circle.setAttribute('class', 'node'); svg.appendChild(circle);
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', p.x + 14); text.setAttribute('y', p.y + 4); text.setAttribute('class', 'label');
    text.textContent = node.label; svg.appendChild(text);
  }}
  document.getElementById('nodes').innerHTML = graph.nodes.filter(n => visible.has(n.id)).map(n => `<li><code>${{n.path}}</code> - ${{n.label}} <small>(${{n.type}})</small></li>`).join('');
}}
document.getElementById('filter').addEventListener('input', event => draw(event.target.value));
draw();
</script>
</body>
</html>
"""


def _graph_report(result: dict, graph_health: dict) -> str:
    lines = [
        f"# Candidate Graph Report - {today()}",
        "",
        f"- Nodes: {result['nodeCount']}",
        f"- Edges: {result['edgeCount']}",
        f"- Orphan nodes: {result['orphanCount']}",
        f"- Hub nodes: {result['hubCount']}",
        f"- Phantom hubs: {result['phantomHubCount']}",
        f"- Fragile bridges: {result['fragileBridgeCount']}",
        f"- Graph JSON: `{result['graphJson']}`",
        f"- Graph HTML: `{result['graphHtml']}`",
        "",
        "## Details",
        "",
        "```json",
        json.dumps(graph_health, indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    return "\n".join(lines)
