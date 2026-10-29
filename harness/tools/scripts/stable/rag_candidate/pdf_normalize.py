"""Page-preserving local PDF normalization with explicit, source-bound corrections."""
from __future__ import annotations

import json
import os
import re
import statistics
import subprocess
from pathlib import Path

from .common import read_text, write_text, rel, sha256_file, sha256_text, slugify, today, safe_run_id, print_json
from .metadata import dump_mapping


def under(root: Path, value: str | Path, boundary: Path | None = None) -> Path:
    path = Path(value)
    path = (path if path.is_absolute() else root / path).resolve()
    path.relative_to((boundary or root).resolve())
    return path


def normalize_text(text: str) -> str:
    # NFKC would turn units and superscripts into different character sequences.
    text = text.translate({code: code - 0xFEE0 for code in range(0xFF01, 0xFF5F)}).replace("\u3000", " ")
    text = re.sub(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])", "", text)
    return text.strip()


def detect_quality(page) -> list[str]:
    text = page.get_text()
    flags = []
    if any("FzBookMaker" in font[3] for font in page.get_fonts()):
        flags.append("suspect-font-mapping")
    bad = sum(c == "\ufffd" or (ord(c) < 32 and c not in "\n\r\t") for c in text)
    if bad / max(len(text), 1) > .01:
        flags.append("invalid-text-encoding")
    if any(0xE000 <= ord(c) <= 0xF8FF for c in text):
        flags.append("private-use-glyphs-require-visual-review")
    # Some legacy Latin fonts map an English alphabet into a run of rare CJK
    # glyphs. This is distinct from a legitimate Symbol-font equation.
    if re.search(r"[\u7280-\u72ff]{8,}", text):
        flags.append("substituted-latin-font-mapping")
    if len(text.strip()) < 20 and (page.get_images() or page.get_drawings()):
        flags.append("image-or-vector-page-without-text")
    return flags


def requires_ocr(flags: list[str]) -> bool:
    return any(flag != "private-use-glyphs-require-visual-review" for flag in flags)


def _watermark(span: dict, source_hash: str, rules: list[dict]) -> bool:
    for rule in rules:
        if source_hash not in rule["sourceHashes"]:
            continue
        if (span["text"] == rule["text"] and span["font"] == rule["font"]
                and span["size"] >= rule["minSize"]
                and span.get("alpha", 255) / 255 <= rule["maxOpacity"]):
            return True
    return False


def text_lines(page, source_hash: str, rules: list[dict]) -> tuple[list[str], list[dict], list[dict]]:
    import fitz
    spans, rotated, removed, suspects = [], [], [], []
    for block in page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if not span["text"].strip():
                    continue
                if _watermark(span, source_hash, rules):
                    removed.append({"text": span["text"], "font": span["font"], "bbox": span["bbox"], "alpha": span.get("alpha", 255)})
                    continue
                if span.get("alpha", 255) < 230:
                    suspects.append({"text": span["text"], "bbox": span["bbox"], "alpha": span["alpha"]})
                if abs(line["dir"][1]) > .1:
                    rotated.append(span["text"])
                else:
                    spans.append(span)
    rows = []
    for span in sorted(spans, key=lambda s: (s["origin"][1], s["bbox"][0])):
        tolerance = min(3.5, max(.8, span["size"] * .18))
        row = next((r for r in reversed(rows[-4:]) if abs(r["y"] - span["origin"][1]) < tolerance), None)
        if row is None:
            row = {"y": span["origin"][1], "spans": []}
            rows.append(row)
        row["spans"].append(span)
    lines = []
    for row in rows:
        ordered = sorted(row["spans"], key=lambda s: s["bbox"][0])
        parts, end = [], None
        size = statistics.median(s["size"] for s in ordered)
        for span in ordered:
            gap = span["bbox"][0] - end if end is not None else 0
            if gap > size * 1.6:
                parts.append("    ")
            elif gap > size * .22 and parts and parts[-1][-1].isascii() and span["text"][0].isascii():
                parts.append(" ")
            parts.append(span["text"])
            end = span["bbox"][2]
        lines.append(normalize_text("".join(parts)))
    if rotated:
        lines.append("旋转文本：" + " ".join(rotated))
    return [line for line in lines if line], removed, suspects


