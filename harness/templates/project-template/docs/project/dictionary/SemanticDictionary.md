---
documentName: harness/templates/project-template/docs/project/dictionary/SemanticDictionary.md
version: v0.1.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目语义字典和术语治理模板。
scope:
  - project-template
  - project-doc-template
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/README.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
outputTo:
  - harness/templates/project-template/docs/project/dictionary/SemanticDictionary.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/templates/project-template/README.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: h4-consolidated
---
# Semantic Dictionary Template（语义字典模板）

## 目的

Maintain canonical project terminology so humans and agents use the same names for domain terms, modules, fields, states and workflows.

## 输入

- architecture facts
- PRD facts
- API and data facts
- source naming conventions
- reviewed user terminology

## 输出

- `projects/<project-id>/docs/project/dictionary/SemanticDictionary.md`
- canonical term table
- alias and forbidden-term table
- candidate term review list

## 敏感边界

Do not include customer secrets, credentials, private settings, raw user data, unredacted logs, private paths or real private repository URLs. Redact or generalize examples.

## 实例化规则

1. Copy this file to `projects/<project-id>/docs/project/dictionary/SemanticDictionary.md`.
2. Prefer terms already used in reviewed project facts.
3. Record unresolved terms as candidates.
4. Update architecture, API, data and test docs when a canonical term changes.

## Core Terms

| Term | Recommended English Name | Definition | Forbidden Alias | Related Docs |
|---|---|---|---|---|
| `<term>` | `<english-name>` | `<definition>` | `<forbidden-alias>` | `<doc-link>` |

## Module Names

| Module | Recommended Name | Responsibility | Forbidden Name | Architecture Layer |
|---|---|---|---|---|
| `<module>` | `<recommended-name>` | `<responsibility>` | `<forbidden-name>` | `<layer>` |

## Field Meanings

| Field | Object | Type | Meaning | Constraint |
|---|---|---|---|---|
| `<field>` | `<object>` | `<type>` | `<meaning>` | `<constraint>` |

## States

| State | Meaning | Trigger | Next State |
|---|---|---|---|
| `<state>` | `<meaning>` | `<trigger>` | `<next-state>` |

## Workflow Names

| Workflow | Recommended Name | Start | End | Description |
|---|---|---|---|---|
| `<workflow>` | `<recommended-name>` | `<start>` | `<end>` | `<description>` |

## Alias Normalization

| Alias | Canonical Term | Reason |
|---|---|---|
| `<alias>` | `<canonical-term>` | `<reason>` |

## Candidate Terms

| Candidate | Source | Question | Review Status |
|---|---|---|---|
| `<candidate>` | `<source>` | `<question>` | `<status>` |
