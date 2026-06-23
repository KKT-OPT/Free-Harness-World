---
documentName: harness/templates/knowledge/ReviewedKnowledgeTemplate.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
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
  decision: h6-complete
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
```

## Statement

在这里写 reviewed knowledge。不得粘贴长篇 source content、credential、private settings、raw logs 或未脱敏 trace。

## Applicability

说明该 knowledge 适用和不适用的范围。

## Key Concepts

| Concept | Definition | Aliases |
|---|---|---|
| `<concept>` | `<definition>` | `<aliases>` |

## Source Trace

| Source | Evidence Summary | Notes |
|---|---|---|
| `<source>` | `<summary>` | `<notes>` |

## Staleness

记录需要 re-review 的条件、日期或信号。

## Governance Notes

- Reviewed Knowledge 必须有 source provenance 和 review。
- Project-specific facts 属于项目 facts，不进入 root-wide knowledge。
- RAG chunks、graph、embedding 和 candidate wiki 不自动成为 reviewed Knowledge。
