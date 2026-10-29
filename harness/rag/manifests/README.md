---
documentName: harness/rag/manifests/README.md
version: v1.3.0-reviewed-profile-and-evidence
updatedAt: 2026-10-29
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
reviewAfter: 2026-11-29
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: user-requested-batch-tool-consolidation-reviewed
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


## 正文准备与收尾配置

- [ReviewedContentProfile.example.json](ReviewedContentProfile.example.json)：原件及规范化哈希、版本事实、完整条款、别名和次要副本追溯。可选项按实际材料保留或删除；草稿编号和日期未知时保持未知。
- [EvidenceBundle.example.json](EvidenceBundle.example.json)：待归档文件、相对目标和精确字节哈希；不在归档阶段重写通过/失败结论。

具体配置只留在user/var。每次规范化使用的profile原始字节和哈希随本批证据保留，不能用后续合并版本冒充旧批配置。工具configHash与JSON文件字节哈希分别记录。新来源TargetMap使用items/sourceId/target结构，必须完整覆盖清单；生成的PromotionMap再增加draft字段。
