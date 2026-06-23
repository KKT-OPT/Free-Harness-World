---
documentName: harness/templates/project-template/docs/project/Acceptance.md
version: v0.3.0-formal-project-package
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目验收标准、审查门禁和完成边界模板。
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
  - harness/templates/project-template/docs/project/Acceptance.md
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
# Acceptance Template（验收模板）

## 目的

Record project-level acceptance criteria, review gates and current completion boundaries.

## 输出

- `projects/<project-id>/docs/project/Acceptance.md`
- acceptance matrix
- review status
- known non-goals and remaining risks

## 验收 Matrix

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
