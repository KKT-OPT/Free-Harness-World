---
documentName: harness/templates/memory/MemoryTemplate.md
version: v1.1.0-executable-memory-gate-template
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 提供 Memory candidate、reviewed memory 和 archived memory 的记录模板。
scope:
  - memory-template
  - memory-candidate
  - reviewed-memory
prerequisites:
  - AGENTS.md
  - harness/memory/MemoryIndex.md
relatedDocuments:
  - harness/memory/MemoryPolicy.md
  - harness/governance/MemoryGovernance.md
  - harness/tools/scripts/stable/invoke-memory.ps1
outputTo:
  - harness/templates/memory/MemoryTemplate.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/memory/MemoryIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: executable-memory-gate-template-aligned
---
# Memory Template（记忆模板）

本模板用于记录 Memory candidate、reviewed memory 或 archived memory。Memory 只保存通用化、非私有、未来可复用的经验。

## 元数据

```yaml
memoryId: <stable-id>
assetState: candidate | reviewed | archived
scope: global | domain | project | agent-operation
projectId: <project-id-or-null>
sourceEvidence: <workflow-or-report-path>
confidence: low | medium | high
reviewedBy: <human-or-approved-process-or-null>
reviewedAt: <date-or-null>
stalenessRule: <date-or-condition>
```

## Memory Statement

在这里写入简洁、可复用、非私有的记忆正文。

## Source And Evidence

| Source | Evidence Summary | Notes |
|---|---|---|
| `<path>` | `<summary>` | `<notes>` |

## Applicability

说明这条 Memory 适用于哪些场景。

## Non-Applicability

说明这条 Memory 不适用于哪些场景，包括与 Project Facts、reviewed Knowledge 或用户当前指令冲突时的边界。

## Review Notes

| Check | Result |
|---|---|
| Stable beyond one task | `yes | no | unknown` |
| Future reuse value | `yes | no | unknown` |
| Sensitive content excluded | `yes | no | unknown` |
| Conflict check completed | `yes | no | unknown` |
| Approval recorded | `yes | no | unknown` |

## Promotion Decision

```yaml
decision: approve | reject | defer
targetState: reviewed | archived | candidate
reviewer: <reviewer-or-null>
decisionDate: <date-or-null>
reason: <reason>
```
