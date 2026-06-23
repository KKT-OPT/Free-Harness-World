---
documentName: harness/observability/ObservabilityIndex.md
version: v1.0.0-h7-observability-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 作为 Harness Observability 的目标入口，路由 trace summary、failure attribution 和 workflow evidence 观测字段。
scope:
  - observability
  - trace-schema
  - failure-attribution
  - workflow-evidence-observability
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/observability/TraceSchema.md
  - harness/observability/FailureAttribution.md
  - harness/verification/VerificationIndex.md
  - harness/governance/GovernanceIndex.md
outputTo:
  - harness/observability/ObservabilityIndex.md
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
# Observability 索引

`harness/observability/` 是 Harness 的观测结构层。Observability，中文解释是观测，负责定义 trace summary、failure attribution 和 workflow evidence 观测字段。它记录发生了什么，不直接判断任务是否通过，也不晋升长期事实。

## 1. 观测资产

| 资产 | 路径 | 说明 |
|---|---|---|
| Trace Schema | `harness/observability/TraceSchema.md` | 定义 trace summary、context snapshot、operation events 和 workflow evidence hooks。 |
| Failure Attribution | `harness/observability/FailureAttribution.md` | 定义失败归因维度、记录字段和修复闭环观测要求。 |

## 2. 边界关系

| 层 | 使用 Observability 的方式 |
|---|---|
| Verification | 使用 trace 和 failure attribution 判断 readiness、validation 和 regression 是否有证据支撑。 |
| Governance | 使用观测摘要判断是否需要 review、promotion、archive 或 cleanup。 |
| Reports | 引用观测证据路径和摘要，不复制 raw logs 或完整 transcript。 |
| Project Workflow Evidence | 保存项目任务的 trace summary、validation summary 和 failure attribution。 |

## 3. 禁止内容

Observability 文档和观测摘要不得保存：

- credentials、tokens、passwords、private keys；
- settings XML 正文、auth 文件正文或 credential helper 内容；
- raw terminal transcript；
- unredacted logs；
- full model context；
- raw external document body；
- 私有仓库细节或本机敏感路径。

## 4. 维护规则

1. 新增观测字段时优先更新 `TraceSchema.md`。
2. 新增失败分类时优先更新 `FailureAttribution.md`。
3. 观测结果只产生 evidence 或 candidates，不自动成为 Knowledge、Memory、Skill、Project Fact 或 Architecture。
4. 需要验证通过与否时，必须路由到 `harness/verification/VerificationIndex.md`。
