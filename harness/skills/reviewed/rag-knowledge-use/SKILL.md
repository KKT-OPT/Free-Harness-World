---
name: rag-knowledge-use
description: 使用已审核的 Harness reviewed Knowledge 与稳定 RAG Knowledge 命令。适用于需要初始化或检查本地知识库、同步 Obsidian Home 单入口、查询并阅读 authoritative reviewed Knowledge、构建 reviewed graph、生成 task-scoped schema context、验证 LLM Wiki 吸收机制、治理重复 reviewed page、生成 candidate-only gap plan、处置 residual workflow gap、执行 canonical vault layout、一键验证、candidate 晋升后清理、人工 review package、用户批准后的 concept 晋升、vault governance 或 raw-to-reviewed pipeline smoke 的场景。
metadata:
  short-description: reviewed Knowledge 查询与治理流程
  asset-state: reviewed
  review-state: approved-by-user
---
# Reviewed Knowledge 使用与治理

## 1. 笔记属性

`SKILL.md` 的 YAML frontmatter 只保留 Skill 校验器允许的元数据；Harness 文档治理所需的笔记属性和关联文档放在正文中维护。

| 属性 | 内容 |
|---|---|
| 文档 | `harness/skills/reviewed/rag-knowledge-use/SKILL.md` |
| 资产状态 | reviewed |
| 审核状态 | approved，用户要求完成该 Skill review 并按验收标准收口 |
| 主题语言 | 中文；专业词、命令、路径、frontmatter key 和技术名词保留英文 |
| 适用对象 | reviewed Knowledge 查询、Obsidian 知识库阅读入口、task-scoped schema context、LLM Wiki 机制验证、candidate gap 治理、重复 reviewed 治理、post-promotion cleanup 和一键验证 |
| 解决问题 | 在不把 raw、candidate、runtime graph 或插件输出误当事实源的前提下，稳定使用已审核知识并维护知识库边界 |
| 输入来源 | Harness 入口文档、RAG/Knowledge policy、reviewed Knowledge、stable command status JSON、用户批准记录 |
| 输出结果 | 基于 reviewed Knowledge 的回答、schema context 摘要、机制验证报告、候选补强计划、审核包、清理计划、验证报告或用户批准后的 reviewed concept 晋升 |

## 2. 关联文档和读取路径

使用本 Skill 前，先按 Harness 入口规则读取全局入口和 RAG/Knowledge 机制文档，再根据任务读取目标 reviewed page 或 candidate review package。

### 2.1 Harness 入口和 Skill 治理

| 文档 | 读取目的 |
|---|---|
| `AGENTS.md` | 获取 Harness Root 入口、读取顺序、敏感边界和文档治理规则。 |
| `INDEX.md` | 从全局索引路由到 Harness、用户知识库和运行态边界。 |
| `harness/HarnessIndex.md` | 确认 General Harness 资产分层和 RAG、Knowledge、Skill、Tool、Governance 入口。 |
| `harness/architecture/PLANS.md` | 确认当前阶段状态和 Knowledge / Memory 闭环验收边界。 |
| `harness/skills/SkillIndex.md` | 确认本 Skill reviewed 路由和是否存在可 patch 的同类 Skill。 |
| `harness/skills/SkillPolicy.md` | 确认 Skill 创建、更新、候选、审核、晋升和 Git 管理规则。 |
| `harness/governance/SkillGovernance.md` | 确认 Skill review gate、promotion gate 和 usage sidecar 要求。 |

### 2.2 RAG / Knowledge 机制

| 文档 | 读取目的 |
|---|---|
| `harness/rag/RAGIndex.md` | 确认 RAG 机制、reviewed Knowledge、candidate Knowledge 和 runtime index 的边界。 |
| `harness/governance/KnowledgePromotionPolicy.md` | 确认 raw -> candidate -> reviewed 的晋升门禁和禁止路径。 |
| `harness/rag/policies/ObsidianLlmWikiPluginBoundary.md` | 确认 Obsidian LLM Wiki 类插件只能作为阅读、候选生成、lint、query 和本地治理辅助。 |
| `harness/rag/policies/CandidatePostPromotionCleanupPolicy.md` | 确认 candidate 完成生命周期后的 full corpus 清理、轻量审计记录和 approved apply 边界。 |
| `harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md` | 确认 schema、granularity、tag vocabulary、source gate、fingerprint、alias dedup、repair order 和 reviewed-only graph retrieval 的吸收边界。 |
| `harness/tools/docs/script-index/ScriptIndex.md` | 查询 stable RAG Knowledge 命令面和脚本文档入口。 |
| `harness/skills/candidate/rag-structured-ingestion/SKILL.md` | 当任务从 raw source 进入 candidate ingestion 时，先使用 raw-to-candidate workflow，再回到本 Skill 使用 reviewed Knowledge。 |
| `user/knowledge/README.md` | 确认真正用户知识库的 raw、candidate、reviewed、Home 和 local-only 边界。 |

