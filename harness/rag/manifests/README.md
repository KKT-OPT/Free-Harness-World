---
documentName: harness/rag/manifests/README.md
version: v1.2.0-source-gate-manifest-fields
updatedAt: 2026-07-03 23:30:00.000 +08:00
status: active
purpose: 说明 RAG manifest schema、profile example 和非私有配置样例的保存边界。
scope:
  - rag-manifest
  - non-private-example
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/rag/policies/README.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
outputTo:
  - harness/rag/manifests/README.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: source-gate-schema-granularity-tag-fields-added
---
# RAG Manifest

本目录保存 RAG manifest schema、离线摄取 profile 和非私有 example。

允许保存：

- 不含真实路径的 ingestion profile；
- converter、OCR、speech-to-text、chunking 和 review requirement 的 schema；
- source gate、source fingerprint、domain schema、extraction granularity、entity/concept cap、batch strategy 和 tag vocabulary 的非私有 schema 字段；
- 明确标记为 example 的配置。

禁止保存：

- 真实用户源文件路径；
- 私有仓库 URL；
- credential、token、password 或 auth 信息；
- raw source material；
- extracted content、chunks、embedding、index 或 cache。
