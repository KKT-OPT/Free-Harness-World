from __future__ import annotations

import json
import re
import shutil
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import Any


ALLOWED_DOC_STATUSES = {
    "draft",
    "review",
    "active",
    "stale",
    "deprecated",
    "archived",
    "superseded",
}
EXPECTED_ASSET_STATE_BY_BUCKET = {
    "candidate": "candidate",
    "reviewed": "reviewed",
    "archive": "archived",
}
REQUIRED_FRONTMATTER_KEYS = [
    "documentName",
    "version",
    "updatedAt",
    "status",
    "purpose",
    "scope",
    "prerequisites",
    "relatedDocuments",
    "outputTo",
    "owner",
    "reviewAfter",
    "dependsOn",
    "review",
]
REQUIRED_REVIEW_KEYS = ["reviewedBy", "reviewedAt", "decision"]
REQUIRED_MEMORY_KEYS = [
    "memoryId",
    "assetState",
    "scope",
    "sourceEvidence",
    "confidence",
    "stalenessRule",
]
SENSITIVE_PATTERNS = [
    ("sensitive/windows-absolute-path", re.compile(r"[A-Za-z]:\\")),
    ("sensitive/credential-assignment", re.compile(r"(?i)\b(password|token|secret|apiKey|apikey)\s*[:=]\s*\S{8,}")),
    ("sensitive/settings-xml-path", re.compile(r"(?i)(settings\.xml|\.m2[\\/])")),
    ("sensitive/private-url-auth", re.compile(r"(?i)https?://[^/\s]+@")),
]


