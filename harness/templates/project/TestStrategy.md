# Test Strategy Template

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Capture the project-level test strategy that connects PRD acceptance, repository commands, validation profiles and workflow evidence.

## Outputs

- `projects/<project-id>/docs/project/TestStrategy.md`
- test pyramid or test scope policy
- quality gates
- evidence expectations

## Test Scope

| Scope | Purpose | Required | Command Surface | Evidence |
|---|---|---|---|---|
| Unit | `<purpose>` | `<yes-no>` | `<command-id>` | `<evidence>` |
| Integration | `<purpose>` | `<yes-no>` | `<command-id>` | `<evidence>` |
| E2E | `<purpose>` | `<yes-no>` | `<command-id>` | `<evidence>` |
| Contract | `<purpose>` | `<yes-no>` | `<command-id>` | `<evidence>` |
| Docs | `<purpose>` | `<yes-no>` | `<command-id>` | `<evidence>` |

## Test Data

| Data Type | Source | Sensitivity | Handling |
|---|---|---|---|
| `<data-type>` | `<source>` | `<class>` | `<handling>` |

## Quality Gates

| Gate | Criteria | Blocking | Owner |
|---|---|---|---|
| `<gate>` | `<criteria>` | `<yes-no>` | `<owner>` |

## Maintenance Rules

1. Keep this file aligned with `Validation.md` and `test/Test.md`.
2. Do not track raw production data, secrets, settings content or unredacted logs.
3. Failed tests belong in workflow evidence or redacted reports; durable conclusions can be promoted after review.
