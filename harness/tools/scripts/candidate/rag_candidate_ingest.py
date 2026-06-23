#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    stable_dir = root / "tools" / "scripts" / "stable"
    sys.path.insert(0, str(stable_dir))

    from rag_candidate.cli import main as cli_main

    return cli_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
