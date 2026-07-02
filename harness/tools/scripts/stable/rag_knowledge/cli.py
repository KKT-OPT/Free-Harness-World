from __future__ import annotations

import argparse
import sys

from rag_candidate.common import print_json

from .commands import (
    run_build_reviewed_graph,
    run_enrich_gap_candidates,
    run_gap_review_package,
    run_govern_vault,
    run_health_reviewed,
    run_init_obsidian_vault,
    run_pipeline_smoke,
    run_promote_gap_candidates,
    run_query_reviewed,
    run_reviewed_gap_plan,
    run_sync_reviewed_index,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harness reviewed knowledge access command facade")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-obsidian-vault", help="initialize local Obsidian vault files for user knowledge")
    init.add_argument("--root", default=".")
    init.add_argument("--vault", default="user/knowledge")
    init.add_argument("--reviewed", default="user/knowledge/reviewed")
    init.add_argument("--run-id", default="reviewed-knowledge")
    init.set_defaults(func=run_init_obsidian_vault)

    sync = sub.add_parser("sync-reviewed-index", help="generate reviewed knowledge index and overview")
    sync.add_argument("--root", default=".")
    sync.add_argument("--vault", default="user/knowledge")
    sync.add_argument("--reviewed", default="user/knowledge/reviewed")
    sync.add_argument("--run-id", default="reviewed-knowledge")
    sync.set_defaults(func=run_sync_reviewed_index)

    graph = sub.add_parser("build-reviewed-graph", help="build graph JSON/HTML for reviewed knowledge")
    graph.add_argument("--root", default=".")
    graph.add_argument("--vault", default="user/knowledge")
    graph.add_argument("--reviewed", default="user/knowledge/reviewed")
    graph.add_argument("--graph", default="var/rag/reviewed-knowledge/graph")
    graph.add_argument("--report", default="var/rag/reviewed-knowledge/evals/graph-report.md")
    graph.add_argument("--run-id", default="reviewed-knowledge")
    graph.set_defaults(func=run_build_reviewed_graph)

    health = sub.add_parser("health-reviewed", help="check reviewed knowledge access layer")
    health.add_argument("--root", default=".")
    health.add_argument("--vault", default="user/knowledge")
    health.add_argument("--reviewed", default="user/knowledge/reviewed")
    health.add_argument("--report", default="var/rag/reviewed-knowledge/evals/health-report.md")
    health.add_argument("--run-id", default="reviewed-knowledge")
    health.set_defaults(func=run_health_reviewed)

    query = sub.add_parser("query-reviewed", help="lookup reviewed knowledge pages")
    query.add_argument("question")
    query.add_argument("--root", default=".")
    query.add_argument("--vault", default="user/knowledge")
    query.add_argument("--reviewed", default="user/knowledge/reviewed")
    query.add_argument("--graph", default="var/rag/reviewed-knowledge/graph/graph.json")
    query.add_argument("--report", default=None)
    query.add_argument("--limit", type=int, default=10)
    query.add_argument("--run-id", default="reviewed-knowledge")
    query.set_defaults(func=run_query_reviewed)

    gaps = sub.add_parser(
        "reviewed-gap-plan",
        help="plan candidate enrichment for unresolved reviewed wikilinks",
    )
    gaps.add_argument("--root", default=".")
    gaps.add_argument("--vault", default="user/knowledge")
    gaps.add_argument("--reviewed", default="user/knowledge/reviewed")
    gaps.add_argument("--graph", default="var/rag/reviewed-knowledge/graph/graph.json")
    gaps.add_argument("--report", default="var/rag/reviewed-knowledge/evals/reviewed-gap-plan.md")
    gaps.add_argument("--candidate-wiki", default="user/knowledge/candidate/reviewed-gap-concepts/wiki")
    gaps.add_argument("--write-candidates", action="store_true")
    gaps.add_argument("--run-id", default="reviewed-knowledge")
    gaps.set_defaults(func=run_reviewed_gap_plan)

    enrich = sub.add_parser(
        "enrich-gap-candidates",
        help="enrich reviewed gap candidate pages from reviewed knowledge evidence",
    )
    enrich.add_argument("--root", default=".")
    enrich.add_argument("--vault", default="user/knowledge")
    enrich.add_argument("--reviewed", default="user/knowledge/reviewed")
    enrich.add_argument("--candidate-wiki", default="user/knowledge/candidate/reviewed-gap-concepts/wiki")
    enrich.add_argument("--report", default="var/rag/reviewed-knowledge/evals/gap-candidate-enrichment.md")
    enrich.add_argument("--run-id", default="reviewed-gap-concepts")
    enrich.set_defaults(func=run_enrich_gap_candidates)

    review = sub.add_parser(
        "gap-review-package",
        help="produce human review package for enriched reviewed gap candidates",
    )
    review.add_argument("--root", default=".")
    review.add_argument("--vault", default="user/knowledge")
    review.add_argument("--reviewed", default="user/knowledge/reviewed")
    review.add_argument("--candidate-wiki", default="user/knowledge/candidate/reviewed-gap-concepts/wiki")
    review.add_argument("--report", default="var/rag/reviewed-knowledge/evals/gap-candidate-review-package.md")
    review.add_argument("--run-id", default="reviewed-gap-concepts")
    review.set_defaults(func=run_gap_review_package)

    promote = sub.add_parser(
        "promote-gap-candidates",
        help="promote approved reviewed gap candidates into reviewed concept pages",
    )
    promote.add_argument("--root", default=".")
    promote.add_argument("--vault", default="user/knowledge")
    promote.add_argument("--reviewed", default="user/knowledge/reviewed")
    promote.add_argument("--candidate-wiki", default="user/knowledge/candidate/reviewed-gap-concepts/wiki")
    promote.add_argument("--target-dir", default="user/knowledge/reviewed/concepts")
    promote.add_argument("--report", default="var/rag/reviewed-knowledge/evals/gap-concept-promotion.md")
    promote.add_argument("--scope", default="user-private")
    promote.add_argument("--reviewer", required=True)
    promote.add_argument("--approval-note", required=True)
    promote.add_argument("--review-after", default="source-updated-or-2026-12-31")
    promote.add_argument("--overwrite", action="store_true")
    promote.add_argument("--run-id", default="reviewed-gap-concepts")
    promote.set_defaults(func=run_promote_gap_candidates)

    govern = sub.add_parser(
        "govern-vault",
        help="generate governed Obsidian entry, review queue, and evidence indexes for user knowledge",
    )
    govern.add_argument("--root", default=".")
    govern.add_argument("--vault", default="user/knowledge")
    govern.add_argument("--reviewed", default="user/knowledge/reviewed")
    govern.add_argument("--candidate", default="user/knowledge/candidate")
    govern.add_argument("--raw", default="user/knowledge/raw")
    govern.add_argument("--report", default="var/rag/reviewed-knowledge/evals/knowledge-vault-governance.md")
    govern.add_argument("--archive-inactive-candidates", action="store_true")
    govern.add_argument("--run-id", default="reviewed-knowledge")
    govern.set_defaults(func=run_govern_vault)

    smoke = sub.add_parser(
        "pipeline-smoke",
        help="run raw -> candidate -> approved promotion -> reviewed vault -> query smoke",
    )
    smoke.add_argument("inputs", nargs="+", help="raw files to ingest for this smoke run")
    smoke.add_argument("--root", default=".")
    smoke.add_argument("--vault", default="user/knowledge")
    smoke.add_argument("--reviewed", default="user/knowledge/reviewed")
    smoke.add_argument("--candidate", default="user/knowledge/candidate")
    smoke.add_argument("--raw", default="user/knowledge/raw")
    smoke.add_argument("--run-id", default=None)
    smoke.add_argument("--scope", default="user-private")
    smoke.add_argument("--target", default=None)
    smoke.add_argument("--reviewer", required=True)
    smoke.add_argument("--approval-note", required=True)
    smoke.add_argument("--review-after", default="source-updated-or-2026-12-31")
    smoke.add_argument("--question", required=True)
    smoke.add_argument("--limit", type=int, default=10)
    smoke.add_argument("--report", default=None)
    smoke.add_argument("--copy-raw", action="store_true")
    smoke.add_argument("--overwrite", action="store_true")
    smoke.add_argument("--archive-promoted-candidate", action="store_true")
    smoke.add_argument("--max-chunk-chars", type=int, default=4000)
    smoke.set_defaults(func=run_pipeline_smoke)

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
