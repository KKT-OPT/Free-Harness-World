# Project Instance Model

Status: draft
Version: v0.1.0-p9-preflight
Date: 2026-06-08

## Purpose

This document defines the minimum project instance structure that P9 must create for the Java demo.

## Required Layout

```text
projects/<project-id>/
  AGENTS.md
  docs/
    project/
      ProjectIndex.md
      workflow/
  src/
  pom.xml
```

The source layout may vary by language or build system, but the project entry files and workflow directory are required.

## Project Facts

`docs/project/ProjectIndex.md` must route to:

- project purpose and scope;
- source layout;
- build and validation commands;
- test strategy;
- sensitive boundaries;
- workflow evidence;
- accepted project decisions.

Project facts must not be copied into the root registry as long-form content.

## Workflow Evidence

Each project task should create one workflow evidence file under:

```text
projects/<project-id>/docs/project/workflow/<taskId>.md
```

The workflow starts with Task Brief and Harness Run Card, then records readiness, plan, changes, validation, acceptance, and governance candidates.
