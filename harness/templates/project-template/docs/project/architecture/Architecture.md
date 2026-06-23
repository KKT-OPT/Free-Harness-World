---
documentName: harness/templates/project-template/docs/project/architecture/Architecture.md
version: v0.1.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目架构事实、模块边界和运行时约束模板。
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
  - harness/templates/project-template/docs/project/architecture/Architecture.md
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
# Project Architecture Template（项目架构模板）

## 目的

Capture reviewed architecture facts for a managed project: positioning, boundaries, module responsibilities, runtime shape, constraints and open questions.

## 输入

- Project profile
- source layout facts
- repository facts
- product or domain context
- accepted ADRs

## 输出

- `projects/<project-id>/docs/project/architecture/Architecture.md`
- architecture fact table
- module boundary map
- runtime and integration notes
- architecture risks and open questions

## 敏感边界

Do not include credentials, auth file content, private settings, unredacted logs, private paths, real private repository URLs or production endpoint secrets. Use reviewed aliases or redacted references.

## 实例化规则

1. Copy this file to `projects/<project-id>/docs/project/architecture/Architecture.md`.
2. Replace placeholders only with reviewed project facts.
3. Record unknowns as `unknown` or `to-be-reviewed`.
4. Create or update an ADR for durable architecture decisions.
5. Keep diagrams abstract unless concrete topology has been reviewed.

## Project Information

| Field | Value |
|---|---|
| Project Name | `<project-name>` |
| Project ID | `<project-id>` |
| Architecture Owner | `<owner>` |
| Current Stage | `<stage>` |
| Last Review | `<last-review-date>` |
| Next Review | `<review-after>` |

## Architecture Positioning

```text
<architecture-positioning>
```

## Goals

1. `<architecture-goal-1>`
2. `<architecture-goal-2>`
3. `<architecture-goal-3>`

## System Boundary

### In Scope

1. `<in-scope-1>`
2. `<in-scope-2>`
3. `<in-scope-3>`

### Out Of Scope

1. `<out-of-scope-1>`
2. `<out-of-scope-2>`
3. `<out-of-scope-3>`

## Module Map

| Layer | Module | Responsibility | Fact Source |
|---|---|---|---|
| Entry | `<module>` | `<responsibility>` | `<source>` |
| Domain | `<module>` | `<responsibility>` | `<source>` |
| Data | `<module>` | `<responsibility>` | `<source>` |
| Infrastructure | `<module>` | `<responsibility>` | `<source>` |

## Runtime Shape

```text
<runtime-shape-summary>
```

## Key Flows

| Flow | Trigger | Main Steps | Result | Related Docs |
|---|---|---|---|---|
| `<flow-name>` | `<trigger>` | `<steps>` | `<result>` | `<doc-link>` |

## Constraints

1. `<constraint-1>`
2. `<constraint-2>`
3. `<constraint-3>`

## ADR Links

| ADR | Decision | Status | Date |
|---|---|---|---|
| `<adr-id>` | `<decision>` | `<status>` | `<date>` |

## Open Questions

| Question | Owner | Review Phase |
|---|---|---|
| `<open-question>` | `<owner>` | `<phase>` |
