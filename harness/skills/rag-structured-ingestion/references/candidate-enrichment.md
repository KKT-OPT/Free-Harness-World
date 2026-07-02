---
documentName: harness/skills/rag-structured-ingestion/references/candidate-enrichment.md
version: v1.1.0-llm-wiki-method
updatedAt: 2026-06-30 19:14:00.837 +08:00
status: active
purpose: 定义 raw extraction 后如何补全 candidate wiki，并保持 candidate-only 边界。
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
  reviewedAt: 2026-06-30
  decision: phase-1-deterministic-absorption
---
# Candidate Wiki 补全参考

raw extraction 完成后，`ingest` 只保证生成可审查 scaffold。若用户需要“待评估的结构化候选知识”，agent 应先运行 `enrichment-plan`，再按本文补全 candidate wiki。

## 1. 执行步骤

1. 运行 `enrichment-plan`，读取输出的 Candidate Enrichment Plan。
2. 阅读 `var/rag/<run-id>/extracted/metadata-manifest.json` 和相关 extracted Markdown。
3. 更新每个 source page，补齐 source-grounded sections：summary、key claims、entities、concepts、contradictions、applicability。
4. 只为有复用价值的人物、组织、工具、方法、理论或框架创建 `entities/` 和 `concepts/` 页面。
5. 更新 `overview.md`，写入 corpus-level synthesis 和必要 wikilinks。
6. 更新 `index.md`，确保每个非 meta page 可从索引或 overview 到达。
7. 更新 `log.md`，记录 ingest 和 agent enrichment step。
8. 重新运行 `health`、`lint` 和 `build-graph`。

## 2. 质量规则

- 每个事实性 claim 必须来自 extracted source，或明确标记为 agent inference。
- 优先写短、可审查页面，不复制长篇 source passage。
- 内部 candidate pages 使用 wikilinks，外部 URL 使用 Markdown links。
- 保留 `title`、`type`、`tags`、`sources` 和 `last_updated` 等 candidate frontmatter。
- unresolved contradictions 应保留为 review notes。
- 本步骤不得写入 reviewed Knowledge、Memory、Project Fact 或 promotion artifact。

## 3. 最小页面集

单个 substantial source 通常至少包含：

- `sources/` 下的 source page；
- `overview.md`、`index.md` 和 `log.md`；
- 基础 `StructuredIngestion` 和 `CandidateKnowledge` concept pages；
- 只有在增加 review value 时才创建额外 concept/entity pages。
