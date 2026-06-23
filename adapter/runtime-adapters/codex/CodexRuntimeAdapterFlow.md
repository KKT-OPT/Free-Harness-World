---
documentName: adapter/runtime-adapters/codex/CodexRuntimeAdapterFlow.md
version: v0.1.1-post-p11-cleanup
updatedAt: 2026-06-17 18:30:00.000 +08:00
status: active
purpose: 维护 Codex Runtime Adapter Flow 的长期文档说明、入口边界或目标骨架，供 Harness 路由、治理或后续阶段重构使用。
scope:
  - adapter-contract
  - agent-runtime-routing
  - task-flow
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/PLANS.md
outputTo:
  - adapter/runtime-adapters/codex/CodexRuntimeAdapterFlow.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-17
  decision: frontmatter-aligned
---
# Codex Runtime Adapter Flow

## 1. Purpose

This document defines how Codex consumes Harness Root for managed project automation.

Codex remains an external agent runtime. Harness provides entry rules, routing, task evidence requirements, stable tools, and governance constraints.

## 2. Entry Prompt

When Codex starts a non-simple Harness task, it should orient from:

```text
HARNESS_ROOT = <HARNESS_ROOT>
Read AGENTS.md, INDEX.md, harness/HarnessIndex.md,
harness/architecture/PLANS.md, then read task-relevant Harness docs
and project entry documents.
```

Codex must not require a runtime-specific project fact format. Project identity and validation routing come from Harness project assets.

## 3. Flow

1. Read root entry:
   - `AGENTS.md`
   - `INDEX.md`
   - `harness/HarnessIndex.md`
   - `harness/architecture/PLANS.md`
2. Build a Task Brief from the user's natural-language prompt.
3. Resolve `projectId` from the prompt, registry example, project profile, or project entry.
4. Read project entry:
   - `projects/<project-id>/AGENTS.md`
   - `projects/<project-id>/docs/project/ProjectIndex.md`
5. Create or update workflow evidence under:

```text
projects/<project-id>/docs/project/workflow/<task-id>.md
```

6. Execute through stable Harness tool surfaces when tools are needed.
7. Record validation result with redacted evidence paths.
8. Return the Common Task Result Contract.

## 4. Workflow Evidence Requirements

Codex workflow evidence must include:

- Task Brief;
- Harness Run Card;
- readiness check;
- execution plan;
- execution record;
- validation summary;
- acceptance state;
- governance candidates.

Runtime-specific details may be recorded in the Harness Run Card when useful, but they must not be copied into project facts.

## 5. Stable Tool Use

For Java/Maven validation, Codex should use:

```text
harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
harness/tools/scripts/stable/invoke-maven-project.ps1
harness/tools/scripts/stable/invoke-java-main.ps1
```

Codex must not inline private settings, credential material, or unredacted command output into tracked docs.

## 6. Result Contract

Codex final replies must follow:

```text
adapter/result-contracts/CommonTaskResultContract.md
```

For this runtime, the contract usually sets:

```yaml
runtime: codex
channel: codex
```

## 7. P10 Acceptance Mapping

| P10 Criterion | Codex Flow |
|---|---|
| Codex can use same root entry and project registry | Starts at `AGENTS.md`, `INDEX.md`, `harness/HarnessIndex.md`, `harness/architecture/PLANS.md`, then project entry. |
| Comparable workflow evidence | Writes under `projects/<project-id>/docs/project/workflow/`. |
| User replies include result, evidence paths, next action | Uses Common Task Result Contract. |
| Runtime details do not leak into project facts | Runtime details stay in Run Card/result, not facts. |

## 8. P10 Scope Boundary

P10 defines the Codex adapter flow and contract. It does not prove that the full Harness framework is production-complete.

P11 later completed controlled framework closeout. Remaining production hardening, real-project onboarding, RAG tooling, live gateway validation, stronger isolation and unified CLI work are now tracked through `harness/architecture/PLANS.md`.
