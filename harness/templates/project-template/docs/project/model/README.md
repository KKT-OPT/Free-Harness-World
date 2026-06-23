---
documentName: harness/templates/project-template/docs/project/model/README.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目实例 model 目录模板，记录项目本地模型说明、假设、边界和待审查事项。
scope:
  - project-model-template
  - project-local-assumptions
prerequisites:
  - projects/<project-id>/AGENTS.md
  - projects/<project-id>/docs/project/ProjectIndex.md
relatedDocuments:
  - harness/templates/project-template/docs/project/ProjectIndex.md
  - harness/templates/project-template/docs/project/architecture/Architecture.md
outputTo:
  - harness/templates/project-template/docs/project/model/README.md
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
# Project Model Notes

This directory stores project-local model notes and onboarding assumptions after instantiation.

Use it for:

- project model boundaries;
- onboarding assumptions;
- project-specific conventions that are not broad enough for Harness Memory;
- reviewed model notes referenced by `ProjectIndex.md`.

Do not store credentials, private settings, raw logs, local absolute paths, private repository URLs, workflow transcripts or full reports here.

Workflow evidence belongs in `docs/project/workflow/`. Reports belong in `docs/project/reports/`.
