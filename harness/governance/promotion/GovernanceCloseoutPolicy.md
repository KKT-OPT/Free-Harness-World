# Governance Closeout Policy

Status: draft
Version: v0.1.0-p11.7
Date: 2026-06-10

## Purpose

This policy defines how Harness closes a task by classifying candidate durable updates without automatically promoting them.

Governance closeout is required for P11 and for later managed tasks that produce reusable decisions, lessons, templates, tools, project facts, Knowledge, Memory, Skill or policy updates.

## Candidate Types

| Type | Meaning | Default Target |
|---|---|---|
| `ProjectFact` | Fact that belongs to one managed project. | `projects/<project-id>/docs/project/` |
| `Knowledge` | Reviewed, citable reusable information. | `rag/knowledge/candidate/` then `rag/knowledge/reviewed/` after approval |
| `Memory` | Scoped operating experience or preference. | `harness/memory/candidate/` then `harness/memory/reviewed/` after approval |
| `Skill` | Reusable workflow for a class of tasks. | `harness/skills/<category>/` or `harness/templates/skill/` after approval |
| `Tool` | Stable command surface, wrapper or documented tool behavior. | `tools/scripts/stable/`, `tools/docs/` |
| `Template` | Reusable task, workflow, report, project, knowledge, skill, memory or governance template. | `harness/templates/` |
| `Governance` | Policy, verification, security, promotion or archive rule. | `harness/governance/` |
| `Architecture` | Change to the final architecture authority. | `harness/architecture/HarnessEngineering.md` |
| `Report` | Redacted evidence or archive disposition. | `harness/reports/` |
| `RAG` | Structured ingestion, corpus, manifest, pipeline or evaluation candidate. | `rag/`, `rag/knowledge/`, `var/rag/` depending on state |

## Disposition States

| Disposition | Meaning |
|---|---|
| `absorbed` | The idea has already been rewritten into a durable current asset during the current task. |
| `candidate` | Worth preserving for review, but not yet promoted. |
| `defer` | Useful, but belongs to a later phase or separate task. |
| `reject` | Not suitable for the new Harness Root. |
| `archive` | Historical value only; not default context. |
| `no-action` | Already covered or not relevant. |
| `needs-user-review` | Requires explicit user judgment before implementation. |

## Required Candidate Record

Every closeout candidate should record:

| Field | Rule |
|---|---|
| `candidateId` | Stable id. |
| `type` | One candidate type. |
| `sourceEvidence` | Workflow/report/asset path; no raw logs. |
| `proposal` | Short proposed durable change. |
| `targetAsset` | Target path or `unknown`. |
| `disposition` | One disposition state. |
| `reason` | Why this disposition was chosen. |
| `approvalRequired` | `yes`, `no`, or `already-approved-for-this-task`. |
| `sensitiveRisk` | `none`, `low`, `medium`, or `high`. |
| `nextAction` | `none`, `review`, `defer`, `repair`, `archive`, or `reject`. |

## Promotion Gate

No candidate may become reviewed Knowledge, reviewed Memory, active Skill, project fact, architecture rule or active governance policy unless:

1. source evidence is recorded;
2. sensitivity check passes;
3. conflict check passes;
4. target asset is correct for the asset class;
5. index or route updates are identified;
6. reviewer or explicit user approval is recorded.

## Forbidden Promotions

Do not directly promote:

- workflow evidence to reviewed Memory, Skill, Knowledge or Project Fact;
- report conclusions to architecture or project facts;
- RAG chunks to reviewed Knowledge;
- runtime logs or status JSON contents to any tracked asset;
- old HarnessVault files by whole-directory copy;
- sensitive settings, credentials, auth files, private repository paths or unredacted logs.

## P11.7 Rule

P11.7 may:

- absorb scoped governance rules needed for the closeout mechanism itself;
- create or update templates that help later review;
- classify P11.0-P11.6 candidates;
- defer project-template hardening, RAG tool installation, real project onboarding and full acceptance to later steps.

P11.7 must not auto-promote operational lessons into active Memory or Skill. It may list them as candidates with review requirements.
