---
documentName: harness/governance/SkillGovernance.md
version: v1.0.0-pre-h8-skill-governance
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Skill candidate 的自动触发、已有 Skill 检查、review、晋升、归档和 usage sidecar 更新治理规则。
scope:
  - governance
  - skill-governance
  - skill-creation
  - skill-promotion
prerequisites:
  - AGENTS.md
  - harness/skills/SkillIndex.md
relatedDocuments:
  - harness/skills/SkillPolicy.md
  - harness/templates/skill/SkillTemplate.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/governance/SkillGovernance.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/skills/SkillIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-skill-governance-aligned
---
# Skill Governance

Skill Governance 负责控制 Skill 创建和更新，防止一次性任务记录直接变成长期 Skill。

## 1. Review Gate

Skill candidate 晋升前必须检查：

- 用户是否明确要求沉淀，或是否满足自动触发条件；
- 现有 Skill 是否可以 patch；
- 内容是否是可复用流程，而不是单次上下文；
- 是否有明确 trigger、inputs、procedure、verification 和 failure handling；
- 是否排除了项目事实、用户私有信息、raw logs、settings 和 auth；
- 是否更新 `harness/skills/SkillIndex.md` 和 usage sidecar。

## 2. 目标资产

| 状态 | 路径 |
|---|---|
| candidate | `harness/skills/candidate/` |
| reviewed | `harness/skills/reviewed/` |
| archived | `harness/skills/archive/` |
| usage | `harness/skills/usage/skill-usage.json` |

## 3. 关联流程

Skill 创建流程以 `harness/skills/SkillPolicy.md` 中的 Mermaid 为准。Governance 负责 review 和 approval gate，不直接绕过 candidate 阶段创建 reviewed Skill。
