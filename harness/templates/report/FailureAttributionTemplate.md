# Failure Attribution Template

Status: template
Version: v0.2.0-p11.6
Date: 2026-06-10

## Purpose

Use this template when a Harness-managed task is failed, partial, blocked, repaired, or passed after repair.

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

## Evidence

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
