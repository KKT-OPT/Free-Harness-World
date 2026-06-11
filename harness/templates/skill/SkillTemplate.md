# Skill Template

Status: template
Version: v0.1.0-p11.7
Date: 2026-06-10

## Metadata

```yaml
skillId: skill.<category>.<name>
state: candidate | reviewed | archived
category: <category>
sourceEvidence: <workflow-or-report-path>
owner: <human-or-team>
reviewedAt: <date-or-null>
reviewAfter: <date-or-condition>
```

## Description

Write a trigger-oriented description of what this skill helps an agent do.

## When To Use

- `<trigger-condition>`
- `<trigger-condition>`

## Inputs

| Input | Required | Notes |
|---|---|---|
| `<input>` | `yes | no` | `<notes>` |

## Procedure

1. `<step>`
2. `<step>`
3. `<step>`

## Preferred Stable Tools

| Tool | Use |
|---|---|
| `<tool-or-none>` | `<use>` |

## Evidence Outputs

- `<workflow-evidence>`
- `<report-or-result-contract>`

## Verification

- `<acceptance-check>`
- `<regression-check-if-needed>`

## Pitfalls

- `<pitfall>`
- `<pitfall>`

## Governance

| Check | Rule |
|---|---|
| One-session content excluded | yes |
| Project facts excluded unless project-scoped | yes |
| Knowledge facts excluded | yes |
| Sensitive content excluded | yes |
| Promotion requires review | yes |

## Related Documents

- `<path>`
