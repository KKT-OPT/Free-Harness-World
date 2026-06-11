# Project Agent Entry

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Define the project-local agent entry rules for a managed Harness project.

## Inputs

- `<project-id>`
- root Harness entry rules
- project index location
- project sensitive boundary policy

## Outputs

- `projects/<project-id>/AGENTS.md`
- project-local read order
- project task evidence expectations

## Sensitive Boundary

Do not include credentials, auth files, private settings, unredacted logs, real local paths, concrete GitHub account values or real repository URLs in this file.

## Instantiation Rules

1. Copy this file to `projects/<project-id>/AGENTS.md`.
2. Replace `<project-id>` and any other placeholders.
3. Keep root Harness rules authoritative when project rules conflict.
4. Do not add phase status or temporary task memory to project `AGENTS.md`.

## Project Boundary

This file is copied into a managed project instance when the project is created.

The project inherits Harness Root rules from the root `AGENTS.md`.

## Required Project Reads

For project tasks, read in this order:

```text
1. <harness-root>/AGENTS.md
2. <harness-root>/harness/INDEX.md
3. projects/<project-id>/AGENTS.md
4. projects/<project-id>/docs/project/ProjectIndex.md
```

Use `harness/INDEX.md` to find plans, policies, templates, tools and governance documents.

## Project Rules

1. Keep project facts inside `docs/project/`.
2. Save task workflow evidence under `docs/project/workflow/`.
3. Do not expose credentials, auth files, private settings or unredacted logs.
4. Use stable Harness tool surfaces when available.
5. Record Task Brief and Harness Run Card at the start of workflow evidence.
6. Keep concrete GitHub account, private repository and local machine values under `user/` local files.
