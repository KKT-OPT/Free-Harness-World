# Regression Policy

Status: draft
Version: v0.1.0-p11.6
Date: 2026-06-10

## Purpose

This policy defines when Harness-managed work must be rerun, rechecked or explicitly closed with risk after a repair.

Regression checks make repair evidence reviewable. They do not replace runtime execution, stable tools, user acceptance or governance review.

## When Regression Is Required

Run a regression check, or record a reviewed skip reason, after any of these changes:

| Trigger | Required Regression |
|---|---|
| Source or test code changed | Relevant project build, test or validation command through stable tool surface. |
| Stable tool behavior or parameters changed | Tool contract check and at least one representative invocation when safe. |
| Documentation route changed | Index/path scan and stale-reference scan. |
| Project facts changed | Project package/routing check and affected workflow evidence review. |
| Governance or security policy changed | Sensitive-boundary scan and policy-conflict review. |
| Template changed | Template route check and one representative evidence/report shape review. |
| Failure repaired | Rerun the failed validation or record why rerun is unsafe or out of scope. |
| Knowledge, Memory, Skill or RAG candidate changed | Promotion-boundary check; do not auto-promote. |

## Regression Types

| Type | Purpose |
|---|---|
| `document-regression` | Check references, index routes, headings, stale phase state and template discoverability. |
| `governance-regression` | Check policy conflicts, approval needs, promotion boundaries and archive rules. |
| `tool-regression` | Rerun or dry-run stable tool surfaces with redacted evidence. |
| `workflow-regression` | Confirm Task Brief, trace summary, result contract and acceptance remain coherent. |
| `security-regression` | Check sensitive terms, concrete private paths, raw logs and credential leakage. |
| `project-regression` | Verify project package, routing, validation profile and project fact boundaries. |
| `knowledge-regression` | Check Knowledge/Memory/Skill/RAG candidate boundaries and review status. |

## Regression Record

Record regression in workflow evidence or a redacted report with these fields:

| Field | Rule |
|---|---|
| `regressionId` | Stable id. |
| `trigger` | Why the regression was required. |
| `scope` | Files, policies, project or tool surfaces checked. |
| `type` | One or more regression types. |
| `runtime` | Runtime used, if any. |
| `commandSurface` | Stable tool name or `none`. |
| `result` | `passed`, `failed`, `partial`, `skipped` or `blocked`. |
| `evidence` | Redacted workflow/report/status path or summary. |
| `remainingRisk` | Residual risk or `none`. |
| `nextAction` | `none`, `repair-needed`, `review-needed`, `clarification-needed` or `blocked`. |

## Repair Closure Rule

A repair can close only when all of the following are true:

1. The failed criterion is still visible in workflow evidence.
2. Failure attribution identifies a primary dimension.
3. The repair action is scoped and approved.
4. Required regression has passed, or a skip reason is explicitly recorded.
5. Residual risk is recorded.
6. The Common Task Result Contract points to the relevant evidence.
7. Governance candidates are listed without auto-promotion.

## Forbidden Closures

Do not close a repair when:

- the failed criterion was removed instead of repaired;
- the rerun was skipped without an explicit reason;
- only model confidence is used in place of validation;
- raw logs or status JSON contents are copied into tracked docs;
- sensitive settings, credentials, auth files or private repository paths are exposed;
- promotion candidates are silently written into Knowledge, Memory or Skill assets.

## P11.6 Application

P11.6 rewrites selected ideas from the old Harness regression policy into this current Harness Root policy.

The P11.4 repaired Java/Maven validation is the first recorded pattern:

```text
initial tool/execution failure
-> attribution as execution with secondary tool dimension
-> repair through writable Harness-managed local repo override
-> rerun stable Java/Maven validation
-> record passed regression and repaired closure
```

This does not prove full Java project landing or full Harness production readiness. It proves the repair-loop evidence pattern for a controlled demo project.
