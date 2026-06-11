# Validation Report Template

Status: template
Version: v0.2.0-p11.5
Date: 2026-06-10

## Summary

State what was validated and whether it passed.

## Scope

List project, files, commands, and validation profile.

## Commands

```text
<command>
```

## Results

```yaml
status: pass | fail | partial
statusJson: <path>
logPath: <path>
traceSummary: <path-or-workflow-section>
resultContract: <path-or-workflow-section>
```

## Failure Attribution

If failed, summarize likely cause and next repair step.

## Findings

List important findings, including partial passes, repaired failures, residual risks, and evidence gaps.

## Recommended Actions

List next actions, review needs, repair tasks, or deferred migration decisions.

## Approval Required

State whether user approval is required before promotion, destructive cleanup, live gateway execution, real project import, or policy/template changes.

## Follow-Up Tasks

List follow-up tasks without treating them as completed work.

## Sensitive Handling

Confirm credentials, private settings, auth files, and unredacted logs were not copied into tracked docs.

Do not paste raw logs, raw status JSON contents, private settings paths, private repository paths, credentials, or auth file contents into this report.
