---
documentName: harness/rag/RAGIndex.md
version: v2.14.0-batch-knowledge-tools
updatedAt: 2026-10-29
status: active
purpose: 路由 Harness RAG 摄取机制资产，并定义真实知识、候选知识和运行态索引的边界。
scope:
  - rag-mechanism
  - knowledge-boundary
  - runtime-rag-boundary
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
  - harness/HarnessIndex.md
  - harness/rag/manifests/README.md
  - harness/rag/pipelines/README.md
  - harness/rag/evals/README.md
  - harness/rag/policies/README.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - user/knowledge/README.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/rag/RAGIndex.md
owner: mixed
reviewAfter: 2026-11-29
supersededBy: null
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: user-requested-batch-tool-consolidation-reviewed
---

# RAG 机制索引

文档摄取按 [PDF 规范化契约](pipelines/PdfNormalizationContract.md) 与 [稳定流水线命令](../tools/docs/command-surfaces/RagDocumentPipeline.md) 执行。原件、规范化副本、审核草稿和 reviewed 正文均保留哈希；全库结构通过不能替代转换质量核验或语义审核。旧语料可先运行 `audit-corpus`，不得自动补造历史晋升封印。

`harness/rag/` 是 Harness 的 RAG 摄取机制层，中文解释是检索增强生成机制层。它保存可复用的 schema、manifest 示例、pipeline 说明、eval 模板和 policy，不保存真实用户知识正文、私有原始资料、embedding、vector index、cache 或 raw extraction output。

## 1. 机制资产

| 分区 | 路径 | 边界 |
|---|---|---|
| Manifest | `harness/rag/manifests/` | Manifest schema、非私有 example、离线摄取 profile。 |
| Pipeline | `harness/rag/pipelines/` | 可复用 ingestion pipeline 说明和非默认 helper。 |
| Eval | `harness/rag/evals/` | evaluation 模板、检查说明和非私有示例。 |
| Policy | `harness/rag/policies/` | chunking、citation、review、promotion、stale、candidate cleanup、LLM Wiki mechanism absorption 和 Obsidian LLM Wiki plugin boundary 规则。 |

## 2. 知识边界

| 资产 | 目标边界 | Git 边界 |
|---|---|---|
| 真实用户知识 | `user/knowledge/` 或外部 private knowledge repo | 默认 local-only。 |
| Raw source | `user/knowledge/raw/<domain>/` 或外部 private raw source repo | 默认 local-only；保存原始材料和长期 normalized source derivative。 |
| Normalized source Markdown | `user/knowledge/raw/<domain>/normalized/` | 原始材料转换后的长期可读派生版本，可被 Source Trace 引用；不是 reviewed 结论。 |
| Candidate Knowledge | `user/knowledge/candidate/<run-id>/wiki` | 默认 local-only，review 前不进入通用 Harness Git。 |
| Reviewed Knowledge | `user/knowledge/reviewed/` 或外部 private knowledge repo | 需要 human review 或用户明确批准。 |
| extracted Markdown / chunks / eval reports | `var/rag/<run-id>/` | 可重建运行态，不进入 Git。 |
| graph / embedding / index / cache | `var/rag/<run-id>/` | 可重建运行态，不进入 Git。 |

## 3. 稳定工具输出

默认 raw-to-candidate workflow 使用：

```text
harness/tools/scripts/stable/invoke-rag-candidate.ps1
```

该工具只能生成：

- runtime extraction artifacts；
- candidate wiki；
- health、lint、graph、enrichment evidence；
- review package 和 promotion plan；
- reviewed Knowledge promotion result，仅限 `promote-reviewed` 且已有用户明确批准；
- graph-aware candidate query result；
- stale source plan；
- status JSON。

它不得在未获用户明确批准时写入 reviewed Knowledge、Memory、Project Fact 或正式治理结论。`promotion-plan` 只能生成计划和阻塞原因，不等同于 promotion approval。`promote-reviewed` 只能在 review gates 通过且用户明确批准后写入 `user/knowledge/reviewed/` 或指定 private knowledge target。

reviewed Knowledge access workflow 使用：

```text
harness/tools/scripts/stable/invoke-rag-knowledge.ps1
```

该工具只面向已经审核通过的 reviewed Knowledge，用于：

