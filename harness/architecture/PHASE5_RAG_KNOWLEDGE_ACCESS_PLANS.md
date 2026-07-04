---
documentName: harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
version: v1.8.0-p5-23-review-fixes
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: review
purpose: 临时记录 Phase 5 Reviewed Knowledge Access Layer、LLM Wiki 吸收判断、知识库治理任务和验收标准。
scope:
  - phase5-rag-knowledge-access
  - reviewed-knowledge
  - obsidian-vault
  - agent-query
  - candidate-gap-plan
  - candidate-archive
  - reviewed-concept-pages
  - pipeline-smoke
  - llm-wiki-pattern
  - knowledge-vault-governance
prerequisites:
  - AGENTS.md
  - harness/architecture/PLANS.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - harness/architecture/PLANS.md
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/skills/rag-structured-ingestion/SKILL.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/reports/redacted/P5-22RagKnowledgeUseSkillReview.md
  - user/knowledge/README.md
outputTo:
  - harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
owner: mixed
reviewAfter: 2026-07-10
supersededBy:
dependsOn:
  - harness/architecture/PLANS.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-04
  decision: p5-23-review-fixes-applied
---
# Phase 5 Reviewed Knowledge Access Layer 临时计划

## 1. 目标

Phase 5 的目标是把已经完成审核和晋升的 reviewed Knowledge 变成可被人类阅读、可被 agent 稳定查询、可被后续 RAG index 重建使用的本地知识库界面。

最小验收目标：

```text
用户能在 Obsidian 打开 reviewed 知识库；
agent 能通过稳定命令查询 reviewed Knowledge；
agent 能基于查询结果阅读 reviewed 文档并回答问题。
```

## 2. 边界

- `user/knowledge/reviewed/` 是 reviewed Knowledge 的事实源位置。
- Obsidian vault、`Home.md` 单入口和 graph 是阅读与导航界面，不反向成为事实源。
- `var/rag/` 下的 graph、query report、health report 和 gap report 是可重建运行态产物。
- raw、candidate、chunks、graph JSON 和 eval reports 不作为 authoritative knowledge。
- unresolved reviewed wikilinks 只能进入 candidate gap plan，不能绕过 review 直接写入 reviewed Knowledge。
- Phase 5 不自动修改 Memory、Project Facts 或 Harness architecture authority。
- Karpathy's LLM Wiki 模式和 Obsidian LLM Wiki 插件只作为知识库组织和候选生成参考；Harness 的事实源仍以 reviewed Knowledge 和 Knowledge Promotion Policy 为准。

### 2.1 用户提供的 llm-wiki Skill 参考分析

用户提供的 llm-wiki Skill 参考文档强调的是 persistent compounding Markdown knowledge base，中文可理解为持续复利式 Markdown 知识库，而不是传统 query-time RAG。其可采纳设计如下：

| 设计点 | Skill 原始意图 | Harness 吸收判断 |
|---|---|---|
| 人机分工 | 用户负责 sources 和分析方向，agent 负责摘要、交叉链接、归档和一致性维护。 | 采纳；但 agent 只能维护 raw/candidate/reviewed 的边界，不能绕过用户审核晋升 reviewed Knowledge。 |
| 三层结构 | raw sources、wiki pages、schema。 | 采纳为 raw / candidate wiki / reviewed domain vault / schema-index-log 纪律层。 |
| 会话恢复 | 每次操作前读 `SCHEMA.md`、`index.md`、近期 `log.md`。 | 采纳为 agent orientation rule；在 Harness 中对应读取 `Home.md`、领域 `index.md`、领域 `schema.md` 和候选 review package。 |
| raw 不可变 | raw source 只读，更新通过 wiki pages 表达。 | 采纳；`raw/<domain>/` 应带 source metadata、hash 或 manifest，变更只能生成 drift/re-ingest candidate。 |
| schema 和 tag taxonomy | schema 约束 frontmatter、文件命名、tag、page threshold。 | 采纳；通用 Harness 提供模板和门禁，具体 schema 位于 user knowledge domain boundary。 |
| index 和 log | index 负责导航，log 记录 ingest/update/query/lint/archive/delete。 | 部分采纳；`Home.md` 保持全局入口，领域 `index.md` 负责目录；log 只能作为 local-only 操作证据，不是事实源。 |
| entity/concept/comparison/query 页面 | wiki 页面由 agent 维护并交叉链接。 | 采纳；但新页面先进入 candidate，reviewed 页面按领域目录组织。 |
| lint | 检查 broken links、orphans、frontmatter、stale、contradictions、source drift、tag sprawl、page size。 | 采纳为 H9-4 Knowledge 一键验证门禁目标。 |
| archive | fully superseded 内容进入 `_archive/`，不直接消失。 | 采纳；已晋升证据和 source trace 关联候选不得直接删除。 |

不采纳或需要约束的部分：

- 不把插件或 Skill 生成的 wiki 直接视为 reviewed Knowledge。
- 不把 query result 默认写回 reviewed；有长期价值的 query/comparison 也必须先进入 candidate。
- 不把 `raw/`、candidate、graph、chunks、eval report 或 Obsidian 生成视图当作事实源。
- 不把本机插件配置、API key、workspace 状态或 Obsidian runtime state 写入通用 Harness Git。

## 3. 阶段任务

