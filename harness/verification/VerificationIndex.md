---
documentName: harness/verification/VerificationIndex.md
version: v1.0.0-h7-verification-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 作为 Harness Verification 的目标入口，路由 readiness、validation、regression 和 Harness validation cases。
scope:
  - verification
  - readiness
  - validation
  - regression
  - harness-validation-cases
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/verification/ReadinessCheckPolicy.md
  - harness/verification/RegressionPolicy.md
  - harness/verification/HarnessValidationPlan.md
  - harness/verification/HarnessValidationCases.md
  - harness/observability/ObservabilityIndex.md
  - harness/governance/GovernanceIndex.md
outputTo:
  - harness/verification/VerificationIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Verification 索引

`harness/verification/` 是 Harness 的验证规则层。Verification，中文解释是验证，负责判断任务是否具备执行条件、结果是否满足验收、修复后是否需要回归确认。

Verification 不直接晋升 Knowledge、Memory、Skill、Project Fact、Tool 或 Governance 资产。晋升、归档、清理和审批由 `harness/governance/` 负责。

## 1. 验证资产

| 资产 | 路径 | 说明 |
|---|---|---|
| Readiness Check Policy | `harness/verification/ReadinessCheckPolicy.md` | 执行前就绪检查和澄清规则。 |
| Regression Policy | `harness/verification/RegressionPolicy.md` | 修复后回归、复验和风险关闭规则。 |
| Harness Validation Plan | `harness/verification/HarnessValidationPlan.md` | Harness 生命周期验证计划。 |
| Harness Validation Cases | `harness/verification/HarnessValidationCases.md` | Harness 验证用例和通过标准。 |

## 2. 边界关系

| 层 | 职责 | 不负责 |
|---|---|---|
| Verification | readiness、validation、regression、validation cases。 | 不决定资产晋升、不执行 archive、不替代用户验收。 |
| Observability | trace summary、failure attribution、观测字段结构。 | 不判断是否通过验收。 |
| Governance | review、promotion、archive、cleanup、approval boundary。 | 不替代验证规则正文。 |
| Reports | 保存经过脱敏的验证或治理输出。 | 不作为事实源。 |

## 3. 输出规则

Verification 输出可以进入：

```text
harness/reports/verification/
projects/<project-id>/docs/project/workflow/
```

输出只记录摘要、路径和判定结果，不复制 raw logs、status JSON 正文、私有 settings、auth 文件或本机敏感路径。

## 4. 维护规则

1. 新增验证规则时优先更新本文。
2. 验证规则路径以 `harness/verification/` 为准。
3. `harness/governance/` 可以引用验证结果，但不保存验证规则正文。
4. 验证失败、部分通过或修复后通过时，应同时记录 `harness/observability/FailureAttribution.md` 和 `harness/verification/RegressionPolicy.md` 所需字段。