- 初始化 `user/knowledge/` 的 Obsidian vault view；
- 同步 `Home.md` 单入口中的 reviewed Knowledge 入口；
- 构建 reviewed graph runtime；
- 执行 reviewed-only query；
- 运行 reviewed health check；
- 生成 unresolved reviewed wikilinks 的 candidate-only gap plan，并可选写入 local-only candidate gap wiki；
- 用 reviewed Knowledge evidence 补强 gap candidate pages，供后续 human review 判断是否值得 promotion；
- 生成 gap review package，列出 ready / dedup / revise 分类和 reviewer decision template；
- 在用户明确批准后，把 approved gap candidates 晋升为 `reviewed/<domain>/concepts/*.md`；
- 处置已明确属于 Harness 机制或 workflow 的 residual gaps，把 reviewed wikilink 归并到 policy / Skill / template 引用，不从当前 PDF 派生候选中晋升 reviewed Knowledge；
- 在进入一键验证门禁前执行 canonical vault layout，确保 raw、candidate archive、reviewed domain、schema、authoritative page 和 validation evidence 使用 source-centered 结构；
- 运行 `validate-knowledge-vault` 一键门禁，检查 local registry、Home 单入口、domain index/schema、reviewed frontmatter、source trace、broken links、duplicate source、archive/audit references、Git ignore boundary、Obsidian plugin boundary 和 LLM Wiki 机制吸收 gate；
- 运行 `candidate-cleanup-plan` dry-run，盘点 post-promotion candidate full corpus、轻量审计记录、reviewed/Home/registry 引用和推荐清理动作；
- 在用户明确批准后运行 `candidate-cleanup-apply`，把完成生命周期的 full candidate corpus 移出 vault，保留轻量审计记录并改写 source trace；
- 按 domain schema 和任务类型运行 `schema-context`，只输出当前任务需要的 schema section；
- 运行 `validate-llm-wiki-mechanisms`，验证 schema context、source gate fixture、extraction granularity fixture、tag vocabulary、alias/body similarity duplicate governance、repair order、reviewed graph PPR 和 auto maintenance boundary；
- 检查同一 raw source 和同一 topic 的重复 reviewed pages，确认只有一个 authoritative page，其余进入 validation evidence、superseded、archived 或 deprecated；
- 治理 `user/knowledge/` Obsidian vault 入口，把 active review queue、evidence-only candidates、raw sources 和 governance rules 分开。
- 执行 `pipeline-smoke`，以稳定命令验证 raw -> candidate -> approved promotion -> reviewed vault -> query 的完整链路。

它不得把 raw source、candidate wiki、chunks、graph JSON 或 eval reports 反向当作 authoritative knowledge。`reviewed-gap-plan`、`enrich-gap-candidates`、`gap-review-package`、`dispose-residual-gaps`、`canonicalize-vault-layout`、`validate-knowledge-vault`、`candidate-cleanup-plan`、`schema-context`、`validate-llm-wiki-mechanisms`、`govern-reviewed-duplicates` 和 `govern-vault` 产生的是候选补强、审核输入、residual gap 处置、canonical layout 迁移、只读门禁、post-promotion cleanup dry-run、schema context 摘要、机制验收报告、重复治理报告或阅读导航；即使生成 review package，也不得绕过 review 或 explicit approval 写入 reviewed Knowledge。`dispose-residual-gaps` 只能处理已知 workflow / mechanism gap，把链接改为 policy / Skill / template 机制引用并记录 disposition；不得把残余 gap 直接晋升为 reviewed Knowledge。`canonicalize-vault-layout` 只能重排已经批准或已归档的 local-only knowledge vault 结构，不新增 promotion。`validate-knowledge-vault` 只能写入 runtime validation report、graph 和 status JSON，不执行 promotion、不重排 vault、不把 plugin/runtime/candidate 当作事实源。`schema-context` 只能读取 registry 和 reviewed domain schema 并输出 task-scoped section，不写任何知识库页面。`validate-llm-wiki-mechanisms` 只能用 reviewed vault 与临时 fixture 验证已吸收机制，不执行 auto maintenance 写入、不执行 promotion。`candidate-cleanup-plan` 只能写入 runtime report 和 status JSON，不删除、不移动、不改写 reviewed source trace。`candidate-cleanup-apply` 只有在 reviewer 和 approval note 齐备时才能移动完成生命周期的 candidate full corpus、写入轻量审计记录并改写 source trace；它不执行 reviewed promotion。`promote-gap-candidates` 是例外的受控晋升命令：只有 reviewer、approval note 和 review gates 齐备时，才能写入 reviewed concept pages。`pipeline-smoke` 是受控验证命令：它必须传入 raw input、reviewer、approval note 和 query，且只能把 candidate/chunks 作为晋升证据和运行态产物，不得把它们作为事实源回答。

## 4. 晋升规则

