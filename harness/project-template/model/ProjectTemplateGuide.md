# Project Template Guide

Status: active
Version: v0.5.0-formal-project-package
Date: 2026-06-12

## Purpose

This guide maps reusable project templates to the Harness project instance model.

The formal project package upgrades the template set from minimum/demo-ready to real-project-onboarding-ready. This does not mean a real business project has already been onboarded. It means the template assets contain the sections needed before a future managed project can be instantiated under `projects/<project-id>`.

## Source Priority

When old HarnessVault inputs conflict, the concrete old HarnessVault directory organization and files are treated as stronger evidence than the old standalone architecture narrative.

For P12.1, the source facts are:

| Old project-template area | New Harness landing |
|---|---|
| project template README and index | `harness/project-template/model/ProjectTemplateGuide.md` and root/project index routing. |
| `architecture/ARCHITECTURE.md` | `harness/templates/project/Architecture.md`. |
| `dictionary/SemanticDictionary.md` | `harness/templates/project/SemanticDictionary.md`. |
| `git/Repository.md` | `harness/templates/project/Repository.md`. |
| `prd/` | `harness/templates/project/PRD.md`. |
| `api/` | `harness/templates/project/Api.md`. |
| `data/` | `harness/templates/project/Data.md`. |
| `test/` | `harness/templates/project/Test.md`. |
| `workflow/` | `harness/templates/project/WorkflowReadme.md` and `harness/templates/workflow/WorkflowTemplate.md`. |
| `decision/ADR-0001-template.md` | `harness/templates/project/ADR-0001-template.md`. |

The old tree is not copied. Its useful structure is rewritten into the current Harness model.

## Template Classes

### Formal Project Package Templates

These templates are required for formal real-project onboarding:

```text
harness/templates/project/README.md
harness/templates/project/ProjectProfile.example.yaml
harness/templates/project/ProjectAGENTS.md
harness/templates/project/ProjectIndex.md
harness/templates/project/SourceLayout.md
harness/templates/project/Validation.md
harness/templates/project/TestStrategy.md
harness/templates/project/SensitiveBoundaries.md
harness/templates/project/Acceptance.md
harness/templates/project/PRD.md
harness/templates/project/Architecture.md
harness/templates/project/SemanticDictionary.md
harness/templates/project/Repository.md
harness/templates/project/Api.md
harness/templates/project/Data.md
harness/templates/project/Test.md
harness/templates/project/ADR-0001-template.md
harness/templates/project/WorkflowReadme.md
harness/templates/project/ValidationProfile.example.yaml
harness/templates/task/TaskBriefTemplate.md
harness/templates/workflow/WorkflowTemplate.md
```

The minimum package is defined in:

```text
harness/project-template/model/StandardProjectPackage.md
```

Reduced demo packages may omit PRD/API/Data/etc. only when the task explicitly states it is a controlled flow-proof demo and not a real-project onboarding validation.

## Instantiation Rules

1. Instantiate project templates only inside `projects/<project-id>`.
2. Keep reusable template bodies under `harness/templates/project/`; keep explanatory rules under `harness/project-template/model/`.
3. Replace placeholders such as `<project-id>`, `<project-name>`, `<repository-ref>`, `<branch-policy>`, `<owner>` and `<review-after>`.
4. Record unknown facts as `unknown` or `to-be-reviewed`; do not invent project facts to fill a template.
5. Do not copy old HarnessVault directories into the current Harness Root.
6. Do not store credentials, private settings, auth files, unredacted logs, real private paths or real repository URLs in template files.
7. Project-specific facts belong in `projects/<project-id>/docs/project/`, not in root templates.
8. Workflow evidence is not automatically promoted to Project Facts, Knowledge, Memory or Skill.

## Module Selection

| Module | Use when | May stay absent when |
|---|---|---|
| Architecture | Module boundaries, runtime shape or design constraints affect the task. | Only controlled demos with no architecture claim. |
| Semantic Dictionary | Naming, domain terms, aliases or data meanings can drift. | Only controlled demos with no reusable terms. |
| Repository | Branch, build, test, PR or agent git rules matter. | Only read-only analysis with no repository operation. |
| PRD | Product intent, users, feature scope or acceptance criteria guide work. | Only infrastructure-only demos. |
| Api | API contracts, integrations or auth boundaries affect work. | Only projects with no API surface. |
| Data | Entities, schemas, privacy or lifecycle facts affect work. | Only projects with no persistent data or schema. |
| Test | Validation strategy must be stable across tasks. | Never absent for real-project onboarding. |
| Workflow | Task evidence must be recorded and partitioned. | Never absent for managed project tasks. |
| Decision | ADR or governance decisions are needed. | Directory may exist before first ADR. |

## Relationship To `java-demo`

`projects/java-demo` remains a controlled flow-proof and contract-proof demo. It can validate that the minimum Harness lifecycle works, but it is not proof that a real business project template has been fully validated.

P12.1 only hardens the reusable templates. A future onboarding task must instantiate these templates for a separate managed project before claiming real-project onboarding validation.

## Non-Goals

- No real business project import.
- No real repository registration.
- No whole-directory migration from old HarnessVault.
- No tool installation.
- No RAG pipeline execution.
- No claim that the Harness framework is production-complete.
