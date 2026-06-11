# Standard Project Package

Status: active
Version: v0.5.0-formal-project-package
Date: 2026-06-12

## Purpose

This document defines the standard Harness-managed project package.

It separates two layers:

1. the formal package required for real managed project onboarding;
2. the reduced minimum package allowed only for controlled flow-proof demos.

The `java-demo` project validates flow and contracts only. It does not validate real business project onboarding by itself.

## Formal Project Package

Every managed project instance must live under:

```text
projects/<project-id>/
```

Formal real-project layout:

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
    prd/
      PRD.md
    architecture/
      Architecture.md
    dictionary/
      SemanticDictionary.md
    git/
      Repository.md
    api/
      Api.md
    data/
      Data.md
    test/
      Test.md
    decision/
      ADR-0001.md
    workflow/
      README.md
```

Formal required facts:

| File | Purpose |
|---|---|
| `AGENTS.md` | Project entry rules that inherit Harness Root constraints. |
| `ProjectIndex.md` | Project identity, routing, fact inventory and workflow location. |
| `ProjectProfile.yaml` | Local routing profile, validation profile, command surface and knowledge scopes. |
| `SourceLayout.md` | Source, test, resource, generated-output and forbidden path layout. |
| `Validation.md` | Stable validation command surface and redacted evidence rules. |
| `TestStrategy.md` | Expected test scope, unit/integration distinction and acceptance expectations. |
| `SensitiveBoundaries.md` | Files, directories, config, settings and log paths that must not enter prompts or tracked docs. |
| `Acceptance.md` | Current acceptance state and project-specific completion criteria. |
| `prd/PRD.md` | Product intent, users, requirements, scope and acceptance context. |
| `architecture/Architecture.md` | Architecture positioning, boundaries, module map, runtime shape and constraints. |
| `dictionary/SemanticDictionary.md` | Canonical terms, aliases, forbidden terms, field meanings and semantic drift control. |
| `git/Repository.md` | Repository reference, branch policy, build/test commands, PR rules and agent git boundaries. |
| `api/Api.md` | API inventory, contract ownership, auth boundary, integration dependencies and compatibility notes. |
| `data/Data.md` | Entities, schemas, privacy class, retention, migration and lineage notes. |
| `test/Test.md` | Test scope details, evidence rules, quality gates and known gaps. |
| `decision/` | ADR-style project decisions. |
| `workflow/` | Task Brief, Run Card, execution, validation, acceptance and governance evidence. |

## Reduced Demo Package

Small flow-proof demos may start with a reduced package only when the task explicitly states that it is not validating real-project onboarding:

```text
projects/<project-id>/docs/project/
  ProjectIndex.md
  ProjectProfile.yaml
  SourceLayout.md
  Validation.md
  TestStrategy.md
  SensitiveBoundaries.md
  Acceptance.md
  workflow/
    README.md
  decision/
```

The reduced package is not enough for a real Java project migration or a real onboarding acceptance claim.

## Project Registry Boundary

The root registry may route to this package, but it must not duplicate project facts.

Allowed registry content:

```text
projectId
root
entry
projectIndex
defaultValidationProfile
knowledgeScopes
sensitiveBoundarySummary
```

P12.2 local registry intentionally omits command surface details. A future reviewed extension may add command surface routing only if it remains metadata and does not duplicate project facts.

Forbidden registry content:

- full architecture facts;
- source details that belong in `SourceLayout.md`;
- validation logs or raw outputs;
- credentials, auth files or private settings paths;
- real private repository URLs;
- git history.

## Template Source Boundary

Reusable templates live in:

```text
harness/templates/project/
harness/templates/task/
harness/templates/workflow/
```

`harness/project-template/model/` explains how the templates work. It must not duplicate the full template bodies.

Old HarnessVault project-template content has been selectively rewritten in P12.1. The old directory tree remains a historical input, not a source to copy into the current root.

## Validation Boundary

`projects/java-demo` validated the minimum/demo-ready lifecycle. It must not be labeled as final real-project template validation.

A future real-project onboarding validation must:

1. create or route a separate managed project under `projects/<project-id>`;
2. instantiate the minimum package;
3. add only the real-project optional modules that are required;
4. record Task Brief, Harness Run Card and workflow evidence;
5. validate sensitive boundaries before tracked documentation is updated;
6. complete user review before promoting new project facts, Knowledge, Memory or Skill.