1. RAG chunk、graph、embedding、cache 和 status JSON 都不是事实源。
2. Candidate Knowledge 只是候选，不是 authoritative knowledge。
3. Reviewed Knowledge 必须经过 source provenance、scope、sensitivity、usage-rights、conflict 和 human review 检查。
4. Promotion，中文解释是晋升，必须通过 governance workflow 或用户明确批准。
5. 同一 raw source 和同一 topic 只能有一个 authoritative reviewed page；重复页必须治理为 validation evidence、superseded、archived 或 deprecated。
6. residual workflow gaps 必须按 dedup、defer 或 separate-candidate 处置；不得从不匹配的当前 raw source 派生候选中直接晋升。
7. 正式 reviewed page 必须使用语义命名，不使用 smoke、pipeline、阶段编号或工具 run id；这些过程名只能保留在 validation evidence、candidate archive 或 runtime report 中。
8. candidate archive 推荐使用 `candidate/_archive/by-source/<source-id>/<bucket>/`，使一份 raw source 的 canonical candidate、validation evidence、gap concepts 和 legacy evidence 可一起追溯。
9. Candidate 晋升、拒绝或归档后，full corpus 默认应移出 Obsidian 默认图谱或删除，只保留轻量审计记录；实际清理前必须运行 `candidate-cleanup-plan` 并获得用户批准，清理后必须运行 `validate-knowledge-vault` 回归。
10. 旧顶层 `rag/` 不再作为 RAG 入口或输出路径。
11. Obsidian LLM Wiki 类插件输出默认属于 candidate boundary；插件配置、API key、workspace state 和 query history 必须留在 local-only，不得作为 reviewed Knowledge 或 RAG Index 的事实源。
12. Harness 可吸收 LLM Wiki 类工具中的 schema config、extraction granularity、tag vocabulary、source gate、source fingerprint、alias-aware dedup、causality-aware repair order、reviewed-only graph retrieval 和 auto maintenance 工程经验，但只能落为模板、门禁、dry-run、candidate-only 或用户批准后的稳定命令。
13. LLM Wiki 机制增强必须通过 `validate-llm-wiki-mechanisms` 复核；真实 raw 到 reviewed 的 Knowledge/RAG 收口必须同时通过 `pipeline-smoke`、`candidate-cleanup-plan` 或 approved apply、`validate-knowledge-vault` 和 reviewed-only query。
14. Source-level reviewed Knowledge 必须具备足够的中文主体综合内容，能让 agent 仅阅读 reviewed page 就理解原始材料的核心主线、概念、方法和边界；concept page 是知识图谱节点，不应替代 source-level reviewed page。
15. 原始材料转换后的 Markdown 应保存到 `user/knowledge/raw/<domain>/normalized/` 或外部 private raw source boundary；`var/rag/<run-id>/extracted/*.md` 只允许作为运行态复现产物，不应作为 reviewed `sourceRefs` 的长期来源。
16. PDF 来源页须包含可独立检索的条款正文、适用条件和关键数值；目录及原件链接不能代替知识内容。逐页来源对齐正文通过 `prepare-reviewed-content` 形成候选，审核后晋升；转换覆盖和语义审核分别标记。
17. 查询应返回相关 reviewed 条款及行号。以回查 raw PDF 或图像补出答案的测试，不能计为 reviewed-only 问答通过。缺少正文或关键条件时登记知识缺口，回到摄取与审核流程补强。
18. 版本适用性独立维护发布日期、实施日期、官方核验时间与适用事项；不按知识维护日期替代法规时序，也不把不同分类轴按年份简单覆盖。

## 查询与验收模式

纯库测试、正式混合使用及补强的来源规则见 [知识查询与评测来源边界](policies/KnowledgeQueryEvaluationPolicy.md)。测试不得搜索网页补状态或日期；库内未核实信息保留缺口。正式使用可以结合外部证据并分别归属来源。

稳定query-reviewed返回模式契约与可选来源前缀筛选；audit-query-evaluation校验提供的整轮记录。局部查询函数的文件守卫只证明局部行为，不能证明整轮没有外部访问；记录不完整不可认定纯库通过。运行态事件和真实知识不进入通用仓库。


## 连续批次构建入口

批量构建优先复用`prepare-reviewed-content`的新来源模式、`compare-pdf-copies`、`query-regression`及`archive-build-evidence`，避免每批手写草稿格式、测试循环和证据复制脚本。命令与输出边界见[统一工具契约](../tools/docs/command-surfaces/RagDocumentPipeline.md)。非私有配置结构由[manifest入口](manifests/README.md)和[eval入口](evals/README.md)路由。Source Trace、次要副本哈希与实际profile版本作为审核输入；图谱、比较结果和回归报告继续属于证据，不晋升为知识事实。
