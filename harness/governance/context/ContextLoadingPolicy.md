# Context Loading Policy

Status: draft
Version: v0.1.0-p10.5
Date: 2026-06-10

## Purpose

This policy defines how agents load context under Harness.

The goal is minimum sufficient context with provenance, not bulk loading.

## Priority Order

```text
current user instruction
> AGENTS.md hard constraints
> harness/INDEX.md and harness/PLANS.md
> task-specific policy/template/skill
> Project Facts
> approved Skill
> reviewed Knowledge
> reviewed or relevant Memory
> workflow evidence
> active redacted reports
> archived reports only when explicitly requested
```

Current user instructions cannot override security, privacy, approval, git boundary, credential, or governance hard stops.

## Required Provenance

Task Brief and workflow evidence should record:

- source documents read;
- inferred fields and source;
- confidence for important inferred fields;
- excluded sensitive sources;
- stale or uncertain context.

## Default Exclusions

Do not load by default:

- `var/**`;
- raw logs and raw terminal transcripts;
- private settings, auth files, credentials;
- RAG indexes, embeddings and caches;
- archived reports;
- old HarnessVault raw reports;
- editor/runtime artifacts;
- generated build outputs.

## RAG Boundary

RAG index results are retrieval hints. They are not facts unless grounded in reviewed Knowledge, Project Facts, or approved metadata.

## P11 Rule

P11 E2E evidence must state which context was loaded and which sensitive/runtime contexts were excluded.