def memory_flow_status(args: Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    report = _resolve_report_path(root, args.report, "var/memory/evals/memory-flow-status.md")
    status_json = root / "var/memory/status/memory-flow-status.json"
    steps = _memory_flow_steps()
    missing = [step for step in steps if step["coverage"] == "missing"]
    partial = [step for step in steps if step["coverage"] == "partial"]
    implemented = [step for step in steps if step["coverage"] == "implemented"]
    result = {
        "state": "passed",
        "scope": "memory-flow-status",
        "architectureSource": "harness/architecture/HarnessEngineering.md#22.2-memory-update-flow",
        "report": _rel(report, root),
        "statusJson": _rel(status_json, root),
        "flowCoverageState": "partial" if missing or partial else "complete",
        "stepCount": len(steps),
        "implementedStepCount": len(implemented),
        "partialStepCount": len(partial),
        "missingStepCount": len(missing),
        "steps": steps,
        "requiredRule": "Every Memory flow transition must be executed by a stable command or stopped as an unsupported flow step.",
        "boundary": "read-only-flow-status-no-memory-mutation",
    }
    _write_flow_status_report(result, report)
    _write_json(status_json, result)
    return result


def validate_memory_store(args: Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    if args.self_test:
        return _run_self_test(root, args)

    memory_root = _resolve_under_root(root, args.memory_root)
    candidate = _resolve_under_root(root, args.candidate)
    reviewed = _resolve_under_root(root, args.reviewed)
    archive = _resolve_under_root(root, args.archive)

    report = _resolve_report_path(root, args.report, "var/memory/evals/memory-validation-report.md")
    status_json = root / "var/memory/status/validate-memory-store.json"

    scan = _scan_memory_store(root, memory_root, candidate, reviewed, archive)
    result = _validation_result(root, scan, report, status_json)
    _write_validation_report(result, scan, report)
    _write_json(status_json, result)
    return result


def candidate_review_package(args: Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    memory_root = _resolve_under_root(root, args.memory_root)
    candidate = _resolve_under_root(root, args.candidate)
    reviewed = _resolve_under_root(root, args.reviewed)
    archive = _resolve_under_root(root, args.archive)

    scan = _scan_memory_store(root, memory_root, candidate, reviewed, archive)
    selected, selection_issues = _select_candidate(root, scan["entries"], args.candidate_id, args.candidate_path)
    issues = list(scan["issues"]) + selection_issues

    default_report = "var/memory/reviews/candidate-review-package.md"
    if selected:
        default_report = f"var/memory/reviews/{selected['memoryId']}-review-package.md"
    report = _resolve_report_path(root, args.report, default_report)
    status_json = root / "var/memory/status/candidate-review-package.json"

    state = "passed" if selected and not _has_error(selection_issues) else "failed"
    result = {
        "state": state,
        "scope": "memory-candidate-review-package",
        "memoryRoot": _rel(memory_root, root),
        "candidate": _rel(candidate, root),
        "reviewed": _rel(reviewed, root),
        "archive": _rel(archive, root),
        "candidateId": selected["memoryId"] if selected else args.candidate_id,
        "candidatePath": selected["path"] if selected else args.candidate_path,
        "report": _rel(report, root),
        "statusJson": _rel(status_json, root),
        "blockingIssues": [issue for issue in issues if issue["severity"] == "error"],
        "reviewState": _candidate_review_state(selected) if selected else None,
        "decisionOptions": ["approve", "reject", "delete", "defer", "revise"],
        "boundary": "read-only-review-package-no-memory-mutation",
    }
    _write_review_package(result, selected, scan, issues, report)
    _write_json(status_json, result)
    return result


def verify_source_evidence(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    source = _source_for_command(args, selected)
    source_path = _source_path(root, source) if source else None
    exists = bool(source_path and source_path.exists())
    result = _flow_command_result(
        root,
        args,
        "verify-source-evidence",
        "var/memory/evals/verify-source-evidence.md",
        "passed" if exists else "failed",
        {
            "sourceEvidence": source,
            "sourcePath": _rel(source_path, root) if source_path else "",
            "sourceExists": exists,
            "candidateId": selected["memoryId"] if selected else "",
        },
        scan=scan,
    )
    return result


def detect_from_workflow(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    source = _source_for_command(args, selected)
    source_path = _source_path(root, source) if source else None
    text = source_path.read_text(encoding="utf-8", errors="replace") if source_path and source_path.exists() else ""
    signals = [line.strip() for line in text.splitlines() if re.search(r"(?i)(memory|candidate|复用|经验|stable tool|稳定工具)", line)]
    result = _flow_command_result(
        root,
        args,
        "detect-from-workflow",
        "var/memory/evals/detect-from-workflow.md",
        "passed" if source_path and source_path.exists() else "failed",
        {
            "sourceEvidence": source,
            "sourcePath": _rel(source_path, root) if source_path else "",
            "signalCount": len(signals),
            "signals": signals[:20],
            "boundary": "read-only-suggestion-no-candidate-write",
        },
        scan=scan,
    )
    return result


def classify_candidate_suitability(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    if not selected:
        return _selection_failed_result(root, args, scan, "classify-candidate-suitability")
    selected_path = selected["path"]
    sensitive_issues = [
        issue
        for issue in scan["issues"]
        if issue.get("path") == selected_path and str(issue.get("code", "")).startswith("sensitive/")
    ]
    sensitive_gate_passed = not sensitive_issues
    notes = {
        "stableBeyondOneTask": _table_check(selected, "Stable beyond one task"),
        "futureReuseValue": _table_check(selected, "Future reuse value"),
        "sensitiveContentExcluded": _table_check(selected, "Sensitive content excluded"),
        "conflictCheckCompleted": _table_check(selected, "Conflict check completed"),
        "approvalRecorded": _table_check(selected, "Approval recorded"),
    }
    suitability = "ready-for-review"
    if notes["sensitiveContentExcluded"] != "yes" and not sensitive_gate_passed:
        suitability = "blocked-sensitive-review-required"
    elif notes["stableBeyondOneTask"] != "yes" or notes["conflictCheckCompleted"] != "yes":
        suitability = "needs-review"
    return _flow_command_result(
        root,
        args,
        "classify-candidate-suitability",
        "var/memory/evals/classify-candidate-suitability.md",
        "passed",
        {
            "candidateId": selected["memoryId"],
            "suitability": suitability,
            "reviewNotes": notes,
            "sensitiveGatePassed": sensitive_gate_passed,
            "sensitiveIssueCount": len(sensitive_issues),
            "boundary": "read-only-classification-no-memory-mutation",
        },
        scan=scan,
    )


def record_no_memory_disposition(args: Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    reason = args.reason or "No Memory candidate should be created for this input."
    return _flow_command_result(
        root,
        args,
        "record-no-memory-disposition",
        "var/memory/evals/no-memory-disposition.md",
        "passed",
        {
            "decision": "keep-in-workflow-or-report",
            "reason": reason,
            "sourceEvidence": args.source_path,
            "boundary": "runtime-disposition-report-only-no-memory-mutation",
        },
    )


def create_candidate(args: Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    memory_root = _resolve_under_root(root, args.memory_root)
    candidate_dir = _resolve_under_root(root, args.candidate)
    memory_id = (args.memory_id or _slugify(args.statement) or "memory-candidate").strip()
    source = args.source_path
    missing = []
    if not args.statement:
        missing.append("Statement")
    if not source:
        missing.append("SourcePath")
    state = "failed" if args.apply and missing else "passed"
    target = candidate_dir / f"{memory_id}.md"
    details: dict[str, Any] = {
        "memoryId": memory_id,
        "targetPath": _rel(target, root),
        "apply": bool(args.apply),
        "missingRequiredInputs": missing,
        "boundary": "controlled-candidate-create",
    }
    if args.apply and not missing:
        _ensure_under(root, target, candidate_dir)
        if target.exists():
            state = "failed"
            details["error"] = "target already exists"
        else:
            text = _render_memory_document(
                root=root,
                bucket="candidate",
                memory_id=memory_id,
                statement=args.statement,
                source=source,
                scope=args.scope,
                project_id=args.project_id,
                confidence=args.confidence,
                staleness_rule=args.staleness_rule or "review-after-new-evidence",
                review_after=args.review_after,
                decision="pending",
                target_state="candidate",
                reviewer="",
                reason=args.reason or "Created by controlled Memory command.",
            )
            _write_text(target, text)
    return _flow_command_result(root, args, "create-candidate", "var/memory/evals/create-candidate.md", state, details)


def classify_memory_type(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    scope = args.scope
    if selected:
        scope = str(selected["metadata"].get("scope", scope))
    allowed = {"global", "domain", "project", "agent-operation", "cross-project-experience", "general-constraint"}
    return _flow_command_result(
        root,
        args,
        "classify-memory-type",
        "var/memory/evals/classify-memory-type.md",
        "passed" if scope in allowed else "failed",
        {
            "candidateId": selected["memoryId"] if selected else "",
            "scope": scope,
            "allowedScopes": sorted(allowed),
            "boundary": "read-only-type-classification",
        },
        scan=scan,
    )


def detect_memory_duplicate_conflict(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    exact_statement_groups: dict[str, list[str]] = {}
    source_groups: dict[str, list[str]] = {}
    for entry in scan["entries"]:
        statement_key = _normalize_text(entry.get("statement", ""))
        if statement_key:
            exact_statement_groups.setdefault(statement_key, []).append(entry["path"])
        source_key = _normalize_text(entry.get("sourceEvidence", ""))
        if source_key:
            source_groups.setdefault(source_key, []).append(entry["path"])
    duplicate_statements = [paths for paths in exact_statement_groups.values() if len(paths) > 1]
    duplicate_sources = [paths for paths in source_groups.values() if len(paths) > 1]
    duplicate_ids = [issue for issue in scan["issues"] if issue["code"] == "memory/duplicate-memory-id"]
    conflict_count = len(duplicate_statements) + len(duplicate_sources) + len(duplicate_ids)
    return _flow_command_result(
        root,
        args,
        "detect-memory-duplicate-conflict",
        "var/memory/evals/detect-memory-duplicate-conflict.md",
        "failed" if duplicate_ids else "passed",
        {
            "candidateId": selected["memoryId"] if selected else "",
            "duplicateIdCount": len(duplicate_ids),
            "duplicateStatementGroups": duplicate_statements,
            "duplicateSourceGroups": duplicate_sources,
            "conflictCount": conflict_count,
            "semanticConflictBoundary": "exact-only; semantic conflict still requires human review",
        },
        scan=scan,
    )


def reject_or_merge_candidate(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    if not selected:
        return _selection_failed_result(root, args, scan, "reject-or-merge-candidate")
    decision = args.decision or "reject"
    return _flow_command_result(
        root,
        args,
        "reject-or-merge-candidate",
        "var/memory/evals/reject-or-merge-candidate.md",
        "passed",
        {
            "candidateId": selected["memoryId"],
            "decision": decision,
            "nextCommand": "delete-candidate"
            if decision in {"delete", "deleted"}
            else "archive-candidate"
            if decision in {"reject", "rejected"}
            else "revise-candidate",
            "apply": bool(args.apply),
            "boundary": "decision-routing-report-only",
        },
        scan=scan,
    )


def conflict_review_package(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    if not selected:
        return _selection_failed_result(root, args, scan, "conflict-review-package")
    duplicate_result = detect_memory_duplicate_conflict(args)
    return _flow_command_result(
        root,
        args,
        "conflict-review-package",
        "var/memory/evals/conflict-review-package.md",
        "passed",
        {
            "candidateId": selected["memoryId"],
            "priorityRule": "current user instruction > Project Fact > reviewed Knowledge > active Memory > candidate Memory > archived Memory",
            "duplicateConflictStatus": duplicate_result.get("statusJson", ""),
            "boundary": "read-only-conflict-review-input",
        },
        scan=scan,
    )


def apply_review_decision(args: Namespace) -> dict[str, Any]:
    decision = (args.decision or "").strip().lower()
    if decision in {"approve", "approved"}:
        return promote_reviewed(args)
    if decision in {"reject", "rejected"}:
        return archive_candidate(args)
    if decision in {"delete", "deleted"}:
        return delete_candidate(args)
    if decision in {"defer", "revise"}:
        return revise_candidate(args)
    root, scan, _selected = _command_context(args)
    return _flow_command_result(
        root,
        args,
        "apply-review-decision",
        "var/memory/evals/apply-review-decision.md",
        "failed",
        {"error": "Decision must be approve, reject, delete, defer, or revise.", "decision": decision},
        scan=scan,
    )


def promote_reviewed(args: Namespace) -> dict[str, Any]:
    return _apply_candidate_transition(args, "reviewed", "approve", "promote-reviewed", "var/memory/evals/promote-reviewed.md")


def archive_candidate(args: Namespace) -> dict[str, Any]:
    decision = (args.decision or "reject").strip().lower()
    if decision not in {"reject", "rejected", "archive", "archived"}:
        decision = "reject"
    return _apply_candidate_transition(args, "archive", decision, "archive-candidate", "var/memory/evals/archive-candidate.md")


def delete_candidate(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    if not selected:
        return _selection_failed_result(root, args, scan, "delete-candidate")
    candidate_dir = _resolve_under_root(root, args.candidate)
    source_path = root / selected["path"]
    decision = (args.decision or "delete").strip().lower()
    if decision not in {"reject", "rejected", "delete", "deleted"}:
        decision = "delete"
    details: dict[str, Any] = {
        "candidateId": selected["memoryId"],
        "sourcePath": _rel(source_path, root),
        "decision": decision,
        "apply": bool(args.apply),
        "boundary": "controlled-candidate-delete",
    }
    state = "passed"
    if args.apply:
        missing = _required_review_inputs(args)
        if missing:
            state = "failed"
            details["missingRequiredInputs"] = missing
        elif selected["bucket"] != "candidate":
            state = "failed"
            details["error"] = "delete-candidate only deletes files from the candidate bucket"
        elif not source_path.exists():
            state = "failed"
            details["error"] = "candidate file does not exist"
        else:
            _ensure_under(root, source_path, candidate_dir)
            source_path.unlink()
    return _flow_command_result(root, args, "delete-candidate", "var/memory/evals/delete-candidate.md", state, details, scan=scan)


def revise_candidate(args: Namespace) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    if not selected:
        return _selection_failed_result(root, args, scan, "revise-candidate")
    details: dict[str, Any] = {
        "candidateId": selected["memoryId"],
        "apply": bool(args.apply),
        "decision": args.decision or "revise",
        "boundary": "controlled-candidate-revision",
    }
    state = "passed"
    if args.apply:
        missing = _required_review_inputs(args)
        if missing:
            state = "failed"
            details["missingRequiredInputs"] = missing
        else:
            candidate_path = root / selected["path"]
            text = candidate_path.read_text(encoding="utf-8")
            if args.new_statement:
                text = _replace_section(text, "Memory Statement", args.new_statement)
            text = _replace_updated_at(text)
            text = _replace_promotion_decision(text, args.decision or "revise", "candidate", args.reviewer, args.reason or args.approval_note)
            candidate_path.write_text(text, encoding="utf-8", newline="\n")
    return _flow_command_result(root, args, "revise-candidate", "var/memory/evals/revise-candidate.md", state, details, scan=scan)


def sync_memory_index(args: Namespace) -> dict[str, Any]:
    root, scan, _selected = _command_context(args)
    return _flow_command_result(
        root,
        args,
        "sync-memory-index",
        "var/memory/evals/sync-memory-index.md",
        "passed",
        {
            "candidateCount": scan["counts"]["candidate"],
            "reviewedCount": scan["counts"]["reviewed"],
            "archiveCount": scan["counts"]["archive"],
            "indexPath": "harness/memory/MemoryIndex.md",
            "apply": bool(args.apply),
            "boundary": "index-sync-report-only-current-implementation",
        },
        scan=scan,
    )


def _memory_flow_steps() -> list[dict[str, Any]]:
    return [
        {
            "node": "A",
            "label": "Task Evidence / User Feedback",
            "requiredCommand": "verify-source-evidence",
            "coverage": "implemented",
            "currentCommand": "verify-source-evidence",
            "executionRule": "Verify workflow evidence or explicit user feedback source before any Memory candidate flow.",
        },
        {
            "node": "B",
            "label": "Detect Memory Candidate",
            "requiredCommand": "detect-from-workflow",
            "coverage": "implemented",
            "currentCommand": "detect-from-workflow",
            "executionRule": "Generate read-only candidate signals; do not write a candidate from detection alone.",
        },
        {
            "node": "C",
            "label": "Is it stable, non-private and reusable?",
            "requiredCommand": "classify-candidate-suitability",
            "coverage": "implemented",
            "currentCommand": "classify-candidate-suitability",
            "executionRule": "Use command output as review input; suitability may still be needs-review.",
        },
        {
            "node": "D",
            "label": "Keep in Workflow / Report only",
            "requiredCommand": "record-no-memory-disposition",
            "coverage": "implemented",
            "currentCommand": "record-no-memory-disposition",
            "executionRule": "Record runtime disposition when no Memory should be created.",
        },
        {
            "node": "E",
            "label": "Create Memory Candidate",
            "requiredCommand": "create-candidate",
            "coverage": "implemented",
            "currentCommand": "create-candidate",
            "executionRule": "Default dry-run; write candidate only with Apply and required source/statement inputs.",
        },
        {
            "node": "F",
            "label": "Classify Memory Type",
            "requiredCommand": "classify-memory-type",
            "coverage": "implemented",
            "currentCommand": "classify-memory-type",
            "executionRule": "Validate declared type against allowed Memory scopes.",
        },
        {
            "node": "G",
            "label": "Check Existing Memory",
            "requiredCommand": "validate-memory-store",
            "coverage": "implemented",
            "currentCommand": "validate-memory-store",
            "executionRule": "Run before any review or write path.",
        },
        {
            "node": "H",
            "label": "Duplicate or conflict?",
            "requiredCommand": "detect-memory-duplicate-conflict",
            "coverage": "implemented",
            "currentCommand": "detect-memory-duplicate-conflict",
            "executionRule": "Run exact duplicate and source conflict checks; semantic conflicts remain explicit review notes.",
        },
        {
            "node": "I",
            "label": "Reject or Merge Candidate",
            "requiredCommand": "reject-or-merge-candidate",
            "coverage": "implemented",
            "currentCommand": "reject-or-merge-candidate",
            "executionRule": "Route reject/merge decision to controlled command path.",
        },
        {
            "node": "J",
            "label": "Conflict Review",
            "requiredCommand": "conflict-review-package",
            "coverage": "implemented",
            "currentCommand": "conflict-review-package",
            "executionRule": "Generate conflict review package; Project Facts and reviewed Knowledge outrank Memory.",
        },
        {
            "node": "K",
            "label": "Human / Governance Review",
            "requiredCommand": "candidate-review-package",
            "coverage": "implemented",
            "currentCommand": "candidate-review-package",
            "executionRule": "Generate review input; do not assume reviewer decision.",
        },
        {
            "node": "L",
            "label": "Approved?",
            "requiredCommand": "apply-review-decision",
            "coverage": "implemented",
            "currentCommand": "apply-review-decision",
            "executionRule": "Route explicit decision to controlled apply command; default is dry-run.",
        },
        {
            "node": "M",
            "label": "Promote to active Memory",
            "requiredCommand": "promote-reviewed",
            "coverage": "implemented",
            "currentCommand": "promote-reviewed",
            "executionRule": "Move candidate to reviewed only with Apply, reviewer, approval note, and reason.",
        },
        {
            "node": "N",
            "label": "Mark rejected / archive or delete candidate",
            "requiredCommand": "archive-candidate|delete-candidate",
            "coverage": "implemented",
            "currentCommand": "archive-candidate or delete-candidate",
            "executionRule": "Move candidate to archive by default, or delete only when explicitly requested, with Apply, reviewer, approval note, and reason.",
        },
        {
            "node": "O",
            "label": "Revise Candidate",
            "requiredCommand": "revise-candidate",
            "coverage": "implemented",
            "currentCommand": "revise-candidate",
            "executionRule": "Revise only with controlled command or explicit user-directed patch.",
        },
        {
            "node": "P",
            "label": "Update MemoryIndex / source / reviewAfter",
            "requiredCommand": "sync-memory-index",
            "coverage": "implemented",
            "currentCommand": "sync-memory-index",
            "executionRule": "Generate index sync status after lifecycle changes.",
        },
        {
            "node": "Q",
            "label": "Closeout",
            "requiredCommand": "validate-memory-store",
            "coverage": "implemented",
            "currentCommand": "validate-memory-store",
            "executionRule": "Run store validation after every lifecycle action.",
        },
    ]


def _write_flow_status_report(result: dict[str, Any], report: Path) -> None:
    lines = [
        "# Memory Flow Status Report",
        "",
        f"- State: `{result['state']}`",
        f"- Architecture source: `{result['architectureSource']}`",
        f"- Flow coverage state: `{result['flowCoverageState']}`",
        f"- Step count: {result['stepCount']}",
        f"- Implemented steps: {result['implementedStepCount']}",
        f"- Partial steps: {result['partialStepCount']}",
        f"- Missing steps: {result['missingStepCount']}",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Flow Step Coverage",
        "",
        "| Node | Label | Coverage | Required command | Current command | Execution rule |",
        "|---|---|---|---|---|---|",
    ]
    for step in result["steps"]:
        lines.append(
            f"| {step['node']} | {step['label']} | `{step['coverage']}` | `{step['requiredCommand']}` | `{step['currentCommand']}` | {step['executionRule']} |"
        )
    _write_text(report, "\n".join(lines) + "\n")


def _command_context(args: Namespace) -> tuple[Path, dict[str, Any], dict[str, Any] | None]:
    root = Path(args.root).resolve()
    memory_root = _resolve_under_root(root, args.memory_root)
    candidate = _resolve_under_root(root, args.candidate)
    reviewed = _resolve_under_root(root, args.reviewed)
    archive = _resolve_under_root(root, args.archive)
    scan = _scan_memory_store(root, memory_root, candidate, reviewed, archive)
    selected, _issues = _select_candidate(root, scan["entries"], getattr(args, "candidate_id", ""), getattr(args, "candidate_path", ""))
    return root, scan, selected


def _flow_command_result(
    root: Path,
    args: Namespace,
    command: str,
    default_report: str,
    state: str,
    details: dict[str, Any],
    scan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = _resolve_report_path(root, args.report, default_report)
    status_json = root / f"var/memory/status/{command}.json"
    result = {
        "state": state,
        "scope": command,
        "report": _rel(report, root),
        "statusJson": _rel(status_json, root),
        "details": details,
        "boundary": details.get("boundary", "memory-command"),
    }
    if scan is not None:
        result["entryCount"] = scan["counts"]["total"]
        result["candidateCount"] = scan["counts"]["candidate"]
        result["reviewedCount"] = scan["counts"]["reviewed"]
        result["archiveCount"] = scan["counts"]["archive"]
    _write_flow_command_report(result, report)
    _write_json(status_json, result)
    return result


def _write_flow_command_report(result: dict[str, Any], report: Path) -> None:
    lines = [
        f"# Memory Command Report: {result['scope']}",
        "",
        f"- State: `{result['state']}`",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Details",
        "",
        "```json",
        json.dumps(result["details"], ensure_ascii=False, indent=2),
        "```",
    ]
    _write_text(report, "\n".join(lines) + "\n")


def _selection_failed_result(root: Path, args: Namespace, scan: dict[str, Any], command: str) -> dict[str, Any]:
    return _flow_command_result(
        root,
        args,
        command,
        f"var/memory/evals/{command}.md",
        "failed",
        {
            "error": "Candidate selection failed. Provide CandidateId or CandidatePath when there is not exactly one candidate.",
            "boundary": "read-only-no-memory-mutation",
        },
        scan=scan,
    )


def _source_for_command(args: Namespace, selected: dict[str, Any] | None) -> str:
    if getattr(args, "source_path", ""):
        return args.source_path
    if selected:
        return selected.get("sourceEvidence", "")
    return ""


def _source_path(root: Path, source: str) -> Path:
    path = Path(source)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return value[:64]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _required_review_inputs(args: Namespace) -> list[str]:
    missing = []
    if not args.reviewer:
        missing.append("Reviewer")
    if not args.approval_note:
        missing.append("ApprovalNote")
    if not args.reason:
        missing.append("Reason")
    return missing


def _apply_candidate_transition(args: Namespace, target_bucket: str, decision: str, command: str, default_report: str) -> dict[str, Any]:
    root, scan, selected = _command_context(args)
    if not selected:
        return _selection_failed_result(root, args, scan, command)
    candidate_dir = _resolve_under_root(root, args.candidate)
    target_dir = _resolve_under_root(root, args.reviewed if target_bucket == "reviewed" else args.archive)
    source_path = root / selected["path"]
    target_path = target_dir / source_path.name
    details: dict[str, Any] = {
        "candidateId": selected["memoryId"],
        "sourcePath": _rel(source_path, root),
        "targetPath": _rel(target_path, root),
        "targetBucket": target_bucket,
        "decision": decision,
        "apply": bool(args.apply),
        "boundary": f"controlled-{command}",
    }
    state = "passed"
    if args.apply:
        missing = _required_review_inputs(args)
        selected_errors = [
            issue
            for issue in scan["issues"]
            if issue["severity"] == "error" and issue.get("path") == selected["path"]
        ]
        if missing:
            state = "failed"
            details["missingRequiredInputs"] = missing
        elif selected_errors:
            state = "failed"
            details["blockingIssues"] = selected_errors
        elif target_path.exists():
            state = "failed"
            details["error"] = "target already exists"
        else:
            _ensure_under(root, source_path, candidate_dir)
            _ensure_under(root, target_path, target_dir)
            text = source_path.read_text(encoding="utf-8")
            asset_state = "reviewed" if target_bucket == "reviewed" else "archived"
            target_state = "reviewed" if target_bucket == "reviewed" else "archived"
            text = text.replace("/candidate/", f"/{target_bucket}/")
            text = _replace_updated_at(text)
            if target_bucket == "reviewed":
                text = _normalize_reviewed_memory_text(text, args.reviewer)
            text = re.sub(r"assetState:\s*\S+", f"assetState: {asset_state}", text, count=1)
            text = _replace_frontmatter_review(text, args.reviewer, datetime.now().date().isoformat(), decision)
            text = _replace_promotion_decision(text, decision, target_state, args.reviewer, args.reason)
            if decision in {"approve", "approved"}:
                text = _replace_review_notes(
                    text,
                    {
                        "Stable beyond one task": "yes",
                        "Future reuse value": "yes",
                        "Sensitive content excluded": "yes",
                        "Conflict check completed": "yes",
                        "Approval recorded": "yes",
                    },
                )
            _write_text(target_path, text)
            source_path.unlink()
    return _flow_command_result(root, args, command, default_report, state, details, scan=scan)


def _render_memory_document(
    root: Path,
    bucket: str,
    memory_id: str,
    statement: str,
    source: str,
    scope: str,
    project_id: str,
    confidence: str,
    staleness_rule: str,
    review_after: str,
    decision: str,
    target_state: str,
    reviewer: str,
    reason: str,
) -> str:
    path = f"harness/memory/{bucket}/{memory_id}.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.000 +08:00")
    frontmatter_reviewed_by = f"  reviewedBy: {reviewer}" if reviewer else "  reviewedBy:"
    promotion_reviewer = f"reviewer: {reviewer}" if reviewer else "reviewer:"
    return f"""---
documentName: {path}
version: v0.1.0-candidate
updatedAt: {now}
status: review
purpose: Memory candidate created by controlled Memory command.
scope:
  - memory-candidate
prerequisites:
  - harness/memory/MemoryPolicy.md
relatedDocuments:
  - {source}
outputTo:
  - {path}
owner: mixed
reviewAfter: {review_after}
supersededBy:
dependsOn:
  - harness/memory/MemoryPolicy.md
review:
{frontmatter_reviewed_by}
  reviewedAt:
  decision: pending
---
# {memory_id}

## 元数据

```yaml
memoryId: {memory_id}
assetState: candidate
scope: {scope}
projectId: {project_id}
sourceEvidence: {source}
confidence: {confidence}
reviewedBy:
reviewedAt:
stalenessRule: {staleness_rule}
```

## Memory Statement

{statement}

## Source And Evidence

| Source | Evidence Summary | Notes |
|---|---|---|
| `{source}` | 受控来源证据。 | 由稳定 Memory 命令创建。 |

## Applicability

待审核。

## Non-Applicability

不得用于项目私有事实、用户私有偏好、raw logs、settings、auth 或凭据。

## Review Notes

| Check | Result |
|---|---|
| Stable beyond one task | unknown |
| Future reuse value | unknown |
| Sensitive content excluded | unknown |
| Conflict check completed | unknown |
| Approval recorded | no |

## Promotion Decision

```yaml
decision: {decision}
targetState: {target_state}
{promotion_reviewer}
decisionDate:
reason: {reason}
```
"""


def _replace_frontmatter_review(text: str, reviewer: str, reviewed_at: str, decision: str) -> str:
    pattern = re.compile(r"review:\n  reviewedBy:.*\n  reviewedAt:.*\n  decision:.*", re.MULTILINE)
    replacement = f"review:\n  reviewedBy: {reviewer}\n  reviewedAt: {reviewed_at}\n  decision: {decision}"
    return pattern.sub(replacement, text, count=1)


def _replace_updated_at(text: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.000 +08:00")
    return re.sub(r"updatedAt:\s*.*", f"updatedAt: {now}", text, count=1)


def _replace_review_notes(text: str, values: dict[str, str]) -> str:
    for check, result in values.items():
        pattern = re.compile(rf"(\| {re.escape(check)} \| )[^|]+(\|)")
        text = pattern.sub(rf"\1{result} \2", text, count=1)
    return text


def _normalize_reviewed_memory_text(text: str, reviewer: str) -> str:
    today = datetime.now().date().isoformat()
    text = re.sub(r"version:\s*.*", "version: v1.0.0-reviewed", text, count=1)
    text = re.sub(r"status:\s*.*", "status: active", text, count=1)
    text = re.sub(r"purpose:\s*.*", "purpose: 记录经用户审核批准并受 Memory policy 管控的 reviewed Memory。", text, count=1)
    text = re.sub(r"scope:\n(?:  - .*\n)+", "scope:\n  - reviewed-memory\n", text, count=1)
    text = re.sub(r"(?m)^reviewedBy:\s*$", f"reviewedBy: {reviewer}", text, count=1)
    text = re.sub(r"(?m)^reviewedAt:\s*$", f"reviewedAt: {today}", text, count=1)
    text = _replace_section(
        text,
        "Applicability",
        "适用于本 Memory Statement 所描述的通用、非私有、可复用场景；具体任务仍以用户当前指令、正式文档、Project Fact、reviewed Knowledge 和 active Memory 冲突优先级为准。",
    )
    return text


def _replace_promotion_decision(text: str, decision: str, target_state: str, reviewer: str, reason: str) -> str:
    replacement = f"""## Promotion Decision

```yaml
decision: {decision}
targetState: {target_state}
reviewer: {reviewer}
decisionDate: {datetime.now().date().isoformat()}
reason: {reason}
```"""
    return re.sub(r"## Promotion Decision\s+```yaml\s+.*?```", replacement, text, flags=re.DOTALL, count=1)


def _replace_section(text: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(## {re.escape(heading)}\n\n).*?(?=\n## |\Z)", re.DOTALL)
    return pattern.sub(rf"\1{body.strip()}\n", text, count=1)


def _ensure_under(root: Path, path: Path, boundary: Path) -> None:
    resolved = path.resolve()
    try:
        resolved.relative_to(boundary.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Refusing to write outside expected boundary: {resolved}") from exc
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Refusing to write outside root: {resolved}") from exc


def _scan_memory_store(root: Path, memory_root: Path, candidate: Path, reviewed: Path, archive: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []

    for bucket_name, bucket_path in {
        "candidate": candidate,
        "reviewed": reviewed,
        "archive": archive,
    }.items():
        if not bucket_path.exists() or not bucket_path.is_dir():
            issues.append(_issue("error", "memory/directory-missing", bucket_path, root, f"{bucket_name} directory is missing."))
            continue
        for path in sorted(bucket_path.rglob("*.md")):
            entry = _parse_memory_file(root, path, bucket_name)
            entries.append(entry)
            issues.extend(_validate_entry(root, entry))

    ids: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        memory_id = entry.get("memoryId")
        if memory_id:
            ids.setdefault(memory_id, []).append(entry)
    for memory_id, matches in sorted(ids.items()):
        if len(matches) > 1:
            paths = [match["path"] for match in matches]
            for match in matches:
                issues.append(_issue(
                    "error",
                    "memory/duplicate-memory-id",
                    root / match["path"],
                    root,
                    f"Duplicate memoryId '{memory_id}' appears in {', '.join(paths)}.",
                    {"memoryId": memory_id, "paths": paths},
                ))

    return {
        "memoryRoot": _rel(memory_root, root),
        "entries": entries,
        "issues": issues,
        "counts": {
            "candidate": sum(1 for entry in entries if entry["bucket"] == "candidate"),
            "reviewed": sum(1 for entry in entries if entry["bucket"] == "reviewed"),
            "archive": sum(1 for entry in entries if entry["bucket"] == "archive"),
            "total": len(entries),
        },
    }


def _parse_memory_file(root: Path, path: Path, bucket: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    frontmatter_raw, body = _split_frontmatter(text)
    frontmatter = _parse_yaml_like(frontmatter_raw or "") if frontmatter_raw is not None else {}
    metadata = _extract_section_yaml(body, ["元数据", "Metadata"])
    decision = _extract_section_yaml(body, ["Promotion Decision", "晋升决策"])
    statement = _extract_section_text(body, ["Memory Statement", "记忆正文"])
    source_section = _extract_section_text(body, ["Source And Evidence", "来源和证据"])
    review_notes = _extract_section_text(body, ["Review Notes", "审核记录"])
    memory_id = str(metadata.get("memoryId", "")).strip()
    asset_state = str(metadata.get("assetState", "")).strip()
    source_evidence = str(metadata.get("sourceEvidence", "")).strip()
    review = frontmatter.get("review") if isinstance(frontmatter.get("review"), dict) else {}
    return {
        "path": _rel(path, root),
        "bucket": bucket,
        "text": text,
        "frontmatterRaw": frontmatter_raw,
        "frontmatter": frontmatter,
        "metadata": metadata,
        "promotionDecision": decision,
        "memoryId": memory_id,
        "assetState": asset_state,
        "sourceEvidence": source_evidence,
        "statement": statement,
        "sourceSection": source_section,
        "reviewNotes": review_notes,
        "frontmatterReview": review,
    }


def _validate_entry(root: Path, entry: dict[str, Any]) -> list[dict[str, Any]]:
    path = root / entry["path"]
    issues: list[dict[str, Any]] = []
    frontmatter = entry["frontmatter"]
    metadata = entry["metadata"]
    review = entry["frontmatterReview"]
    bucket = entry["bucket"]

    if entry["frontmatterRaw"] is None:
        issues.append(_issue("error", "memory/frontmatter-missing", path, root, "Markdown frontmatter is missing."))
    else:
        for key in REQUIRED_FRONTMATTER_KEYS:
            if key not in frontmatter:
                issues.append(_issue("error", "memory/frontmatter-key-missing", path, root, f"Frontmatter key '{key}' is missing.", {"key": key}))
        status = str(frontmatter.get("status", "")).strip()
        if status and status not in ALLOWED_DOC_STATUSES:
            issues.append(_issue("error", "memory/frontmatter-status-invalid", path, root, f"Invalid document status '{status}'.", {"status": status}))
        if not isinstance(frontmatter.get("review"), dict):
            issues.append(_issue("error", "memory/review-fields-missing", path, root, "Frontmatter review object is missing."))
        else:
            for key in REQUIRED_REVIEW_KEYS:
                if key not in review:
                    issues.append(_issue("error", "memory/review-field-missing", path, root, f"Frontmatter review.{key} is missing.", {"key": key}))

    for key in REQUIRED_MEMORY_KEYS:
        if not str(metadata.get(key, "")).strip():
            issues.append(_issue("error", "memory/metadata-key-missing", path, root, f"Memory metadata key '{key}' is missing.", {"key": key}))

    expected_state = EXPECTED_ASSET_STATE_BY_BUCKET[bucket]
    asset_state = str(metadata.get("assetState", "")).strip()
    if asset_state and asset_state != expected_state:
        issues.append(_issue(
            "error",
            "memory/asset-state-invalid",
            path,
            root,
            f"Memory in {bucket} must declare assetState={expected_state}, found {asset_state}.",
            {"expected": expected_state, "actual": asset_state},
        ))

    if not entry["sourceEvidence"]:
        issues.append(_issue("error", "memory/source-evidence-missing", path, root, "sourceEvidence is missing."))
    if not entry["sourceSection"].strip():
        issues.append(_issue("warning", "memory/source-section-missing", path, root, "Source And Evidence section is missing or empty."))
    if not entry["statement"].strip():
        issues.append(_issue("error", "memory/statement-missing", path, root, "Memory Statement section is missing or empty."))

    for code, pattern in SENSITIVE_PATTERNS:
        if pattern.search(entry["text"]):
            issues.append(_issue("error", code, path, root, "Sensitive or local-only pattern detected in Memory file."))

    if bucket == "reviewed":
        for key in REQUIRED_REVIEW_KEYS:
            if not str(review.get(key, "")).strip():
                issues.append(_issue("error", "memory/reviewed-review-value-missing", path, root, f"Reviewed Memory requires non-empty review.{key}.", {"key": key}))
        decision = str(entry["promotionDecision"].get("decision", "")).strip()
        if decision not in {"approve", "approved"}:
            issues.append(_issue("error", "memory/reviewed-promotion-decision-invalid", path, root, "Reviewed Memory must carry approved promotion decision."))

    if bucket == "candidate":
        decision = str(entry["promotionDecision"].get("decision", "")).strip()
        target = str(entry["promotionDecision"].get("targetState", "")).strip()
        if not decision:
            issues.append(_issue("warning", "memory/candidate-decision-missing", path, root, "Candidate has no Promotion Decision decision."))
        elif decision not in {"approve", "approved", "reject", "rejected", "defer", "revise", "pending"}:
            issues.append(_issue("error", "memory/candidate-decision-invalid", path, root, f"Unsupported candidate decision '{decision}'.", {"decision": decision}))
        if target and target not in {"candidate", "reviewed", "archived"}:
            issues.append(_issue("error", "memory/candidate-target-state-invalid", path, root, f"Unsupported targetState '{target}'.", {"targetState": target}))

    if bucket == "archive":
        decision = str(entry["promotionDecision"].get("decision", "")).strip()
        if decision in {"approve", "approved"}:
            issues.append(_issue("error", "memory/archive-approved-decision-invalid", path, root, "Archived Memory cannot carry approved decision."))

    return issues


def _validation_result(root: Path, scan: dict[str, Any], report: Path, status_json: Path) -> dict[str, Any]:
    errors = [issue for issue in scan["issues"] if issue["severity"] == "error"]
    warnings = [issue for issue in scan["issues"] if issue["severity"] == "warning"]
    candidate_states = [
        {
            "memoryId": entry["memoryId"],
            "path": entry["path"],
            "assetState": entry["assetState"],
            "frontmatterDecision": entry["frontmatterReview"].get("decision", ""),
            "promotionDecision": entry["promotionDecision"].get("decision", ""),
            "targetState": entry["promotionDecision"].get("targetState", ""),
        }
        for entry in scan["entries"]
        if entry["bucket"] == "candidate"
    ]
    return {
        "state": "failed" if errors else "passed",
        "scope": "memory-store-validation",
        "memoryRoot": scan["memoryRoot"],
        "report": _rel(report, root),
        "statusJson": _rel(status_json, root),
        "entryCount": scan["counts"]["total"],
        "candidateCount": scan["counts"]["candidate"],
        "reviewedCount": scan["counts"]["reviewed"],
        "archiveCount": scan["counts"]["archive"],
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "blockingIssues": errors,
        "candidateStates": candidate_states,
        "checks": [
            "directory-structure",
            "frontmatter-required-fields",
            "review-fields",
            "memory-metadata",
            "asset-state-by-directory",
            "source-evidence",
            "duplicate-memory-id",
            "sensitive-patterns",
            "reviewed-approval-state",
        ],
        "boundary": "read-only-validation-no-memory-mutation",
    }


def _write_validation_report(result: dict[str, Any], scan: dict[str, Any], report: Path) -> None:
    lines = [
        "# Memory Store Validation Report",
        "",
        f"- State: `{result['state']}`",
        f"- Entry count: {result['entryCount']}",
        f"- Candidate count: {result['candidateCount']}",
        f"- Reviewed count: {result['reviewedCount']}",
        f"- Archive count: {result['archiveCount']}",
        f"- Error count: {result['errorCount']}",
        f"- Warning count: {result['warningCount']}",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Candidate States",
        "",
        "| memoryId | path | assetState | frontmatter decision | promotion decision | targetState |",
        "|---|---|---|---|---|---|",
    ]
    for state in result["candidateStates"]:
        lines.append(
            f"| `{state['memoryId']}` | `{state['path']}` | `{state['assetState']}` | `{state['frontmatterDecision']}` | `{state['promotionDecision']}` | `{state['targetState']}` |"
        )
    lines.extend(["", "## Issues", ""])
    if scan["issues"]:
        lines.append("| severity | code | path | message |")
        lines.append("|---|---|---|---|")
        for issue in scan["issues"]:
            lines.append(f"| {issue['severity']} | `{issue['code']}` | `{issue.get('path', '')}` | {issue['message']} |")
    else:
        lines.append("No issues.")
    _write_text(report, "\n".join(lines) + "\n")


def _write_review_package(result: dict[str, Any], selected: dict[str, Any] | None, scan: dict[str, Any], issues: list[dict[str, Any]], report: Path) -> None:
    lines = [
        "# Memory Candidate Review Package",
        "",
        f"- State: `{result['state']}`",
        f"- Boundary: `{result['boundary']}`",
        f"- Generated at: `{datetime.now().isoformat(timespec='seconds')}`",
        "",
    ]
    if not selected:
        lines.extend(["## Selection Failure", ""])
        for issue in issues:
            lines.append(f"- `{issue['severity']}` `{issue['code']}`: {issue['message']}")
        _write_text(report, "\n".join(lines) + "\n")
        return

    review_state = _candidate_review_state(selected)
    candidate_issues = [issue for issue in issues if issue.get("path") == selected["path"]]
    lines.extend([
        "## Candidate Summary",
        "",
        f"- memoryId: `{selected['memoryId']}`",
        f"- path: `{selected['path']}`",
        f"- assetState: `{selected['assetState']}`",
        f"- sourceEvidence: `{selected['sourceEvidence']}`",
        f"- confidence: `{selected['metadata'].get('confidence', '')}`",
        f"- stalenessRule: `{selected['metadata'].get('stalenessRule', '')}`",
        f"- current frontmatter review decision: `{review_state['frontmatterDecision']}`",
        f"- current promotion decision: `{review_state['promotionDecision']}`",
        f"- current targetState: `{review_state['targetState']}`",
        "",
        "## Memory Statement",
        "",
        selected["statement"].strip() or "_Missing statement._",
        "",
        "## Review Gate Summary",
        "",
        "| Check | Result | Notes |",
        "|---|---|---|",
        f"| Stable beyond one task | `{_table_check(selected, 'Stable beyond one task')}` | 来自候选 Review Notes。 |",
        f"| Future reuse value | `{_table_check(selected, 'Future reuse value')}` | 来自候选 Review Notes。 |",
        f"| Sensitive content excluded | `{_table_check(selected, 'Sensitive content excluded')}` | 门禁也会扫描敏感模式。 |",
        f"| Conflict check completed | `{_table_check(selected, 'Conflict check completed')}` | 必须在 approve 前完成。 |",
        f"| Approval recorded | `{_table_check(selected, 'Approval recorded')}` | 写入命令要求用户明确审核输入。 |",
        "",
        "## Validation Issues For This Candidate",
        "",
    ])
    if candidate_issues:
        lines.append("| severity | code | message |")
        lines.append("|---|---|---|")
        for issue in candidate_issues:
            lines.append(f"| {issue['severity']} | `{issue['code']}` | {issue['message']} |")
    else:
        lines.append("No candidate-specific validation issues.")

    lines.extend([
        "",
        "## Reviewer Decision Options",
        "",
        "| Decision | Meaning | Controlled command |",
        "|---|---|---|",
        "| approve | 候选已足够通用、非私有、可复用，可进入 reviewed Memory。 | `promote-reviewed`。 |",
        "| reject | 候选不应进入 Memory，默认保留归档审计记录。 | `archive-candidate`。 |",
        "| delete | 用户明确要求候选不保留在 archive。 | `delete-candidate`。 |",
        "| defer | 候选仍有价值但证据不足或需要更多真实任务验证。 | `revise-candidate` 更新 defer metadata。 |",
        "| revise | 候选需要改写后再审。 | `revise-candidate` 后重新运行 gate 和 review package。 |",
        "",
        "## Required Reviewer Input",
        "",
        "```yaml",
        "decision: approve | reject | delete | defer | revise",
        "reviewer: <human-reviewer>",
        "decisionDate: <yyyy-mm-dd>",
        "approvalNote: <required for approve/reject/delete/defer/revise apply>",
        "reason: <why this decision is correct>",
        "```",
        "",
        "## Boundary",
        "",
        "This package is review input only. It does not write reviewed Memory, archive or delete candidate Memory, or change project facts.",
    ])
    _write_text(report, "\n".join(lines) + "\n")


def _candidate_review_state(entry: dict[str, Any] | None) -> dict[str, str]:
    if not entry:
        return {}
    return {
        "frontmatterDecision": str(entry["frontmatterReview"].get("decision", "")),
        "promotionDecision": str(entry["promotionDecision"].get("decision", "")),
        "targetState": str(entry["promotionDecision"].get("targetState", "")),
    }


def _select_candidate(root: Path, entries: list[dict[str, Any]], candidate_id: str, candidate_path: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    candidates = [entry for entry in entries if entry["bucket"] == "candidate"]
    if candidate_path:
        normalized = candidate_path.replace("\\", "/")
        matches = [entry for entry in candidates if entry["path"] == normalized or str((root / entry["path"]).resolve()) == str(Path(candidate_path).resolve())]
    elif candidate_id:
        matches = [entry for entry in candidates if entry["memoryId"] == candidate_id]
    elif len(candidates) == 1:
        matches = candidates
    else:
        matches = []
        issues.append(_issue("error", "memory/candidate-selection-required", root, root, "CandidateId or CandidatePath is required when there is not exactly one candidate."))

    if not matches:
        if not issues:
            issues.append(_issue("error", "memory/candidate-not-found", root, root, "Candidate Memory was not found."))
        return None, issues
    if len(matches) > 1:
        issues.append(_issue("error", "memory/candidate-selection-ambiguous", root, root, "Candidate selection matched multiple files."))
        return None, issues
    return matches[0], issues


def _run_self_test(root: Path, args: Namespace) -> dict[str, Any]:
    fixture = root / "var/tmp/memory-tool-self-test"
    _safe_runtime_rmtree(root, fixture)
    memory_root = fixture / "harness/memory"
    candidate = memory_root / "candidate"
    reviewed = memory_root / "reviewed"
    archive = memory_root / "archive"
    candidate.mkdir(parents=True, exist_ok=True)
    reviewed.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)

    (candidate / "missing-frontmatter.md").write_text("# Missing Frontmatter\n\nNo metadata.\n", encoding="utf-8")
    _write_text(candidate / "duplicate-a.md", _memory_fixture("duplicate-memory", source="evidence/a.md"))
    _write_text(candidate / "duplicate-b.md", _memory_fixture("duplicate-memory", source="evidence/b.md"))
    _write_text(candidate / "sensitive.md", _memory_fixture("sensitive-memory", extra="password: 1234567890\n"))
    _write_text(candidate / "missing-source.md", _memory_fixture("missing-source", source=""))
    _write_text(candidate / "illegal-state.md", _memory_fixture("illegal-state", asset_state="reviewed", source="evidence/c.md"))
    _write_text(candidate / "missing-review-fields.md", _memory_fixture("missing-review", source="evidence/d.md", include_review=False))

    scan = _scan_memory_store(root, memory_root, candidate, reviewed, archive)
    issue_codes = {issue["code"] for issue in scan["issues"]}
    expected_codes = {
        "memory/frontmatter-missing",
        "memory/duplicate-memory-id",
        "sensitive/credential-assignment",
        "memory/metadata-key-missing",
        "memory/source-evidence-missing",
        "memory/asset-state-invalid",
        "memory/review-fields-missing",
    }
    missing = sorted(expected_codes - issue_codes)
    report = _resolve_report_path(root, args.report, "var/memory/evals/memory-tool-self-test.md")
    status_json = root / "var/memory/status/memory-tool-self-test.json"
    result = {
        "state": "passed" if not missing else "failed",
        "scope": "memory-tool-self-test",
        "fixture": _rel(fixture, root),
        "expectedIssueCodes": sorted(expected_codes),
        "detectedIssueCodes": sorted(issue_codes),
        "missingExpectedIssueCodes": missing,
        "report": _rel(report, root),
        "statusJson": _rel(status_json, root),
        "boundary": "runtime-fixture-only-no-memory-store-mutation",
    }
    _write_self_test_report(result, scan, report)
    _write_json(status_json, result)
    return result


def _write_self_test_report(result: dict[str, Any], scan: dict[str, Any], report: Path) -> None:
    lines = [
        "# Memory Tool Self-Test Report",
        "",
        f"- State: `{result['state']}`",
        f"- Fixture: `{result['fixture']}`",
        f"- Boundary: `{result['boundary']}`",
        "",
        "## Expected Issue Codes",
        "",
    ]
    for code in result["expectedIssueCodes"]:
        marker = "ok" if code in result["detectedIssueCodes"] else "missing"
        lines.append(f"- `{code}`: {marker}")
    lines.extend(["", "## Detected Issues", "", "| severity | code | path | message |", "|---|---|---|---|"])
    for issue in scan["issues"]:
        lines.append(f"| {issue['severity']} | `{issue['code']}` | `{issue.get('path', '')}` | {issue['message']} |")
    _write_text(report, "\n".join(lines) + "\n")


def _memory_fixture(memory_id: str, asset_state: str = "candidate", source: str = "evidence.md", include_review: bool = True, extra: str = "") -> str:
    review_block = "review:\n  reviewedBy:\n  reviewedAt:\n  decision: pending\n" if include_review else ""
    return f"""---
documentName: harness/memory/candidate/{memory_id}.md
version: v0.1.0-test
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: review
purpose: Test fixture.
scope:
  - memory-candidate
prerequisites:
  - harness/memory/MemoryPolicy.md
relatedDocuments:
  - harness/memory/MemoryPolicy.md
outputTo:
  - harness/memory/candidate/{memory_id}.md
owner: agent
reviewAfter: 2026-07-11
supersededBy:
dependsOn:
  - harness/memory/MemoryPolicy.md
{review_block}---
# Fixture

## 元数据

```yaml
memoryId: {memory_id}
assetState: {asset_state}
scope: agent-operation
projectId: null
sourceEvidence: {source}
confidence: medium
reviewedBy:
reviewedAt:
stalenessRule: test
```

## Memory Statement

Reusable test memory.

{extra}
## Source And Evidence

| Source | Evidence Summary | Notes |
|---|---|---|
| `{source}` | test | test |

## Review Notes

| Check | Result |
|---|---|
| Stable beyond one task | unknown |
| Future reuse value | yes |
| Sensitive content excluded | yes |
| Conflict check completed | partial |
| Approval recorded | no |

## Promotion Decision

```yaml
decision: defer
targetState: candidate
reviewer:
decisionDate:
reason: test
```
"""


def _split_frontmatter(text: str) -> tuple[str | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return None, text


def _parse_yaml_like(block: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]
    for raw_line in block.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        stripped = raw_line.strip()
        if stripped.startswith("- "):
            continue
        if ":" not in stripped:
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else result
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value
    return result


def _extract_section_yaml(body: str, headings: list[str]) -> dict[str, str]:
    section = _extract_section_text(body, headings)
    match = re.search(r"```yaml\s*(.*?)```", section, re.DOTALL | re.IGNORECASE)
    if not match:
        return {}
    flat = _parse_yaml_like(match.group(1))
    return {key: str(value) if not isinstance(value, dict) else "" for key, value in flat.items()}


def _extract_section_text(body: str, headings: list[str]) -> str:
    for heading in headings:
        pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
        match = pattern.search(body)
        if not match:
            continue
        start = match.end()
        next_match = re.search(r"^##\s+", body[start:], re.MULTILINE)
        end = start + next_match.start() if next_match else len(body)
        return body[start:end].strip()
    return ""


def _table_check(entry: dict[str, Any], check_name: str) -> str:
    pattern = re.compile(rf"\|\s*{re.escape(check_name)}\s*\|\s*([^|]+)\|", re.IGNORECASE)
    match = pattern.search(entry.get("reviewNotes", ""))
    if not match:
        return "unknown"
    return match.group(1).strip().strip("`")


def _issue(severity: str, code: str, path: Path, root: Path, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    issue = {
        "severity": severity,
        "code": code,
        "path": _rel(path, root),
        "message": message,
    }
    if details:
        issue["details"] = details
    return issue


def _has_error(issues: list[dict[str, Any]]) -> bool:
    return any(issue["severity"] == "error" for issue in issues)


def _resolve_under_root(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _resolve_report_path(root: Path, value: str, default: str) -> Path:
    target = Path(value or default)
    if not target.is_absolute():
        target = root / target
    return target.resolve()


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    _write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _safe_runtime_rmtree(root: Path, path: Path) -> None:
    resolved = path.resolve()
    allowed = (root / "var/tmp").resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise RuntimeError(f"Refusing to remove non-runtime fixture path: {resolved}") from exc
    if resolved.exists():
        shutil.rmtree(resolved)
