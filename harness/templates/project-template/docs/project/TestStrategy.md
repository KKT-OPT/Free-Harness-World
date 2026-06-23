---
documentName: harness/templates/project-template/docs/project/TestStrategy.md
version: v0.3.0-formal-project-package
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目级测试策略和质量门禁模板。
scope:
  - project-template
  - project-doc-template
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/README.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
outputTo:
  - harness/templates/project-template/docs/project/TestStrategy.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/templates/project-template/README.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: h4-consolidated
---
# Test Strategy Template（测试策略模板）

## 目的

Capture the project-level test strategy that connects PRD acceptance, repository commands, validation profiles and workflow evidence.

## 输出

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
