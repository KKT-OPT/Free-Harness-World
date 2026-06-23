---
documentName: harness/templates/project-template/docs/project/data/Data.md
version: v0.1.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目数据实体、隐私等级和生命周期模板。
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
  - harness/templates/project-template/docs/project/data/Data.md
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
# Data Template（数据模板）

## 目的

Capture data entities, schemas, privacy class, retention, lineage, migration and validation rules.

## 输入

- architecture facts
- API facts
- database or storage facts
- privacy and compliance constraints
- migration requirements

## 输出

- `projects/<project-id>/docs/project/data/Data.md`
- entity and schema inventory
- data sensitivity classification
- lifecycle and migration notes

## 敏感边界

Do not include real personal data, credentials, auth file content, private settings, unredacted logs, private paths, private repository URLs or secret database connection details.

## 实例化规则

1. Copy this file to `projects/<project-id>/docs/project/data/Data.md`.
2. Use schema summaries and reviewed examples, not raw sensitive records.
3. Classify sensitivity before adding samples.
4. Link migration decisions to ADRs when they change durable behavior.

## Entities

| Entity | Meaning | Owner | Source | Sensitivity |
|---|---|---|---|---|
| `<entity>` | `<meaning>` | `<owner>` | `<source>` | `<class>` |

## Schema Summary

| Object | Field | Type | Constraint | Notes |
|---|---|---|---|---|
| `<object>` | `<field>` | `<type>` | `<constraint>` | `<notes>` |

## Data Lifecycle

| Data | Created By | Stored In | Retention | Deletion Rule |
|---|---|---|---|---|
| `<data>` | `<creator>` | `<store>` | `<retention>` | `<deletion-rule>` |

## Migration Notes

| Migration | Trigger | Validation | Rollback |
|---|---|---|---|
| `<migration>` | `<trigger>` | `<validation>` | `<rollback>` |

## Open Questions

| Question | Owner | Review Phase |
|---|---|---|
| `<question>` | `<owner>` | `<phase>` |
