---
documentName: harness/governance/archive/GovernanceIndex.md
version: v1.0.0-h7-archived-route-note
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: archived
purpose: 作为历史治理索引的归档说明，记录旧 preflight 路由已被当前 Governance、Verification 和 Observability 入口取代。
scope:
  - governance-archive
  - historical-route-note
prerequisites:
  - AGENTS.md
relatedDocuments:
  - harness/governance/GovernanceIndex.md
  - harness/verification/VerificationIndex.md
  - harness/observability/ObservabilityIndex.md
outputTo:
  - harness/governance/archive/GovernanceIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
  - harness/governance/GovernanceIndex.md
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Governance 历史索引归档

本文只记录旧 preflight 治理路由的历史背景，默认不参与上下文加载。

当前稳定入口如下：

```text
harness/governance/GovernanceIndex.md
harness/verification/VerificationIndex.md
harness/observability/ObservabilityIndex.md
```

当前边界：

- Governance 负责 review、promotion、archive、cleanup 和 approval boundary；
- Verification 负责 readiness、validation、regression 和 Harness validation cases；
- Observability 负责 trace summary 和 failure attribution schema。

旧 preflight 中把 verification 规则放在 governance 子路径的组织方式已被 H7 目标布局取代。
