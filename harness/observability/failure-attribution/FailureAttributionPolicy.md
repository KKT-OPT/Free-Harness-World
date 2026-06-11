# Failure Attribution Policy

Status: draft
Version: v0.2.0-p11.6
Date: 2026-06-10

## Purpose

This policy defines how Harness attributes failures and closes repair loops without blaming every failure on the model.

Failure attribution is required for failed, partial, blocked or repaired validation. A repaired task may finish with `passed`, but it still needs an attribution record when an earlier failure affected the task outcome.

## Scope

This policy applies to:

- P11 validation and later Harness-managed workflow evidence;
- stable tool validation failures;
- documentation, governance, project package and routing validation failures;
- any task result that returns `failed`, `partial`, `blocked`, `repaired` or `passed-after-repair`.

This policy does not execute repairs by itself. It defines the record required before repair, the rerun required after repair, and the closure conditions.

## Attribution Dimensions

| Dimension | Meaning | Typical Repair Direction |
|---|---|---|
| `model` | Reasoning, instruction following, or generation failure. | Restate task, reduce ambiguity, add targeted context or ask user. |
| `context` | Missing, stale, excessive, or polluted context. | Reload authoritative docs, exclude polluted context, update routing. |
| `tool` | Stable tool interface, parameter, output, or interpretation failure. | Fix tool contract, parameter, parser, docs or wrapper behavior. |
| `execution` | Runtime, sandbox, filesystem, command, permission, or environment failure. | Change approved execution boundary, writable path, retry policy or environment. |
| `lifecycle` | Skipped Task Brief, readiness, plan, evidence, acceptance, or repair loop. | Recreate missing lifecycle evidence and rerun the required check. |
| `verification` | Missing, insufficient, stale, or incorrectly interpreted validation. | Add or rerun validation, document skipped checks and residual risk. |
| `governance` | Security, approval, redaction, promotion, archive, or git-boundary failure. | Stop promotion, redact, request approval, update policy or archive route. |
| `project-fact` | Missing, stale, conflicting, or misplaced project facts. | Update project facts through review; do not patch root registry as a shortcut. |
| `user-input` | Ambiguous, changed, or conflicting user requirement. | Ask clarification or record the newest instruction as controlling scope. |
| `external` | External dependency, network, toolchain, or third-party service failure. | Retry only if safe, isolate dependency, record fallback or defer. |

Multiple dimensions may apply. Record the primary dimension and any secondary dimensions.

## Required Record

Failure attribution must include:

| Field | Rule |
|---|---|
| `failureId` | Stable id for the failure event. |
| `taskId` | Workflow or task id. |
| `projectId` | Managed project id or `none`. |
| `failedCriterion` | Acceptance or validation criterion that failed. |
| `failureStage` | Stage such as intake, routing, tool, validation, evidence, governance or acceptance. |
| `affectedAsset` | Harness-relative file, tool or evidence path. |
| `errorSummary` | Short redacted summary, not a raw log excerpt. |
| `primaryDimension` | One attribution dimension. |
| `secondaryDimensions` | Optional list. |
| `reproducible` | `yes`, `no` or `unknown`. |
| `retryable` | `yes`, `no` or `conditional`. |
| `repairAction` | Smallest safe repair or clarification. |
| `regressionRequired` | Required rerun or explicit skip reason. |
| `repairResult` | `pending`, `passed`, `failed`, `partial`, `blocked` or `not-attempted`. |
| `remainingRisk` | Residual risk after repair or `none`. |
| `closureState` | `open`, `repaired`, `accepted-with-risk`, `deferred` or `blocked`. |

## Repair Loop

Use this loop for failed, partial, blocked or repaired work:

```text
failure or partial result
-> collect redacted trace summary
-> identify failed criterion and stage
-> assign attribution dimension
-> define smallest safe repair
-> apply repair only within approved scope
-> run regression or record skip reason
-> update workflow evidence and result contract
-> close, defer or mark blocked with residual risk
```

The repair loop must start from prior workflow evidence and the failure attribution record. It must not silently discard previous acceptance criteria.

## P11.4 Example Pattern

The P11.4 Java/Maven validation had a failed initial stable invocation and a successful repaired invocation. The correct attribution pattern is:

| Field | Value |
|---|---|
| failedCriterion | stable Java/Maven validation should pass through documented command surface |
| failureStage | stable tool validation |
| primaryDimension | `execution` |
| secondaryDimensions | `tool` |
| errorSummary | configured local repository was not writable by the sandbox runtime |
| repairAction | rerun the same stable command surface with a Harness-managed writable local repository override |
| regressionRequired | rerun the stable Maven validation |
| closureState | `repaired` after rerun passed |

The record must use redacted evidence paths only. It must not include private settings paths, private repository paths, raw logs or status JSON contents.

## Forbidden Record

Do not paste:

- raw logs;
- raw terminal transcripts;
- credentials, tokens, passwords or auth file contents;
- private settings paths;
- private repository paths;
- status JSON contents that contain private local paths;
- long command transcripts;
- full model context.

## Relationship To Regression Policy

Failure attribution says why a failure happened and what repair is safe.

Regression policy says what must be rerun or explicitly skipped before the task can close.

Use:

```text
harness/governance/verification/RegressionPolicy.md
```

for rerun triggers, regression record fields and closure checks.
