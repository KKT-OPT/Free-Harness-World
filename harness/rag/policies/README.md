---
documentName: harness/rag/policies/README.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
status: active
purpose: 说明 RAG chunking、citation、review、promotion 和运行态边界规则。
scope:
  - rag-policy
  - knowledge-promotion
  - runtime-boundary
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/rag/policies/README.md
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
# RAG Policy（RAG 策略）

本目录保存 RAG 机制层 policy。长期规则：

1. Raw source 不是 reviewed Knowledge。
2. Extracted Markdown、chunks、graph、embedding、index 和 cache 都是可重建产物。
3. Candidate Knowledge 必须保留 source provenance，并停在 user-local 或 private repo 边界内等待 review。
4. Reviewed Knowledge 必须经过 human review 或用户明确批准。
5. RAG Index 只能从 reviewed source 重建，不能反向成为事实源。
6. 任何涉及私有资料、版权风险或矛盾结论的晋升，都必须进入 Governance review。
