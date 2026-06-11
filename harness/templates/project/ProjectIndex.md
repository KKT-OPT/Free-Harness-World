# Project Index

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Provide the project fact index and routing entry for a formal Harness-managed project package.

## Inputs

- `<project-id>`
- `<project-type>`
- `ProjectProfile.yaml`
- formal project package facts
- source layout, validation, sensitive boundary and acceptance facts
- PRD, architecture, repository, API, data, test, decision and workflow modules

## Outputs

- `projects/<project-id>/docs/project/ProjectIndex.md`
- project fact inventory
- workflow and decision routing

## Sensitive Boundary

Do not include credentials, auth files, private settings, unredacted logs, real local paths, real GitHub account values or real private repository URLs.

Use reviewed placeholders until private values are stored under `user/` local files or separately approved as redacted references.

## Instantiation Rules

1. Copy this file to `projects/<project-id>/docs/project/ProjectIndex.md`.
2. Replace placeholders with reviewed project facts.
3. Instantiate the formal module set unless the project is explicitly a tiny flow-proof demo.
4. Keep this file as an index; detailed facts belong in their own project documents.

## Project Identity

```yaml
projectId: <project-id>
projectType: <project-type>
root: projects/<project-id>
```

## Source Layout

| Module | Location | Status |
|---|---|---|
| Source layout | `SourceLayout.md` | `<status>` |
| Repository | `git/Repository.md` | `<status>` |
| Architecture | `architecture/Architecture.md` | `<status>` |

## Validation

| Fact | Location | Status |
|---|---|---|
| Validation profiles | `Validation.md` | `<status>` |
| Test strategy | `TestStrategy.md` | `<status>` |
| Test module | `test/Test.md` | `<status>` |
| Acceptance | `Acceptance.md` | `<status>` |

## Project Fact Modules

| Module | Location | Status |
|---|---|---|
| Sensitive boundaries | `SensitiveBoundaries.md` | `<status>` |
| PRD | `prd/PRD.md` | `<status>` |
| API | `api/Api.md` | `<status>` |
| Data | `data/Data.md` | `<status>` |
| Semantic dictionary | `dictionary/SemanticDictionary.md` | `<status>` |
| Decisions | `decision/` | `<status>` |
| Workflow evidence | `workflow/` | `<status>` |

## Local And Git Boundary

| Boundary | Rule |
|---|---|
| Harness Root Git | Tracks reusable Harness framework assets only. |
| Project Git | Project work copy may have its own separate repository. |
| Local user values | Stored under `user/`, not in this project index. |
| Private repository URL | Use `<private-repository-ref>` or a reviewed redacted reference. |
| GitHub account | Use `<github-account-ref>`; concrete account data stays under `user/`. |

## Workflow Evidence

Workflow evidence lives under:

```text
docs/project/workflow/
```

Each task evidence file starts with:

1. Task Brief;
2. Harness Run Card;
3. Readiness Check;
4. Plan;
5. Execution and validation record;
6. Acceptance and governance candidates.

## Decisions

Project decisions live under:

```text
docs/project/decision/
```
