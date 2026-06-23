---
documentName: harness/templates/project-template/docs/project/prd/PRD.md
version: v0.1.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目需求、范围、非目标和验收上下文模板。
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
  - harness/templates/project-template/docs/project/prd/PRD.md
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
# PRD Template（产品需求模板）

## 目的

Capture product requirements, users, scope, non-goals and acceptance context for a managed project or feature.

## 输入

- user request
- product goals
- stakeholder constraints
- existing project facts
- acceptance criteria

## 输出

- `projects/<project-id>/docs/project/prd/PRD.md`
- product scope summary
- acceptance criteria
- open questions and risks

## 敏感边界

Do not include customer secrets, credentials, private settings, raw personal data, unredacted logs, private paths or real private repository URLs. Use redacted examples.

## 实例化规则

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

## 范围

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

## 验收标准

| ID | Criteria | Validation |
|---|---|---|
| `<AC-001>` | `<criteria>` | `<validation>` |

## Open Questions

| Question | Owner | Needed By |
|---|---|---|
| `<question>` | `<owner>` | `<phase>` |
