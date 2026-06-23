---
documentName: harness/memory/MemoryIndex.md
version: v1.0.0-pre-h8-memory-mechanism
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 作为 Harness Memory 入口，路由 Memory policy、candidate、reviewed 和 archive 边界。
scope:
  - memory
  - memory-index
  - memory-lifecycle
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/memory/MemoryPolicy.md
  - harness/governance/MemoryGovernance.md
  - harness/templates/memory/MemoryTemplate.md
outputTo:
  - harness/memory/MemoryIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-memory-mechanism-aligned
---
# Memory 索引

`harness/memory/` 保存通用化、非私有、未来可复用的经验。Memory 不是项目事实源、不是任务历史、不是 RAG 文档，也不保存用户私有偏好。

## 1. 路由

| 资产 | 路径 | 说明 |
|---|---|---|
| Memory Policy | `harness/memory/MemoryPolicy.md` | Memory 边界、生命周期、冲突规则和晋升流程。 |
| Candidate Memory | `harness/memory/candidate/` | 等待 review 的候选记忆。 |
| Reviewed Memory | `harness/memory/reviewed/` | 经 review 或用户明确批准的 active memory。 |
| Archived Memory | `harness/memory/archive/` | 被拒绝、过期或只具历史价值的 memory。 |
| Memory Template | `harness/templates/memory/MemoryTemplate.md` | Candidate / reviewed memory 的记录模板。 |

## 2. 维护规则

1. 新增 Memory 前必须经过 `harness/governance/MemoryGovernance.md`。
2. 项目事实优先于 reviewed Knowledge，reviewed Knowledge 优先于 active Memory。
3. Memory 冲突必须记录并交给 review 或用户决策，不得静默覆盖。
4. raw logs、task transcript、settings、auth、私有路径和不通用的用户偏好不得进入 Memory。
