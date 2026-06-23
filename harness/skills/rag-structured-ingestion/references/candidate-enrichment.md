---
documentName: harness/skills/rag-structured-ingestion/references/candidate-enrichment.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
status: active
purpose: 定义 raw extraction 后如何补全 candidate wiki，且不晋升为 reviewed knowledge。
scope:
  - candidate-enrichment
  - rag-skill-reference
prerequisites:
  - harness/skills/rag-structured-ingestion/SKILL.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
outputTo:
  - harness/skills/rag-structured-ingestion/references/candidate-enrichment.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/skills/rag-structured-ingestion/SKILL.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: h6-complete
---
# Candidate Wiki 补全参考

raw extraction 完成后，如果 candidate wiki 需要供 agent 或 human review 使用，可以按本文补全。

## 1. 步骤

1. 读取 `var/rag/<run-id>/extracted/metadata-manifest.json` 和相关 extracted Markdown。
2. 更新每个 source page，加入 source-grounded sections：summary、key claims、entities、concepts、contradictions、applicability。
3. 只为可复用的人物、组织、工具、方法、理论或框架创建 `entities/` 和 `concepts/` 页面。
4. 更新 `overview.md`，写入 corpus-level synthesis 和 wikilinks。
5. 更新 `index.md`，确保每个非 meta page 可达。
6. 更新 `log.md`，记录 ingest 和 agent enrichment step。
7. 通过 stable wrapper 重新运行 health、lint 和 build-graph。

## 2. 质量规则

- 每个事实性 claim 必须来自 extracted source，或明确标记为 agent inference。
- 优先写短、可审查页面，不复制长篇 source passage。
- 内部 candidate pages 使用 wikilinks，外部 URL 使用 Markdown links。
- 保留 `title`、`type`、`tags`、`sources` 和 `last_updated` 等 candidate frontmatter。
- unresolved contradictions 应保留为 review notes。
- 本步骤不得写入 reviewed knowledge。

## 3. 最小页面集

单个 substantial source 通常至少包含：

- `sources/` 下的 source page；
- `overview.md`、`index.md` 和 `log.md`；
- 基础 `StructuredIngestion` 和 `CandidateKnowledge` concept pages；
- 只有在增加 review value 时才创建额外 concept/entity pages。
