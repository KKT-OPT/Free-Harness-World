---
documentName: CommonTaskResultContract.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '定义 Harness 管理任务的通用用户结果契约、证据边界和运行时返回格式。'
scope:
  - adapter-result-contract
  - workflow-evidence-boundary
  - user-facing-result
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - adapter/AdapterIndex.md
  - harness/observability/ObservabilityIndex.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - adapter/result-contracts/CommonTaskResultContract.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: mixed
  reviewedAt: 2026-06-23
  decision: pre-h8-frontmatter-alignment
---
# Common Task Result Contract（通用任务结果契约）

## 1. Purpose

本文定义 Harness 管理任务对用户返回的通用结果契约。

Codex、Hermes 和未来 Agent Runtime 可以使用不同执行机制，但完成后的任务结果必须能在 Harness 层比较。

Harness 负责维护该契约；Agent Runtime 负责推理、工具调用、会话执行和渠道投递。

## 2. Contract Principles

1. 结果契约是摘要和路由资产，不是原始证据。
2. Workflow Evidence 仍然是任务记录的权威证据。
3. Runtime 日志和 Status JSON 是运行态状态，不得晋升为项目事实。
4. 面向用户的回复必须包含结果、证据路径和下一步动作。
5. 私有 settings、凭据、auth 文件、未脱敏日志和私有仓库路径不得写入结果契约。

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

人类可读回复应使用以下结构：

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

当渠道消息长度受限时，可以使用更短回复，但必须保留结果、Workflow Evidence 和下一步动作。

## 6. Evidence Boundary

结果中允许包含：

- relative Harness paths;
- redacted status/log paths;
- trace summary path or workflow section;
- concise validation result;
- governance candidate types and review action;
- next action.

结果中禁止包含：

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

P11 使用该契约让分阶段框架验证在不同 runtime 之间可比较。

对于分阶段 P11 步骤：

- `status` reports the step result, not full Harness production acceptance;
- `nextAction` should usually be `review-needed` or the next P11 step;
- `traceSummary`, `validationReport`, and `failureAttribution` may point to sections inside the consolidated P11 report or project workflow evidence;
- runtime evidence paths are allowed, but raw status JSON contents and raw logs are not.
