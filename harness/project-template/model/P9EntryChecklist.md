# P9 Entry Checklist

Status: retained-gate
Version: v0.4.0-p11.8
Date: 2026-06-09

## Purpose

This checklist is the acceptance gate for entering P9 Java Demo Flow Proof.

P9 may start only after every required item below passes.

This document records the pre-P9 gate. It is not a current-state description after P9 source, tests, workflow evidence, and P10 contracts have been added.

## Root Organization

- `harness/architecture/` contains the single final architecture authority.
- `harness/architecture/HarnessEngineering.md` exists as the canonical architecture entry.
- `docs/` exists only as a temporary compatibility stub layer. By P12.4, durable Harness content is routed through `harness/`, `adapter/`, `tools/`, `rag/`, `user/`, `sandbox/`, or `projects/`.
- Long-term layer directories exist for `adapter/`, `adapter/agents/`, `sandbox/`, `harness/skills/`, `rag/knowledge/`, `harness/memory/`, `rag/`, `harness/templates/`, and `var/`.
- Stable scripts are physically under `tools/scripts/stable/`; historical scripts are under `tools/scripts/historical/`; runtime prompt/helper candidates are under `tools/scripts/runtime/`.
- Runtime state is physically under `var/`, including logs, tmp, cache downloads, homes, Maven repositories, Gradle caches, and historical evidence.
- Empty directories may have `.gitkeep`; `.gitkeep` files must stay empty.
- `harness/INDEX.md` and `harness/PLANS.md` route to current locations.

## P9 Project Preparation

- `harness/project-template/model/` contains project registration, instance, template, and P9 entry guidance.
- `harness/templates/project/` contains project profile, project AGENTS, ProjectIndex, workflow README, and validation profile templates.
- `harness/templates/task/` and `harness/templates/workflow/` contain Task Brief and Workflow templates.
- `projects/java-demo` exists as an empty project skeleton with `AGENTS.md`, `docs/project/ProjectIndex.md`, and `docs/project/workflow/`.
- `projects/java-demo` does not yet contain Java source, Maven `pom.xml`, validation report, or workflow evidence.
- `projects/java-smoke-test` is not reused as the formal P9 instance.

## ETCLOVG Readiness

P9 demo must be able to touch every ETCLOVG lens:

| Lens | P9 Evidence |
|---|---|
| Execution | sandbox profile and project-local execution path |
| Tooling | documented Java/Maven command surface |
| Context | project facts, knowledge scopes, and excluded sensitive sources |
| Lifecycle | Task Brief, readiness, plan, execution, validation, acceptance |
| Observability | workflow evidence, command status, log path, failure attribution |
| Verification | Maven validation command and result summary |
| Governance | sensitive boundary, approval posture, promotion candidates |

## RAG Readiness

- `rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml` exists.
- The profile is offline by default.
- `network: disabled`.
- `llmApiRequired: false`.
- Outputs stay in `extracted` or `candidate` state.
- No vector store is selected before P9.

## Non-Goals Before P9

- Do not implement Java/Maven source or tests inside `projects/java-demo` before P9 starts.
- Do not import real business project source.
- Do not import old HarnessVault.
- Do not install RAG tools.
- Do not convert real documents.
- Do not choose a final vector store.
