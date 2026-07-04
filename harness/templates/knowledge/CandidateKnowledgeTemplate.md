---
documentName: harness/templates/knowledge/CandidateKnowledgeTemplate.md
version: v1.1.0-alias-tag-governance
updatedAt: 2026-07-03 22:30:00.000 +08:00
status: active
purpose: 提供 candidate knowledge 记录模板，确保候选知识不会自动晋升为 reviewed knowledge。
scope:
  - knowledge-template
  - candidate-knowledge
prerequisites:
  - AGENTS.md
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - harness/templates/knowledge/ReviewedKnowledgeTemplate.md
outputTo:
  - harness/templates/knowledge/CandidateKnowledgeTemplate.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/governance/KnowledgePromotionPolicy.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: p5-21-5-alias-and-tag-fields-added
---
# Candidate Knowledge 模板

## Source

```yaml
sourceRef: <source>
sourceType: raw | extracted | structured | workflow-evidence | project-fact | report | other
scope: global | domain | project-reviewed | user-private
projectId: null
domain: null
confidence: low | medium | high
reviewStatus: candidate
submittedBy: human | agent | unknown
usageRights: unknown | permitted | restricted
sensitiveRisk: none | low | medium | high
aliases: []
tags: []
tagVocabularyRef: <domain-schema-or-null>
```

## Candidate Statement

在这里写候选知识。候选知识不是 reviewed Knowledge。

## 证据

列出 source files、sections、hashes 或 workflow evidence references。不得粘贴 raw logs、credential、private settings 或未脱敏 trace。

## Applicability

说明该 candidate 适用和不适用的边界。

## Review Notes

记录晋升前必须检查的事项。

## Alias And Tag Notes

记录 aliases、同义词、跨语言别名和受控标签检查结果。Candidate 使用的 tags 必须来自目标 domain schema 或 review package 中的受控 tag vocabulary。

## Promotion Decision

```yaml
decision: approve | reject | defer
targetAsset: <user/knowledge/reviewed/path-or-private-repo-path-or-null>
reviewer: <reviewer-or-null>
decisionDate: <date-or-null>
reason: <reason>
```
