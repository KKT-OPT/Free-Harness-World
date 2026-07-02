---
documentName: harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
version: v0.9.0-pipeline-smoke
updatedAt: 2026-07-02 00:00:00.000 +08:00
status: review
purpose: 临时记录 Phase 5 Reviewed Knowledge Access Layer 的阶段性目标、任务和验收标准。
scope:
  - phase5-rag-knowledge-access
  - reviewed-knowledge
  - obsidian-vault
  - agent-query
  - candidate-gap-plan
  - candidate-archive
  - reviewed-concept-pages
  - pipeline-smoke
prerequisites:
  - AGENTS.md
  - harness/architecture/PLANS.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - harness/architecture/PLANS.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/skills/rag-structured-ingestion/SKILL.md
  - harness/skills/candidate/rag-knowledge-use/SKILL.md
outputTo:
  - harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
owner: mixed
reviewAfter: 2026-07-07
supersededBy:
dependsOn:
  - harness/architecture/PLANS.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-02
  decision: p5-15-pipeline-smoke-passed
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
| P5-14 Approved gap candidates to reviewed concept pages | `promote-gap-candidates`、`user/knowledge/reviewed/concepts/*.md` | 已把 7 个 approved gap candidates 晋升为 reviewed concept pages；2 个 dedup 项保留为 candidate gap；reviewed graph broken links 从 9 降到 2；query 能命中 concept page。 | complete |
| P5-15 Full pipeline smoke | `pipeline-smoke`、`p5-15-pipeline-smoke.md` | 已用真实 raw PDF 跑通 raw -> candidate -> approved promotion -> reviewed vault -> query；query 首位命中新晋升 reviewed page；candidate smoke run 已归档为 promoted evidence。 | complete |

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
| `enrich-gap-candidates` | 用 reviewed Knowledge 的 Key Concepts 和引用段落补强 gap candidate pages，仍停留在 candidate-only boundary。 |
| `gap-review-package` | 生成 human review package，汇总 ready / dedup / revise 分类、review gates 和 reviewer decision template。 |
| `promote-gap-candidates` | 在用户明确批准后，将 approved reviewed gap candidates 晋升为 `reviewed/concepts/*.md`；dedup/revise 项保留为候选，不自动晋升。 |
| `govern-vault` | 生成 Obsidian `Home.md` 单入口、candidate review queue、archive summary、raw source summary 和 governance rules。 |
| `govern-vault -ArchiveInactiveCandidates` | 将 inactive candidate corpus 非破坏性移动到 `candidate/_archive/`，并同步 reviewed source trace；不执行 reviewed promotion。 |
| `pipeline-smoke` | 用一个稳定命令验证 raw -> candidate -> review package -> approved promotion -> reviewed vault -> query 的端到端链路；仍要求 reviewer 和 approval note。 |

## 5. 验收案例

使用 Phase 4 已晋升的 reviewed Knowledge：

```text
user/knowledge/reviewed/llm-wiki-absorption-pdf-smoke.md
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
- 已运行 `query-reviewed`，命中 `user/knowledge/reviewed/llm-wiki-absorption-pdf-smoke.md`。

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
- 新增 `promote-gap-candidates` 子命令，读取 `reviewed-gap-concepts` review package，把用户批准的 approved gap candidates 写入 `user/knowledge/reviewed/concepts/`。
- 本轮已晋升 7 个 reviewed concept pages：`AdaptiveHarnessOptimization`、`BindingConstraintThesis`、`ContextDrift`、`ETCLOVGTaxonomy`、`HarnessCouplingProblem`、`StandardHandoffProtocol`、`TraceNativeEvaluation`。
- `CandidateKnowledgeConcept` 和 `StructuredIngestion` 保持 deferred / dedup，不直接晋升。
- P5-14 晋升后 `Home.md` reviewed list 显示 8 篇 reviewed pages；candidate queue 摘要显示 `promoted=7, deferred=2, skipped=0`。
- 新增 `pipeline-smoke` 子命令，把真实 raw PDF 到 reviewed query 的完整链路封装为稳定 smoke。
- P5-15 使用 `user/knowledge/raw/legacy-rag/Agent Harness Engineering A Survey.pdf` 执行 `p5-15-pipeline-smoke`。
- P5-15 生成并晋升 `user/knowledge/reviewed/p5-15-pipeline-smoke.md`，随后 `Home.md` reviewed list 显示 9 篇 reviewed pages。
- P5-15 的 candidate smoke run 已通过 `govern-vault` 归档到 `candidate/_archive/promoted-evidence/p5-15-pipeline-smoke`，不留在 active review queue。

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
| Reviewed concept pages | `Get-ChildItem user/knowledge/reviewed/concepts` | passed，7 篇 reviewed concept pages 已生成 |
| Remaining reviewed gaps | `invoke-rag-knowledge.ps1 -Command reviewed-gap-plan` | passed，gap count = 2，仅剩 `CandidateKnowledge` 和 `StructuredIngestion` 两个 dedup 项 |
| Reviewed concept query | `invoke-rag-knowledge.ps1 -Command query-reviewed -Question "TraceNativeEvaluation 是什么？"` | passed，首位命中 `reviewed/concepts/TraceNativeEvaluation.md` |
| P5-15 pipeline smoke | `invoke-rag-knowledge.ps1 -Command pipeline-smoke ...` | passed，run id = `p5-15-pipeline-smoke`，target = `user/knowledge/reviewed/p5-15-pipeline-smoke.md`，query hits target = true |
| P5-15 candidate gates | pipeline smoke step summary | passed，candidate health / lint / graph / enrichment-plan 通过，review package = `ready-for-human-review`，promotion result = `promoted` |
| P5-15 reviewed vault | pipeline smoke step summary 和独立 reviewed checks | passed，vault governance 通过，reviewed health page count = 9，reviewed graph = 10 nodes / 35 edges / 2 broken links |
| P5-15 reviewed query | `query-reviewed -Question "p5-15-pipeline-smoke Agent Harness Engineering 的核心结论是什么？"` | passed，首位命中 `user/knowledge/reviewed/p5-15-pipeline-smoke.md` |
| Skill frontmatter | frontmatter 基础校验 | passed |
| Markdown whitespace | `git diff --check` | passed |

当前 reviewed graph 仍有 2 个 broken links，对应 `CandidateKnowledge` 和 `StructuredIngestion` 两个 dedup / workflow 项；它们不表示 reviewed query 失败，也不会自动晋升为 reviewed Knowledge。

## 8. 后续任务

- 用户或 reviewer 决定哪些概念值得进入正式 review / promotion。
- 如用户批准 selected concepts，再设计 reviewed concept promotion 命令或人工 promotion 记录；不得由 review package 自动晋升。
- 在更多 reviewed docs 上验证 query、`Home.md` 单入口、graph 和 gap plan 行为。
- 后续如 `rag-knowledge-use` candidate Skill 通过 review，可迁入 reviewed Skill 边界并同步 usage sidecar。
