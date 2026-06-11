# PRD Template

Status: template
Version: v0.1.0-p12.1
Date: 2026-06-10

## Purpose

Capture product requirements, users, scope, non-goals and acceptance context for a managed project or feature.

## Inputs

- user request
- product goals
- stakeholder constraints
- existing project facts
- acceptance criteria

## Outputs

- `projects/<project-id>/docs/project/prd/PRD.md`
- product scope summary
- acceptance criteria
- open questions and risks

## Sensitive Boundary

Do not include customer secrets, credentials, private settings, raw personal data, unredacted logs, private paths or real private repository URLs. Use redacted examples.

## Instantiation Rules

1. Copy this file to `projects/<project-id>/docs/project/prd/PRD.md`.
2. Keep product facts separate from workflow evidence until reviewed.
3. Mark inferred requirements explicitly.
4. Do not turn speculative ideas into accepted project facts without review.

## Product Goal

```text
<product-goal>
```

## Users And Stakeholders

| Role | Need | Notes |
|---|---|---|
| `<role>` | `<need>` | `<notes>` |

## Scope

### In Scope

1. `<in-scope-1>`
2. `<in-scope-2>`
3. `<in-scope-3>`

### Out Of Scope

1. `<out-of-scope-1>`
2. `<out-of-scope-2>`
3. `<out-of-scope-3>`

## Requirements

| ID | Requirement | Priority | Source | Status |
|---|---|---|---|---|
| `<REQ-001>` | `<requirement>` | `<priority>` | `<source>` | `<status>` |

## Acceptance Criteria

| ID | Criteria | Validation |
|---|---|---|
| `<AC-001>` | `<criteria>` | `<validation>` |

## Open Questions

| Question | Owner | Needed By |
|---|---|---|
| `<question>` | `<owner>` | `<phase>` |