| 任务 | 目标输出 | 验收标准 | 状态 |
|---|---|---|---|
| P5-1 临时计划 | 本文件 | 目标、边界、任务和验收标准清晰。 | complete |
| P5-2 Obsidian vault 初始化 | `user/knowledge/.obsidian/`、`Home.md` | 用户可把 `user/knowledge/` 作为 Obsidian vault 打开。 | complete |
| P5-3 Reviewed index 同步 | `Home.md` 中的 Reviewed Knowledge 区块 | 已晋升 reviewed 文档可从单入口进入，入口不包含 raw/candidate 正文。 | complete |
| P5-4 Reviewed graph | `var/rag/reviewed-knowledge/graph/graph.json` 和 `graph.html` | 图谱只扫描 reviewed layer 和 vault index pages。 | complete |
| P5-5 Reviewed query | 稳定命令 `query-reviewed` | 查询命中 reviewed 文档并返回路径、标题、分数、匹配段落和相关链接。 | complete |
| P5-6 Agent 使用验证 | 本轮最终回答 | agent 使用稳定查询结果阅读 reviewed 文档并回答知识库问题。 | complete |
| P5-7 Reviewed gap plan | `reviewed-gap-plan` 和 gap report | unresolved reviewed wikilinks 被转为 candidate-only 补强任务。 | complete |
| P5-8 Gap candidate wiki | `user/knowledge/candidate/reviewed-gap-concepts/wiki` | candidate health、lint 和 graph 验证通过，不写入 reviewed Knowledge。 | complete |
| P5-9 Reviewed knowledge use Skill | `harness/skills/candidate/rag-knowledge-use/SKILL.md` | Skill 进入 candidate flow，说明使用场景、稳定命令、边界、完成标准。 | complete |
| P5-10 Gap candidate source-grounded enrichment | `enrich-gap-candidates` 和 enriched candidate pages | gap candidate pages 从 reviewed Knowledge 提取定义、evidence、适用范围和 promotion hint，验证通过且不写入 reviewed Knowledge。 | complete |
| P5-11 Gap candidate review package | `gap-review-package` 和 reviewer decision template | review package 汇总 ready / dedup / revise 分类、门禁和审核模板；不写入 reviewed Knowledge。 | complete |
| P5-12 Knowledge vault pre-review governance | `govern-vault`、`Home.md` | 审核前把 active review、archived candidates、raw provenance 和 reviewed facts 分开；不晋升 reviewed Knowledge。 | complete |
| P5-13 Non-destructive archive and single entry rebuild | `govern-vault -ArchiveInactiveCandidates`、`candidate/_archive/`、`Home.md` | `user/knowledge` 根目录只保留 README、Home、raw、candidate、reviewed 和 `.obsidian`；`candidate/` 根目录只保留 active candidate 和 `_archive`；reviewed source trace 已同步；查询和健康检查通过。 | complete |
| P5-14 Approved gap candidates to reviewed concept pages | `promote-gap-candidates`、`user/knowledge/reviewed/agent/concepts/*.md` | 已把 7 个 approved gap candidates 晋升为 reviewed concept pages；2 个 dedup 项保留为 candidate gap；reviewed graph broken links 从 9 降到 2；query 能命中 concept page。 | complete |
| P5-15 Full pipeline smoke | `pipeline-smoke`、`p5-15-pipeline-smoke.md` | 已用真实 raw PDF 跑通 raw -> candidate -> approved promotion -> reviewed vault -> query；query 首位命中新晋升 reviewed page；candidate smoke run 已归档为 promoted evidence。 | complete |
| P5-16 Knowledge local registry | `user/registry/knowledge.local.json` | 本地知识库 registry 存在，记录 local-only knowledge roots、scope、status 和 sensitive boundary summary；不写入真实知识正文或私有同步信息。 | complete |
| P5-17 Domain vault layout | `raw/<domain>/`、`reviewed/<domain>/index.md`、`reviewed/<domain>/concepts/` | 原始材料按知识领域归档；reviewed Knowledge 按领域组织；`Home.md` 仍是全局入口。 | complete |
| P5-18 Duplicate reviewed knowledge governance | reviewed supersede/archive plan | 同一 raw source、同一主题的重复 reviewed 文档只能保留一个 active authoritative page，其余进入 superseded/archive 或明确作为验证证据。 | complete |
| P5-19 Residual gap disposition | `CandidateKnowledge` / `StructuredIngestion` disposition | 残余 gap 按 dedup / defer / separate-candidate 处理，不从当前 PDF 派生候选中直接晋升。 | complete |
| P5-19.5 P5-20 pre canonical vault layout | `canonicalize-vault-layout` | 在进入一键验证门禁前，把知识库收敛为 source-centered、domain-aware、semantic-name 布局。 | complete |
| P5-20 Knowledge one-click validation gate | `validate-knowledge-vault` | 一键检查 registry、Home、domain index/schema、reviewed frontmatter、source trace、broken links、duplicate source、archive references、Git ignore boundary 和 plugin boundary。 | complete |
| P5-21 Obsidian LLM Wiki plugin boundary | plugin usage policy | 插件可作为 candidate generation / human reading UI；不得直接写 reviewed；插件配置和 API key 留在 local-only。 | complete |
| P5-21.5 Candidate post-promotion cleanup policy | `CandidatePostPromotionCleanupPolicy.md`、`candidate-cleanup-plan`、`candidate-cleanup-apply` | 晋升、拒绝或归档后的 candidate full corpus 默认移出 Obsidian 默认图谱或删除，只保留轻量审计记录；dry-run 命令可盘点 full corpus、引用和推荐动作；apply 命令在用户批准后移动 full corpus、保留审计记录并改写 source trace。 | complete |
| P5-21.6 LLM Wiki mechanism absorption | `LlmWikiMechanismAbsorptionPolicy.md`、manifest/template/architecture updates、validation gate | 吸收 schema config、extraction granularity、tag vocabulary、source gate、source fingerprint、alias-aware dedup、repair order、reviewed-only graph retrieval 和 auto maintenance 边界，并通过 `validate-knowledge-vault` 检查落地状态。 | complete |
| P5-22 `rag-knowledge-use` Skill review | `harness/skills/reviewed/rag-knowledge-use/SKILL.md`、`harness/reports/redacted/P5-22RagKnowledgeUseSkillReview.md` | 在目录口径和验证门禁稳定后，已将 candidate Skill 晋升 reviewed，清理 candidate 路由，同步 SkillIndex、usage sidecar 和验收记录。 | complete |
| P5-23 LLM Wiki remaining mechanism hardening | `schema-context`、`validate-llm-wiki-mechanisms`、真实 PDF full pipeline validation | 已补齐 task-scoped schema context、提取颗粒度实际策略、强制 authoritative tags、source gate fixture、alias/body similarity duplicate governance、reviewed graph PPR 验证和 auto maintenance boundary validation；新增真实 PDF 已完成 raw -> candidate -> reviewed -> cleanup -> query 全流程验证。 | complete |
| P5-23.1 User review fixes for source depth and normalized raw markdown | reviewed Knowledge 内容修正、normalized Markdown raw boundary、source trace gate | 根据用户审核意见，修正 reviewed page 主体语言为中文，补足 source-level reviewed page 的 Source Overview / Core Framework / Knowledge Implications，并把原始材料转换后的 Markdown 长期保存到 `raw/<domain>/normalized/`；门禁阻止 authoritative reviewed sourceRefs 依赖 `var/rag/<run-id>/extracted/*.md`。 | complete |

## 4. 稳定命令设计

reviewed knowledge access facade：

```text
harness/tools/scripts/stable/invoke-rag-knowledge.ps1
```

Subcommands：

