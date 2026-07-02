---
documentName: harness/governance/SkillGovernance.md
version: v1.1.0-user-directed-skill-git-gate
updatedAt: 2026-07-02 18:12:00.000 +08:00
status: active
purpose: 定义 Skill candidate 的用户指定触发、自动触发、已有 Skill 检查、review、晋升、归档、Git 管理和 usage sidecar 更新治理规则。
scope:
  - governance
  - skill-governance
  - skill-creation
  - skill-promotion
  - skill-git-management
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
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: user-directed-skill-git-gate-added
---
# Skill Governance

Skill Governance 负责控制 Skill 创建和更新，防止一次性任务记录直接变成长期 Skill。

## 1. Review Gate

Skill candidate 晋升前必须检查：

- 触发模式是用户指定触发，还是自动触发；
- 用户是否明确要求沉淀，或是否满足自动触发条件；
- 现有 Skill 是否可以 patch；
- 内容是否是可复用流程，而不是单次上下文；
- 是否有明确 trigger、inputs、procedure、verification 和 failure handling；
- 是否排除了项目事实、用户私有信息、raw logs、settings 和 auth；
- 是否更新 `harness/skills/SkillIndex.md` 和 usage sidecar。

用户指定触发时，治理记录必须说明：本次不是自动化 Skill 创建过程，而是用户明确要求进入 Skill 机制；但仍需要 candidate-first、review-first 和 approval gate。

## 2. Promotion Gate

Skill candidate 获得 approve 后，晋升收口必须检查：

| 检查项 | 要求 |
|---|---|
| Reviewed 路径 | Skill 文件迁入 `harness/skills/reviewed/<skill-name>/` 或治理批准的 reviewed 分类路径。 |
| Candidate 清理 | 同名活跃 candidate 不再被 `SkillIndex.md` 路由，避免 candidate 和 reviewed 并存。 |
| SkillIndex | `harness/skills/SkillIndex.md` 指向 reviewed Skill。 |
| Usage sidecar | `harness/skills/usage/skill-usage.json` 记录 reviewed 状态、使用、修订和晋升决策。 |
| Review evidence | 审核包或阶段记录保存最终决策、修订轮次和验证结果。 |
| Git 管理 | reviewed Skill 以及必要的索引、usage 和审核记录必须进入 Git 管理范围。 |

## 3. Git Management Gate

reviewed Skill 是 Harness 长期资产，不得停留为未跟踪文件。收口时必须：

1. 用限定路径检查 `git status --short`，确认 reviewed Skill 文件状态；
2. 用限定路径 `git add` 纳入本次 Skill 晋升相关文件；
3. 避免 stage 无关变更；
4. 确认 `.gitignore` 没有阻断 reviewed Skill 入库；
5. 在 final summary 或收口记录中说明 Git 管理结果。

## 4. 目标资产

| 状态 | 路径 |
|---|---|
| candidate | `harness/skills/candidate/` |
| reviewed | `harness/skills/reviewed/` |
| archived | `harness/skills/archive/` |
| usage | `harness/skills/usage/skill-usage.json` |

## 5. 关联流程

Skill 创建流程以 `harness/skills/SkillPolicy.md` 中的 Mermaid 为准。Governance 负责 review 和 approval gate，不直接绕过 candidate 阶段创建 reviewed Skill。
