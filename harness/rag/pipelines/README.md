---
documentName: harness/rag/pipelines/README.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
status: active
purpose: 说明 RAG ingestion pipeline 的长期机制边界和非默认 helper 保存规则。
scope:
  - rag-pipeline
  - ingestion-mechanism
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/tools/docs/script-index/ScriptIndex.md
outputTo:
  - harness/rag/pipelines/README.md
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
# RAG Pipeline

本目录保存可复用的 RAG ingestion pipeline 说明和非默认 helper。默认执行入口仍是稳定工具：

```text
harness/tools/scripts/stable/invoke-rag-candidate.ps1
```

`harness/rag/pipelines/` 可以保存：

- pipeline contract；
- converter selection rule；
- chunking / manifest / candidate wiki 生成流程；
- 非默认、需审查后才可能纳入 stable tool 的 helper。

本目录不得保存真实用户材料、candidate wiki 正文、eval runtime report、embedding、index、cache 或 raw logs。

## 当前 helper

| Helper | 定位 |
|---|---|
| `pdf-text-extraction/extract_pdf_text.py` | 历史 PDF 文本提取 helper，作为 pipeline 参考实现保留；默认 Agent 调用仍应使用 stable wrapper。 |
