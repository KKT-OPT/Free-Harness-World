# Validation Template

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Define the stable validation command surfaces, evidence rules and acceptance gates for a managed project.

## Outputs

- `projects/<project-id>/docs/project/Validation.md`
- validation profile map
- command-to-evidence mapping
- known validation gaps

## Sensitive Boundary

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

## Evidence Rules

1. Record command, mode, exit code, timestamp and redacted summary.
2. Store raw logs only under runtime state or ignored project output.
3. Do not paste credentials, settings XML, auth material or private paths.
4. Record skipped checks as gaps, not as success.

## Known Gaps

| Gap | Risk | Mitigation | Review Trigger |
|---|---|---|---|
| `<gap>` | `<risk>` | `<mitigation>` | `<trigger>` |
