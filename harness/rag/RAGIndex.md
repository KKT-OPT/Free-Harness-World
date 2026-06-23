---
documentName: harness/rag/RAGIndex.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
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
  reviewedAt: 2026-06-22
  decision: h6-complete
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
- health、lint、graph evidence；
- status JSON。

它不得写入 reviewed Knowledge、Memory、Project Fact 或正式治理结论。

## 4. 晋升规则

1. RAG chunk、graph、embedding、cache 和 status JSON 都不是事实源。
2. Candidate Knowledge 只是候选，不是 authoritative knowledge。
3. Reviewed Knowledge 必须经过 source provenance、scope、sensitivity、usage-rights、conflict 和 human review 检查。
4. Promotion，中文解释是晋升，必须通过 governance workflow 或用户明确批准。
5. 旧顶层 `rag/` 不再作为 RAG 入口或输出路径。
