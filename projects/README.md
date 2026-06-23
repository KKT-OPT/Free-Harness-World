---
documentName: projects/README.md
version: v1.0.0-frontmatter-aligned
updatedAt: 2026-06-17 18:30:00.000 +08:00
status: active
purpose: 维护 Project Instances 的长期文档说明、入口边界或目标骨架，供 Harness 路由、治理或后续阶段重构使用。
scope:
  - project-instance-boundary
  - distribution-readme
  - h3
prerequisites:
  - AGENTS.md
relatedDocuments:
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
outputTo:
  - projects/README.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-17
  decision: frontmatter-aligned
---
# Project Instances（项目实例）

`projects/` 是受管项目实例的目标挂载点。

每个真实项目实例应放在：

```text
projects/<project-id>/
```

规则：

- 项目实例是独立 Git 仓库或本地工作区；
- 项目事实位于 `projects/<project-id>/docs/project/`；
- 项目根 `AGENTS.md` 是项目级 Agent 入口；
- 项目 workflow evidence 位于 `projects/<project-id>/docs/project/workflow/`；
- 项目代码和项目 Git 历史不得进入 Harness Distribution Repo。

本文被 Git 跟踪，用于给 Distribution Repo 保留稳定项目挂载点。真实项目目录默认被 Git 忽略。
