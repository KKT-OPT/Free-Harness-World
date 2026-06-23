---
documentName: harness/observability/FailureAttribution.md
version: v1.0.0-h7-observability-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 定义 Harness failure attribution 的分类维度、记录字段和修复闭环观测要求。
scope:
  - observability
  - failure-attribution
  - repair-loop
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/observability/ObservabilityIndex.md
relatedDocuments:
  - harness/observability/TraceSchema.md
  - harness/verification/RegressionPolicy.md
  - harness/verification/HarnessValidationPlan.md
outputTo:
  - harness/observability/FailureAttribution.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/observability/ObservabilityIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Failure Attribution

Failure Attribution，中文解释是失败归因，用于说明任务失败、部分通过、阻断或修复后通过的主要原因和最小安全修复方向。失败归因不是责备模型，也不是验证结论本身。

failed、partial、blocked、repaired 或 passed-after-repair 的结果都需要归因记录。修复后的任务可以最终返回 `passed`，但只要中间失败影响过任务结果，就仍需要保留失败归因。

## 1. Scope

This policy applies to:

- Harness-managed workflow evidence;
- stable tool validation failures;
- documentation, governance, project package and routing validation failures;
- any task result that returns `failed`, `partial`, `blocked`, `repaired` or `passed-after-repair`.

This policy does not execute repairs by itself. It defines the record required before repair, the rerun required after repair, and the closure conditions.

## 2. Attribution Dimensions

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

## 3. Required Record

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

## 4. Repair Loop

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

## 5. Forbidden Record

Do not paste:

- raw logs;
- raw terminal transcripts;
- credentials, tokens, passwords or auth file contents;
- private settings paths;
- private repository paths;
- status JSON contents that contain private local paths;
- long command transcripts;
- full model context.

## 6. Relationship To Regression Policy

Failure attribution says why a failure happened and what repair is safe.

Regression policy says what must be rerun or explicitly skipped before the task can close.

Use:

```text
harness/verification/RegressionPolicy.md
```

for rerun triggers, regression record fields and closure checks.
