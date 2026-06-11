# Acceptance Template

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Record project-level acceptance criteria, review gates and current completion boundaries.

## Outputs

- `projects/<project-id>/docs/project/Acceptance.md`
- acceptance matrix
- review status
- known non-goals and remaining risks

## Acceptance Matrix

| ID | Criterion | Source | Validation | Status |
|---|---|---|---|---|
| `<AC-001>` | `<criterion>` | `<source>` | `<validation>` | `<status>` |

## Review Gates

| Gate | Required Evidence | Reviewer | Status |
|---|---|---|---|
| Readiness | Task Brief and sensitive boundary check | `<reviewer>` | `<status>` |
| Implementation | Scope evidence and changed files | `<reviewer>` | `<status>` |
| Validation | Command summaries and gaps | `<reviewer>` | `<status>` |
| Governance | promotion candidates and exclusions | `<reviewer>` | `<status>` |

## Non-Goals

1. `<non-goal-1>`
2. `<non-goal-2>`
3. `<non-goal-3>`

## Open Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `<risk>` | `<impact>` | `<mitigation>` | `<owner>` |

## Maintenance Rules

1. Acceptance claims must link to validation evidence.
2. Gaps must stay visible until reviewed closed.
3. Do not treat a flow-proof demo as full real-project acceptance.
