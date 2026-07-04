from __future__ import annotations

import argparse
import json
import sys

from memory_tool.commands import (
    apply_review_decision,
    archive_candidate,
    candidate_review_package,
    classify_candidate_suitability,
    classify_memory_type,
    conflict_review_package,
    create_candidate,
    delete_candidate,
    detect_from_workflow,
    detect_memory_duplicate_conflict,
    memory_flow_status,
    promote_reviewed,
    record_no_memory_disposition,
    reject_or_merge_candidate,
    revise_candidate,
    sync_memory_index,
    validate_memory_store,
    verify_source_evidence,
)


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".")
    parser.add_argument("--memory-root", default="harness/memory")
    parser.add_argument("--candidate", default="harness/memory/candidate")
    parser.add_argument("--reviewed", default="harness/memory/reviewed")
    parser.add_argument("--archive", default="harness/memory/archive")
    parser.add_argument("--report", default="")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--source-path", default="")
    parser.add_argument("--memory-id", default="")
    parser.add_argument("--statement", default="")
    parser.add_argument("--scope", default="agent-operation")
    parser.add_argument("--project-id", default="null")
    parser.add_argument("--confidence", default="medium")
    parser.add_argument("--staleness-rule", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--approval-note", default="")
    parser.add_argument("--reason", default="")
    parser.add_argument("--review-after", default="")
    parser.add_argument("--new-statement", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory_tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-memory-store")
    _add_common_args(validate_parser)

    flow_parser = subparsers.add_parser("memory-flow-status")
    _add_common_args(flow_parser)

    for command in [
        "verify-source-evidence",
        "detect-from-workflow",
        "classify-candidate-suitability",
        "record-no-memory-disposition",
        "create-candidate",
        "classify-memory-type",
        "detect-memory-duplicate-conflict",
        "reject-or-merge-candidate",
        "conflict-review-package",
        "apply-review-decision",
        "promote-reviewed",
        "archive-candidate",
        "delete-candidate",
        "revise-candidate",
        "sync-memory-index",
    ]:
        command_parser = subparsers.add_parser(command)
        _add_common_args(command_parser)
        command_parser.add_argument("--candidate-id", default="")
        command_parser.add_argument("--candidate-path", default="")

    review_parser = subparsers.add_parser("candidate-review-package")
    _add_common_args(review_parser)
    review_parser.add_argument("--candidate-id", default="")
    review_parser.add_argument("--candidate-path", default="")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-memory-store":
        result = validate_memory_store(args)
    elif args.command == "memory-flow-status":
        result = memory_flow_status(args)
    elif args.command == "verify-source-evidence":
        result = verify_source_evidence(args)
    elif args.command == "detect-from-workflow":
        result = detect_from_workflow(args)
    elif args.command == "classify-candidate-suitability":
        result = classify_candidate_suitability(args)
    elif args.command == "record-no-memory-disposition":
        result = record_no_memory_disposition(args)
    elif args.command == "create-candidate":
        result = create_candidate(args)
    elif args.command == "classify-memory-type":
        result = classify_memory_type(args)
    elif args.command == "detect-memory-duplicate-conflict":
        result = detect_memory_duplicate_conflict(args)
    elif args.command == "reject-or-merge-candidate":
        result = reject_or_merge_candidate(args)
    elif args.command == "conflict-review-package":
        result = conflict_review_package(args)
    elif args.command == "apply-review-decision":
        result = apply_review_decision(args)
    elif args.command == "promote-reviewed":
        result = promote_reviewed(args)
    elif args.command == "archive-candidate":
        result = archive_candidate(args)
    elif args.command == "delete-candidate":
        result = delete_candidate(args)
    elif args.command == "revise-candidate":
        result = revise_candidate(args)
    elif args.command == "sync-memory-index":
        result = sync_memory_index(args)
    elif args.command == "candidate-review-package":
        result = candidate_review_package(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("state") == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
