---
documentName: harness/templates/project-template/docs/project/test/Test.md
version: v0.1.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目测试范围、质量门禁和证据策略模板。
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
  - harness/templates/project-template/docs/project/test/Test.md
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
# Test Template（测试模板）

## 目的

Capture the project testing strategy, quality gates, validation commands, evidence rules and known gaps.

## 输入

- validation profile
- repository command surfaces
- acceptance criteria
- architecture and risk facts
- previous workflow evidence

## 输出

- `projects/<project-id>/docs/project/test/Test.md`
- test scope matrix
- command and evidence map
- quality gates and known gaps

## 敏感边界

Do not include credentials, auth file content, private settings, unredacted logs, private paths, real private repository URLs or raw production data in test evidence.

## 实例化规则

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

## 证据 Rules

1. Summaries may enter workflow evidence.
2. Raw logs must be redacted before tracked docs.
3. Generated outputs are not Project Facts unless reviewed.
