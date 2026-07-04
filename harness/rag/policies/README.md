---
documentName: harness/rag/policies/README.md
version: v1.3.0-executable-cleanup-and-mechanism-gates
updatedAt: 2026-07-03 23:30:00.000 +08:00
status: active
purpose: 说明 RAG chunking、citation、review、promotion、插件和运行态边界规则。
scope:
  - rag-policy
  - knowledge-promotion
  - runtime-boundary
  - obsidian-plugin-boundary
  - candidate-cleanup
  - llm-wiki-mechanism-absorption
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
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
  reviewedAt: 2026-07-03
  decision: executable-cleanup-and-mechanism-gates-linked
---
# RAG Policy（RAG 策略）

本目录保存 RAG 机制层 policy。长期规则：

1. Raw source 不是 reviewed Knowledge。
2. Extracted Markdown、chunks、graph、embedding、index 和 cache 都是可重建产物。
3. Candidate Knowledge 必须保留 source provenance，并停在 user-local 或 private repo 边界内等待 review。
4. Reviewed Knowledge 必须经过 human review 或用户明确批准。
5. RAG Index 只能从 reviewed source 重建，不能反向成为事实源。
6. 任何涉及私有资料、版权风险或矛盾结论的晋升，都必须进入 Governance review。
7. Obsidian LLM Wiki 类插件只能作为阅读、候选生成和本地治理辅助；插件输出不得绕过 review 写入 reviewed Knowledge。
8. Candidate 晋升、拒绝或归档后，full corpus 默认应移出 Obsidian 默认图谱或删除，只保留轻量审计记录。
9. LLM Wiki 类工具中的 schema、受控标签、source gate、fingerprint、alias 去重、修复顺序和 graph retrieval 机制可被 Harness 吸收为通用规则和稳定门禁。

## Policy 文件

| 文件 | 用途 |
|---|---|
| `ObsidianLlmWikiPluginBoundary.md` | 定义 Obsidian / LLM Wiki 类插件的允许用途、禁止路径、local-only 配置边界、reviewed 写入门禁和 `reviewed/_archive` 处置规则。 |
| `CandidatePostPromotionCleanupPolicy.md` | 定义 candidate 晋升、拒绝或归档后的 full corpus 清理规则、轻量审计记录要求、`candidate-cleanup-plan` dry-run 命令和 `candidate-cleanup-apply` 显式批准命令。 |
| `LlmWikiMechanismAbsorptionPolicy.md` | 定义从 obsidian-llm-wiki 吸收到 Harness RAG/Knowledge 的 schema、granularity、tag vocabulary、source gate、source fingerprint、alias dedup、graph retrieval 和 auto maintenance 边界。 |
