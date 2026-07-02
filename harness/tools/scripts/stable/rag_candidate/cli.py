from __future__ import annotations

import argparse
import sys

from .commands import (
    run_build_graph,
    run_enrichment_plan,
    run_health,
    run_ingest,
    run_lint,
    run_promotion_plan,
    run_promote_reviewed,
    run_query,
    run_review_package,
    run_stale_plan,
)
from .common import print_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harness RAG raw-to-candidate command facade")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="convert raw files into extracted artifacts and candidate wiki")
    ingest.add_argument("inputs", nargs="+", help="files, directories, or globs to ingest")
    ingest.add_argument("--root", default=".", help="Harness root")
    ingest.add_argument("--run-id", default=None, help="stable run id; default uses timestamp")
    ingest.add_argument("--copy-raw", action="store_true", help="copy source files into user/knowledge/raw/<run-id>")
    ingest.add_argument("--max-chunk-chars", type=int, default=4000)
    ingest.set_defaults(func=run_ingest)

    health = sub.add_parser("health", help="fast deterministic candidate wiki health check")
    health.add_argument("--root", default=".")
    health.add_argument("--wiki", required=True)
    health.add_argument("--report", default=None)
    health.add_argument("--run-id", default=None)
    health.set_defaults(func=run_health)

    lint = sub.add_parser("lint", help="candidate wiki structural lint")
    lint.add_argument("--root", default=".")
    lint.add_argument("--wiki", required=True)
    lint.add_argument("--report", default=None)
    lint.add_argument("--run-id", default=None)
    lint.set_defaults(func=run_lint)

    graph = sub.add_parser("build-graph", help="build graph.json and graph.html from wikilinks")
    graph.add_argument("--root", default=".")
    graph.add_argument("--wiki", required=True)
    graph.add_argument("--graph", required=True)
    graph.add_argument("--report", default=None)
    graph.add_argument("--run-id", default=None)
    graph.set_defaults(func=run_build_graph)

    query = sub.add_parser("query", help="keyword lookup over candidate wiki pages")
    query.add_argument("question")
    query.add_argument("--root", default=".")
    query.add_argument("--wiki", required=True)
    query.add_argument("--limit", type=int, default=10)
    query.set_defaults(func=run_query)

    enrichment = sub.add_parser("enrichment-plan", help="produce a source-grounded candidate enrichment checklist")
    enrichment.add_argument("--root", default=".")
    enrichment.add_argument("--manifest", required=True)
    enrichment.add_argument("--wiki", required=True)
    enrichment.add_argument("--report", default=None)
    enrichment.add_argument("--run-id", default=None)
    enrichment.set_defaults(func=run_enrichment_plan)

    review = sub.add_parser("review-package", help="produce a human-review package for candidate knowledge")
    review.add_argument("--root", default=".")
    review.add_argument("--manifest", required=True)
    review.add_argument("--wiki", required=True)
    review.add_argument("--report", default=None)
    review.add_argument("--run-id", default=None)
    review.set_defaults(func=run_review_package)

    promotion = sub.add_parser("promotion-plan", help="produce a plan for reviewed-knowledge promotion without writing reviewed knowledge")
    promotion.add_argument("--root", default=".")
    promotion.add_argument("--manifest", required=True)
    promotion.add_argument("--wiki", required=True)
    promotion.add_argument("--scope", default="user-private", choices=["global", "domain", "project-reviewed", "user-private"])
    promotion.add_argument("--target", default=None)
    promotion.add_argument("--report", default=None)
    promotion.add_argument("--run-id", default=None)
    promotion.set_defaults(func=run_promotion_plan)

    promote = sub.add_parser("promote-reviewed", help="write reviewed knowledge after explicit approval")
    promote.add_argument("--root", default=".")
    promote.add_argument("--manifest", required=True)
    promote.add_argument("--wiki", required=True)
    promote.add_argument("--scope", default="user-private", choices=["global", "domain", "project-reviewed", "user-private"])
    promote.add_argument("--target", required=True)
    promote.add_argument("--reviewer", required=True)
    promote.add_argument("--approval-note", required=True)
    promote.add_argument("--review-after", default="source-updated-or-2026-12-31")
    promote.add_argument("--report", default=None)
    promote.add_argument("--run-id", default=None)
    promote.add_argument("--overwrite", action="store_true")
    promote.set_defaults(func=run_promote_reviewed)

    stale = sub.add_parser("stale-plan", help="compare manifest source hashes and produce a plan only")
    stale.add_argument("--root", default=".")
    stale.add_argument("--manifest", required=True)
    stale.set_defaults(func=run_stale_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as exc:
        print_json({"state": "failed", "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
