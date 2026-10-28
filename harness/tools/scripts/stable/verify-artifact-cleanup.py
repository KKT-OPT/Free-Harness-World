"""Stable explicit-file cleanup receipts. No delete, migration, or dependency inference."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys

SCHEMA = "harness.artifact-cleanup.v1"
HASH_BLOCK_BYTES = 64 * 1024


def read_json(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def resolve_entry(root, value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("entries must be nonempty POSIX relative file paths")
    relative = PurePosixPath(value)
    if relative.is_absolute() or PureWindowsPath(value).drive:
        raise ValueError("absolute paths and drive prefixes are forbidden")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("non-canonical path components are forbidden")
    if any(part.endswith((" ", ".")) for part in relative.parts):
        raise ValueError("Windows trailing-dot or trailing-space aliases are forbidden")
    candidate = root.joinpath(*relative.parts)
    cursor = candidate
    while cursor != root:
        if cursor.is_symlink() or (hasattr(cursor, "is_junction") and cursor.is_junction()):
            raise ValueError("symbolic links and junctions are forbidden")
        try:
            attributes = getattr(cursor.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            attributes = 0
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError("reparse points are forbidden")
        cursor = cursor.parent
    if not candidate.resolve().is_relative_to(root):
        raise ValueError("entry escapes the selected workspace")
    return candidate


def validate_document(root, document, receipt=False):
    if not isinstance(document, dict) or document.get("schemaVersion") != SCHEMA:
        raise ValueError("unsupported manifest or receipt schema")
    expected = {"schemaVersion", "remove", "protect"}
    if set(document) != expected:
        raise ValueError("manifest/receipt keys must be schemaVersion, remove and protect")
    seen = set()
    for role in ("remove", "protect"):
        entries = document[role]
        if not isinstance(entries, list):
            raise ValueError("remove and protect must be arrays")
        for entry in entries:
            if receipt:
                if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "bytes"}:
                    raise ValueError("invalid receipt entry")
                if not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
                    raise ValueError("invalid receipt digest")
                if type(entry["bytes"]) is not int or entry["bytes"] < 0:
                    raise ValueError("invalid receipt byte size")
                value = entry["path"]
            else:
                value = entry
            path = resolve_entry(root, value)
            identity = os.path.normcase(str(path))
            if identity in seen:
                raise ValueError("duplicate or overlapping file roles")
            seen.add(identity)
    if not document["protect"]:
        raise ValueError("at least one protected file is required")


def fingerprint(path, relative):
    if not path.is_file():
        raise ValueError("snapshot entries must be existing regular files")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(HASH_BLOCK_BYTES), b""):
            size += len(block)
            digest.update(block)
    return {"path": relative, "sha256": digest.hexdigest(), "bytes": size}


def snapshot(root, manifest):
    validate_document(root, manifest)
    result = {"schemaVersion": SCHEMA}
    for role in ("remove", "protect"):
        result[role] = [fingerprint(resolve_entry(root, name), name) for name in manifest[role]]
    return result


def verify(root, receipt):
    validate_document(root, receipt, receipt=True)
    findings = []
    for item in receipt["remove"]:
        if resolve_entry(root, item["path"]).exists():
            findings.append({"code": "removalTargetStillPresent", "path": item["path"]})
    for item in receipt["protect"]:
        path = resolve_entry(root, item["path"])
        if not path.is_file():
            findings.append({"code": "protectedFileMissing", "path": item["path"]})
        elif fingerprint(path, item["path"]) != item:
            findings.append({"code": "protectedFileChanged", "path": item["path"]})
    return {
        "status": "failed" if findings else "passed",
        "mode": "verify",
        "removedCount": len(receipt["remove"]),
        "protectedCount": len(receipt["protect"]),
        "findings": findings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    before = commands.add_parser("snapshot")
    before.add_argument("--root", required=True)
    before.add_argument("--manifest", required=True)
    before.add_argument("--receipt", required=True)
    after = commands.add_parser("verify")
    after.add_argument("--root", required=True)
    after.add_argument("--receipt", required=True)
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("workspace root must be a directory")
        if args.command == "snapshot":
            result = snapshot(root, read_json(args.manifest))
            output = Path(args.receipt).absolute()
            listed_paths = {resolve_entry(root, item["path"]) for role in ("remove", "protect") for item in result[role]}
            if output.resolve() in listed_paths or output.resolve() == Path(args.manifest).resolve():
                raise ValueError("receipt cannot replace an input asset")
            # Exclusive creation prevents replacing a prior audit receipt or any existing file.
            with output.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(result, stream, ensure_ascii=True, indent=2)
                stream.write("\n")
            summary = {"status": "passed", "mode": "snapshot", "removeCount": len(result["remove"]), "protectedCount": len(result["protect"])}
        else:
            summary = verify(root, read_json(args.receipt))
    except (OSError, ValueError) as error:
        message = str(error) if isinstance(error, ValueError) else "filesystem operation failed; check inputs, receipt existence and permissions"
        summary = {"status": "failed", "mode": args.command, "failureMode": "invalid-input-or-filesystem", "message": message}
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
