# Workflow Template

Status: template
Version: v0.2.0-p11.5
Date: 2026-06-10

> Workflow，中文解释是工作流证据。项目任务必须把 Task Brief 放在开头。

## 1. Task Brief

Paste or embed the completed Task Brief here.

## 2. Metadata

| Field | Value |
|---|---|
| taskId |  |
| projectId |  |
| stage |  |
| runtime |  |
| channel |  |
| status | draft |
| owner | human |
| startedAt |  |
| endedAt |  |

## 3. Harness Run Card

> Harness Run Card，中文解释是运行卡。用于披露本次任务运行的 Harness 配置，避免把模型能力、工具能力、上下文和治理策略混在一起评价。

```yaml
runtime:
  name: hermes | codex | other
  version: <optional>
channel: wecom | codex | hermes-cli | other
entryDocuments:
  - path: AGENTS.md
    version: <version-or-date>
  - path: harness/INDEX.md
    version: <version-or-date>
  - path: harness/PLANS.md
    version: <version-or-date>
project:
  projectId: <project-id-or-unknown>
  profile: <profile-ref-or-missing>
sandbox:
  profile: <local | docker | vm | remote | unknown>
  approvalMode: <approval-profile>
tools:
  commandSurfaces: []
  stableToolAssets: []
context:
  projectFacts: []
  knowledgeScopes: []
  memoryRefs: []
  ragIndexes: []
validation:
  profile: <validation-profile>
  expectedEvidence: []
sensitiveHandling:
  credentialsRead: false
  privateSettingsRead: false
  rawLogsTracked: false
```

## 4. Context Loaded And Excluded

Loaded context:

```text
AGENTS.md
harness/INDEX.md
harness/PLANS.md
```

Excluded context:

```text
var/**
raw logs
private settings
auth files
credentials
RAG indexes
archived reports unless explicitly requested
```

## 5. Readiness Check

| Check | Result | Evidence |
|---|---|---|
| projectId known | pass/fail |  |
| goal known | pass/fail |  |
| scope known | pass/fail |  |
| acceptance criteria known | pass/fail |  |
| validation plan known | pass/fail |  |
| sensitive boundary checked | pass/fail |  |
| approval requirement checked | pass/fail |  |
| handoff/provenance checked | pass/fail |  |

Clarification required:

```text
yes | no
```

## 6. Execution Plan

- Files or modules likely to change:
- Skill used:
- Tool Assets used:
- Validation commands:
- Expected evidence:
- Repair path if validation fails:
- Handoff contract if delegating to another agent/tool/human:

## 7. Execution Record

| Step | Action | Evidence |
|---|---|---|
| 1 |  |  |

## 8. File Change Summary

| File | Change | Reason |
|---|---|---|
|  |  |  |

## 9. Tool Invocation Evidence

| Tool | Command Surface | Status JSON | Log Path | Result |
|---|---|---|---|---|
|  |  |  |  |  |

## 10. Trace Summary

| Field | Value |
|---|---|
| traceId |  |
| taskId |  |
| runtime |  |
| channel |  |
| projectId |  |
| status | passed / failed / partial / blocked |
| entryDocs |  |
| projectDocs |  |
| policyDocs |  |
| toolsUsed |  |
| validationResult |  |
| sensitiveHandling | raw logs/settings/auth/credentials excluded |

Operation events:

| Event | Type | Target | Result | Evidence |
|---|---|---|---|---|
|  | read/write/command/validation/report |  | passed/failed/skipped |  |

## 11. Verification Report

- Result: passed | failed | partial | blocked
- Acceptance criteria checked:
- Failed criteria:
- Failure attribution:
- Remaining risk:

## 12. Common Task Result Contract

```yaml
taskId:
runtime:
channel:
projectId:
status:
workflow:
traceSummary:
statusJson:
log:
validationReport:
failureAttribution:
summary:
nextAction:
governanceCandidates: []
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```

## 13. User Acceptance

- Accepted: yes | no | pending
- User feedback:
- Repair task needed:

## 14. Governance Candidates

| Candidate Type | Candidate | Action |
|---|---|---|
| Project Fact |  | review / reject / defer |
| Memory |  | review / reject / defer |
| Skill |  | review / reject / defer |
| Knowledge |  | review / reject / defer |
| Tool Asset |  | review / reject / defer |
| Governance |  | review / reject / defer |

## 15. Legacy Or Prior Asset Judgment

Record whether previous templates, policies, reports, scripts, or old Harness assets should be rewritten, migrated, archived, deferred, or excluded for this task.
