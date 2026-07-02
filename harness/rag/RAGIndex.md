---
documentName: harness/rag/RAGIndex.md
version: v2.0.0-pipeline-smoke
updatedAt: 2026-07-02 00:00:00.000 +08:00
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
  - harness/HarnessIndex.md
  - harness/rag/manifests/README.md
  - harness/rag/pipelines/README.md
  - harness/rag/evals/README.md
  - harness/rag/policies/README.md
  - user/knowledge/README.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/rag/RAGIndex.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-02
  decision: p5-15-pipeline-smoke-boundary-added
---
# RAG 机制索引

`harness/rag/` 是 Harness 的 RAG 摄取机制层，中文解释是检索增强生成机制层。它保存可复用的 schema、manifest 示例、pipeline 说明、eval 模板和 policy，不保存真实用户知识正文、私有原始资料、embedding、vector index、cache 或 raw extraction output。

## 1. 机制资产

| 分区 | 路径 | 边界 |
|---|---|---|
| Manifest | `harness/rag/manifests/` | Manifest schema、非私有 example、离线摄取 profile。 |
| Pipeline | `harness/rag/pipelines/` | 可复用 ingestion pipeline 说明和非默认 helper。 |
| Eval | `harness/rag/evals/` | evaluation 模板、检查说明和非私有示例。 |
| Policy | `harness/rag/policies/` | chunking、citation、review、promotion 和 stale 规则。 |

## 2. 知识边界

| 资产 | 目标边界 | Git 边界 |
|---|---|---|
| 真实用户知识 | `user/knowledge/` 或外部 private knowledge repo | 默认 local-only。 |
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
- 在用户明确批准后，把 approved gap candidates 晋升为 `reviewed/concepts/*.md`；
- 治理 `user/knowledge/` Obsidian vault 入口，把 active review queue、evidence-only candidates、raw sources 和 governance rules 分开。
- 执行 `pipeline-smoke`，以稳定命令验证 raw -> candidate -> approved promotion -> reviewed vault -> query 的完整链路。

它不得把 raw source、candidate wiki、chunks、graph JSON 或 eval reports 反向当作 authoritative knowledge。`reviewed-gap-plan`、`enrich-gap-candidates`、`gap-review-package` 和 `govern-vault` 产生的是候选补强、审核输入或阅读导航；即使生成 review package，也不得绕过 review 或 explicit approval 写入 reviewed Knowledge。`promote-gap-candidates` 是例外的受控晋升命令：只有 reviewer、approval note 和 review gates 齐备时，才能写入 reviewed concept pages。`pipeline-smoke` 是受控验证命令：它必须传入 raw input、reviewer、approval note 和 query，且只能把 candidate/chunks 作为晋升证据和运行态产物，不得把它们作为事实源回答。

## 4. 晋升规则

1. RAG chunk、graph、embedding、cache 和 status JSON 都不是事实源。
2. Candidate Knowledge 只是候选，不是 authoritative knowledge。
3. Reviewed Knowledge 必须经过 source provenance、scope、sensitivity、usage-rights、conflict 和 human review 检查。
4. Promotion，中文解释是晋升，必须通过 governance workflow 或用户明确批准。
5. 旧顶层 `rag/` 不再作为 RAG 入口或输出路径。