## 3. 边界规则

- 事实回答只使用 `user/knowledge/reviewed/` 或用户指定 private reviewed knowledge repo 中的 authoritative reviewed pages。
- 不把 raw source、candidate wiki、chunks、graph JSON、eval reports、Obsidian generated index、plugin runtime 或 query history 当作 authoritative knowledge。
- 原始材料转换后的 normalized Markdown 应位于 `user/knowledge/raw/<domain>/normalized/` 或外部 private raw source boundary；不要把 `var/rag/<run-id>/extracted/*.md` 当作长期 Source Trace。
- Source-level reviewed page 应提供中文主体综合内容，能覆盖原材料的核心主线、概念、方法和边界；concept page 只是知识图谱节点，不替代 source-level reviewed page。
- `query-reviewed` 只用于定位 reviewed pages；回答前必须读取命中页正文、frontmatter、Source Trace 和 Governance Notes。
- `reviewed-gap-plan`、`enrich-gap-candidates`、`gap-review-package`、`candidate-cleanup-plan` 和 validation reports 都是候选或治理输入，不等于 reviewed Knowledge。
- 写入 reviewed Knowledge 只能通过 review gates 和用户明确批准的稳定命令；插件输出不得绕过 review 直接进入 reviewed。
- 本 Skill 不保存真实用户知识正文、raw source、未脱敏日志、本机绝对路径、插件配置、API key、settings、auth 或 token。

## 4. 稳定命令

