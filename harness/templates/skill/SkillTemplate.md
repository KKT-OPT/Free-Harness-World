---
documentName: harness/templates/skill/SkillTemplate.md
version: v1.0.0-pre-h8-skill-template
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 提供 Skill candidate、reviewed skill 和 archived skill 的记录模板。
scope:
  - skill-template
  - skill-candidate
  - reviewed-skill
prerequisites:
  - AGENTS.md
  - harness/skills/SkillIndex.md
relatedDocuments:
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
outputTo:
  - harness/templates/skill/SkillTemplate.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/skills/SkillIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-skill-mechanism-aligned
---
# Skill Template（技能模板）

本模板用于记录 Skill candidate、reviewed skill 或 archived skill。Skill 描述可复用 workflow 或程序性经验，不保存项目事实、用户私有知识或一次性任务记录。

## 元数据

```yaml
skillId: skill.<category>.<name>
assetState: candidate | reviewed | archived
category: <category>
sourceEvidence: <workflow-or-report-path>
owner: <human-or-team>
reviewedAt: <date-or-null>
reviewAfter: <date-or-condition>
```

## Description

Write a trigger-oriented description of what this skill helps an agent do.

## When To Use

- `<trigger-condition>`
- `<trigger-condition>`

## 输入

| Input | Required | Notes |
|---|---|---|
| `<input>` | `yes | no` | `<notes>` |

## Procedure

1. `<step>`
2. `<step>`
3. `<step>`

## Preferred Stable Tools

| Tool | Use |
|---|---|
| `<tool-or-none>` | `<use>` |

## 证据 Outputs

- `<workflow-evidence>`
- `<report-or-result-contract>`

## Verification

- `<acceptance-check>`
- `<regression-check-if-needed>`

## Pitfalls

- `<pitfall>`
- `<pitfall>`

## 治理

| Check | Rule |
|---|---|
| One-session content excluded | yes |
| Project facts excluded unless project-scoped | yes |
| Knowledge facts excluded | yes |
| Sensitive content excluded | yes |
| Promotion requires review | yes |

## 相关文档

- `<path>`