| Command | 用途 |
|---|---|
| `init-obsidian-vault` | 初始化 `user/knowledge/` 的 Obsidian vault 推荐配置和入口页。 |
| `sync-reviewed-index` | 扫描 reviewed Knowledge，同步 `Home.md` 中的 reviewed 入口。 |
| `build-reviewed-graph` | 从 reviewed layer 和 vault index pages 生成 graph JSON / HTML。 |
| `health-reviewed` | 检查 reviewed Knowledge 和 vault index 的基础结构。 |
| `query-reviewed` | 对 reviewed Knowledge 做 deterministic lookup，供 agent 阅读和回答。 |
| `reviewed-gap-plan` | 扫描 reviewed docs 中的 unresolved wikilinks，生成 candidate-only gap plan；可选 `-WriteCandidates` 写入候选概念页。 |
| `dispose-residual-gaps` | 处置 reviewed gap plan 中明确属于 Harness 机制或 workflow 的残余 gap：改写已审核页面中的残余 wikilink 为 policy / Skill / template 引用，标记候选页 disposition，不执行 reviewed Knowledge 晋升。 |
| `canonicalize-vault-layout` | 在 P5-20 前把当前知识库迁移到 canonical layout：`raw/<domain>/`、`reviewed/<domain>/index.md`、`reviewed/<domain>/schema.md`、语义命名 authoritative page、source-centered candidate archive 和 archived validation evidence。 |
| `validate-knowledge-vault` | P5-20 一键 Knowledge validation gate；只写 runtime report 和 status JSON，检查 local registry、Home 单入口、domain schema、reviewed frontmatter、source trace、reviewed graph、gap plan、duplicate source governance、archive/audit references、Git ignore boundary、Obsidian plugin boundary 和 LLM Wiki 机制吸收 gate。 |
| `candidate-cleanup-plan` | P5-21.5 post-promotion cleanup dry-run；只写 runtime report 和 status JSON，盘点 candidate full corpus、轻量审计记录、reviewed/Home/registry 引用和推荐清理动作，不删除、不移动、不改写 reviewed source trace。 |
| `candidate-cleanup-apply` | P5-21.5 post-promotion cleanup apply；需要 reviewer 和 approval note，移动 candidate full corpus 到 `var/rag/candidate-full-corpus-archive/`，写入 `candidate/_audit/post-promotion/` 轻量审计记录，改写 source trace，并更新 Obsidian graph filter。 |
| `schema-context` | 按 domain schema 和任务类型裁剪注入 schema section；只输出任务所需的 schema context，不写 reviewed Knowledge。 |
| `validate-llm-wiki-mechanisms` | 对 obsidian-llm-wiki 已吸收机制执行一键验证，覆盖 schema context、source gate fixture、extraction granularity fixture、tag vocabulary、alias/body similarity duplicate governance、repair order、reviewed graph PPR 和 auto maintenance boundary。 |
| `govern-reviewed-duplicates` | 检查同 raw source / topic 的重复 reviewed pages 是否只有一个 authoritative page，其余是否已治理为 validation evidence、superseded、archived 或 deprecated。 |
| `enrich-gap-candidates` | 用 reviewed Knowledge 的 Key Concepts 和引用段落补强 gap candidate pages，仍停留在 candidate-only boundary。 |
| `gap-review-package` | 生成 human review package，汇总 ready / dedup / revise 分类、review gates 和 reviewer decision template。 |
| `promote-gap-candidates` | 在用户明确批准后，将 approved reviewed gap candidates 晋升为 `reviewed/<domain>/concepts/*.md`；PowerShell facade 使用 `-Domain` 指定领域，dedup/revise 项保留为候选，不自动晋升。 |
| `govern-vault` | 生成 Obsidian `Home.md` 单入口、candidate review queue、archive summary、raw source summary 和 governance rules。 |
| `govern-vault -ArchiveInactiveCandidates` | 将 inactive candidate corpus 非破坏性移动到 `candidate/_archive/`，并同步 reviewed source trace；不执行 reviewed promotion。 |
| `pipeline-smoke` | 用一个稳定命令验证 raw -> candidate -> review package -> approved promotion -> reviewed vault -> query 的端到端链路；默认 target 是 `reviewed/<domain>/<run-id>.md` 形式的验证输出，仍要求 reviewer 和 approval note；进入正式 vault 前必须通过 `canonicalize-vault-layout` 收口为语义命名 authoritative page 或 validation evidence archive。 |

## 5. 验收案例

使用 Phase 4 已晋升的 reviewed Knowledge：

```text
user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md
```

验收查询：

```text
Agent Harness Engineering 的核心结论是什么？
```

通过标准：

- `query-reviewed` 返回该 reviewed 文档；
- agent 阅读该 reviewed 文档；
- 回答明确基于 reviewed Knowledge 的 Statement、Key Concepts、Source Trace；
- 不引用 raw PDF、candidate scaffold 或 chunks 作为事实源。

## 6. 本轮执行记录

Phase 5 minimum acceptance 已完成：

- 新增 stable facade：`harness/tools/scripts/stable/invoke-rag-knowledge.ps1`。
- 新增 Python command package：`harness/tools/scripts/stable/rag_knowledge/`。
- 已运行 `init-obsidian-vault`，生成 `user/knowledge/.obsidian/` 和 `Home.md`。
- 已运行 `health-reviewed`，状态为 `passed`。
- 已运行 `build-reviewed-graph`，生成 reviewed graph runtime。
- 已运行 `query-reviewed`，命中 `user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md`。

本阶段新增执行记录：

