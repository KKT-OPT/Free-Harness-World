# Project Workflow Directory

Status: template
Version: v0.2.0-p12.1
Date: 2026-06-10

## Purpose

Describe how project task workflow evidence is stored and partitioned.

## Inputs

- Task Brief
- Harness Run Card
- execution plan
- validation outputs
- acceptance decisions
- governance candidates

## Outputs

- workflow evidence file under `docs/project/workflow/`
- trace summary
- validation record
- promotion candidates, if any

## Sensitive Boundary

Do not paste credentials, private settings, auth file content, unredacted logs, private paths or raw terminal transcripts into workflow evidence.

## Instantiation Rules

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

## Required Opening Sections

1. Task Brief
2. Harness Run Card
3. Readiness Check
4. Plan
5. Execution
6. Validation
7. Acceptance
8. Governance Candidates

Workflow evidence is not automatically promoted to Project Facts, Knowledge, Memory or Skill. Promotion requires review or explicit user approval.
