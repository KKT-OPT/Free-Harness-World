# ADR-0001 Template

Status: template
Version: v0.3.0-p12.1
Date: 2026-06-10

## Purpose

Record a durable project decision that affects architecture, governance, validation, user workflow, project facts or long-term maintenance.

## Inputs

- decision context
- considered options
- affected project facts
- validation impact
- governance impact

## Outputs

- `projects/<project-id>/docs/project/decision/ADR-0001.md`
- decision status
- chosen option
- consequences and follow-up actions

## Sensitive Boundary

Do not include credentials, auth file content, private settings, unredacted logs, private paths or real private repository URLs. Link to redacted evidence when needed.

## Instantiation Rules

1. Copy this file to `projects/<project-id>/docs/project/decision/ADR-0001.md`.
2. Rename the file number when creating additional ADRs.
3. Keep one durable decision per ADR.
4. Update related project fact documents after the ADR is accepted.

## Status

```text
proposed | accepted | deprecated | superseded
```

## Decision

Record the project decision in one sentence.

## Context

Explain the project-specific context, constraints and evidence.

## Options Considered

| Option | Pros | Cons | Decision |
|---|---|---|---|
| `<option>` | `<pros>` | `<cons>` | `<result>` |

## Chosen Option

State the chosen option and why it was accepted.

## Consequences

Record expected impact, follow-up tasks and validation needs.

## Impact

List affected project docs, source areas, validation surfaces, tools, governance rules or user workflows.

## Risks

| Risk | Mitigation |
|---|---|
| `<risk>` | `<mitigation>` |

## Follow-Up Actions

| Action | Owner | Due/Phase |
|---|---|---|
| `<action>` | `<owner>` | `<due-or-phase>` |

## Review

| Field | Value |
|---|---|
| owner | `<owner>` |
| reviewedAt | `<reviewed-at>` |
| nextReview | `<next-review>` |
