---
documentName: harness/templates/project-template/docs/project/reports/README.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目实例 reports 目录模板，定义项目级报告证据边界和晋升规则。
scope:
  - project-reports-template
  - report-boundary
prerequisites:
  - projects/<project-id>/AGENTS.md
  - projects/<project-id>/docs/project/ProjectIndex.md
relatedDocuments:
  - harness/templates/project-template/docs/project/ProjectIndex.md
  - harness/templates/project-template/docs/project/workflow/README.md
outputTo:
  - harness/templates/project-template/docs/project/reports/README.md
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
# Project Reports

This directory stores redacted project-level reports after instantiation.

Reports may include:

- validation summaries;
- governance summaries;
- architecture review reports;
- test reports;
- failure analysis summaries.

Reports are evidence, not project facts. A report recommendation becomes a project fact only after review and an explicit update to the target project fact document.

Do not store raw logs, raw terminal transcripts, credentials, auth files, private settings, local absolute paths, private repository URLs or customer data here.
