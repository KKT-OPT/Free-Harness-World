---
documentName: harness/templates/governance/GovernanceCloseoutTemplate.md
version: v1.0.0-pre-h8-governance-template
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 提供任务收口时分类长期候选更新的模板，确保 candidate-first、review-first 和 human approval。
scope:
  - governance-template
  - closeout
  - promotion-candidate
prerequisites:
  - AGENTS.md
  - harness/governance/ArtifactLifecycle.md
relatedDocuments:
  - harness/governance/ArtifactLifecycle.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/governance/MemoryGovernance.md
  - harness/governance/SkillGovernance.md
outputTo:
  - harness/templates/governance/GovernanceCloseoutTemplate.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/governance/ArtifactLifecycle.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-governance-mechanism-aligned
---
# Governance Closeout Template（治理收口模板）

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
