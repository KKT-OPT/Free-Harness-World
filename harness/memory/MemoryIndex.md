---
documentName: harness/memory/MemoryIndex.md
version: v1.2.0-reviewed-entry-reading-order
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 作为 Harness Memory 入口，路由 Memory policy、candidate、reviewed、archive、显式候选删除边界、reviewed Memory 路由和可执行验证门禁。
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
  - harness/tools/scripts/stable/invoke-memory.ps1
outputTo:
  - harness/memory/MemoryIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: entry-reading-order-reviewed-and-governance-gate-added
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
| Memory Stable Command | `harness/tools/scripts/stable/invoke-memory.ps1` | Memory 流程状态、候选审核、受控晋升、受控归档或删除、索引同步和 store 验证的稳定命令入口。 |

## 2. Reviewed Memory

| memoryId | 路径 | scope | 说明 |
|---|---|---|---|
| `harness-entry-reading-order` | `harness/memory/reviewed/harness-entry-reading-order.md` | `general-constraint` | Harness Root 非简单任务的一般入口读取顺序和澄清边界。 |

## 3. 维护规则

1. 新增 Memory 前必须经过 `harness/governance/MemoryGovernance.md`。
2. 项目事实优先于 reviewed Knowledge，reviewed Knowledge 优先于 active Memory。
3. Memory 冲突必须记录并交给 review 或用户决策，不得静默覆盖。
4. raw logs、task transcript、settings、auth、私有路径和不通用的用户偏好不得进入 Memory。
5. 被 reject 的 candidate 默认归档；只有用户明确要求删除时，才允许通过稳定命令删除 candidate，并在删除后运行 store 验证。
6. Memory 资产变更后必须运行 `invoke-memory.ps1 -Command validate-memory-store`；通用治理自检还应运行该命令的 `-SelfTest`，确保门禁本身仍能识别负向样例。