def ocr_lines(result: dict) -> list[str]:
    rows = []
    for line in result["lines"]:
        words = sorted(line["words"], key=lambda w: w["x"])
        height = statistics.median([w["h"] for w in words] or [20])
        parts, end = [], None
        for word in words:
            token = word["text"]
            if not token:
                continue
            gap = word["x"] - end if end is not None else 0
            if gap > height * 1.8:
                parts.append("    ")
            elif parts and parts[-1][-1].isascii() and token[0].isascii():
                # Preserve numeric token boundaries; OCR spacing is not proof of a digit join.
                parts.append(" ")
            parts.append(token)
            end = word["x"] + word["w"]
        if parts:
            rows.append((min(w["y"] for w in words), normalize_text("".join(parts))))
    return [text for _, text in sorted(rows)]


def load_profile(path: Path | None) -> dict:
    profile = json.loads(read_text(path)) if path else {}
    for rule in profile.get("watermarks", []):
        required = ["text", "font", "minSize", "maxOpacity", "sourceHashes", "reviewedBy", "evidence"]
        if any(not rule.get(key) and rule.get(key) != 0 for key in required):
            raise ValueError("watermark rule requires exact text/font/size/opacity, source hashes and review evidence")
        if not 0 <= rule["maxOpacity"] <= 1 or rule["minSize"] <= 0 or not isinstance(rule["sourceHashes"], list):
            raise ValueError("invalid watermark rule bounds")
    for fix in profile.get("corrections", []):
        if any(not fix.get(key) for key in ["sourceHashSha256", "page", "old", "new", "reviewedBy", "evidence"]):
            raise ValueError("correction requires a source hash, physical page, exact old/new text and review evidence")
    override_keys = set()
    for override in profile.get("pageOverrides", []):
        required = ["sourceHashSha256", "page", "expectedTextHashSha256", "text", "reviewedBy", "evidence"]
        if any(not override.get(key) for key in required):
            raise ValueError("page override requires source/page, machine-text hash, complete reviewed text and evidence")
        if (not re.fullmatch(r"[0-9a-f]{64}", override["sourceHashSha256"])
                or not re.fullmatch(r"[0-9a-f]{64}", override["expectedTextHashSha256"])
                or not isinstance(override["page"], int) or override["page"] < 1
                or len(override["text"].strip()) < 20
                or re.search(r"(?m)^## PDF 第 \d+ 页", override["text"])):
            raise ValueError("invalid reviewed page override")
        key = (override["sourceHashSha256"], override["page"])
        if key in override_keys:
            raise ValueError("duplicate reviewed page override")
        override_keys.add(key)
    return profile


def _run_ocr(jobs: list[dict], runtime: Path) -> None:
    if not jobs:
        return
    if os.name != "nt":
        raise RuntimeError("Windows OCR unavailable; use --ocr-mode none to produce a review queue")
    queue = runtime / "ocr-queue.json"
    write_text(queue, json.dumps(jobs, ensure_ascii=False))
    helper = Path(__file__).with_name("pdf_ocr_windows.ps1")
    process = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(helper), "-Queue", str(queue)],
                             capture_output=True, timeout=300)
    if process.returncode:
        raise RuntimeError("offline OCR failed: " + process.stderr.decode("utf-8", "replace")[-800:])
    failed = [item["output"] for item in jobs if not Path(item["output"]).exists()]
    if failed:
        raise RuntimeError(f"OCR did not produce {len(failed)} expected page results")


