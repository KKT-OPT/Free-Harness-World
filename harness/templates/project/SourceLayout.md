# Source Layout Template

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Capture the source, test, resource, generated-output and forbidden-path layout for a managed project.

## Outputs

- `projects/<project-id>/docs/project/SourceLayout.md`
- source boundary map
- generated-output rules
- project-local path conventions

## Sensitive Boundary

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
