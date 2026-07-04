---
documentName: harness/memory/MemoryPolicy.md
version: v1.2.0-executable-memory-gate
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 定义 Memory 边界、候选生成、冲突处理、review、晋升、归档、显式候选删除规则和可执行验证门禁。
scope:
  - memory
  - memory-boundary
  - memory-promotion
  - memory-conflict
prerequisites:
  - AGENTS.md
  - harness/memory/MemoryIndex.md
relatedDocuments:
  - harness/governance/MemoryGovernance.md
  - harness/templates/memory/MemoryTemplate.md
  - harness/tools/scripts/stable/invoke-memory.ps1
  - harness/tools/scripts/stable/test-harness-governance.ps1
outputTo:
  - harness/memory/MemoryPolicy.md
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
# Memory Policy（记忆策略）

Memory 是小而稳定、未来可复用、已经通用化的经验。Memory 不区分用户 Memory 和通用 Memory；不够通用或包含用户私有偏好的内容不得晋升为长期 Memory。

## 1. 适合进入 Memory 的内容

- 多个项目或多次任务可复用的经验；
- Agent 操作注意事项；
- 跨任务复用的失败解决经验；
- 经审查的候选记忆；
- 对通用 Harness 使用有帮助的非私有经验。

## 2. 不适合进入 Memory 的内容

- 大段日志、代码、任务 transcript 或一次性 TODO；
- 未验证推测；
- 外部知识长文；
- 已写入 Project Facts 或 reviewed Knowledge 的完整内容；
- 用户信息、本机信息、私有 settings 或 credentials；
- 不具备通用性的用户偏好。

## 3. Memory Update Flow

```mermaid
flowchart TD
    A["Task Evidence / User Feedback"] --> B["Detect Memory Candidate"]
    B --> C{"Is it stable, non-private and reusable?"}
    C -->|no| D["Keep in Workflow / Report only"]
    C -->|yes| E["Create Memory Candidate"]
    E --> F["Classify Memory Type<br/>Agent Operation / Cross-project Experience / General Constraint"]
    F --> G["Check Existing Memory"]
    G --> H{"Duplicate or conflict?"}
    H -->|duplicate| I["Reject or Merge Candidate"]
    H -->|conflict| J["Conflict Review<br/>Project Facts > RAG > active Memory"]
    H -->|new| K["Human / Governance Review"]
    J --> K
    K --> L{"Approved?"}
    L -->|approved| M["Promote to active Memory"]
    L -->|rejected| N["Mark rejected / archive or delete candidate"]
    L -->|needs repair| O["Revise Candidate"]
    O --> K
    M --> P["Update MemoryIndex / source / reviewAfter"]
    P --> Q["Closeout"]
    N --> Q
    I --> Q
    D --> Q
```

## 4. 冲突优先级

```text
用户当前明确指令
> Project Fact / 正式文档
> reviewed Knowledge / RAG
> active Memory
> candidate Memory
> archived Memory
```

当 Memory 与正式文档冲突时，应报告冲突，由用户审批决策，不得静默覆盖。

## 5. Reject、Archive 和 Delete

候选 Memory 被 reject 后，默认处置是归档到 `harness/memory/archive/`，以保留轻量审计记录。

只有用户明确要求删除候选时，才允许使用受控删除路径。删除必须满足：

1. 已经有明确的用户 reject/delete 决策；
2. 使用稳定命令执行，不手工删除；
3. 提供 reviewer、approval note、reason 和 `-Apply`；
4. 删除边界只允许作用于 `harness/memory/candidate/` 下的目标候选；
5. 删除后重新运行 Memory store 验证。

## 6. 可执行门禁

Memory 生命周期不能只依赖文档约束。涉及 candidate 创建、修订、review 决策、reviewed 晋升、archive、delete 或 index 同步时，应优先使用稳定命令：

```text
harness/tools/scripts/stable/invoke-memory.ps1
```

最低验证要求：

1. 写入前先运行与当前步骤对应的 dry-run 或 report-only 命令；
2. 写入必须显式传入 `-Apply`，并提供 reviewer、approval note 和 reason；
3. 写入后运行 `invoke-memory.ps1 -Command validate-memory-store`；
4. 通用治理自检必须运行 `validate-memory-store` 和 `validate-memory-store -SelfTest`；
5. 门禁失败时不得继续把 candidate 当作 active Memory，也不得把 reviewed Memory 作为稳定事实引用。
