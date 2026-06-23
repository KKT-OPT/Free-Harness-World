---
documentName: FailureAttributionTemplate.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '提供失败、部分成功、阻塞、修复后通过场景的归因和修复记录模板。'
scope:
  - failure-attribution-template
  - repair-evidence
  - governance-candidate-review
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/templates/TemplateIndex.md
  - harness/observability/FailureAttribution.md
outputTo:
  - harness/templates/report/FailureAttributionTemplate.md
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
# Failure Attribution Template（失败归因模板）

## 目的

当 Harness 管理任务失败、部分成功、阻塞、已修复或修复后通过时，使用本模板。

Do not paste raw logs, raw terminal transcripts, status JSON contents, private settings paths, private repository paths, credentials, or auth file contents.

## Failure Summary

| Field | Value |
|---|---|
| failureId | `<failure-id>` |
| taskId | `<task-id>` |
| projectId | `<project-id-or-none>` |
| failedCriterion | `<acceptance-or-validation-criterion>` |
| failureStage | `intake | routing | context | tool | execution | validation | evidence | governance | acceptance` |
| affectedAsset | `<harness-relative-path-or-tool-surface>` |
| errorSummary | `<short-redacted-summary>` |

## 证据

| Evidence Type | Path Or Summary |
|---|---|
| workflowEvidence | `<workflow-evidence-path>` |
| traceSummary | `<trace-summary-section-or-path>` |
| statusJson | `<redacted-status-json-path-or-none>` |
| redactedLog | `<redacted-log-path-or-none>` |
| commandSurface | `<stable-tool-or-none>` |
| relatedPolicy | `<policy-path>` |

## Classification

```yaml
primaryDimension: model | context | tool | execution | lifecycle | verification | governance | project-fact | user-input | external
secondaryDimensions: []
confidence: low | medium | high
reproducible: yes | no | unknown
retryable: yes | no | conditional
```

## Repair Plan

| Field | Value |
|---|---|
| repairAction | `<smallest-safe-repair-or-clarification>` |
| approvalRequired | `yes | no | already-approved` |
| regressionRequired | `<rerun-or-skip-reason>` |
| repairOwner | `agent | user | external | unknown` |

## Regression Result

| Field | Value |
|---|---|
| regressionId | `<regression-id>` |
| regressionType | `document-regression | governance-regression | tool-regression | workflow-regression | security-regression | project-regression | knowledge-regression` |
| result | `passed | failed | partial | skipped | blocked` |
| evidence | `<redacted-evidence-path-or-summary>` |
| remainingRisk | `<risk-or-none>` |

## Closure

```yaml
closureState: open | repaired | accepted-with-risk | deferred | blocked
resultContract: <path-or-section>
nextAction: none | repair-needed | review-needed | clarification-needed | blocked
governanceCandidates: []
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```
