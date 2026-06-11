# Common Task Result Contract

Status: draft
Version: v0.2.0-p11.5
Date: 2026-06-10

## 1. Purpose

This document defines the common user-facing result contract for Harness-managed tasks.

Codex, Hermes, and future agent runtimes may use different execution mechanics, but their completed task result must be comparable at the Harness layer.

Harness owns this contract. Agent runtimes own reasoning, tool invocation, session execution, and channel delivery.

## 2. Contract Principles

1. The result contract is a summary and routing artifact, not raw evidence.
2. Workflow evidence remains the authoritative task record.
3. Runtime logs and status JSON are runtime state and must not be promoted into project facts.
4. User-facing replies must include result, evidence paths, and next action.
5. Private settings, credentials, auth files, unredacted logs, and private repository paths must not be included.

## 3. Required Shape

```yaml
taskId: <task-id>
runtime: codex | hermes | other
channel: codex | wecom | cli | other
projectId: <project-id-or-none>
status: passed | failed | partial | blocked
workflow: projects/<project-id>/docs/project/workflow/<task-id>.md
traceSummary: <workflow-section-or-report-path>
statusJson: var/logs/<redacted-status-file>.json | null
log: var/logs/<redacted-log-file>.log | null
validationReport: <report-path-or-workflow-section>
failureAttribution: <path-or-workflow-section-or-null>
summary: <short-user-facing-summary>
nextAction: none | review-needed | repair-needed | clarification-needed | blocked
governanceCandidates:
  - type: Project Fact | Knowledge | Memory | Skill | Tool | Governance
    action: review | reject | defer
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```

## 4. Field Rules

| Field | Rule |
|---|---|
| `taskId` | Stable identifier for this task evidence. |
| `runtime` | Runtime that executed or coordinated the task. Runtime-specific details stay out of project facts. |
| `channel` | User interaction channel, such as Codex UI, Hermes CLI, or WeCom. |
| `projectId` | Project resolved through Harness routing. Use `none` only for root-level Harness tasks. |
| `status` | Final task state from the Harness perspective. |
| `workflow` | Redacted workflow evidence path. Required for project execution tasks. |
| `traceSummary` | Path or workflow section containing the trace summary. Do not inline raw traces. |
| `statusJson` | Optional redacted runtime status path. Do not inline contents. |
| `log` | Optional redacted runtime log path. Do not inline contents. |
| `validationReport` | Path or workflow/report section containing validation result. |
| `failureAttribution` | Required when the task is failed, partial, repaired, or has residual risk; otherwise `null`. |
| `summary` | One short result statement suitable for the user. |
| `nextAction` | What the user or next runtime should do next. |
| `governanceCandidates` | Candidate long-term asset updates; they are not auto-promoted. |
| `sensitiveHandling` | Explicit proof that restricted material was not included in the result. |

## 5. User-Facing Reply Format

Human-readable replies should use this shape:

```text
Result: <passed|failed|partial|blocked>
Project: <project-id-or-none>
Summary: <short summary>
Workflow: <workflow evidence path>
Trace: <trace summary path or section>
Status: <status JSON path or none>
Log: <redacted log path or none>
Validation: <validation report path or section>
Failure Attribution: <path/section or none>
Next: <next action>
```

Shorter channel-specific replies are allowed when message length is constrained, but they must preserve result, workflow evidence, and next action.

## 6. Evidence Boundary

Allowed in the result:

- relative Harness paths;
- redacted status/log paths;
- trace summary path or workflow section;
- concise validation result;
- governance candidate types and review action;
- next action.

Forbidden in the result:

- Maven settings contents or private settings paths;
- credentials, tokens, auth files, or server usernames;
- unredacted runtime logs;
- raw command output containing local private paths;
- runtime-internal prompts as project facts.

## 7. P10 Acceptance Mapping

| P10 Criterion | Contract Coverage |
|---|---|
| Hermes can be prompted from Harness Root | Hermes adapter must produce this contract. |
| Codex can use same root entry and project registry | Codex adapter must produce this contract. |
| Comparable workflow evidence | `workflow` points to the same project evidence pattern. |
| User replies include result, evidence paths, next action | Required reply shape. |
| Runtime details do not leak into project facts | Runtime fields stay in result/workflow, not project facts. |

## 8. P11 Evidence Mapping

P11 uses this contract to make staged framework validation comparable across runtimes.

For a staged P11 step:

- `status` reports the step result, not full Harness production acceptance;
- `nextAction` should usually be `review-needed` or the next P11 step;
- `traceSummary`, `validationReport`, and `failureAttribution` may point to sections inside the consolidated P11 report or project workflow evidence;
- runtime evidence paths are allowed, but raw status JSON contents and raw logs are not.
