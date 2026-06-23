---
documentName: user/knowledge/README.md
version: v1.0.0-pre-h8-knowledge-boundary
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义真实用户知识、候选知识和 reviewed knowledge 的本地边界。
scope:
  - user-knowledge-boundary
  - local-only-boundary
  - candidate-knowledge
prerequisites:
  - AGENTS.md
  - INDEX.md
relatedDocuments:
  - INDEX.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/architecture/PLANS.md
outputTo:
  - user/knowledge/README.md
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
  decision: pre-h8-knowledge-promotion-aligned
---
# 用户知识边界

`user/knowledge/` 是真实用户知识和 candidate knowledge 的本地边界。除本 README 外，目录内容默认 local-only，不进入通用 Harness Git。

可放入本目录的内容包括：

- 用户提供的 raw source；
- candidate wiki；
- reviewed user knowledge；
- project-specific knowledge；
- 不适合进入通用 Harness Git 的私有知识库工作副本。

默认子路径建议：

| 子路径 | 用途 | Git 边界 |
|---|---|---|
| `raw/<run-id>/` | 用户提供或工具复制的 raw source。 | local-only |
| `candidate/<run-id>/wiki` | raw-to-candidate workflow 生成的候选知识。 | local-only |
| `reviewed/` | 经 human review 或用户批准后的用户知识。 | local-only 或外部 private repo |
| `project-id/<project-id>/` | 项目相关知识。 | local-only 或外部 private repo |

`harness/rag/` 只保存可复用摄取机制；`var/rag/` 保存 extracted artifacts、eval reports、graph、embedding、index 和 cache。

禁止把 credential、auth 文件、private settings、raw logs、未脱敏 trace 或私有仓库细节写入 tracked docs。