def normalize_pdf(root: Path, source: Path, output: Path, runtime: Path, profile: dict,
                  ocr_mode="auto", language="auto", overwrite=False, dpi=180) -> dict:
    import fitz
    source_hash = sha256_file(source)
    source_id = profile.get("sourceIds", {}).get(source_hash) or (slugify(source.stem)[:64] + "-" + source_hash[:12])
    if not re.fullmatch(r"[\w.-]+", source_id) or source_id.startswith("."):
        raise ValueError("invalid source id")
    config_hash = sha256_text(json.dumps({"profile": profile, "ocr": ocr_mode, "language": language, "dpi": dpi,
                                        "converterVersion": 1}, sort_keys=True, ensure_ascii=False))
    target = output / (source_id + ".md")
    assets = output / "assets" / source_id
    record_file = assets / "conversion.json"
    if target.exists() and not overwrite:
        if record_file.exists():
            cached = json.loads(read_text(record_file))
            if (cached.get("sourceHashSha256") == source_hash and cached.get("configHashSha256") == config_hash
                    and cached.get("normalizedHashSha256") == sha256_file(target)
                    and all((root / p["imageRef"]).exists() for p in cached["pages"] if p.get("imageRef"))):
                return cached
        raise FileExistsError("normalized output exists or was edited; use --overwrite after review: " + rel(root, target))
    runtime.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)
    with fitz.open(source) as pdf:
        records, ocr_jobs = [], []
        for number, page in enumerate(pdf, 1):
            flags = detect_quality(page)
            record = {"page": number, "qualityFlags": flags, "method": "pdf-text-coordinate-order"}
            image = assets / f"page-{number:03d}.png"
            if flags:
                page.get_pixmap(dpi=dpi, alpha=False).save(image)
                record["imageRef"] = rel(root, image)
            if requires_ocr(flags):
                record["method"] = "needs-ocr"
                if ocr_mode != "none":
                    lang = profile.get("languages", {}).get(source_hash, language)
                    lang = "zh-Hans-CN" if lang == "auto" else lang
                    result = runtime / f"{source_hash}-{number:03d}-{lang}.json"
                    ocr_jobs.append({"image": str(image), "output": str(result), "language": lang})
                    record["ocrResult"] = rel(root, result)
            records.append(record)
        _run_ocr(ocr_jobs, runtime)
        # Automatic English retry is based on actual text, not source filenames.
        english_jobs = []
        if language == "auto":
            for job in ocr_jobs:
                result = json.loads(read_text(Path(job["output"])))
                text = result.get("text", "")
                latin = sum(c.isascii() and c.isalpha() for c in text)
                cjk = sum("\u4e00" <= c <= "\u9fff" for c in text)
                if job["language"] == "zh-Hans-CN" and latin > 100 and cjk / max(len(text), 1) < .12:
                    english_jobs.append(dict(job, output=job["output"].replace(".json", "-en.json"), language="en-US"))
            _run_ocr(english_jobs, runtime)
        current_english_outputs = {Path(job["output"]).resolve() for job in english_jobs}
        body = [f"# {source.stem}", "", "> 原件逐页转换稿。OCR、自动表格、公式及上下标需结合原页复核；不是 reviewed 结论。", ""]
        for record, page in zip(records, pdf):
            number = record["page"]
            image = assets / f"page-{number:03d}.png"
            removed, tables, suspects = [], [], []
            if record.get("ocrResult"):
                result_path = root / record["ocrResult"]
                english = result_path.with_name(result_path.stem + "-en.json")
                if english.resolve() in current_english_outputs:
                    result_path = english
                result = json.loads(read_text(result_path))
                lines = ocr_lines(result)
                record.update(method="offline-ocr-" + result["language"], ocrResult=rel(root, result_path))
                record["qualityFlags"].append("ocr-requires-source-review")
                if not any(line.strip() for line in lines):
                    record["method"] = "needs-ocr"
                    record["qualityFlags"].append("ocr-produced-no-readable-text")
            elif record["method"] == "needs-ocr":
                lines = []
            else:
                lines, removed, suspects = text_lines(page, source_hash, profile.get("watermarks", []))
                if suspects:
                    record["qualityFlags"].append("low-opacity-text-retained-for-review")
                if len(page.get_drawings()) > 5 and not removed:
                    try:
                        tables = [table.to_markdown() for table in page.find_tables(strategy="lines_strict").tables
                                  if table.row_count > 1 and table.col_count > 1]
                    except Exception:
                        record["qualityFlags"].append("table-extraction-needs-review")
                # Table text extraction must not reintroduce a filtered watermark.
                if removed:
                    record["qualityFlags"].append("watermark-filtered-tables-preserved-as-image")
            applied = []
            for fix in profile.get("corrections", []):
                if fix["sourceHashSha256"] == source_hash and fix["page"] == number:
                    count = sum(line.count(fix["old"]) for line in lines)
                    if count != fix.get("expectedCount", 1):
                        raise ValueError(f"correction precondition mismatch at page {number}; no inferred replacement")
                    lines = [line.replace(fix["old"], fix["new"]) for line in lines]
                    applied.append(fix)
            text = "\n".join(lines)
            for override in profile.get("pageOverrides", []):
                if override["sourceHashSha256"] == source_hash and override["page"] == number:
                    if record["method"] == "needs-ocr":
                        raise ValueError("unresolved OCR cannot be bypassed by a reviewed page override")
                    if sha256_text(text) != override["expectedTextHashSha256"]:
                        raise ValueError(f"reviewed page override precondition mismatch at page {number}")
                    text = override["text"].strip()
                    tables = []  # A complete reviewed page must not be followed by obsolete auto tables.
                    record["method"] += "+reviewed-page-override"
                    record["qualityFlags"].append("page-text-verified-against-source-image")
                    record["pageOverride"] = {key: override[key] for key in
                                              ["expectedTextHashSha256", "reviewedBy", "evidence"]}
                    record["pageOverride"]["replacementHashSha256"] = sha256_text(text)
            complex_page = bool(record["qualityFlags"] or tables or removed or page.get_images()
                                or len(page.get_drawings()) > 6 or re.search(r"[∑∫√≤≥≈±²³]", text))
            if complex_page:
                if not image.exists():
                    page.get_pixmap(dpi=dpi, alpha=False).save(image)
                record["imageRef"] = rel(root, image)
            record.update(textChars=len(text), textHashSha256=sha256_text(text), tables=len(tables),
                          filteredWatermarks=removed, retainedLowOpacityText=suspects, corrections=applied)
            pdf_link = Path(os.path.relpath(source, output)).as_posix()
            body += [f"## PDF 第 {number} 页", "", f"[原 PDF 页](<{pdf_link}#page={number}>) · `{record['method']}`", "", text or "本页无可靠可提取文本，请查看原页。", ""]
            for table in tables:
                body += ["自动重建表格（请核对原页）：", "", table, ""]
            if record.get("imageRef"):
                body += [f"![PDF 第 {number} 页原图](assets/{source_id}/page-{number:03d}.png)", ""]
        header = {"title": source.stem, "source": rel(root, source), "sourceSha256": source_hash,
                  "sourcePages": len(pdf), "conversionDate": today(), "assetRole": "normalized-source-derivative",
                  "authoritative": False, "configHashSha256": config_hash}
        if sha256_file(source) != source_hash:
            raise RuntimeError("source changed during normalization")
        write_text(target, "---\n" + dump_mapping(header) + "\n---\n\n" + "\n".join(body))
    incomplete = [p["page"] for p in records if p["method"] == "needs-ocr"]
    result = {"id": source_id, "sourceRef": rel(root, source), "sourceHashSha256": source_hash,
              "normalizedMarkdown": rel(root, target), "normalizedHashSha256": sha256_file(target),
              "pageCount": len(records), "pages": records, "configHashSha256": config_hash,
              "candidateAllowed": not incomplete, "unresolvedPages": incomplete,
              "qualityState": "needs-review" if any(p["qualityFlags"] for p in records) else "converted"}
    write_text(record_file, json.dumps(result, ensure_ascii=False, indent=2))
    return result


