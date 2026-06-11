# Test Template

Status: template
Version: v0.1.0-p12.1
Date: 2026-06-10

## Purpose

Capture the project testing strategy, quality gates, validation commands, evidence rules and known gaps.

## Inputs

- validation profile
- repository command surfaces
- acceptance criteria
- architecture and risk facts
- previous workflow evidence

## Outputs

- `projects/<project-id>/docs/project/test/Test.md`
- test scope matrix
- command and evidence map
- quality gates and known gaps

## Sensitive Boundary

Do not include credentials, auth file content, private settings, unredacted logs, private paths, real private repository URLs or raw production data in test evidence.

## Instantiation Rules

1. Copy this file to `projects/<project-id>/docs/project/test/Test.md`.
2. Prefer stable Harness command surfaces over ad hoc commands.
3. Keep raw reports outside tracked docs unless redacted.
4. Record validation gaps explicitly rather than claiming full coverage.

## Test Scope

| Scope | Purpose | Command Surface | Required For Acceptance |
|---|---|---|---|
| unit | `<purpose>` | `<command-id>` | `<yes-no>` |
| integration | `<purpose>` | `<command-id>` | `<yes-no>` |
| e2e | `<purpose>` | `<command-id>` | `<yes-no>` |
| docs | `<purpose>` | `<command-id>` | `<yes-no>` |

## Quality Gates

| Gate | Criteria | Evidence |
|---|---|---|
| `<gate>` | `<criteria>` | `<evidence>` |

## Known Gaps

| Gap | Risk | Mitigation | Owner |
|---|---|---|---|
| `<gap>` | `<risk>` | `<mitigation>` | `<owner>` |

## Evidence Rules

1. Summaries may enter workflow evidence.
2. Raw logs must be redacted before tracked docs.
3. Generated outputs are not Project Facts unless reviewed.