- 新增 `reviewed-gap-plan` 子命令和 `-WriteCandidates` 参数。
- `reviewed-gap-plan` 发现 9 个 unresolved reviewed wikilinks，并生成 `var/rag/reviewed-knowledge/evals/reviewed-gap-plan.md`。
- `-WriteCandidates` 生成 `user/knowledge/candidate/reviewed-gap-concepts/wiki`，作为 local-only candidate gap wiki。
- 新增 candidate Skill：`harness/skills/candidate/rag-knowledge-use/SKILL.md`。
- 更新工具、RAG 和 Skill 索引，记录 reviewed gap plan 与 reviewed Knowledge use workflow。
- 新增 `enrich-gap-candidates` 子命令，用 reviewed Knowledge evidence 补强 gap candidate pages。
- 已补强 9 个 gap candidate pages，其中 7 个来自 reviewed Key Concepts，2 个标记为 workflow / dedup 待审。
- 新增 `gap-review-package` 子命令，生成 `var/rag/reviewed-knowledge/evals/gap-candidate-review-package.md`。
- review package 状态为 `ready-for-human-review`；7 个概念建议进入人工审核，2 个概念建议先去重。
- 新增 `govern-vault` 子命令，治理 `user/knowledge/` Obsidian vault 单入口。
- 新增 `-ArchiveInactiveCandidates` 参数，将 inactive candidates 非破坏性归档到 `candidate/_archive/`，并同步 reviewed source trace。
- 归档后当前 active candidate corpus 1 个：`reviewed-gap-concepts`；archived candidates 4 个；raw source 1 个。
- `Home.md` 成为唯一 Obsidian 主入口；Candidate Review Queue、Current Candidate Items、Archived Candidate Evidence 和 Raw Sources 均折叠进 `Home.md`。
- `user/knowledge` 根目录已收敛为 `.obsidian/`、`README.md`、`Home.md`、`raw/`、`candidate/`、`reviewed/`。
- 新增 `promote-gap-candidates` 子命令，读取 `reviewed-gap-concepts` review package，把用户批准的 approved gap candidates 写入 `user/knowledge/reviewed/agent/concepts/`。
- 本轮已晋升 7 个 reviewed concept pages：`AdaptiveHarnessOptimization`、`BindingConstraintThesis`、`ContextDrift`、`ETCLOVGTaxonomy`、`HarnessCouplingProblem`、`StandardHandoffProtocol`、`TraceNativeEvaluation`。
- `CandidateKnowledgeConcept` 和 `StructuredIngestion` 保持 deferred / dedup，不直接晋升。
- P5-14 晋升后 `Home.md` reviewed list 显示 8 篇 reviewed pages；candidate queue 摘要显示 `promoted=7, deferred=2, skipped=0`。
- 新增 `pipeline-smoke` 子命令，把真实 raw PDF 到 reviewed query 的完整链路封装为稳定 smoke。
- P5-15 使用 `user/knowledge/raw/agent/Agent Harness Engineering A Survey.pdf` 执行 `p5-15-pipeline-smoke`。
- P5-15 生成并晋升 `user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md`，随后 `Home.md` reviewed list 显示 9 篇 reviewed pages。
- P5-15 的 candidate smoke run 已通过 `govern-vault` 归档到 `candidate/_archive/promoted-evidence/p5-15-pipeline-smoke`，不留在 active review queue。
- P5-16 已创建 `user/registry/knowledge.local.json`，接入 `user/knowledge` local-only knowledge vault。
- P5-16 registry 只记录 relative route metadata：`Home.md`、`raw/`、`candidate/` 和 `reviewed/`；不记录 raw 正文、私有同步配置、API key、auth、token、本机绝对路径或私有外部仓库信息。
- P5-16 registry 已确认被 `.gitignore` 的 `user/registry/*.local.json` 规则排除，不进入通用 Harness Git。
- P5-17 已将用户提供的领域名 `agent ` 规范化为 `agent`，并把当前原始材料迁移到 `user/knowledge/raw/agent/`。
- P5-17 已将当前 reviewed Knowledge 迁移到 `user/knowledge/reviewed/agent/`，7 个 reviewed concepts 迁移到 `user/knowledge/reviewed/agent/concepts/`。
- P5-17 已新增 `user/knowledge/reviewed/agent/index.md` 作为领域入口，`Home.md` 仍保持 Obsidian 全局入口，并新增 `Reviewed Domains` 区块指向 `[[reviewed/agent/index|Agent]]`。
- P5-17 已在 `user/registry/knowledge.local.json` 中补充 `agent` domain route metadata；该 registry 仍为 local-only ignore boundary。
- P5-17 已将 `promote-gap-candidates` 和 `pipeline-smoke` 的默认 reviewed 输出调整为 domain-aware：默认 `--domain agent`，显式 `--target-dir` 或 `--target` 仍可覆盖。
- P5-17 已让 `govern-vault` / `sync-reviewed-index` 生成 `Reviewed Domains` 区块，并把 domain `index.md` 从 `Home.md` 的 Reviewed Knowledge 明细中排除，避免领域入口重复出现。
- P5-17 已去除迁移后 reviewed Markdown 的 UTF-8 BOM，避免 `health-reviewed` 把已有 frontmatter 误判为 missing。
- P5-17 已修正 reviewed frontmatter 解析：普通 key 只读取 YAML frontmatter block，嵌套 `review.reviewedBy` / `review.reviewedAt` 按行读取，避免 query metadata 被后续正文污染。
- P5-17 已同步 `ScriptIndex.md`、`RAGIndex.md` 和 candidate `rag-knowledge-use` Skill 中的旧 reviewed 根层路径，统一改为 `reviewed/<domain>/...` 口径。
- P5-18 已新增 `govern-reviewed-duplicates` 稳定命令，输出 `var/rag/reviewed-knowledge/evals/duplicate-reviewed-governance.md`，用于检查同 raw source / topic 的重复 reviewed pages 是否只有一个 authoritative page。
- P5-18 已将 `user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md` 标记为 `knowledgeRole: authoritative` 和 `authoritative: true`，作为 `Agent Harness Engineering A Survey.pdf` 在 agent domain 下的 authoritative reviewed Knowledge。
- P5-18 已将 `user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md` 标记为 `knowledgeRole: validation-evidence`、`authoritative: false` 和 `duplicateDisposition: evidence-only`，只作为 P5-15 pipeline smoke validation evidence。
- P5-18 已让 `query-reviewed`、`reviewed-gap-plan` 和 reviewed concept enrichment 默认只使用 authoritative reviewed pages；reviewed graph 保留 evidence 节点作为导航，但 query 的 graph-neighbor 扩展不会返回 non-authoritative evidence。
- P5-18 已让 `Home.md` 单入口拆分 `Reviewed Knowledge` 和 `Reviewed Validation Evidence`，并明确默认事实源是 `reviewed/` 中的 authoritative pages。
- P5-18 已同步 `KnowledgePromotionPolicy.md`、`RAGIndex.md`、`ScriptIndex.md` 和 candidate `rag-knowledge-use` Skill 的 duplicate reviewed governance 规则。
- P5-19 已新增 `dispose-residual-gaps` 稳定命令，输出 `var/rag/reviewed-knowledge/evals/residual-gap-disposition.md`，用于处置不应从当前 PDF 派生候选中晋升的 residual workflow gaps。
- P5-19 已将 `CandidateKnowledge` 归并到 Harness Knowledge Promotion 机制：`harness/governance/KnowledgePromotionPolicy.md` 和 `harness/templates/knowledge/CandidateKnowledgeTemplate.md`。
- P5-19 已将 `StructuredIngestion` 归并到 RAG structured ingestion 机制：`harness/skills/rag-structured-ingestion/SKILL.md` 和 `harness/templates/knowledge/StructuredIngestionManifestTemplate.md`。
- P5-19 已把 authoritative reviewed page 中的 `[[CandidateKnowledge]]` 和 `[[StructuredIngestion]]` 残余 wikilink 改写为普通机制引用，避免 reviewed graph 继续把它们识别为 broken links。
- P5-19 已在对应 candidate pages 中写入 disposition 记录，并通过 `govern-vault -ArchiveInactiveCandidates` 将 `reviewed-gap-concepts` 归档为 promoted evidence；不新增 reviewed Knowledge。
- P5-19.5 已新增 `canonicalize-vault-layout` 稳定命令，输出 `var/rag/reviewed-knowledge/evals/canonical-vault-layout.md`。
- P5-19.5 已将当前宽泛 `agent` domain 收敛为 `agent-harness-engineering` domain：raw source 位于 `user/knowledge/raw/agent-harness-engineering/`，reviewed domain 位于 `user/knowledge/reviewed/agent-harness-engineering/`。
- P5-19.5 已将 authoritative reviewed page 从验证过程命名 `llm-wiki-absorption-pdf-smoke.md` 改为语义命名 `agent-harness-engineering-survey.md`。
- P5-19.5 已新增 `user/knowledge/reviewed/agent-harness-engineering/schema.md`，并将 `p5-15-pipeline-smoke.md` 移入 `user/knowledge/reviewed/_archive/validation-evidence/agent-harness-engineering/`。
- P5-19.5 已把 candidate archive 改为 source-centered 结构：`user/knowledge/candidate/_archive/by-source/agent-harness-engineering-a-survey/`，其中包含 canonical candidate、validation evidence、gap concepts、legacy 和 layout evidence。
- P5-20 已新增 `validate-knowledge-vault` 稳定命令，输出 `var/rag/reviewed-knowledge/evals/knowledge-validation-gate.md`。
- P5-20 一键门禁已覆盖 12 类检查：local registry、Home 单入口、domain layout/schema、reviewed frontmatter health、source trace、reviewed graph links、reviewed gap plan、duplicate source governance、archive/audit references、Git ignore boundary、Obsidian plugin boundary 和 LLM Wiki mechanism absorption gate。
- P5-20 门禁边界是 read-only validation：只生成 runtime report、graph 和 status JSON，不执行 reviewed promotion，不重排 vault，不把 raw/candidate/chunks/plugin runtime 当作事实源。
- P5-21 已新增 `harness/rag/policies/ObsidianLlmWikiPluginBoundary.md`，把 Obsidian LLM Wiki 类插件定位为 human reading UI、candidate generation、lint、query 和本地治理辅助。
- P5-21 已同步 `HarnessEngineering.md`、`RAGIndex.md`、`KnowledgePromotionPolicy.md`、`user/knowledge/README.md` 和当时仍处于 candidate 状态的 `rag-knowledge-use` Skill 的插件边界链接。
- P5-21 判断：当前不存在 `user/knowledge/reviewed/_achieve/`；实际存在的是 `user/knowledge/reviewed/_archive/`。`reviewed/_archive/` 保存 reviewed validation evidence，被 source trace、duplicate governance 或 validation report 引用时不应删除。
- P5-21.5 已新增并执行 `candidate-cleanup-apply` 稳定命令，输出 `var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-apply.md`；用户批准后已移动 full corpus = 6 到 `var/rag/candidate-full-corpus-archive/2026-07-03/`，生成 post-promotion audit records = 6，并改写 reviewed/Home source trace。
- P5-21.5 cleanup 回归结果：`candidate-cleanup-plan` 显示 active candidate = 0、full corpus = 0、lightweight audit records = 7、recommended cleanup actions = 0；Obsidian graph filter 已设置 `-path:candidate -path:raw -path:.obsidian`。
- P5-21.6 已新增 `harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md`，记录从 `green-dalii/obsidian-llm-wiki` 吸收的 schema config、extraction granularity、tag vocabulary、source gate、source fingerprint、alias-aware dedup、repair order、reviewed-only graph retrieval 和 auto maintenance 边界。
- P5-21.6 已同步 `HarnessEngineering.md`、`RAGIndex.md`、`KnowledgePromotionPolicy.md`、`user/knowledge/README.md`、knowledge templates、`ScriptIndex.md` 和当时仍处于 candidate 状态的 `rag-knowledge-use` Skill；当前 `validate-knowledge-vault` 中 `llm-wiki-mechanism-absorption` gate 已通过。
- P5-22 已完成 `rag-knowledge-use` Skill review：把 Skill 从 `harness/skills/candidate/rag-knowledge-use/` 晋升到 `harness/skills/reviewed/rag-knowledge-use/`，并把 YAML frontmatter 收敛为 Skill 校验器允许的 `name`、`description` 和 `metadata`。
- P5-22 已新增 `harness/reports/redacted/P5-22RagKnowledgeUseSkillReview.md`，记录 user-directed review、existing Skill 检查、promotion disposition、验证命令和下一轮 Knowledge/RAG 收口边界。
- P5-22 已同步 `SkillIndex.md`、`skill-usage.json`、`rag-structured-ingestion` handoff 和相关 RAG policy 链接，移除同名 active candidate 路由，避免 candidate/reviewed 双路由。
- P5-23 已补齐 `schema-context` 稳定命令，按 `ingest`、`promotion`、`query`、`validation`、`cleanup` 等任务裁剪 domain schema section，避免每次任务注入完整 schema 文档。
- P5-23 已补齐 `validate-llm-wiki-mechanisms` 稳定命令，把 schema context、source gate fixture、extraction granularity fixture、tag vocabulary、alias/body similarity duplicate governance、repair order、reviewed graph PPR 和 auto maintenance boundary 合并为一键机制验收。
- P5-23 已让 extraction granularity 从 manifest 记录扩展为实际策略：影响 chunk size、preview limits、batch id、entity cap、concept cap 和 batch strategy 记录。
- P5-23 已把 reviewed authoritative page 的 `tags` 从“存在则越界检查”提升为机制验收要求；domain schema 的 controlled tag vocabulary 是 reviewed tag 的约束来源。
- P5-23 已用新增真实 PDF `Externalization in LLM Agents A Unified Review of Memory Sklls Protocols and Harness Engineering.pdf` 跑通 raw -> candidate -> review package -> approved reviewed promotion -> concept pages -> vault governance -> post-promotion cleanup -> reviewed-only query。
- P5-23 已新增 reviewed domain `llm-agent-externalization`，并让新 reviewed page 与既有 `agent-harness-engineering` domain 建立 wikilink 关系；最终 reviewed graph 无 broken links 和 orphan pages。
- P5-23 full corpus cleanup 已执行 approved apply：本轮新增 promoted candidate full corpus 移入 `var/rag/candidate-full-corpus-archive/2026-07-04/`，vault 中只保留 lightweight audit record；回归 dry-run 显示 full corpus = 0、recommended cleanup actions = 0。
- P5-23 Knowledge/RAG 收口结论：Knowledge/RAG 部分可提交用户审核；H9-4 整体仍需 Memory 闭环另行完成。
- P5-23.1 用户审核发现两个阻塞点：`externalization-in-llm-agents-review` 及部分 concept page 主体语言偏英文；reviewed Source Trace 依赖 `var/rag/.../extracted/*.md`，不符合 var 运行态可清理边界；source-level reviewed page 也需要承载足够的原材料核心内容，而不是只保存关键词或几句摘要。
- P5-23.1 已修正 `externalization-in-llm-agents-review` 和 `agent-harness-engineering-survey`：主体说明改为中文，新增 Source Overview、Core Framework 和 Knowledge Implications，Source Trace 改为引用 `raw/<domain>/normalized/*.md`。
- P5-23.1 已把两份原始材料转换后的 Markdown 复制到 `user/knowledge/raw/agent-harness-engineering/normalized/` 和 `user/knowledge/raw/llm-agent-externalization/normalized/`；这些是 user-local raw source derivative，不进入通用 Harness Git。
- P5-23.1 已同步修正 concept page 生成模板和现有概念页：concept page 增加 Concept Detail，明确概念页只是知识图谱节点，复杂问题应回到 source-level reviewed page。
- P5-23.1 已增强 `validate-knowledge-vault`：authoritative reviewed page 的 `sourceRefs` 若指向 `var/rag/<run-id>/extracted/*.md`，门禁失败，要求改用 raw domain normalized Markdown 或外部 private raw source boundary。

