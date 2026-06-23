---
documentName: harness/skills/SkillIndex.md
version: v1.0.0-pre-h8-skill-mechanism
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 作为 Harness Skill 入口，路由 Skill policy、candidate、reviewed、archive、usage sidecar 和现有 skill 包。
scope:
  - skill
  - skill-index
  - skill-lifecycle
  - skill-usage
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
  - harness/templates/skill/SkillTemplate.md
outputTo:
  - harness/skills/SkillIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-skill-mechanism-aligned
---
# Skill 索引

`harness/skills/` 保存可复用 workflow 或程序性经验。Skill 不是 Knowledge、不是 Memory、不是 Tool Asset，也不是一次性任务记录。

## 1. 目标结构

| 分区 | 路径 | 说明 |
|---|---|---|
| Skill Policy | `harness/skills/SkillPolicy.md` | Skill 边界、触发条件、创建/更新流程和晋升规则。 |
| Candidate Skills | `harness/skills/candidate/` | 等待 review 的新 skill 或 patch candidate。 |
| Reviewed Skills | `harness/skills/reviewed/` | 经 review 或用户明确批准的 skill。 |
| Archived Skills | `harness/skills/archive/` | 被拒绝、过期或只具历史价值的 skill。 |
| Usage Sidecar | `harness/skills/usage/skill-usage.json` | Skill 动态使用统计；更新规则见 `SkillPolicy.md`。 |
| Skill Template | `harness/templates/skill/SkillTemplate.md` | Candidate / reviewed skill 的记录模板。 |

## 2. 当前已知 Skill 包

| Skill | 当前路径 | 说明 |
|---|---|---|
| RAG Structured Ingestion | `harness/skills/rag-structured-ingestion/SKILL.md` | raw-to-candidate knowledge workflow。 |
| Obsidian Skills | `harness/skills/obsidian-skills/` | Obsidian Markdown、Bases、Canvas、CLI 等辅助技能包。 |

现有 skill 包在后续 review 时可迁入 `reviewed/<category>/<skill-name>/`。新增或自动创建 skill 必须先进入 candidate flow，不得绕过 review。

## 3. 维护规则

1. 新增 Skill 前必须检查现有 Skill 是否可 patch。
2. 自动创建或更新 Skill 必须符合 `SkillPolicy.md` 的触发条件。
3. `SKILL.md` frontmatter 只保存静态治理信息；动态使用统计进入 usage sidecar。
4. Skill 不能保存项目事实、用户私有知识、raw logs、settings、auth 或私有路径。
