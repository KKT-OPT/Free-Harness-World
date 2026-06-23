from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any


META_FILES = {
    "index.md",
    "log.md",
    "health-report.md",
    "lint-report.md",
    "graph-report.md",
}

SENSITIVE_PATTERNS = [
    ("concretePrivatePath", re.compile(r"[A-Za-z]:\\[A-Za-z0-9_. $(){}\[\]-]")),
    ("possibleCredentialValue", re.compile(r"(?i)(password|token|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{8,}")),
]


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def timestamp_id() -> str:
    return datetime.now().strftime("rag-candidate-%Y%m%d-%H%M%S")


def safe_run_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip(".-")
    if not cleaned:
        raise ValueError("run id became empty after sanitization")
    return cleaned[:96]


def slugify(value: str) -> str:
    value = Path(value).stem.lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value).strip("-")
    return value or "source"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def package_version(name: str) -> str:
    try:
        return importlib_metadata.version(name)
    except importlib_metadata.PackageNotFoundError:
        return "not-installed"


def split_chunks(text: str, max_chars: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = paragraph if not current else current + "\n\n" + paragraph
    if current:
        chunks.append(current)
    return chunks or [text[:max_chars]]


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def extract_wikilinks(text: str) -> list[str]:
    links: list[str] = []
    for match in re.findall(r"\[\[([^\]]+)\]\]", text):
        target = match.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target)
    return links


def all_wiki_pages(wiki_dir: Path) -> list[Path]:
    return [
        p for p in sorted(wiki_dir.rglob("*.md"))
        if p.name not in META_FILES
    ]


def infer_run_id_from_wiki(wiki: Path) -> str | None:
    parts = list(wiki.resolve().parts)
    lowered = [p.lower() for p in parts]
    markers = (
        ["user", "knowledge", "candidate"],
        ["rag", "knowledge", "candidate"],
    )
    for marker in markers:
        for index in range(len(lowered) - len(marker) + 1):
            if lowered[index:index + len(marker)] == marker:
                next_index = index + len(marker)
                if next_index < len(parts):
                    return parts[next_index]
    return None


def update_status(root: Path, run_id: str | None, values: dict[str, Any]) -> None:
    if not run_id:
        return
    status_path = root / "var" / "logs" / f"{run_id}.json"
    current: dict[str, Any] = {}
    if status_path.exists():
        try:
            current = json.loads(read_text(status_path))
        except json.JSONDecodeError:
            current = {}
    current.update(values)
    current["statusJson"] = rel(root, status_path)
    write_text(status_path, json.dumps(current, indent=2, ensure_ascii=False))


def print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def scan_sensitive_text(root: Path, files: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in files:
        text = read_text(path)
        for code, pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                findings.append({
                    "code": code,
                    "path": rel(root, path),
                    "message": "Potential sensitive value detected in generated text.",
                })
    return findings