## 7. 验收结果

| 验证项 | 命令或证据 | 结果 |
|---|---|---|
| Python 语法检查 | `python -m py_compile ...rag_candidate... ...rag_knowledge...` | passed |
| Reviewed index sync | `invoke-rag-knowledge.ps1 -Command sync-reviewed-index` | passed，reviewed page count = 9 |
| Reviewed health | `invoke-rag-knowledge.ps1 -Command health-reviewed` | passed，reviewed page count = 9 |
| Reviewed graph | `invoke-rag-knowledge.ps1 -Command build-reviewed-graph` | passed，node count = 10，edge count = 35，broken link count = 2 |
| Reviewed query | `invoke-rag-knowledge.ps1 -Command query-reviewed -Question ...` | passed，命中 reviewed 文档 1 篇 |
| Gap plan | `invoke-rag-knowledge.ps1 -Command reviewed-gap-plan -WriteCandidates` | passed，gap count = 9，candidate written = true |
| Gap candidate health | `invoke-rag-candidate.ps1 -Command health` | passed，page count = 12 |
| Gap candidate lint | `invoke-rag-candidate.ps1 -Command lint` | passed，无 broken links、orphans、sparse pages |
| Gap candidate graph | `invoke-rag-candidate.ps1 -Command build-graph` | passed，node count = 12，edge count = 33 |
| Gap candidate enrichment | `invoke-rag-knowledge.ps1 -Command enrich-gap-candidates` | passed，enriched page count = 9 |
| Enriched candidate health | `invoke-rag-candidate.ps1 -Command health` | passed，page count = 12 |
| Enriched candidate lint | `invoke-rag-candidate.ps1 -Command lint` | passed，无 broken links、orphans、sparse pages |
| Enriched candidate graph | `invoke-rag-candidate.ps1 -Command build-graph` | passed，node count = 12，edge count = 46 |
| Enriched candidate query | `invoke-rag-candidate.ps1 -Command query` | passed，命中 `concepts/TraceNativeEvaluation.md` |
| Reviewed boundary after enrichment（P5-10 历史记录） | `health-reviewed` 和 `build-reviewed-graph` | passed，reviewed page count = 8，reviewed graph node count = 9 |
| Gap review package | `invoke-rag-knowledge.ps1 -Command gap-review-package` | passed，state = `ready-for-human-review`，ready = 7，dedup = 2，revise = 0 |
| Candidate validation after review package | candidate `health` / `lint` / `build-graph` | passed，page count = 12，edge count = 46 |
| Reviewed boundary after review package（P5-11 历史记录） | `health-reviewed` 和 `query-reviewed` | passed，reviewed page count = 8，query 只命中 reviewed 文档 |
| Knowledge vault governance（P5-13 历史记录） | `invoke-rag-knowledge.ps1 -Command govern-vault -ArchiveInactiveCandidates` | passed，active review = 1，archived candidates = 4，raw source = 1，archive actions = 4 |
| Obsidian review entry | `Home.md` | passed，用户审核入口已收敛到 Home 中的 active review queue |
| Knowledge root cleanup | `Get-ChildItem user/knowledge` | passed，根目录只保留 `.obsidian/`、`README.md`、`Home.md`、`raw/`、`candidate/`、`reviewed/` |
| Candidate root cleanup | `Get-ChildItem user/knowledge/candidate` | passed，candidate 根目录只保留 `reviewed-gap-concepts/` 和 `_archive/` |
| Reviewed source trace rewrite | `rg candidate/_archive/promoted-evidence ...reviewed...` | passed，promoted candidate evidence path 已同步到 reviewed source trace |
| Gap concept promotion | `invoke-rag-knowledge.ps1 -Command promote-gap-candidates ...` | passed，promoted = 7，deferred = 2 |
| Reviewed concept pages | `Get-ChildItem user/knowledge/reviewed/agent/concepts` | passed，7 篇 reviewed concept pages 已生成 |
| Remaining reviewed gaps | `invoke-rag-knowledge.ps1 -Command reviewed-gap-plan` | passed，gap count = 2，仅剩 `CandidateKnowledge` 和 `StructuredIngestion` 两个 dedup 项 |
| Reviewed concept query | `invoke-rag-knowledge.ps1 -Command query-reviewed -Question "TraceNativeEvaluation 是什么？"` | passed，首位命中 `reviewed/agent/concepts/TraceNativeEvaluation.md` |
| P5-15 pipeline smoke | `invoke-rag-knowledge.ps1 -Command pipeline-smoke ...` | passed，run id = `p5-15-pipeline-smoke`，target = `user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md`，query hits target = true |
| P5-15 candidate gates | pipeline smoke step summary | passed，candidate health / lint / graph / enrichment-plan 通过，review package = `ready-for-human-review`，promotion result = `promoted` |
| P5-15 reviewed vault | pipeline smoke step summary 和独立 reviewed checks | passed，vault governance 通过，reviewed health page count = 9，reviewed graph = 10 nodes / 35 edges / 2 broken links |
| P5-15 reviewed query | `query-reviewed -Question "p5-15-pipeline-smoke Agent Harness Engineering 的核心结论是什么？"` | passed，首位命中 `user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md` |
| P5-16 registry parse | `ConvertFrom-Json user/registry/knowledge.local.json` | passed，schemaVersion = `harness.knowledgeRegistry.v1`，registryKind = `local`，sourceCount = 1 |
| P5-16 registry route check | `Test-Path` 检查 `Home.md`、`raw/`、`candidate/`、`reviewed/` | passed，全部为相对路径且目标存在 |
| P5-16 registry Git boundary | `git check-ignore -v user/registry/knowledge.local.json` | passed，命中 `.gitignore:13:/user/registry/*.local.json` |
| P5-16 sensitive boundary check | registry 文本扫描绝对路径、URL、credential key、raw source 正文和私有同步配置 | passed，未发现本机绝对路径、URL、token、password、apiKey、secret、settings.xml、raw knowledge 正文或私有同步信息 |
| P5-17 domain directories | `Test-Path user/knowledge/raw/agent`、`Test-Path user/knowledge/reviewed/agent/index.md`、`Test-Path user/knowledge/reviewed/agent/concepts` | passed |
| P5-17 reviewed root cleanup | `Get-ChildItem user/knowledge/reviewed -File -Filter *.md` | passed，reviewed 根层无 active markdown page |
| P5-17 govern-vault after domain layout | `invoke-rag-knowledge.ps1 -Command govern-vault` | passed，reviewed page count = 10，raw source count = 1，`Home.md` 保留 `Reviewed Domains` |
| P5-17 reviewed health | `invoke-rag-knowledge.ps1 -Command health-reviewed` | passed，reviewed page count = 10，missing frontmatter = 0，missing review metadata = 0 |
| P5-17 reviewed graph | `invoke-rag-knowledge.ps1 -Command build-reviewed-graph` | passed，node count = 11，edge count = 45，broken link count = 2 |
| P5-17 reviewed query | `invoke-rag-knowledge.ps1 -Command query-reviewed -Question "TraceNativeEvaluation 是什么？"` | passed，首位命中 `user/knowledge/reviewed/agent/concepts/TraceNativeEvaluation.md`，domain index metadata 正常 |
| P5-17 old reference cleanup | `rg` scan over `harness/` and `user/knowledge/` for old layout refs | passed，未发现旧布局引用 |
| P5-17 Home global entry | `Home.md` | passed，包含 `[[reviewed/agent/index|Agent]]`，且 reviewed 明细仍从全局入口进入 |
| P5-17 stable command defaults | `rg "--domain|reviewed/\\{domain\\}" harness/tools/scripts/stable/rag_knowledge` | passed，默认输出已转为 `reviewed/<domain>/...` |
| P5-17 BOM cleanup | reviewed domain markdown byte-prefix scan | passed，未发现 UTF-8 BOM |
| P5-17 script syntax | `python -m py_compile ...rag_knowledge/cli.py ...rag_knowledge/commands.py` | passed |
| P5-18 duplicate governance | `invoke-rag-knowledge.ps1 -Command govern-reviewed-duplicates` | passed，duplicate group count = 1，authoritative page = `user/knowledge/reviewed/agent/llm-wiki-absorption-pdf-smoke.md`，non-authoritative page = `user/knowledge/reviewed/agent/p5-15-pipeline-smoke.md` |
| P5-18 reviewed health | `invoke-rag-knowledge.ps1 -Command health-reviewed` | passed，reviewed page count = 10，authoritative = 9，evidence = 1，missing frontmatter = 0 |
| P5-18 Home split | `govern-vault` 和 `Home.md` | passed，`p5-15-pipeline-smoke.md` 出现在 `Reviewed Validation Evidence`，不出现在 `Reviewed Knowledge` |
| P5-18 reviewed graph | `invoke-rag-knowledge.ps1 -Command build-reviewed-graph` | passed，node count = 11，edge count = 46，broken link count = 2，evidence 节点可导航 |
| P5-18 reviewed query | `query-reviewed -Question "p5-15-pipeline-smoke Agent Harness Engineering 的核心结论是什么？"` | passed，首位命中 authoritative `llm-wiki-absorption-pdf-smoke.md`，未返回 evidence-only `p5-15-pipeline-smoke.md` |
| P5-18 gap plan boundary | `invoke-rag-knowledge.ps1 -Command reviewed-gap-plan` | passed，gap count = 2，引用来源只包含 authoritative `llm-wiki-absorption-pdf-smoke.md` |
| P5-18 script syntax | `python -m py_compile ...rag_knowledge/cli.py ...rag_knowledge/commands.py` | passed |
| P5-19 residual gap disposition | `invoke-rag-knowledge.ps1 -Command dispose-residual-gaps` | passed，disposed links = `CandidateKnowledge` / `StructuredIngestion`，remaining residual gaps = 0，promotion = `none`；幂等复跑 page actions = 0 |
| P5-19 gap plan boundary | `invoke-rag-knowledge.ps1 -Command reviewed-gap-plan` | passed，gap count = 0 |
| P5-19 reviewed health | `invoke-rag-knowledge.ps1 -Command health-reviewed` | passed，reviewed page count = 10，authoritative = 9，evidence = 1 |
| P5-19 reviewed graph | `invoke-rag-knowledge.ps1 -Command build-reviewed-graph` | passed，node count = 11，edge count = 46，broken link count = 0 |
| P5-19 reviewed query | `query-reviewed -Question "p5-15-pipeline-smoke Agent Harness Engineering 的核心结论是什么？"` | passed，首位命中 authoritative `llm-wiki-absorption-pdf-smoke.md`，未直接返回 evidence-only `p5-15-pipeline-smoke.md` |
| P5-19 duplicate governance | `invoke-rag-knowledge.ps1 -Command govern-reviewed-duplicates` | passed，duplicate group count = 1，blocking issues = 0 |
| P5-19 vault governance archive | `invoke-rag-knowledge.ps1 -Command govern-vault -ArchiveInactiveCandidates` | passed，active review = 0，archived candidates = 6，幂等复跑 archive actions = 0 |
| P5-19 reviewed residual link scan | `rg "\\[\\[CandidateKnowledge\\]\\]|\\[\\[StructuredIngestion\\]\\]" user/knowledge/reviewed` | passed，无命中 |
| P5-19 local-only Git boundary | `git check-ignore -v user/knowledge/... user/registry/knowledge.local.json` | passed，命中 `user/knowledge/**` 和 `user/registry/*.local.json` ignore 规则 |
| P5-19.5 canonical layout | `invoke-rag-knowledge.ps1 -Command canonicalize-vault-layout` | passed，canonical page = `reviewed/agent-harness-engineering/agent-harness-engineering-survey.md`，archived validation evidence = `reviewed/_archive/validation-evidence/agent-harness-engineering/p5-15-pipeline-smoke.md` |
| P5-19.5 canonical idempotence | `invoke-rag-knowledge.ps1 -Command canonicalize-vault-layout` 二次执行 | passed，无新增移动；旧路径均为 source-missing |
| P5-19.5 reviewed health | `invoke-rag-knowledge.ps1 -Command health-reviewed` | passed，reviewed page count = 11，authoritative = 10，evidence = 1 |
| P5-19.5 reviewed graph | `invoke-rag-knowledge.ps1 -Command build-reviewed-graph` | passed，node count = 12，edge count = 46，broken link count = 0 |
| P5-19.5 duplicate governance | `invoke-rag-knowledge.ps1 -Command govern-reviewed-duplicates` | passed，authoritative page = `user/knowledge/reviewed/agent-harness-engineering/agent-harness-engineering-survey.md`，non-authoritative page = archived validation evidence |
| P5-19.5 reviewed query | `query-reviewed -Question "Agent Harness Engineering 的核心结论是什么？"` | passed，首位命中 canonical authoritative page |
| P5-19.5 old layout scan | `rg "reviewed/agent/|raw/agent/|llm-wiki-absorption-pdf-smoke"` over reviewed/Home/registry | passed，正式 reviewed 和 registry 无旧布局或旧 smoke 正式命名 |
| P5-19.5 local-only Git boundary | `git check-ignore -v user/knowledge/... user/registry/knowledge.local.json` | passed，命中 local-only ignore 规则 |
| P5-20 command syntax | `python -m py_compile ...rag_knowledge/cli.py ...rag_knowledge/commands.py` | passed |
| P5-20 command help | `python -m rag_knowledge.cli validate-knowledge-vault --help` | passed，命令参数可见 |
| P5-20 one-click validation gate | `invoke-rag-knowledge.ps1 -Command validate-knowledge-vault` | passed，check count = 12，passed = 12，blocking issues = 0 |
| P5-20 registry/Home/domain gate | `validate-knowledge-vault` | passed，registry domain count = 1，Home single-entry checked，domain schema/index 存在 |
| P5-20 reviewed evidence gate | `validate-knowledge-vault` | passed，reviewed health = 11 pages，source trace checked pages = 9，graph nodes = 12，broken links = 0，gap count = 0 |
| P5-20 duplicate/archive/boundary gate | `validate-knowledge-vault` | passed，duplicate groups = 1，archived candidates = 6，reviewed archive pages = 1，Git ignore 和 Obsidian plugin boundary 通过 |
| P5-21 plugin policy document | `Test-Path harness/rag/policies/ObsidianLlmWikiPluginBoundary.md` | passed，policy 已定义允许用途、禁止路径、local-only 配置边界、reviewed 写入门禁、`reviewed/_archive` 处置规则和验证命令 |
| P5-21 plugin config boundary | `git check-ignore -v user/knowledge/.obsidian/plugins/karpathywiki/data.json` 和插件 `data.json` 检查 | passed，插件目录被 local-only ignore 覆盖，`apiKey` 为空，auto watch 和 auto smart fix 关闭 |
| P5-21 reviewed source boundary | `validate-knowledge-vault` 和 reviewed source trace scan | passed，reviewed source trace 不引用 `.obsidian/`、plugin runtime 或 plugin config |
| P5-21 reviewed archive decision | `Test-Path user/knowledge/reviewed/_achieve`、`Test-Path user/knowledge/reviewed/_archive` | passed，`_achieve` 不存在；`_archive` 存在且保留为 reviewed validation evidence，不删除 |
| P5-21.5 candidate cleanup dry-run | `invoke-rag-knowledge.ps1 -Command candidate-cleanup-plan` | passed，active candidate = 0，full corpus = 0，lightweight audit records = 7，recommended cleanup actions = 0 |
| P5-21.5 candidate cleanup apply | `invoke-rag-knowledge.ps1 -Command candidate-cleanup-apply -Reviewer user -ApprovalNote ...` | passed，moved corpus = 6，audit records = 6，rewritten files = 15，graph filter 已排除 candidate/raw/.obsidian |
| P5-21.5 cleanup policy document | `Test-Path harness/rag/policies/CandidatePostPromotionCleanupPolicy.md` | passed，policy 已定义 full corpus 默认移出图谱/删除、轻量审计记录、dry-run 命令和 approved apply 命令边界 |
| P5-21.6 mechanism absorption policy | `validate-knowledge-vault` / `Test-Path harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md` | passed，机制吸收 gate 通过；schema、granularity、tag vocabulary、source gate、fingerprint、alias dedup、repair order、graph retrieval 和 auto maintenance 边界已记录 |
| P5-22 reviewed Skill path | `Test-Path harness/skills/reviewed/rag-knowledge-use/SKILL.md` | passed，reviewed Skill 已存在 |
| P5-22 candidate route cleanup | `Test-Path harness/skills/candidate/rag-knowledge-use` | passed，同名 active candidate 路径已移除 |
| P5-22 Skill quick validate | `PYTHONUTF8=1 quick_validate.py harness/skills/reviewed/rag-knowledge-use` | passed，frontmatter 满足 Skill 校验器 |
| P5-22 SkillIndex / usage sidecar | `rg` 和 `ConvertFrom-Json harness/skills/usage/skill-usage.json` | passed，SkillIndex 指向 reviewed，usage sidecar 记录 reviewed 状态 |
| P5-22 Knowledge validation gate | `invoke-rag-knowledge.ps1 -Command validate-knowledge-vault` | passed，check count = 12，blocking issues = 0 |
| P5-22 candidate cleanup dry-run | `invoke-rag-knowledge.ps1 -Command candidate-cleanup-plan` | passed，full corpus = 0，recommended cleanup actions = 0 |
| P5-22 old candidate route scan | `rg "harness/skills/candidate/rag-knowledge-use" harness/skills harness/rag harness/governance harness/tools` | passed，正式路由无旧 candidate 路径；阶段历史说明和审核报告保留原 candidate 记录 |
| P5-23 command syntax | `python -m py_compile ...rag_candidate... ...rag_knowledge...` | passed |
| P5-23 command help | `python -m rag_knowledge.cli schema-context --help` 和 `python -m rag_knowledge.cli validate-llm-wiki-mechanisms --help` | passed |
| P5-23 schema context | `invoke-rag-knowledge.ps1 -Command schema-context -Domain llm-agent-externalization -Task promotion` | passed，selected sections = 5，包含 Required Reviewed Page Sections、Controlled Tag Vocabulary、Alias Rules、Source Gate Rules 和 Validation Rules |
| P5-23 LLM Wiki mechanism gate | `invoke-rag-knowledge.ps1 -Command validate-llm-wiki-mechanisms` | passed，mechanism checks = 9/9，domain count = 2，schema context task sections = 10，source gate / granularity / tag / duplicate / PPR / auto boundary 均通过 |
| P5-23 real PDF full pipeline | `invoke-rag-knowledge.ps1 -Command pipeline-smoke ... -InputPath "user/knowledge/raw/Externalization in LLM Agents A Unified Review of Memory Sklls Protocols and Harness Engineering.pdf" -Domain llm-agent-externalization ...` | passed，raw -> candidate -> approved promotion -> reviewed vault -> query 全链路通过，query hits target = true |
| P5-23 reviewed domain linkage | pipeline smoke、`build-reviewed-graph` 和 `validate-knowledge-vault` | passed，新 domain `llm-agent-externalization` 与既有 `agent-harness-engineering` reviewed page 通过 wikilink 关联，reviewed graph broken links = 0、orphan pages = 0 |
| P5-23 candidate cleanup apply | `invoke-rag-knowledge.ps1 -Command candidate-cleanup-apply -Reviewer user -ApprovalNote ...` | passed，moved corpus = 2，audit records = 8，remaining full corpus = 0 |
| P5-23 candidate cleanup dry-run | `invoke-rag-knowledge.ps1 -Command candidate-cleanup-plan` | passed，active candidate = 0，full corpus = 0，lightweight audit records = 9，recommended cleanup actions = 0 |
| P5-23 one-click validation gate | `invoke-rag-knowledge.ps1 -Command validate-knowledge-vault` | passed，check count = 12，passed = 12，blocking issues = 0，reviewed pages = 22，domain count = 2，reviewed graph nodes = 23，edges = 100 |
| P5-23 reviewed-only focused query | `invoke-rag-knowledge.ps1 -Command query-reviewed -Question "externalized memory skill library protocol mediated coordination governed external state"` | passed，首位命中 `user/knowledge/reviewed/llm-agent-externalization/externalization-in-llm-agents-review.md` |
| P5-23.1 normalized markdown placement | `Get-ChildItem user/knowledge/raw -Recurse -File` | passed，两份原始材料均有 raw PDF 和 `raw/<domain>/normalized/*.md` 长期派生 Markdown |
| P5-23.1 reviewed language/source-depth scan | `rg "var/rag/.*/extracted|$name|Useful for|This concept|Approved authoritative|No direct|Review note|Generated only|This reviewed Knowledge|Core conclusions|runtime artifact" user/knowledge/reviewed` | passed，无命中；source-level reviewed page 已包含中文主体 Source Overview 和 Core Framework |
| P5-23.1 source trace validation gate | `invoke-rag-knowledge.ps1 -Command validate-knowledge-vault` | passed，check count = 12，source-trace passed，authoritative sourceRefs 不依赖 `var/rag/<run-id>/extracted/*.md` |
| P5-23.1 mechanism validation gate | `invoke-rag-knowledge.ps1 -Command validate-llm-wiki-mechanisms` | passed，check count = 9，blocking issues = 0；fixture 顺序执行后无 active candidate 残留 |
| P5-23.1 Skill validate | `PYTHONUTF8=1 quick_validate.py harness/skills/reviewed/rag-knowledge-use` | passed |
| Skill frontmatter | reviewed Skill frontmatter 基础校验 | passed |
| Markdown/script whitespace | `git diff --check` | passed |

当前 reviewed graph 的 residual workflow gap 已处置完成，broken link count = 0。`CandidateKnowledge` 和 `StructuredIngestion` 不作为当前 PDF 派生的 reviewed Knowledge 晋升，而是分别归并到 Harness policy / Skill / template 机制引用。

## 8. 后续任务

本阶段后续任务按 Knowledge 和 Memory 分开执行；以下仅覆盖 Knowledge/RAG：

1. Knowledge/RAG 本轮已完成机制补齐和真实 PDF 全流程验证，可提交用户审核是否收口。
2. 后续新增 domain 或 raw source 时，应复用 `pipeline-smoke`、`candidate-cleanup-plan/apply`、`validate-knowledge-vault` 和 `validate-llm-wiki-mechanisms`，不得绕过 reviewed promotion approval。
3. H9-4 整体完成仍以 Knowledge/RAG 和 Memory 均收口为准；Knowledge/RAG 用户审核通过后，下一步进入 Memory 闭环验证。
