---
documentName: harness/templates/project-template/model/ProjectTemplateGuide.md
version: v1.0.0-pre-h8-clean-template-route
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 说明统一项目模板包如何映射到受管项目实例，并定义实例化规则和模块选择规则。
scope:
  - project-template-guide
  - instantiation-rules
  - module-selection
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/model/StandardProjectPackage.md
  - harness/templates/project-template/model/ProjectInstanceModel.md
  - harness/templates/project-template/model/ProjectRegistrationModel.md
outputTo:
  - harness/templates/project-template/model/ProjectTemplateGuide.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/templates/project-template/README.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: pre-h8-compatibility-cleanup
---
# Project Template（项目模板） Guide

This guide maps reusable project templates to the Harness project instance model.

The project template package is real-project-onboarding-ready in structure, but it does not claim that a real business project has already been onboarded. It provides placeholders, sections, routing rules and safety boundaries only.

## Template Source

The only active reusable project template source is:

```text
harness/templates/project-template/
```

旧项目模板路径不再作为入口维护。不要向旧路径新增模板正文。

## Mapping

| Project Instance Target | Template Source |
|---|---|
| `projects/<project-id>/AGENTS.md` | `harness/templates/project-template/AGENTS.md` |
| `docs/project/ProjectIndex.md` | `harness/templates/project-template/docs/project/ProjectIndex.md` |
| `docs/project/ProjectProfile.yaml` | `harness/templates/project-template/docs/project/ProjectProfile.example.yaml` |
| `docs/project/ValidationProfile.yaml` | `harness/templates/project-template/docs/project/ValidationProfile.example.yaml` |
| `docs/project/SourceLayout.md` | `harness/templates/project-template/docs/project/SourceLayout.md` |
| `docs/project/Validation.md` | `harness/templates/project-template/docs/project/Validation.md` |
| `docs/project/TestStrategy.md` | `harness/templates/project-template/docs/project/TestStrategy.md` |
| `docs/project/SensitiveBoundaries.md` | `harness/templates/project-template/docs/project/SensitiveBoundaries.md` |
| `docs/project/Acceptance.md` | `harness/templates/project-template/docs/project/Acceptance.md` |
| `docs/project/prd/PRD.md` | `harness/templates/project-template/docs/project/prd/PRD.md` |
| `docs/project/architecture/Architecture.md` | `harness/templates/project-template/docs/project/architecture/Architecture.md` |
| `docs/project/dictionary/SemanticDictionary.md` | `harness/templates/project-template/docs/project/dictionary/SemanticDictionary.md` |
| `docs/project/git/Repository.md` | `harness/templates/project-template/docs/project/git/Repository.md` |
| `docs/project/api/Api.md` | `harness/templates/project-template/docs/project/api/Api.md` |
| `docs/project/data/Data.md` | `harness/templates/project-template/docs/project/data/Data.md` |
| `docs/project/test/Test.md` | `harness/templates/project-template/docs/project/test/Test.md` |
| `docs/project/decision/ADR-0001.md` | `harness/templates/project-template/docs/project/decision/ADR-0001.md` |
| `docs/project/workflow/README.md` | `harness/templates/project-template/docs/project/workflow/README.md` |
| `docs/project/model/README.md` | `harness/templates/project-template/docs/project/model/README.md` |
| `docs/project/reports/README.md` | `harness/templates/project-template/docs/project/reports/README.md` |

## 实例化规则

1. Instantiate templates only under `projects/<project-id>`.
2. Replace placeholders with reviewed project facts or leave them as `unknown` / `to-be-reviewed`.
3. Do not invent project facts to fill a template.
4. Do not copy local registry values, credentials, private settings, auth files, unredacted logs, private repository URLs, concrete account names or local absolute paths into templates.
5. Project-specific facts belong in `projects/<project-id>/docs/project/`.
6. Workflow evidence belongs in `projects/<project-id>/docs/project/workflow/`.
7. Reports are evidence and do not become project facts until reviewed and written to the target fact document.

## Module Selection

| Module | Required For Managed Project | Notes |
|---|---|---|
| PRD | yes | Product intent, requirements, non-goals and acceptance context. |
| Architecture | yes | Boundaries, module responsibilities, runtime shape and constraints. |
| Dictionary | yes | Canonical terms and semantic drift control. |
| Git | yes | Repository reference, branch policy and agent git boundary. |
| API | when applicable | Use `not-applicable` only after review. |
| Data | when applicable | Use `not-applicable` only after review. |
| Test | yes | Test scope, quality gates and evidence policy. |
| Workflow | yes | Task evidence and governance candidates. |
| Decision | yes | Directory can be empty until the first ADR. |
| Model | yes | Project-local model notes and onboarding assumptions. |
| Reports | yes | Redacted reports and validation summaries. |

Reduced packages are allowed only for explicitly scoped flow-proof demos. They do not validate real-project onboarding.
