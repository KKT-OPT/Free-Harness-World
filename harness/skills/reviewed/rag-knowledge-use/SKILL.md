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
| `harness/rag/pipelines/PdfNormalizationContract.md` | PDF 按物理页规范化、OCR、水印规则与纠错配置。 |
| `harness/tools/docs/command-surfaces/RagDocumentPipeline.md` | manifest 摄取、完整晋升映射、审核快照、正文封印及旧语料审计。 |
| `harness/skills/candidate/rag-structured-ingestion/SKILL.md` | 当任务从 raw source 进入 candidate ingestion 时，先使用 raw-to-candidate workflow，再回到本 Skill 使用 reviewed Knowledge。 |
| `user/knowledge/README.md` | 确认真正用户知识库的 raw、candidate、reviewed、Home 和 local-only 边界。 |

## 3. 边界规则

- 知识库事实只使用 `user/knowledge/reviewed/` 或用户指定 private reviewed knowledge repo 中的 authoritative reviewed pages。正式混合问答的外部证据分别标注，不把它称为已审核知识。
- 不把 raw source、candidate wiki、chunks、graph JSON、eval reports、Obsidian generated index、plugin runtime 或 query history 当作 authoritative knowledge。
- 原始材料转换后的 normalized Markdown 应位于 `user/knowledge/raw/<domain>/normalized/` 或外部 private raw source boundary；不要把 `var/rag/<run-id>/extracted/*.md` 当作长期 Source Trace。
- Source-level reviewed page 应提供中文主体综合内容，能覆盖原材料的核心主线、概念、方法和边界；concept page 只是知识图谱节点，不替代 source-level reviewed page。
- `query-reviewed` 返回命中的 reviewed 条款正文及行号；完整的条款片段可直接支持回答。适用范围、版本或质量标记不清时继续读取对应 reviewed 页；目录与链接不替代答案证据。
- `reviewed-gap-plan`、`enrich-gap-candidates`、`gap-review-package`、`candidate-cleanup-plan` 和 validation reports 都是候选或治理输入，不等于 reviewed Knowledge。
- 写入 reviewed Knowledge 只能通过 review gates 和用户明确批准的稳定命令；插件输出不得绕过 review 直接进入 reviewed。
- 本 Skill 不保存真实用户知识正文、raw source、未脱敏日志、本机绝对路径、插件配置、API key、settings、auth 或 token。

### 3.1 测试与正式使用模式

用户要求测试、验证或评测知识库查询时，使用 `knowledge-only`：答题事实及版本判断仅来自 reviewed，允许依据库内条件推理；不得搜索网页或打开来源外链，也不得以“只核验元数据”为例外。缺少正文、时效或替代关系证据时报告知识缺口。

正式使用按任务需要可选 `mixed`，允许知识库与网页结合，分别注明来源及核验范围；外部事实不会因此自动晋升。两个模式不能混计验收。已有库内网页核验记录只能按其已保存的时间与范围引用。

完整规则与审计格式见 [知识查询与评测来源边界](../../../rag/policies/KnowledgeQueryEvaluationPolicy.md)。局部文件守卫不证明整轮没有网页调用；更正一次越界记录也不是新的独立复测。

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
| `audit-query-evaluation` | 校验整轮评测输入记录、来源事件、证据哈希与行号；不提供运行时隔离或日志真实性证明。 |
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

1. 明确任务模式，运行 `query-reviewed -Question <question> -Mode knowledge-only` 或正式使用的 `-Mode mixed`；按指定适用日期传入 `-AsOf YYYY-MM-DD`。用户限定来源标识时传 `-SourcePrefix`；例如国标范围使用 `GB`，不把行业标准当作国家标准依据。
2. 阅读 query JSON 中的 authoritative reviewed 条款片段、行号、质量标记和版本上下文；必要时继续读取对应 reviewed 页。
3. 如果命中的是 concept page，继续读取其 source-level reviewed page；不要只基于概念页的一句话回答复杂问题。
4. 只用 reviewed page 的正文、frontmatter、Source Trace、Key Concepts、Source Overview、Core Framework 和 Governance Notes 作为事实依据。
5. 如 reviewed 内容不足以独立覆盖问题，明确记录知识缺口。原件与 normalized 核验属于摄取补强流程，应形成候选、审核并晋升完整条款；不以回查 PDF 或图像后补出的答案冒充 reviewed-only 查询通过。
6. 不要回退读取 candidate、runtime artifacts、`var/rag/<run-id>/extracted/*.md` 或插件输出作为事实依据。
7. 回答中说明依据来自 reviewed Knowledge，并保留必要的 scope、reviewedAt、source trace 或 staleness caveat。
8. 版本冲突先核对同一事项、适用范围和替代关系，再优先采用适用日期已生效的最新规定。发布日期、实施日期、官方状态核验时间和 reviewedAt 分开；未知状态保持未知，不把较新年份的不同分类口径直接覆盖旧条款。
9. 纯库测试的第8步只使用库内版本证据，不能联网补证；记录整轮实际工具来源与推理前提，使用 `audit-query-evaluation -EvaluationRecord <runtime-record.json>` 校验。事件不全或未分类不可验收；网页访问使该次纯库测试无效，即使查到的正文数值没有变化。

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

