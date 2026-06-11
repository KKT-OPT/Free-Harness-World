# Trace Schema

Status: draft
Version: v0.1.0-p10.5
Date: 2026-06-10

## Purpose

This document defines the minimum trace summary that Harness may retain from an agent-managed task.

Harness stores trace summaries, not complete raw traces.

## Trace Metadata

| Field | Rule |
|---|---|
| `traceId` | Stable trace identifier. |
| `taskId` | Workflow task identifier. |
| `runtime` | `codex`, `hermes`, or other. |
| `channel` | `codex`, `cli`, `wecom`, or other. |
| `projectId` | Project id or `none` for root-level Harness tasks. |
| `startedAt` | Start timestamp if known. |
| `endedAt` | End timestamp if known. |
| `status` | `passed`, `failed`, `partial`, or `blocked`. |

## Context Snapshot

Record paths and summaries only:

- entry docs;
- policy docs;
- project docs;
- knowledge scopes;
- memory refs;
- excluded context;
- sensitive handling statement.

Do not record full context windows.

## Operation Events

Each key operation should be summarized as:

```yaml
eventId: <event-id>
eventType: read | write | command | validation | approval | report | handoff
target: <path-or-tool-summary>
intent: <why-the-operation-was-needed>
result: passed | failed | skipped
evidence: <workflow-or-redacted-log-path>
risk: low | medium | high
```

## Tool and Validation Summary

Record:

- stable tools used;
- commands summarized by command surface, not raw shell transcript;
- status JSON path;
- redacted log path;
- validation result;
- failure attribution path when needed.

## Forbidden Content

Trace summaries must not contain:

- credentials, tokens, passwords, auth files or private keys;
- Maven settings contents or private settings paths;
- raw terminal transcripts;
- unredacted logs;
- full model context;
- raw external documents;
- private repository details.

## Promotion Candidates

Trace may identify candidates for:

- Project Fact update;
- Memory update;
- Skill update;
- Knowledge candidate;
- Tool asset improvement;
- Governance fix.

Candidates do not become active assets without review or explicit user approval.
