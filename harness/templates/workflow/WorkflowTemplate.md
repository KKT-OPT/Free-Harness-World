---
documentName: harness/templates/workflow/WorkflowTemplate.md
version: v0.3.0-project-lifecycle-evidence-gate
updatedAt: 2026-07-02 21:20:00.000 +08:00
status: active
purpose: 维护 Workflow Template 的长期文档说明、入口边界或目标骨架，供 Harness 路由、治理或后续阶段重构使用。
scope:
  - template
  - project-or-workflow-entry
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/PLANS.md
  - harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
outputTo:
  - harness/templates/workflow/WorkflowTemplate.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: h9-3-project-lifecycle-evidence-gate-added
---
# Workflow Template（工作流证据模板）

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
  - path: INDEX.md
    version: <version-or-date>
  - path: harness/HarnessIndex.md
    version: <version-or-date>
  - path: harness/architecture/PLANS.md
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
INDEX.md
harness/HarnessIndex.md
harness/architecture/PLANS.md
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

## 15. Lifecycle Evidence Gate

Before claiming a real project task is closed, run the stable lifecycle evidence gate when applicable:

```text
harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
```

Record the summary:

```yaml
lifecycleEvidenceGate:
  command:
  status:
  workflowEvidence:
  projectReport:
  findings:
```

## 16. Legacy Or Prior Asset Judgment

Record whether previous templates, policies, reports, scripts, or old Harness assets should be rewritten, migrated, archived, deferred, or excluded for this task.