统一使用 stable wrapper：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root <HARNESS_ROOT> -Command <command>
```

常用 commands：

| Command | 用途 |
|---|---|
| `init-obsidian-vault` | 初始化 `user/knowledge/` Obsidian vault view。 |
| `sync-reviewed-index` | 扫描 reviewed Knowledge 并同步单入口 `Home.md`。 |
| `health-reviewed` | 检查 reviewed docs、index files、frontmatter 和敏感模式。 |
| `build-reviewed-graph` | 重建 reviewed graph runtime。 |
| `query-reviewed` | 对 authoritative reviewed Knowledge 做 deterministic lookup。 |
| `reviewed-gap-plan` | 把 reviewed 文档里的 unresolved wikilinks 转为 candidate enrichment plan。 |
| `dispose-residual-gaps` | 把已知 workflow / mechanism residual gap 归并到 policy / Skill / template 机制引用，不执行 reviewed Knowledge 晋升。 |
| `canonicalize-vault-layout` | 把 local-only knowledge vault 收敛为 source-centered、domain-aware、semantic-name 布局。 |
| `validate-knowledge-vault` | 运行一键 Knowledge validation gate，检查 registry、Home、domain schema、source trace、graph、duplicate、archive、Git ignore、plugin boundary 和 LLM Wiki 机制吸收。 |
| `schema-context` | 按 domain schema 和任务类型输出 task-scoped schema context；只读 registry 和 reviewed domain schema，不写知识库页面。 |
| `validate-llm-wiki-mechanisms` | 验证 schema context、source gate fixture、extraction granularity fixture、tag vocabulary、alias/body similarity duplicate governance、repair order、reviewed graph PPR 和 auto maintenance boundary。 |
| `candidate-cleanup-plan` | dry-run 盘点 post-promotion candidate full corpus、轻量审计记录、reviewed/Home/registry 引用和推荐清理动作。 |
| `candidate-cleanup-apply` | 在用户批准后移动完成生命周期的 full candidate corpus、保留轻量审计记录并改写 source trace。 |
| `govern-reviewed-duplicates` | 检查同 raw source / topic 的重复 reviewed pages 是否只有一个 authoritative page。 |
| `enrich-gap-candidates` | 用 reviewed Knowledge evidence 补强 gap candidate pages。 |
| `gap-review-package` | 生成 human review package，列出 ready / dedup / revise 决策输入。 |
| `promote-gap-candidates` | 在用户明确批准后，将 approved gap candidates 晋升为 reviewed concept pages。 |
| `govern-vault` | 治理 Obsidian vault 单入口、candidate review queue、archive summary 和 raw source summary。 |
| `govern-vault -ArchiveInactiveCandidates` | 将 inactive candidates 非破坏性移动到 `candidate/_archive/`，并同步 reviewed source trace。 |
| `pipeline-smoke` | 用一个稳定命令验证 raw -> candidate -> approved promotion -> reviewed vault -> query 的完整链路。 |

## 5. 回答 reviewed Knowledge 问题

1. 运行 `query-reviewed -Question <question>`。
2. 读取 query JSON 中命中的 authoritative reviewed page。
3. 如果命中的是 concept page，继续读取其 source-level reviewed page；不要只基于概念页的一句话回答复杂问题。
4. 只用 reviewed page 的正文、frontmatter、Source Trace、Key Concepts、Source Overview、Core Framework 和 Governance Notes 作为事实依据。
5. 如 reviewed page 明确不足以覆盖问题，但 Source Trace 指向 `raw/<domain>/normalized/`，可以把 normalized Markdown 作为原始材料的可读派生版本辅助理解，并在回答中说明 reviewed Knowledge 仍是结论层事实源。
6. 不要回退读取 candidate、runtime artifacts、`var/rag/<run-id>/extracted/*.md` 或插件输出作为事实依据。
7. 回答中说明依据来自 reviewed Knowledge，并保留必要的 scope、reviewedAt、source trace 或 staleness caveat。

## 6. Obsidian 阅读入口

1. 运行 `init-obsidian-vault` 或 `sync-reviewed-index`。
2. 人类用户在 Obsidian 中打开 `user/knowledge/` vault。
3. 从 `Home.md` 进入 reviewed domains 和 reviewed pages。
4. 不依赖旧的 `KnowledgeIndex.md`、`ReviewedKnowledgeIndex.md` 或 `ReviewedOverview.md`。
5. Obsidian view 是阅读界面，不是事实源；事实源仍是 reviewed docs。
6. Obsidian LLM Wiki 类插件只能辅助阅读、candidate generation、lint、query 和本地治理；插件配置和 API key 必须留在 local-only。

## 7. Gap 和治理流程

1. 运行 `build-reviewed-graph` 或直接运行 `reviewed-gap-plan`。
2. 默认只生成 gap report；需要创建候选概念页时加 `-WriteCandidates`。
3. `-WriteCandidates` 写入 local-only candidate knowledge；该目录仍等待 review。
4. 运行 `enrich-gap-candidates`，从 reviewed docs 的 Key Concepts 和引用段落补充候选定义、evidence、适用范围和 promotion hint。
5. 对候选 gap wiki 运行 candidate `health`、`lint` 和 `build-graph`。
6. 运行 `gap-review-package`，生成 reviewer decision template。
7. 如果 review package 或 gap plan 中仍有 workflow / mechanism residual gap，运行 `dispose-residual-gaps`；该命令只改写机制引用和记录 disposition，不晋升 reviewed Knowledge。
8. 只有用户明确批准后，运行 `promote-gap-candidates -Domain <domain> -Reviewer <reviewer> -ApprovalNote <note>`，把 approved concepts 写入 `user/knowledge/reviewed/<domain>/concepts/`。
9. 运行 `govern-reviewed-duplicates`，确认同一 raw source 和同一 topic 只有一个 authoritative reviewed page。
10. 对已晋升、拒绝或归档的 candidate，运行 `candidate-cleanup-plan`；如果 report 建议清理 full corpus，先取得用户批准并保留轻量审计记录，再执行 `candidate-cleanup-apply`。
11. 运行 `canonicalize-vault-layout`，确保 raw、candidate archive、reviewed domain、schema、authoritative page 和 validation evidence 使用 source-centered 结构。
12. 如任务需要按 schema 约束执行 ingest、promotion、query、validation 或 cleanup，运行 `schema-context -Domain <domain> -Task <task>`，只注入当前任务所需的 schema section。
13. 运行 `validate-llm-wiki-mechanisms`，确认 LLM Wiki 吸收机制仍然可执行。
14. 运行 `govern-vault`，刷新 `Home.md` 单入口。
15. 运行 `validate-knowledge-vault`，作为一键收口门禁。

## 8. 验收清单

- 已使用 `invoke-rag-knowledge.ps1`，不手动调用 Python internals。
- reviewed query 返回命中页，且 agent 已阅读命中页再回答。
- Obsidian vault view 可从 `user/knowledge/` 打开，并以 `Home.md` 作为单一入口。
- 如使用 Obsidian LLM Wiki 类插件，已遵守插件边界策略，并通过 `validate-knowledge-vault` 的 plugin boundary 检查。
- gap plan 明确列出 unresolved wikilinks、引用来源、candidate target 和 `candidate-only-no-promotion` boundary。
- 如写入 candidate gap wiki，已运行 `enrich-gap-candidates`、`gap-review-package` 和 `govern-vault`，并且 candidate `health`、`lint` 和 `build-graph` 均通过或给出明确 repair action。
- 如用户批准晋升，`promote-gap-candidates` 已生成 `reviewed/<domain>/concepts/` concept pages，并且 reviewed `health`、`build-reviewed-graph`、`query-reviewed` 均通过。
- 如存在 workflow / mechanism residual gap，`dispose-residual-gaps` 已通过，`reviewed-gap-plan` gap count 为 0，`build-reviewed-graph` broken link count 为 0。
- `canonicalize-vault-layout` 已通过且幂等；`raw/<domain>/`、`reviewed/<domain>/index.md`、`reviewed/<domain>/schema.md`、source-centered candidate archive、semantic-name authoritative page 均存在。
- `validate-knowledge-vault` 已通过；local registry、Home、domain schema、reviewed frontmatter、source trace、reviewed graph、gap plan、duplicate governance、archive reference、Git ignore boundary、Obsidian plugin boundary 和 LLM Wiki mechanism absorption 均无 blocking issues。
- Source-level reviewed page 已包含中文主体的 Source Overview、Core Framework 或等价结构，能概括原材料的核心内容。
- reviewed `sourceRefs` 不引用 `var/rag/<run-id>/extracted/*.md` 作为长期 source；如有 normalized Markdown，应位于 `raw/<domain>/normalized/`。
- `schema-context` 可按任务输出 domain schema section，且不写知识库页面。
- `validate-llm-wiki-mechanisms` 已通过；schema context、source gate fixture、extraction granularity fixture、tag vocabulary、alias/body similarity duplicate governance、repair order、reviewed graph PPR 和 auto maintenance boundary 均无 blocking issues。
- `candidate-cleanup-plan` 已在需要时运行；post-promotion full corpus 的保留、移出或删除已有 dry-run report 和用户批准路径。
- 如存在重复 reviewed pages，`govern-reviewed-duplicates` 已通过，且 query 不返回 evidence-only page 作为事实来源。
- 如用户要求 full pipeline smoke，使用 `pipeline-smoke -InputPath <raw> -Reviewer <reviewer> -ApprovalNote <note> -Question <query>`；通过标准是 candidate gates、promotion、vault governance、reviewed health、reviewed graph 和 reviewed query 全部通过，且 query 命中新晋升 reviewed target。
- 未经用户明确批准，不写入 reviewed Knowledge、Memory、Project Fact 或 Harness architecture authority。

## 9. 治理

| 检查项 | 规则 |
|---|---|
| 文档 | `harness/skills/reviewed/rag-knowledge-use/SKILL.md` |
| 版本 | `v1.1.0-knowledge-rag-closeout` |
| 状态 | `active` |
| 资产状态 | reviewed |
| 关联文档 | 已在正文列出 Harness 入口、SkillIndex、SkillPolicy、SkillGovernance、RAGIndex、KnowledgePromotionPolicy、插件边界、candidate cleanup、LLM Wiki 机制吸收、ScriptIndex 和 raw-to-candidate Skill。 |
| 事实边界 | 事实回答只来自 authoritative reviewed Knowledge；candidate、raw、runtime 和插件输出不作为事实源。 |
| 敏感边界 | 不保存真实知识正文、raw source、未脱敏日志、本机绝对路径、插件配置或凭据。 |
| 晋升记录 | 用户已要求完成审核与验收；本 Skill 由 candidate 晋升为 reviewed Skill。 |
