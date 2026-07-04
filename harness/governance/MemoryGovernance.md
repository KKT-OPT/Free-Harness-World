---
documentName: harness/governance/MemoryGovernance.md
version: v1.2.0-executable-memory-gate
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 定义 Memory candidate 的检测、冲突检查、review、晋升、归档、显式删除、索引更新和可执行治理门禁规则。
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
  - harness/tools/scripts/stable/invoke-memory.ps1
  - harness/tools/scripts/stable/test-harness-governance.ps1
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
  reviewedAt: 2026-07-05
  decision: executable-memory-gate-added
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

被 reject 的 candidate 默认进入 archive。只有用户明确要求 delete 时，才允许通过稳定命令删除 `harness/memory/candidate/` 内目标文件；删除命令必须要求 reviewer、approval note、reason 和 `-Apply`，并在删除后运行 Memory store 验证。

## 3. 关联流程

Memory 更新流程以 `harness/memory/MemoryPolicy.md` 中的 Mermaid 为准。Governance 负责 review 和 approval gate，不直接绕过 candidate 阶段写入 reviewed memory。

## 4. 可执行治理门禁

Memory Governance 的执行入口是：

```text
harness/tools/scripts/stable/invoke-memory.ps1
```

治理规则：

1. review 前使用 `candidate-review-package` 输出候选审核包；
2. approve、reject、archive、delete 或 revise 都必须先经过 dry-run，再在 reviewer、approval note、reason 齐备时使用 `-Apply`；
3. reviewed 晋升后应同步 `MemoryIndex.md` 或机器可读索引；
4. 每次 Memory 资产写入后运行 `validate-memory-store`；
5. `test-harness-governance.ps1` 必须把 `validate-memory-store` 和 `validate-memory-store -SelfTest` 作为 governance self-check 的一部分；
6. governance self-check 失败时，Memory 资产不得被视为已收口。
