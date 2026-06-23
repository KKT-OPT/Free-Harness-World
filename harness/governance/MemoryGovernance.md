---
documentName: harness/governance/MemoryGovernance.md
version: v1.0.0-pre-h8-memory-governance
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Memory candidate 的检测、冲突检查、review、晋升、归档和索引更新治理规则。
scope:
  - governance
  - memory-governance
  - memory-promotion
prerequisites:
  - AGENTS.md
  - harness/memory/MemoryIndex.md
relatedDocuments:
  - harness/memory/MemoryPolicy.md
  - harness/templates/memory/MemoryTemplate.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/governance/MemoryGovernance.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/memory/MemoryIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-memory-governance-aligned
---
# Memory Governance

Memory Governance 负责确保 Memory 只保存通用化、非私有、未来可复用的经验。一次性任务过程、项目事实、用户私有偏好和 raw logs 不得晋升为 Memory。

## 1. Review Gate

Memory candidate 晋升前必须检查：

- 是否稳定并超出单次任务；
- 是否不含用户私有信息；
- 是否可跨任务或跨项目复用；
- 是否与 Project Fact、reviewed Knowledge 或 active Memory 冲突；
- 是否记录 source evidence、reviewer、reviewAfter 和 staleness rule。

## 2. 目标资产

| 状态 | 路径 |
|---|---|
| candidate | `harness/memory/candidate/` |
| reviewed | `harness/memory/reviewed/` |
| archived | `harness/memory/archive/` |

## 3. 关联流程

Memory 更新流程以 `harness/memory/MemoryPolicy.md` 中的 Mermaid 为准。Governance 负责 review 和 approval gate，不直接绕过 candidate 阶段写入 reviewed memory。
