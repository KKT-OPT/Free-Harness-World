---
documentName: harness/templates/project-template/model/README.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 路由项目模板模型说明、实例化模型、注册模型和历史归档 checklist。
scope:
  - project-template-model
  - model-index
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/model/ProjectTemplateGuide.md
  - harness/templates/project-template/model/StandardProjectPackage.md
  - harness/templates/project-template/model/ProjectInstanceModel.md
  - harness/templates/project-template/model/ProjectRegistrationModel.md
outputTo:
  - harness/templates/project-template/model/README.md
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
# Project Template Model

This directory contains model-level guidance for the reusable project template package.

It is not copied wholesale into a project instance. Project instances receive the project entry template and the `docs/project/` template tree.

## Active Model Documents

| Document | Purpose |
|---|---|
| `ProjectTemplateGuide.md` | Explains how template files map to project instances. |
| `StandardProjectPackage.md` | Defines the standard managed project package and required modules. |
| `ProjectInstanceModel.md` | Defines project instance boundaries and required entry files. |
| `ProjectRegistrationModel.md` | Defines local registry routing metadata and forbidden content. |

## Archive

Historical P-stage checklist documents are kept under `archive/` for background only. They are not default template inputs and are not current acceptance gates.
