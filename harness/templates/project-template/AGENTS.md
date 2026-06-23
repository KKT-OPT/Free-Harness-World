---
documentName: harness/templates/project-template/AGENTS.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目根 AGENTS.md 模板，定义每个项目定制化技术栈、全局约束、重要规则和项目级读取顺序。
scope:
  - project-entry-template
  - technical-stack-contract
  - project-hard-constraints
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/docs/project/ProjectIndex.md
  - harness/templates/project-template/docs/project/SensitiveBoundaries.md
  - harness/templates/project-template/docs/project/Validation.md
outputTo:
  - harness/templates/project-template/AGENTS.md
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
# Project Agent Entry

This file is the template for:

```text
projects/<project-id>/AGENTS.md
```

It stores project-level entry rules, technical stack summary, global constraints and important rules. It does not store full project facts, plans, memory, workflow evidence, task history, credentials, private settings or raw logs.

## 1. Project Identity

```yaml
projectId: <project-id>
projectName: <project-name>
projectType: <project-type>
projectRoot: projects/<project-id>
projectIndex: docs/project/ProjectIndex.md
```

Use placeholders until the project owner reviews concrete values.

## 2. Required Read Order

For any non-simple project task, read:

```text
1. <HARNESS_ROOT>/AGENTS.md
2. <HARNESS_ROOT>/INDEX.md
3. <HARNESS_ROOT>/harness/HarnessIndex.md
4. <HARNESS_ROOT>/harness/architecture/PLANS.md
5. projects/<project-id>/AGENTS.md
6. projects/<project-id>/docs/project/ProjectIndex.md
7. Task-relevant project fact documents routed by ProjectIndex.md
```

Root Harness rules remain authoritative when project-local rules conflict with global safety constraints.

## 3. Technical Stack

Record only reviewed stack facts or placeholders:

| Layer | Value | Source | Status |
|---|---|---|---|
| Primary language | `<language>` | `<source>` | `<status>` |
| Runtime | `<runtime>` | `<source>` | `<status>` |
| Build tool | `<build-tool>` | `<source>` | `<status>` |
| Test framework | `<test-framework>` | `<source>` | `<status>` |
| Package manager | `<package-manager>` | `<source>` | `<status>` |
| Deployment target | `<deployment-target>` | `<source>` | `<status>` |

Do not write real local paths, private repository URLs, private Maven settings, auth files or secret endpoint details here.

## 4. Global Project Constraints

1. Keep project facts under `docs/project/`.
2. Keep task workflow evidence under `docs/project/workflow/`.
3. Keep decisions under `docs/project/decision/`.
4. Keep reports under `docs/project/reports/`.
5. Use stable Harness tools when available.
6. Record Task Brief, Harness Run Card, readiness check, execution notes, validation summary and governance candidates in workflow evidence for complex tasks.
7. Do not promote workflow evidence into Project Facts, Knowledge, Memory, Skill or Template without review.

## 5. Important Rules

1. Do not expose credentials, auth files, private settings, unredacted logs, real local paths, concrete account values or private repository URLs.
2. Do not modify external business source outside `projects/<project-id>` unless the user explicitly approves that scope.
3. Do not mix project Git history into Harness Root Git.
4. Do not store temporary phase status, task TODOs or runtime transcript snippets in project `AGENTS.md`.
5. If the task goal, scope, validation, sensitive boundary or target project is unclear, ask for clarification before high-risk work.
6. If a project fact is inferred, mark it as inferred and include its source until reviewed.

## 6. Project Fact Entry

Continue with:

```text
docs/project/ProjectIndex.md
```