def run_normalize_pdf(args) -> dict:
    from .convert import collect_inputs
    root = Path(args.root).resolve()
    raw = root / "user/knowledge/raw"
    output = under(root, args.normalized_dir, raw)
    if "normalized" not in output.relative_to(raw).parts:
        raise ValueError("PDF derivatives must live in raw/<domain>/normalized")
    files = [path for path in collect_inputs([str(root / p) if not Path(p).is_absolute() else p for p in args.inputs]) if path.suffix.lower() == ".pdf"]
    if not files:
        raise ValueError("normalize-pdf found no PDF inputs")
    for source in files:
        under(root, source, raw)
    run_id = safe_run_id(args.run_id or "pdf-normalization")
    runtime = root / "var/rag" / run_id
    profile = load_profile(under(root, args.pdf_profile) if args.pdf_profile else None)
    sources = [normalize_pdf(root, source.resolve(), output, runtime / "ocr", profile,
                             args.ocr_mode, args.ocr_language, args.overwrite, args.dpi) for source in files]
    manifest = runtime / "normalization-manifest.json"
    result = {"schemaVersion": "harness.pdfNormalization.v1", "manifestId": run_id,
              "state": "passed" if all(s["candidateAllowed"] for s in sources) else "partial",
              "sources": sources, "sourceCount": len(sources), "pdfPageCount": sum(s["pageCount"] for s in sources),
              "manifest": rel(root, manifest), "boundary": "raw-derivative-only-no-promotion"}
    write_text(manifest, json.dumps(result, ensure_ascii=False, indent=2))
    print_json(result)
    return result
