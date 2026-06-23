---
documentName: harness/verification/RegressionPolicy.md
version: v1.0.0-h7-verification-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 定义 Harness-managed work 在修复、路径变更、策略变更或验证失败后的 regression check 和风险关闭规则。
scope:
  - verification
  - regression
  - repair-loop
  - validation-closure
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/verification/VerificationIndex.md
relatedDocuments:
  - harness/observability/FailureAttribution.md
  - harness/observability/TraceSchema.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/verification/RegressionPolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/verification/VerificationIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Regression Policy（回归策略）

Regression Check，中文解释是回归检查，用于确认修复、路径变更、策略变更或验证失败后的结果是否仍满足验收。Regression 让修复证据可审查，但不替代真实执行、稳定工具、用户验收或 Governance Review。

## 1. 需要 Regression 的触发条件

发生以下变更后，必须运行 regression check，或者记录经过 review 的跳过理由：

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

## 2. Regression 类型

| Type | Purpose |
|---|---|
| `document-regression` | Check references, index routes, headings, stale phase state and template discoverability. |
| `governance-regression` | Check policy conflicts, approval needs, promotion boundaries and archive rules. |
| `tool-regression` | Rerun or dry-run stable tool surfaces with redacted evidence. |
| `workflow-regression` | Confirm Task Brief, trace summary, result contract and acceptance remain coherent. |
| `security-regression` | Check sensitive terms, concrete private paths, raw logs and credential leakage. |
| `project-regression` | Verify project package, routing, validation profile and project fact boundaries. |
| `knowledge-regression` | Check Knowledge/Memory/Skill/RAG candidate boundaries and review status. |

## 3. Regression 记录

Regression 结果应进入 workflow evidence 或 redacted report，并至少包含以下字段：

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

## 4. 修复关闭规则

只有同时满足以下条件，修复才能关闭：

1. The failed criterion is still visible in workflow evidence.
2. Failure attribution identifies a primary dimension.
3. The repair action is scoped and approved.
4. Required regression has passed, or a skip reason is explicitly recorded.
5. Residual risk is recorded.
6. The Common Task Result Contract points to the relevant evidence.
7. Governance candidates are listed without auto-promotion.

## 5. 禁止关闭的情况

出现以下情况时，不得关闭修复：

- the failed criterion was removed instead of repaired;
- the rerun was skipped without an explicit reason;
- only model confidence is used in place of validation;
- raw logs or status JSON contents are copied into tracked docs;
- sensitive settings, credentials, auth files or private repository paths are exposed;
- promotion candidates are silently written into Knowledge, Memory or Skill assets.

## 6. 与 Failure Attribution 的关系

Failure Attribution，中文解释是失败归因，说明失败原因和最小安全修复方向；Regression Policy 说明关闭前必须重新运行或明确跳过的验证。

配套使用：

```text
harness/observability/FailureAttribution.md
harness/verification/RegressionPolicy.md
```

Regression 记录不得包含 raw logs、完整 status JSON 正文、私有 settings、auth 文件、私有仓库细节或本机敏感路径。
