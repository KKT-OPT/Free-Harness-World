---
documentName: harness/templates/project-template/model/ProjectInstanceModel.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 定义受管项目实例的边界、入口、项目事实和 workflow evidence 位置。
scope:
  - project-instance
  - project-boundary
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/model/StandardProjectPackage.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
outputTo:
  - harness/templates/project-template/model/ProjectInstanceModel.md
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
# Project Instance Model

A managed project instance lives under:

```text
projects/<project-id>/
```

It may be a nested project repository or a local project worktree. It must not mix real project Git history into Harness Root Git.

## 必需入口文件

```text
projects/<project-id>/AGENTS.md
projects/<project-id>/docs/project/ProjectIndex.md
```

`AGENTS.md` stores project-local entry rules and constraints. `ProjectIndex.md` routes project facts.

## Project Facts

Project facts belong under:

```text
projects/<project-id>/docs/project/
```

Project facts include PRD, architecture, dictionary, repository, API, data, test, acceptance and sensitive boundary documents after review.

## Workflow Evidence

Workflow evidence belongs under:

```text
projects/<project-id>/docs/project/workflow/
```

Evidence starts with Task Brief and Harness Run Card, then records readiness, plan, execution, validation, acceptance and governance candidates.

Workflow evidence does not automatically become Project Fact, Knowledge, Memory, Skill or Template.

## Local Registry Boundary

The local registry may route to a project instance, but it must not duplicate project facts or private execution details.
