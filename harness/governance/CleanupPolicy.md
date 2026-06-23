---
documentName: harness/governance/CleanupPolicy.md
version: v1.0.0-pre-h8-cleanup-policy
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Harness cleanup 的 dry-run、report-first、approval-first 和安全删除边界。
scope:
  - governance
  - cleanup
  - dry-run
  - runtime-boundary
prerequisites:
  - AGENTS.md
  - harness/governance/GovernanceIndex.md
relatedDocuments:
  - harness/tools/scripts/stable/clean-sandbox.ps1
  - harness/governance/IndexMaintenancePolicy.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/governance/CleanupPolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-cleanup-policy-aligned
---
# Cleanup Policy（清理策略）

Cleanup 默认 dry-run、report-first。删除运行态、兼容文件或历史输入前，必须确认目标资产已存在、索引已更新、敏感边界无风险。

## 1. 可自动清理的内容

- `var/` 下的可重建 runtime、tmp、cache；
- 空的架构外目录；
- 已被目标路径替代且不再被 active route 引用的 compatibility stub；
- 生成物、空 `.gitkeep` 或 stale placeholder。

## 2. 需要用户审批的内容

- Git commit、push、branch rewrite；
- 真实项目文件；
- 用户知识正文；
- settings、auth、credential；
- 架构权威正文；
- 不确定是否还有历史审计价值的输入文档。

## 3. 禁止清理方式

不得使用未验证目标路径的递归删除。删除前应确认 resolved path 位于 Harness Root 或明确目标目录内。
