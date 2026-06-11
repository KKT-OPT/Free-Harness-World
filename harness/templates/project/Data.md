# Data Template

Status: template
Version: v0.1.0-p12.1
Date: 2026-06-10

## Purpose

Capture data entities, schemas, privacy class, retention, lineage, migration and validation rules.

## Inputs

- architecture facts
- API facts
- database or storage facts
- privacy and compliance constraints
- migration requirements

## Outputs

- `projects/<project-id>/docs/project/data/Data.md`
- entity and schema inventory
- data sensitivity classification
- lifecycle and migration notes

## Sensitive Boundary

Do not include real personal data, credentials, auth file content, private settings, unredacted logs, private paths, private repository URLs or secret database connection details.

## Instantiation Rules

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
