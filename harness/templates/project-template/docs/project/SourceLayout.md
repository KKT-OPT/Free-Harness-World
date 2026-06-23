---
documentName: harness/templates/project-template/docs/project/SourceLayout.md
version: v0.3.0-formal-project-package
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目源码布局、生成物和禁止路径模板。
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
  - harness/templates/project-template/docs/project/SourceLayout.md
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
# Source Layout Template（源码布局模板）

## 目的

Capture the source, test, resource, generated-output and forbidden-path layout for a managed project.

## 输出

- `projects/<project-id>/docs/project/SourceLayout.md`
- source boundary map
- generated-output rules
- project-local path conventions

## 敏感边界

Do not include real local absolute paths, credentials, auth files, private settings, unredacted logs, raw customer data or private repository URLs.

Use project-relative paths such as `src/main/java` or placeholders such as `<source-root>`.

## Source Roots

| Area | Project-Relative Path | Owner | Notes |
|---|---|---|---|
| Main source | `<main-source-path>` | `<owner>` | `<notes>` |
| Test source | `<test-source-path>` | `<owner>` | `<notes>` |
| Resources | `<resource-path>` | `<owner>` | `<notes>` |
| Configuration | `<config-path>` | `<owner>` | `<notes>` |

## Module Layout

| Module | Path | Responsibility | Build Surface |
|---|---|---|---|
| `<module-name>` | `<module-path>` | `<responsibility>` | `<command-id>` |

## Generated Outputs

| Output | Path | Producer | Git Policy |
|---|---|---|---|
| `<output-name>` | `<relative-path>` | `<tool-or-command>` | `<ignored-or-tracked>` |

## Forbidden Paths

| Path Pattern | Reason | Handling |
|---|---|---|
| `<forbidden-pattern>` | `<reason>` | `<handling>` |

## Maintenance Rules

1. Keep paths project-relative unless a reviewed placeholder is required.
2. Update this file when modules, generated outputs or source roots move.
3. Do not duplicate repository policy; link to `git/Repository.md`.
4. Do not duplicate sensitive rules; link to `SensitiveBoundaries.md`.
