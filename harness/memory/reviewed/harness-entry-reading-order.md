---
documentName: harness/memory/reviewed/harness-entry-reading-order.md
version: v1.0.0-reviewed
updatedAt: 2026-07-05 05:41:36.000 +08:00
status: active
purpose: 记录经用户审核批准的 Harness Root 非简单任务入口读取顺序通用记忆。
scope:
  - reviewed-memory
prerequisites:
  - harness/memory/MemoryPolicy.md
relatedDocuments:
  - AGENTS.md
outputTo:
  - harness/memory/reviewed/harness-entry-reading-order.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/memory/MemoryPolicy.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-05
  decision: approve
---
# harness-entry-reading-order

## 元数据

```yaml
memoryId: harness-entry-reading-order
assetState: reviewed
scope: general-constraint
projectId: null
sourceEvidence: AGENTS.md
confidence: high
reviewedBy: user
reviewedAt: 2026-07-05
stalenessRule: review-after-entry-contract-change
```

## Memory Statement

处理 Harness Root 的非简单任务时，先读取 AGENTS.md、INDEX.md、harness/HarnessIndex.md，再按索引路由到架构权威、Memory、Skill、Tool、Policy、Project 等当前任务相关文档；涉及项目时再读取 Project Profile 和项目 AGENTS/ProjectIndex；目标、范围、验收或风险边界缺失且会影响执行时，先澄清。

## Source And Evidence

| Source | Evidence Summary | Notes |
|---|---|---|
| `AGENTS.md` | 受控来源证据。 | 由稳定 Memory 命令创建并晋升。 |

## Applicability

适用于 Harness Root 下的非简单任务入口读取、任务路由和风险边界判断。该记忆只作为通用入口经验使用，具体任务仍以 AGENTS.md、INDEX.md、HarnessIndex 和当前任务相关正式文档为准。

## Non-Applicability

不得用于项目私有事实、用户私有偏好、raw logs、settings、auth 或凭据。

## Review Notes

| Check | Result |
|---|---|
| Stable beyond one task | yes |
| Future reuse value | yes |
| Sensitive content excluded | yes |
| Conflict check completed | yes |
| Approval recorded | yes |

## Promotion Decision

```yaml
decision: approve
targetState: reviewed
reviewer: user
decisionDate: 2026-07-05
reason: 该记忆是 Harness Root 的通用入口读取约束，非私有、可复用，且已移除阶段性计划文档读取表述。
```
