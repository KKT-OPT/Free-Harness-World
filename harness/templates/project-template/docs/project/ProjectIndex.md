---
documentName: harness/templates/project-template/docs/project/ProjectIndex.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目事实入口模板，路由项目身份、事实模块、workflow evidence、decision、model 和 reports。
scope:
  - project-fact-index-template
  - project-routing
  - project-document-inventory
prerequisites:
  - projects/<project-id>/AGENTS.md
relatedDocuments:
  - harness/templates/project-template/AGENTS.md
  - harness/templates/project-template/docs/project/SensitiveBoundaries.md
  - harness/templates/project-template/docs/project/Validation.md
outputTo:
  - harness/templates/project-template/docs/project/ProjectIndex.md
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
# Project Index（项目事实索引模板）

This file is the template for:

```text
projects/<project-id>/docs/project/ProjectIndex.md
```

It is the project fact routing entry. It is not workflow evidence, not a plan file, not a memory store and not a place for credentials or raw logs.

## 1. Project Identity

```yaml
projectId: <project-id>
projectName: <project-name>
projectType: <project-type>
root: projects/<project-id>
entry: AGENTS.md
projectIndex: docs/project/ProjectIndex.md
status: <draft|review|active|stale|archived>
```

Use `unknown` or `to-be-reviewed` when a fact has not been reviewed.

## 2. Required Fact Modules

| Area | Location | Status |
|---|---|---|
| Profile | `ProjectProfile.yaml` | `<status>` |
| Source layout | `SourceLayout.md` | `<status>` |
| Validation | `Validation.md` | `<status>` |
| Test strategy | `TestStrategy.md` | `<status>` |
| Sensitive boundaries | `SensitiveBoundaries.md` | `<status>` |
| Acceptance | `Acceptance.md` | `<status>` |
| PRD | `prd/PRD.md` | `<status>` |
| Architecture | `architecture/Architecture.md` | `<status>` |
| Dictionary | `dictionary/SemanticDictionary.md` | `<status>` |
| Git | `git/Repository.md` | `<status>` |
| API | `api/Api.md` | `<status>` |
| Data | `data/Data.md` | `<status>` |
| Test details | `test/Test.md` | `<status>` |
| Workflow evidence | `workflow/` | active |
| Decisions | `decision/` | active |
| Project model notes | `model/` | `<status>` |
| Reports | `reports/` | active |

## 3. Workflow Evidence

Workflow evidence lives under:

```text
docs/project/workflow/
```

Each complex task should record:

1. Task Brief;
2. Harness Run Card;
3. readiness check;
4. plan;
5. execution record;
6. validation summary;
7. acceptance state;
8. governance candidates.

Workflow evidence only produces candidates. It does not automatically become Project Fact, Knowledge, Memory, Skill or Template.

## 4. Decisions

Project decisions live under:

```text
docs/project/decision/
```

Use ADR-style files for durable decisions that affect architecture, validation, governance, project facts or long-term maintenance.

## 5. Reports

Project reports live under:

```text
docs/project/reports/
```

Reports are evidence, not facts. A report recommendation becomes a project fact only after review and an explicit update to the target fact document.

## 6. Sensitive Boundary

Do not include credentials, auth files, private settings, unredacted logs, real local paths, concrete account values, real repository URLs, raw customer data or private endpoint details in this index.
