# Harness Validation Plan

Status: draft
Version: v0.3.0-p11.7
Date: 2026-06-10

## Purpose

This plan defines how P11 validates the Harness framework lifecycle.

P11 is not merely Java feature testing. It validates whether Harness can guide an agent from task intake to verified result and governance closeout.

## Validation Principles

1. Start from `AGENTS.md`, `harness/INDEX.md`, and `harness/PLANS.md`.
2. Use a controlled project under `projects/<project-id>`.
3. Use stable tool surfaces.
4. Produce workflow evidence.
5. Produce trace summary.
6. Produce validation report.
7. Produce failure attribution if anything fails.
8. Rerun or explicitly skip required regression after repair.
9. Return Common Task Result Contract.
10. Do not auto-promote candidates.
11. Do not expose credentials, settings, auth files or raw logs.
12. Classify governance candidates with disposition, target and approval requirement.

## Validation Scope

| Area | P11 Question |
|---|---|
| Entry | Can an agent discover Harness Root and current plans? |
| Task Intake | Can a natural prompt become a Task Brief? |
| Readiness | Are missing or risky fields handled? |
| Context | Is context loaded with provenance and exclusions? |
| Project Routing | Does `projectId` resolve to a managed project? |
| Tooling | Are stable tools used instead of ad hoc command chains? |
| Observability | Is a trace summary produced? |
| Verification | Is validation repeatable and summarized? |
| Repair Loop | Are failed, partial or repaired results attributed and regressed before closure? |
| Reports | Is the result report-first and redacted? |
| Governance | Are candidates listed without auto-promotion? |
| Closeout | Are candidate dispositions, approval requirements and deferred backlog clear? |

## P11 Output

P11 must produce a redacted report under:

```text
harness/reports/redacted/
```

and project workflow evidence under:

```text
projects/<project-id>/docs/project/workflow/
```

## Failure Handling

Any failed, partial or blocked criterion must link to:

```text
harness/observability/failure-attribution/FailureAttributionPolicy.md
harness/governance/verification/RegressionPolicy.md
```

and define a repair path.

## Repair Closure

Any repaired result must record:

- the original failed criterion;
- the attribution dimension;
- the repair action;
- the regression or explicit skip reason;
- residual risk;
- Common Task Result Contract output.

A repaired result may be marked `passed` only after the required regression passes or the skip reason is reviewed and recorded.
