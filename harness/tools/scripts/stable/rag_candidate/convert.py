from __future__ import annotations

from pathlib import Path

from .common import read_text


SUPPORTED_EXTENSIONS = {
    ".md", ".pdf", ".docx", ".pptx", ".xlsx", ".xls",
    ".html", ".htm", ".txt", ".csv", ".json", ".xml",
    ".rst", ".rtf", ".epub", ".ipynb", ".yaml", ".yml", ".tsv",
    ".wav", ".mp3",
}


def collect_inputs(raw_inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in raw_inputs:
        path = Path(item)
        matches = list(Path().glob(item)) if any(ch in item for ch in "*?[]") else []
        candidates = matches or [path]
        for candidate in candidates:
            if candidate.is_dir():
                files.extend(
                    p for p in sorted(candidate.rglob("*"))
                    if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
                )
            elif candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(candidate)
            else:
                raise FileNotFoundError(f"unsupported or missing input: {item}")

    unique: list[Path] = []
    seen: set[Path] = set()
    for file in files:
        resolved = file.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(file)
    if not unique:
        raise FileNotFoundError("no supported input files found")
    return unique


def convert_file(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return read_text(path), "direct-markdown"
    if suffix == ".pdf":
        import pymupdf4llm

        return pymupdf4llm.to_markdown(str(path)), "pymupdf4llm"

    from markitdown import MarkItDown

    result = MarkItDown(enable_plugins=False).convert(str(path))
    return result.text_content, "markitdown"
