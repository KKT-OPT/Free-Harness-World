# Formal Project Template Package

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

This package is the reusable formal template set for a Harness-managed project instance.

It is inspired by the old HarnessVault `project-template` directory shape and extended with the current Harness routing, validation, sensitive-boundary and workflow evidence requirements.

## Target Instance Layout

Instantiate these templates only under:

```text
projects/<project-id>/
  AGENTS.md
  docs/project/
    ProjectIndex.md
    ProjectProfile.yaml
    SourceLayout.md
    Validation.md
    TestStrategy.md
    SensitiveBoundaries.md
    Acceptance.md
    prd/PRD.md
    architecture/Architecture.md
    dictionary/SemanticDictionary.md
    git/Repository.md
    api/Api.md
    data/Data.md
    test/Test.md
    decision/ADR-0001.md
    workflow/README.md
```

## Template Mapping

| Target file | Template source |
|---|---|
| `AGENTS.md` | `ProjectAGENTS.md` |
| `docs/project/ProjectIndex.md` | `ProjectIndex.md` |
| `docs/project/ProjectProfile.yaml` | `ProjectProfile.example.yaml` |
| `docs/project/SourceLayout.md` | `SourceLayout.md` |
| `docs/project/Validation.md` | `Validation.md` |
| `docs/project/TestStrategy.md` | `TestStrategy.md` |
| `docs/project/SensitiveBoundaries.md` | `SensitiveBoundaries.md` |
| `docs/project/Acceptance.md` | `Acceptance.md` |
| `docs/project/prd/PRD.md` | `PRD.md` |
| `docs/project/architecture/Architecture.md` | `Architecture.md` |
| `docs/project/dictionary/SemanticDictionary.md` | `SemanticDictionary.md` |
| `docs/project/git/Repository.md` | `Repository.md` |
| `docs/project/api/Api.md` | `Api.md` |
| `docs/project/data/Data.md` | `Data.md` |
| `docs/project/test/Test.md` | `Test.md` |
| `docs/project/decision/ADR-0001.md` | `ADR-0001-template.md` |
| `docs/project/workflow/README.md` | `WorkflowReadme.md` |

## Boundary

Templates may contain placeholders such as `<project-id>`, `<repository-ref>`, `<github-owner-or-org>` and `<validation-profile-id>`.

Templates must not contain real local paths, real GitHub account values, private repository URLs, Maven settings content, tokens, passwords, auth file content, raw logs or customer data.

Concrete local values belong under `user/` local files and must stay outside Git.
