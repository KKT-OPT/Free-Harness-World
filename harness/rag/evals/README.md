---
documentName: harness/rag/evals/README.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
status: active
purpose: 说明 RAG evaluation 模板和运行态 eval report 的分离边界。
scope:
  - rag-evaluation
  - runtime-evidence-boundary
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/rag/policies/README.md
outputTo:
  - harness/rag/evals/README.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: h6-complete
---
# RAG Eval

本目录保存 RAG evaluation 模板、检查维度和非私有示例。

运行时生成的 health report、lint report、graph report、graph JSON、graph HTML、embedding、index 和 cache 应写入：

```text
var/rag/<run-id>/
```

这些运行态产物可重建，不是事实源，不进入通用 Harness Git。
