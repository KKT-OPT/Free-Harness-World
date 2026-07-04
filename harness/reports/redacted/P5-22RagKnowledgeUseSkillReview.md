---
documentName: harness/reports/redacted/P5-22RagKnowledgeUseSkillReview.md
version: v1.0.0-rag-knowledge-use-reviewed
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: active
purpose: 记录 rag-knowledge-use Skill candidate 的审核、晋升、路由清理、usage sidecar 更新和 Knowledge validation 验收结果。
scope:
  - skill-candidate-review
  - rag-knowledge-use
  - reviewed-knowledge
  - knowledge-validation
prerequisites:
  - AGENTS.md
  - harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
relatedDocuments:
  - harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
  - harness/architecture/PLANS.md
  - harness/skills/SkillIndex.md
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
outputTo:
  - harness/reports/redacted/P5-22RagKnowledgeUseSkillReview.md
owner: agent
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-04
  decision: approved-promoted-to-reviewed-skill
---
# rag-knowledge-use Skill Review

## 1. Candidate

| 字段 | 内容 |
|---|---|
| Skill | `rag-knowledge-use` |
| 原 candidate 路径 | `harness/skills/candidate/rag-knowledge-use/SKILL.md` |
| 晋升路径 | `harness/skills/reviewed/rag-knowledge-use/SKILL.md` |
| 类型 | user-directed Skill review / promotion |
| 来源 | reviewed Knowledge access、Knowledge validation gate、Obsidian LLM Wiki plugin boundary、candidate cleanup 和 LLM Wiki 机制吸收流程 |
| 当前状态 | approved，已晋升为 reviewed Skill |

## 2. Existing Skill 检查

已检查 Harness 当前 Skill 分工：

| Skill | 判断 |
|---|---|
| `rag-structured-ingestion` | 负责 raw-to-candidate ingestion 和 reviewed promotion 前的候选生成；不能替代 reviewed Knowledge 查询、gap 治理和 vault validation。 |
| `simulation-failure-triage` | 负责 Java / 服务仿真失败排查；不覆盖 RAG / Knowledge 使用流程。 |
| `obsidian-skills/*` | 负责 Obsidian Markdown、Canvas、CLI 等辅助能力；不能替代 Harness reviewed Knowledge 边界和晋升治理。 |

结论：`rag-knowledge-use` 覆盖的是 reviewed Knowledge 使用和治理流程，现有 Skill 不能完整替代，因此晋升为独立 reviewed Skill。

## 3. Review Gate

| 检查项 | 结果 |
|---|---|
| 触发模式 | 通过；本次是用户指定完成审核和验收，不是自动化 Skill 创建。 |
| Candidate-first | 通过；该 Skill 已先在 candidate 路径迭代，等待目录口径和验证门禁稳定后再 review。 |
| 可复用性 | 通过；流程覆盖 reviewed query、Obsidian Home、gap plan、duplicate governance、candidate cleanup、validation gate 和 pipeline smoke。 |
| 临时表述 | 通过；reviewed Skill 正文去除阶段编号和临时 run 命名，只保留稳定场景和命令面。 |
| Frontmatter | 通过；YAML 只保留 Skill 校验器允许的 `name`、`description` 和 `metadata`，Harness 笔记属性放入正文。 |
| 关联文档 | 通过；正文列出 AGENTS、SkillIndex、SkillPolicy、SkillGovernance、RAGIndex、KnowledgePromotionPolicy、插件边界、candidate cleanup、LLM Wiki 机制吸收和 ScriptIndex。 |
| 敏感边界 | 通过；Skill 不保存真实知识正文、raw source、插件配置、API key、本机绝对路径、settings、auth、token 或未脱敏日志。 |

## 4. Promotion Disposition

| 项目 | 结果 |
|---|---|
| Reviewed Skill | `harness/skills/reviewed/rag-knowledge-use/SKILL.md` |
| UI metadata | `harness/skills/reviewed/rag-knowledge-use/agents/openai.yaml` |
| Candidate 处置 | 原同名 candidate 路径已移除，避免 candidate/reviewed 双路由。 |
| SkillIndex | 已指向 reviewed Skill。 |
| Usage sidecar | 已记录 reviewed 状态、user-directed 触发、promotion decision 和 Git managed 预期。 |
| Handoff | `rag-structured-ingestion` 已把 reviewed Knowledge handoff 指向 reviewed Skill。 |

## 5. Validation

验收命令在 P5-22 收口时执行，目标是证明 Skill 本体可被校验、知识库机制仍通过一键门禁、旧 candidate 路由被清理、reviewed Skill 可进入 Git 管理范围。

| 验证项 | 命令或证据 | 结果 |
|---|---|---|
| Skill quick validate | `PYTHONUTF8=1 python quick_validate.py harness/skills/reviewed/rag-knowledge-use` | passed |
| Reviewed Skill path | `Test-Path harness/skills/reviewed/rag-knowledge-use/SKILL.md` | passed |
| Candidate path cleanup | `Test-Path harness/skills/candidate/rag-knowledge-use` | false |
| Usage sidecar JSON | `ConvertFrom-Json harness/skills/usage/skill-usage.json` | passed |
| Knowledge validation gate | `invoke-rag-knowledge.ps1 -Command validate-knowledge-vault` | passed，check count = 12，blocking issues = 0 |
| Candidate cleanup dry-run | `invoke-rag-knowledge.ps1 -Command candidate-cleanup-plan` | passed，full corpus = 0，recommended cleanup actions = 0 |
| Old candidate route scan | `rg harness/skills/candidate/rag-knowledge-use harness/skills harness/rag harness/governance harness/tools` | no active route |
| Git diff whitespace | `git diff --check` | passed |

## 6. 后续边界

本次收口完成 `rag-knowledge-use` 的 Skill 晋升，不等于 Knowledge/RAG 全部增强完成。下一轮 Knowledge/RAG 收口应继续处理 obsidian-llm-wiki 机制中仍值得增强的功能，并以全部机制验证通过作为完成标准。
