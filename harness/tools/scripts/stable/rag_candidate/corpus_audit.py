"""Read-only corpus checks, including physical pages, provenance and promotion seals."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

from .common import read_text, write_text, sha256_file, rel, print_json, slugify
from .metadata import frontmatter, metadata, list_values
from .pdf_normalize import under, detect_quality, requires_ocr


def local_links(root: Path, path: Path, text: str) -> list[str]:
    missing = []
    for match in re.finditer(r"\]\((?:<([^>]+)>|([^\s)]+))\)", text):
        value = (match[1] or match[2]).split("#", 1)[0]
        if not value or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", value):
            continue
        try:
            target = under(root, path.parent / unquote(value))
            if not target.is_file():
                missing.append(value)
        except ValueError:
            missing.append(value)
    return missing


def audit_corpus(root: Path, manifest: dict, reviewed: Path | None = None, seal: dict | None = None, require_sealed=False) -> dict:
    import fitz
    errors, warnings, records = [], [], []
    reviewed_by_source = {}
    if reviewed:
        for page in reviewed.rglob("*.md"):
            text = read_text(page)
            if frontmatter(text).get("knowledgeRole") in {"domain-index", "domain-schema"}:
                continue
            for ref in list_values(metadata(text).get("sourceRefs")):
                reviewed_by_source.setdefault(ref, []).append(page)
    sealed = {item["target"]: item for item in (seal or {}).get("entries", [])}
    for source in manifest.get("sources", []):
        source_ref = source.get("sourceRef") or source.get("source")
        normalized_ref = source.get("normalizedMarkdown") or source.get("normalized")
        expected_hash = source.get("sourceHashSha256") or source.get("sourceSha256") or source.get("sha256")
        source_id = source.get("id") or slugify(Path(source_ref).stem)
        item_errors, item_warnings = [], []
        original, normalized = under(root, source_ref), under(root, normalized_ref)
        if not expected_hash or not original.is_file() or not normalized.is_file():
            errors.append({"sourceId": source_id, "issues": ["missing original/normalized file or expected source hash"]})
            continue
        actual_hash = sha256_file(original)
        if actual_hash != expected_hash:
            item_errors.append("source-hash-mismatch")
        text = read_text(normalized)
        if "\ufffd" in text:
            item_errors.append("replacement-character-in-normalized-text")
        header = frontmatter(text)
        if header.get("sourceSha256") and header["sourceSha256"] != actual_hash:
            item_errors.append("normalized-header-source-hash-mismatch")
        if source.get("normalizedHashSha256") and sha256_file(normalized) != source["normalizedHashSha256"]:
            item_errors.append("normalized-content-changed")
        headings = list(re.finditer(r"(?m)^## PDF 第 (\d+) 页\s*$", text))
        numbers = [int(match[1]) for match in headings]
        page_records = []
        if original.suffix.lower() == ".pdf":
            with fitz.open(original) as pdf:
                count = len(pdf)
                if numbers != list(range(1, count + 1)):
                    item_errors.append("physical-page-coverage-mismatch")
                for i, page in enumerate(pdf):
                    block = text[headings[i].end():headings[i + 1].start() if i + 1 < len(headings) else len(text)] if i < len(headings) else ""
                    method_match = re.search(r"`((?:offline-ocr|pdf-text-coordinate-order|needs-ocr)[^`]*)`", block)
                    method = method_match[1] if method_match else "legacy-unspecified"
                    quality = detect_quality(page)
                    if requires_ocr(quality) and not method.startswith("offline-ocr"):
                        item_errors.append(f"page-{i+1}-unreliable-text-without-ocr")
                    images = re.findall(r"!\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))\)", block)
                    image_refs = []
                    for left, right in images:
                        image = under(root, normalized.parent / unquote(left or right))
                        image_refs.append(rel(root, image))
                    if method.startswith("offline-ocr"):
                        item_warnings.append(f"page-{i+1}-ocr-semantic-review-required")
                        if not image_refs:
                            item_errors.append(f"page-{i+1}-ocr-image-missing")
                    elif "private-use-glyphs-require-visual-review" in quality:
                        item_warnings.append(f"page-{i+1}-private-use-glyphs-require-visual-review")
                        if not image_refs:
                            item_errors.append(f"page-{i+1}-private-use-glyph-image-missing")
                    page_records.append({"page": i + 1, "method": method, "qualityFlags": quality,
                                         "imageRef": image_refs[0] if image_refs else None})
        else:
            count = source.get("pageCount", 0)
        item_errors.extend("broken-normalized-link:" + value for value in local_links(root, normalized, text))
        pages = reviewed_by_source.get(source_ref, []) if reviewed else []
        if not reviewed and source.get("reviewed"):
            pages = [under(root, source["reviewed"])]
        if reviewed and len(pages) != 1:
            item_errors.append("reviewed-source-mapping-not-one-to-one")
        for page in pages:
            body = read_text(page)
            from .reviewed_content import validate_content
            try:
                validate_content(root, {**source, 'sourceRef': source_ref, 'normalizedMarkdown': normalized_ref,
                                       'normalizedHashSha256': sha256_file(normalized), 'pageCount': count,
                                       'pages': source.get('pages', page_records)}, page, body)
            except ValueError as exc:
                item_errors.append(str(exc))
            refs = list_values(metadata(body).get("sourceRefs"))
            if source_ref not in refs or normalized_ref not in refs or any(ref.startswith("var/") for ref in refs):
                item_errors.append("reviewed-source-boundary-mismatch")
            item_errors.extend("broken-reviewed-link:" + value for value in local_links(root, page, body))
            entry = sealed.get(rel(root, page))
            if entry:
                if entry["contentHashSha256"] != sha256_file(page) or entry["sourceHashSha256"] != actual_hash:
                    item_errors.append("promotion-seal-mismatch")
            elif require_sealed:
                item_errors.append("reviewed-content-unsealed")
            else:
                item_warnings.append("reviewed-content-unsealed")
        if sha256_file(original) != actual_hash:
            item_errors.append("source-changed-during-audit")
        records.append({"id": source_id, "sourceRef": source_ref, "sourceHashSha256": actual_hash,
                        "normalizedMarkdown": normalized_ref, "normalizedHashSha256": sha256_file(normalized),
                        "pageCount": count, "pages": page_records, "candidateAllowed": not item_errors,
                        "qualityState": "needs-review" if item_warnings else "converted",
                        "issues": item_errors, "warnings": item_warnings,
                        "reviewed": [rel(root, p) for p in pages]})
        if item_errors:
            errors.append({"sourceId": source_id, "issues": item_errors})
        if item_warnings:
            warnings.append({"sourceId": source_id, "warnings": item_warnings})
    if not manifest.get("sources"):
        errors.append({"issues": ["manifest has no sources"]})
    return {"state": "failed" if errors else "passed", "scope": "explicit-corpus-structural-audit",
            "semanticState": "not-proven-by-structural-checks", "sourceCount": len(records),
            "pdfPageCount": sum(item["pageCount"] for item in records), "issues": errors, "warnings": warnings, "sources": records}


def run_audit_corpus(args) -> dict:
    root = Path(args.root).resolve()
    manifest = json.loads(read_text(under(root, args.manifest)))
    seal = json.loads(read_text(under(root, args.promotion_record))) if args.promotion_record else None
    result = audit_corpus(root, manifest, under(root, args.reviewed) if args.reviewed else None, seal, args.require_sealed)
    if args.export_manifest:
        output = under(root, args.export_manifest, root / "var/rag")
        exported = {"schemaVersion": "harness.pdfNormalization.v1", "manifestId": output.parent.name,
                    "conversionOrigin": "adopted-existing-normalized-no-regeneration", "sources": result["sources"]}
        write_text(output, json.dumps(exported, ensure_ascii=False, indent=2))
    report = under(root, args.report) if args.report else root / "var/rag/corpus-audit/report.json"
    if not report.is_relative_to(root / "var"):
        raise ValueError("audit report must remain in runtime var boundary")
    result["report"] = rel(root, report)
    write_text(report, json.dumps(result, ensure_ascii=False, indent=2))
    print_json(result)
    if result["issues"]:
        raise ValueError("corpus audit failed; inspect issues in the report")
    return result
