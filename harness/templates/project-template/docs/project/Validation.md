---
documentName: harness/templates/project-template/docs/project/Validation.md
version: v0.3.0-formal-project-package
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目验证命令表面和证据规则模板。
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
  - harness/templates/project-template/docs/project/Validation.md
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
# Validation Template（验证模板）

## 目的

Define the stable validation command surfaces, evidence rules and acceptance gates for a managed project.

## 输出

- `projects/<project-id>/docs/project/Validation.md`
- validation profile map
- command-to-evidence mapping
- known validation gaps

## 敏感边界

Validation summaries may be tracked. Raw logs, Maven settings content, auth files, secrets, local machine paths and unredacted terminal output must not be tracked.

## Validation Profiles

| Profile ID | Purpose | Stable Command | Required For |
|---|---|---|---|
| `<validation-profile-id>` | `<purpose>` | `<command-id>` | `<acceptance-stage>` |

## Command Surface

| Scenario | Command ID | Tool | Evidence Location | Pass Criteria |
|---|---|---|---|---|
| Build | `<build-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |
| Unit test | `<unit-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |
| Integration test | `<integration-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |
| Static check | `<static-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |

## 证据 Rules

1. Record command, mode, exit code, timestamp and redacted summary.
2. Store raw logs only under runtime state or ignored project output.
3. Do not paste credentials, settings XML, auth material or private paths.
4. Record skipped checks as gaps, not as success.

## Known Gaps

| Gap | Risk | Mitigation | Review Trigger |
|---|---|---|---|
| `<gap>` | `<risk>` | `<mitigation>` | `<trigger>` |
