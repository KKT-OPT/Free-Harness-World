# Governance Closeout Template

Status: template
Version: v0.1.0-p11.7
Date: 2026-06-10

## Purpose

Use this template at task closeout to classify durable update candidates without auto-promoting them.

## Closeout Metadata

```yaml
taskId: <task-id>
projectId: <project-id-or-none>
runtime: codex | hermes | other
workflowEvidence: <path>
report: <path-or-none>
resultContract: <path-or-section>
closeoutStatus: draft | ready-for-review | accepted | deferred
```

## Candidate Table

| candidateId | type | proposal | sourceEvidence | targetAsset | disposition | approvalRequired | nextAction |
|---|---|---|---|---|---|---|---|
| `<id>` | `ProjectFact | Knowledge | Memory | Skill | Tool | Template | Governance | Architecture | Report | RAG` | `<summary>` | `<path>` | `<target>` | `absorbed | candidate | defer | reject | archive | no-action | needs-user-review` | `yes | no | already-approved-for-this-task` | `<action>` |

## Review Checks

| Check | Result | Notes |
|---|---|---|
| Source evidence recorded | `pass | fail | n/a` | |
| Sensitive boundary checked | `pass | fail | n/a` | |
| Target asset class is correct | `pass | fail | n/a` | |
| Conflict check completed | `pass | fail | n/a` | |
| Index or route update identified | `pass | fail | n/a` | |
| Approval requirement recorded | `pass | fail | n/a` | |

## Non-Promotion Statement

```text
Candidates listed here are not promoted until review or explicit user approval.
```

## Follow-Up Backlog

| Item | Owner | Timing | Notes |
|---|---|---|---|
| `<item>` | `<owner>` | `<phase-or-date>` | `<notes>` |
