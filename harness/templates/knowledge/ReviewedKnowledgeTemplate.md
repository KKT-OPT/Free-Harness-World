---
documentName: harness/templates/knowledge/ReviewedKnowledgeTemplate.md
version: v1.2.0-normalized-source-depth
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: active
purpose: 提供 reviewed knowledge 模板，确保知识晋升具备来源、scope、review 和 stale 规则。
scope:
  - knowledge-template
  - reviewed-knowledge
prerequisites:
  - AGENTS.md
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - harness/templates/knowledge/CandidateKnowledgeTemplate.md
  - user/knowledge/README.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
outputTo:
  - harness/templates/knowledge/ReviewedKnowledgeTemplate.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/governance/KnowledgePromotionPolicy.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: normalized-source-and-source-depth-rules-added
---
# Reviewed Knowledge 模板

## 元数据

```yaml
knowledgeId: <stable-id>
scope: global | domain | project-reviewed | user-private
domain: null
projectId: null
reviewedAt: <date>
reviewedBy: <human-or-approved-process>
sourceRefs: []
supersedes: []
reviewAfter: <date-or-condition>
sensitiveRisk: none | low | medium | high
storageBoundary: user/knowledge/reviewed | external-private-repo
aliases: []
tags: []
tagVocabularyRef: <domain-schema-or-null>
```

## Statement

在这里写 reviewed knowledge 的核心结论。不得粘贴长篇 source content、credential、private settings、raw logs 或未脱敏 trace。

Source-level reviewed page 不能只是关键词卡片；应能让 agent 在不读取 raw PDF 的情况下理解原始材料的核心主线、概念、方法和边界。

## Source Overview

概括原始材料的主题、问题意识、章节结构和主要贡献。该部分应是中文主体说明，专业术语、概念名、代码标识和论文原名可以保留英文。

## Core Framework

用列表、表格或短段落总结原始材料的核心框架、方法、taxonomy、workflow 或关键论证关系。

## Applicability

说明该 knowledge 适用和不适用的范围。

## Key Concepts

| Concept | Definition | Aliases |
|---|---|---|
| `<concept>` | `<definition>` | `<aliases>` |

Aliases 是 duplicate governance 的输入，不只是展示字段。跨语言别名、缩写和同义词应写入 aliases 或 Key Concepts 表格，供 alias-aware dedup 使用。

## Source Trace

| Source | Evidence Summary | Notes |
|---|---|---|
| `user/knowledge/raw/<domain>/<source>.pdf` | 原始 source。 | 用户审核通过后作为 reviewed Knowledge 来源。 |
| `user/knowledge/raw/<domain>/normalized/<source>.md` | 原始材料转换后的 normalized Markdown。 | 长期保存在 raw domain，供 agent 理解原材料结构；不是 reviewed 结论本身。 |
| `user/knowledge/candidate/_audit/post-promotion/<audit>.md` | post-promotion 轻量审计记录。 | 记录 candidate full corpus 的 review 和 cleanup 处置。 |

## Staleness

记录需要 re-review 的条件、日期或信号。

## Governance Notes

- Reviewed Knowledge 必须有 source provenance 和 review。
- Project-specific facts 属于项目 facts，不进入 root-wide knowledge。
- RAG chunks、graph、embedding 和 candidate wiki 不自动成为 reviewed Knowledge。
- Reviewed tags 必须来自 domain schema 或受控 tag vocabulary。
- reviewed `sourceRefs` 不应把 `var/rag/<run-id>/extracted/*.md` 作为长期来源；原始材料转换后的 Markdown 应保存在 `user/knowledge/raw/<domain>/normalized/` 或外部 private raw source boundary。
