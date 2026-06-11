# Memory Template

Status: template
Version: v0.1.0-p11.7
Date: 2026-06-10

## Metadata

```yaml
memoryId: <stable-id>
state: candidate | reviewed | archived
scope: global | domain | project | user | agent-operation
projectId: <project-id-or-null>
sourceEvidence: <workflow-or-report-path>
confidence: low | medium | high
reviewedBy: <human-or-approved-process-or-null>
reviewedAt: <date-or-null>
stalenessRule: <date-or-condition>
```

## Memory Statement

Write the concise reusable memory here.

## Source And Evidence

| Source | Evidence Summary | Notes |
|---|---|---|
| `<path>` | `<summary>` | `<notes>` |

## Applicability

Describe when this memory may be used.

## Non-Applicability

Describe when this memory must not be used, including conflicts with Project Facts, reviewed Knowledge or current user instructions.

## Review Notes

| Check | Result |
|---|---|
| Stable beyond one task | `yes | no | unknown` |
| Future reuse value | `yes | no | unknown` |
| Sensitive content excluded | `yes | no | unknown` |
| Conflict check completed | `yes | no | unknown` |
| Approval recorded | `yes | no | unknown` |

## Promotion Decision

```yaml
decision: approve | reject | defer
targetState: reviewed | archived | candidate
reviewer: <reviewer-or-null>
decisionDate: <date-or-null>
reason: <reason>
```
