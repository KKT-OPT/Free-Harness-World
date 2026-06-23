---
documentName: harness/observability/TraceSchema.md
version: v1.0.0-h7-observability-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 定义 Harness 可保留的 trace summary 最小结构，确保任务过程可观测、可审查且不泄露敏感运行态内容。
scope:
  - observability
  - trace-summary
  - workflow-evidence
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/observability/ObservabilityIndex.md
relatedDocuments:
  - harness/observability/FailureAttribution.md
  - harness/verification/VerificationIndex.md
  - harness/templates/workflow/WorkflowTemplate.md
outputTo:
  - harness/observability/TraceSchema.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/observability/ObservabilityIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Trace Schema

Trace Summary，中文解释是执行轨迹摘要，是 Harness 可以保留的任务过程观测结构。Harness 保存摘要、路径和判定结果，不保存完整 raw trace。

## 1. Trace Metadata

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

## 2. Context Snapshot

只记录路径和摘要：

- entry docs;
- policy docs;
- project docs;
- knowledge scopes;
- memory refs;
- excluded context;
- sensitive handling statement.

不得记录完整 context window。

## 3. Operation Events

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

## 4. Tool and Validation Summary

Record:

- stable tools used;
- commands summarized by command surface, not raw shell transcript;
- status JSON path;
- redacted log path;
- validation result;
- failure attribution path when needed.

## 5. Workflow Evidence Hooks

复杂任务的 workflow evidence 至少应能看到：

- Task Brief；
- Harness Run Card；
- stable tool command surface；
- status JSON path；
- redacted log path；
- validation summary；
- failure attribution if validation fails；
- sensitive handling statement。

Harness 不要求每个任务都有专用 tracing backend，但要求证据路径、验证状态和敏感边界可被安全摘要。

## 6. Forbidden Content

Trace summaries must not contain:

- credentials, tokens, passwords, auth files or private keys;
- Maven settings contents or private settings paths;
- raw terminal transcripts;
- unredacted logs;
- full model context;
- raw external documents;
- private repository details.

## 7. Promotion Candidates

Trace may identify candidates for:

- Project Fact update;
- Memory update;
- Skill update;
- Knowledge candidate;
- Tool asset improvement;
- Governance fix.

Candidates do not become active assets without review or explicit user approval.
