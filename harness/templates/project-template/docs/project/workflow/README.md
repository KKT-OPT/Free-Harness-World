---
documentName: harness/templates/project-template/docs/project/workflow/README.md
version: v0.2.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目 workflow evidence 目录模板。
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
  - harness/templates/project-template/docs/project/workflow/README.md
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
# Project Workflow Directory

## 目的

Describe how project task workflow evidence is stored and partitioned.

## 输入

- Task Brief
- Harness Run Card
- execution plan
- validation outputs
- acceptance decisions
- governance candidates

## 输出

- workflow evidence file under `docs/project/workflow/`
- trace summary
- validation record
- promotion candidates, if any

## 敏感边界

Do not paste credentials, private settings, auth file content, unredacted logs, private paths or raw terminal transcripts into workflow evidence.

## 实例化规则

1. Copy this file to `projects/<project-id>/docs/project/workflow/README.md`.
2. Use `harness/templates/workflow/WorkflowTemplate.md` for task evidence files.
3. Keep workflow evidence separate from Project Facts until reviewed.
4. Do not create one-off temporary Markdown files for each minor task when a phase-level or project-level workflow evidence file can absorb the record.

## File Naming

Recommended task evidence name:

```text
<task-id>.md
```

Recommended phase evidence name:

```text
<phase-id>-<short-purpose>.md
```

## 必需开场章节

1. Task Brief
2. Harness Run Card
3. Readiness Check
4. Plan
5. Execution
6. Validation
7. Acceptance
8. Governance Candidates

Workflow evidence is not automatically promoted to Project Facts, Knowledge, Memory or Skill. Promotion requires review or explicit user approval.
