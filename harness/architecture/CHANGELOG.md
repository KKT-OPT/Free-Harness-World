---
documentName: harness/architecture/CHANGELOG.md
version: v1.0.0-pre-h8-structure
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 记录 Harness 架构权威和落地计划的长期版本级变更摘要，不替代 HarnessEngineering.md 或 PLANS.md。
scope:
  - architecture-changelog
  - release-summary
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/architecture/CHANGELOG.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-structure-aligned
---
# Harness 架构变更日志

本文只记录版本级架构变更摘要。架构规则以 `harness/architecture/HarnessEngineering.md` 为准；阶段计划、验收结果和下一步以 `harness/architecture/PLANS.md` 为准。

## v2.4.0-target-architecture

- 确认 Harness Distribution Repo、Harness Workspace 和 Project Instance 的长期边界。
- 确认 `INDEX.md`、`harness/HarnessIndex.md` 和 `harness/architecture/PLANS.md` 的目标路径。
- 确认 Project Template、Tool Asset、RAG / Knowledge、Verification、Observability、Memory 和 Skill 的长期边界。
- 确认 workflow evidence 只产生候选，Governance 必须 candidate-first、review-first、human approval。