处理 PDF 或修复旧转换结果时，先调用 candidate 稳定门面的 `normalize-pdf` 或 `audit-corpus`。原件保留不变；规范化副本留在 raw 的 `normalized/`，按物理页保留原图、提取方法和来源哈希。缺少可靠文本/OCR 时停止候选摄取；特殊公式字形应保留原图，不能直接按乱码丢弃。

水印过滤及数值纠错只使用原件哈希绑定、有审核人与证据的本地配置。不得把特定标准号、专业知识或词表硬编码到通用工具，也不得使用全局 NFKC 改写上标和单位。

多源晋升先准备完整 `PromotionMap`，为每个 source 显式指定 `sourceId`、`target` 与 `draft`；单源也应提交审核过的草稿。草稿保留原件和规范化副本的 `sourceRefs`。运行 `review-package` 后再 `promote-reviewed`，两次使用相同绑定参数；来源或草稿变化后重新审核。晋升后核对正文哈希，不再用脚本覆盖目标。

结构门禁、转换质量检查和语义审核分别记录。`audit-corpus -RequireSealed` 可要求正文与历史晋升记录一致；缺少旧记录只能报告未封印，不能补造历史批准。机器检查不能证明摘要、数值、引文或法规状态准确。

PDF 来源页必须有可独立查询的条款正文和适用条件，不能只有章节入口。已有来源页可用 candidate 门面的 `prepare-reviewed-content` 准备逐页来源对齐草稿和完整 PromotionMap，再经审核晋升。`contentCoverage` 检查文本覆盖，页级校核标记表达语义复核范围。验收应包含实际问答和仅开放 reviewed 的读取测试，核对完整结论、数值边界和引用行号；不只检查命中文档。

测试先冻结知识版本与来源范围，失败时保留问题。原件核验、联网补强、草稿修订及晋升属于后续构建流程；不能改好知识后把同一冻结基线记为通过。跨页逻辑条款必须保留完整条件；同一回答的网页来源审计与局部I/O守卫分别记录。

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
- 如用户要求 full pipeline smoke，使用 `pipeline-smoke -InputPath <raw> -ReviewedDraft <draft> -Reviewer <reviewer> -ApprovalNote <note> -Question <query>`；草稿必须已结合原件审核。通过标准是 candidate gates、promotion、vault governance、reviewed health、reviewed graph 和 reviewed query 全部通过，且 query 命中新晋升 reviewed target。工具不会按关键词编造正文，也不附带晋升 concepts；现有 RunId 不允许清空重跑。
- 未经用户明确批准，不写入 reviewed Knowledge、Memory、Project Fact 或 Harness architecture authority。

## 9. 治理

| 检查项 | 规则 |
|---|---|
| 文档 | `harness/skills/reviewed/rag-knowledge-use/SKILL.md` |
| 版本 | `v1.4.0-query-evaluation-boundary` |
| 最近复查 | 2026-10-29，用户审核通过构建规则和评测边界并授权沉淀及提交；双PowerShell各67项回归与工具审查见 `harness/reports/redacted/RagToolReliabilityReview.md`。 |
| 状态 | `active` |
| 资产状态 | reviewed |
| 关联文档 | 已在正文列出 Harness 入口、SkillIndex、SkillPolicy、SkillGovernance、RAGIndex、KnowledgePromotionPolicy、插件边界、candidate cleanup、LLM Wiki 机制吸收、ScriptIndex 和 raw-to-candidate Skill。 |
| 事实边界 | 知识库事实来自 authoritative reviewed Knowledge；纯库测试不外查，正式混合使用的外部证据单独归属，candidate、raw、runtime和插件输出不作为已审核知识。 |
| 敏感边界 | 不保存真实知识正文、raw source、未脱敏日志、本机绝对路径、插件配置或凭据。 |
| 晋升记录 | 用户已要求完成审核与验收；本 Skill 由 candidate 晋升为 reviewed Skill。 |
