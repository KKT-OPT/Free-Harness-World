from __future__ import annotations

import argparse
import sys

from rag_candidate.common import print_json

from .commands import (
    run_build_reviewed_graph,
    run_candidate_cleanup_apply,
    run_candidate_cleanup_plan,
    run_canonicalize_vault_layout,
    run_enrich_gap_candidates,
    run_gap_review_package,
    run_govern_reviewed_duplicates,
    run_govern_vault,
    run_health_reviewed,
    run_init_obsidian_vault,
    run_pipeline_smoke,
    run_promote_gap_candidates,
    run_query_reviewed,
    run_dispose_residual_gaps,
    run_reviewed_gap_plan,
    run_schema_context,
    run_sync_reviewed_index,
    run_validate_knowledge_vault,
    run_validate_llm_wiki_mechanisms,
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

    duplicates = sub.add_parser(
        "govern-reviewed-duplicates",
        help="check duplicate reviewed pages sharing the same raw source and domain",
    )
    duplicates.add_argument("--root", default=".")
    duplicates.add_argument("--vault", default="user/knowledge")
    duplicates.add_argument("--reviewed", default="user/knowledge/reviewed")
    duplicates.add_argument("--report", default="var/rag/reviewed-knowledge/evals/duplicate-reviewed-governance.md")
    duplicates.add_argument("--run-id", default="reviewed-knowledge")
    duplicates.set_defaults(func=run_govern_reviewed_duplicates)

    dispose = sub.add_parser(
        "dispose-residual-gaps",
        help="dedup or defer residual reviewed workflow gaps without promotion",
    )
    dispose.add_argument("--root", default=".")
    dispose.add_argument("--vault", default="user/knowledge")
    dispose.add_argument("--reviewed", default="user/knowledge/reviewed")
    dispose.add_argument("--candidate-wiki", default="user/knowledge/candidate/reviewed-gap-concepts/wiki")
    dispose.add_argument("--candidate-run-id", default="reviewed-gap-concepts")
    dispose.add_argument("--report", default="var/rag/reviewed-knowledge/evals/residual-gap-disposition.md")
    dispose.add_argument("--run-id", default="reviewed-knowledge")
    dispose.set_defaults(func=run_dispose_residual_gaps)

    canonicalize = sub.add_parser(
        "canonicalize-vault-layout",
        help="canonicalize a source-centered knowledge vault layout before one-click validation",
    )
    canonicalize.add_argument("--root", default=".")
    canonicalize.add_argument("--vault", default="user/knowledge")
    canonicalize.add_argument("--reviewed", default="user/knowledge/reviewed")
    canonicalize.add_argument("--candidate", default="user/knowledge/candidate")
    canonicalize.add_argument("--raw", default="user/knowledge/raw")
    canonicalize.add_argument("--registry", default="user/registry/knowledge.local.json")
    canonicalize.add_argument("--source-domain", default="agent")
    canonicalize.add_argument("--target-domain", default="agent-harness-engineering")
    canonicalize.add_argument("--source-id", default="agent-harness-engineering-a-survey")
    canonicalize.add_argument("--canonical-page", default="agent-harness-engineering-survey")
    canonicalize.add_argument("--report", default="var/rag/reviewed-knowledge/evals/canonical-vault-layout.md")
    canonicalize.add_argument("--run-id", default="reviewed-knowledge")
    canonicalize.set_defaults(func=run_canonicalize_vault_layout)

    validate = sub.add_parser(
        "validate-knowledge-vault",
        help="run the one-click validation gate for the local knowledge vault",
    )
    validate.add_argument("--root", default=".")
    validate.add_argument("--vault", default="user/knowledge")
    validate.add_argument("--reviewed", default="user/knowledge/reviewed")
    validate.add_argument("--candidate", default="user/knowledge/candidate")
    validate.add_argument("--raw", default="user/knowledge/raw")
    validate.add_argument("--registry", default="user/registry/knowledge.local.json")
    validate.add_argument("--graph", default="var/rag/reviewed-knowledge/graph")
    validate.add_argument("--report", default="var/rag/reviewed-knowledge/evals/knowledge-validation-gate.md")
    validate.add_argument("--run-id", default="reviewed-knowledge")
    validate.set_defaults(func=run_validate_knowledge_vault)

    schema_context = sub.add_parser(
        "schema-context",
        help="render task-scoped schema context for a reviewed knowledge domain",
    )
    schema_context.add_argument("--root", default=".")
    schema_context.add_argument("--vault", default="user/knowledge")
    schema_context.add_argument("--reviewed", default="user/knowledge/reviewed")
    schema_context.add_argument("--registry", default="user/registry/knowledge.local.json")
    schema_context.add_argument("--domain", required=True)
    schema_context.add_argument("--task", default="validation", choices=["ingest", "promotion", "query", "validation", "cleanup", "all"])
    schema_context.add_argument("--report", default=None)
    schema_context.add_argument("--run-id", default="reviewed-knowledge")
    schema_context.set_defaults(func=run_schema_context)

    mechanisms = sub.add_parser(
        "validate-llm-wiki-mechanisms",
        help="validate absorbed Obsidian LLM Wiki mechanisms with executable fixtures",
    )
    mechanisms.add_argument("--root", default=".")
    mechanisms.add_argument("--vault", default="user/knowledge")
    mechanisms.add_argument("--reviewed", default="user/knowledge/reviewed")
    mechanisms.add_argument("--candidate", default="user/knowledge/candidate")
    mechanisms.add_argument("--raw", default="user/knowledge/raw")
    mechanisms.add_argument("--registry", default="user/registry/knowledge.local.json")
    mechanisms.add_argument("--graph", default="var/rag/reviewed-knowledge/graph")
    mechanisms.add_argument("--report", default="var/rag/reviewed-knowledge/evals/llm-wiki-mechanism-validation.md")
    mechanisms.add_argument("--run-id", default="reviewed-knowledge")
    mechanisms.set_defaults(func=run_validate_llm_wiki_mechanisms)

    cleanup = sub.add_parser(
        "candidate-cleanup-plan",
        help="dry-run post-promotion candidate cleanup plan",
    )
    cleanup.add_argument("--root", default=".")
    cleanup.add_argument("--vault", default="user/knowledge")
    cleanup.add_argument("--reviewed", default="user/knowledge/reviewed")
    cleanup.add_argument("--candidate", default="user/knowledge/candidate")
    cleanup.add_argument("--raw", default="user/knowledge/raw")
    cleanup.add_argument("--registry", default="user/registry/knowledge.local.json")
    cleanup.add_argument("--report", default="var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-plan.md")
    cleanup.add_argument("--run-id", default="reviewed-knowledge")
    cleanup.set_defaults(func=run_candidate_cleanup_plan)

    cleanup_apply = sub.add_parser(
        "candidate-cleanup-apply",
        help="apply approved post-promotion candidate cleanup",
    )
    cleanup_apply.add_argument("--root", default=".")
    cleanup_apply.add_argument("--vault", default="user/knowledge")
    cleanup_apply.add_argument("--reviewed", default="user/knowledge/reviewed")
    cleanup_apply.add_argument("--candidate", default="user/knowledge/candidate")
    cleanup_apply.add_argument("--raw", default="user/knowledge/raw")
    cleanup_apply.add_argument("--registry", default="user/registry/knowledge.local.json")
    cleanup_apply.add_argument("--backup-root", default="var/rag/candidate-full-corpus-archive")
    cleanup_apply.add_argument("--report", default="var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-apply.md")
    cleanup_apply.add_argument("--reviewer", required=True)
    cleanup_apply.add_argument("--approval-note", required=True)
    cleanup_apply.add_argument("--run-id", default="reviewed-knowledge")
    cleanup_apply.set_defaults(func=run_candidate_cleanup_apply)

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
    promote.add_argument("--domain", default="agent")
    promote.add_argument("--target-dir", default=None)
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
    smoke.add_argument("--registry", default="user/registry/knowledge.local.json")
    smoke.add_argument("--run-id", default=None)
    smoke.add_argument("--domain", default="agent")
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
    smoke.add_argument("--extraction-granularity", default="standard", choices=["fine", "standard", "coarse", "minimal", "custom"])
    smoke.add_argument("--entity-cap", type=int, default=None)
    smoke.add_argument("--concept-cap", type=int, default=None)
    smoke.add_argument("--batch-strategy", default="single-pass-local-conversion")
    smoke.add_argument("--tag-vocabulary-mode", default="default", choices=["default", "custom"])
    smoke.add_argument("--allowed-tags", nargs="*", default=[])
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
