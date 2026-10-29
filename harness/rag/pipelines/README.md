---
documentName: harness/rag/pipelines/README.md
version: v1.1.0-source-bound-pdf-normalization
updatedAt: 2026-10-29
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
reviewAfter: 2026-11-12
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: user-requested-source-bound-pipeline-reviewed-and-tested
---
# RAG Pipeline

PDF 默认使用稳定门面的 `normalize-pdf`，再用 `ingest -NormalizationManifest` 接入现有 candidate 流程；审核包、显式晋升映射和审计保持同一套工具链。详见 [PDF 规范化契约](PdfNormalizationContract.md) 与 [命令说明](../../tools/docs/command-surfaces/RagDocumentPipeline.md)。历史 helper 不再扩展为另一套默认流程。

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
