---
documentName: harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md
version: v1.0.0-project-feedback-triage-template
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 提供真实项目任务反向优化通用 Harness 时的候选分类、审批和验证记录模板。
scope:
  - governance-template
  - project-harness-feedback
  - promotion-triage
prerequisites:
  - AGENTS.md
  - harness/governance/ProjectHarnessFeedbackPolicy.md
relatedDocuments:
  - harness/governance/ProjectHarnessFeedbackPolicy.md
  - harness/governance/ArtifactLifecycle.md
  - harness/templates/governance/GovernanceCloseoutTemplate.md
outputTo:
  - harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/governance/ProjectHarnessFeedbackPolicy.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: project-feedback-triage-template-created
---
# Project Harness Feedback Triage Template（项目反向优化 Harness 分类模板）

本模板用于真实项目任务收口时，判断哪些项目经验可以进入通用 Harness，哪些必须留在项目、知识库、本地运行态或不处理。

## 1. Metadata

```yaml
taskId: <task-id>
projectId: <project-id>
projectEvidence:
  - <workflow-evidence-or-report-path>
sourceTaskStatus: accepted | rejected | in-progress | blocked
triageStatus: draft | ready-for-review | approved | rejected | deferred
reviewer:
reviewedAt:
approvalNote:
sensitiveBoundaryChecked: yes | no
```

## 2. Source Evidence

| Source | Type | Boundary | Notes |
|---|---|---|---|
| `<path-or-summary>` | `workflow | report | code | test | user-feedback | knowledge | command` | `project | harness | user-local | runtime` | |

## 3. Feedback Signal Matrix

| signalId | Signal | Source Evidence | Candidate Type | Target Asset | Disposition | Approval Required | Validation Gate | Next Action |
|---|---|---|---|---|---|---|---|---|
| `<id>` | `<summary>` | `<path-or-section>` | `Memory | Skill | Knowledge | ProjectFact | Tool | Template | Governance | Verification | Observability | Architecture | Report | no-action` | `<target-path-or-none>` | `absorbed | candidate | defer | reject | archive | no-action | needs-user-review` | `yes | no | already-approved-for-this-task` | `<command-or-document-gate>` | `<next-step>` |

## 4. Classification Notes

### Workflow To Memory

| Check | Result | Notes |
|---|---|---|
| 通用化、非私有、未来可复用 | `pass | fail | n/a` | |
| 不是项目事实、知识或流程手册 | `pass | fail | n/a` | |
| 已检查重复和冲突 | `pass | fail | n/a` | |
| Memory gate 已运行 | `pass | fail | n/a` | |

### Code To Standards

| Check | Result | Notes |
|---|---|---|
| 已区分项目专属规范和跨项目规范 | `pass | fail | n/a` | |
| 未复制真实项目源码到通用 Harness | `pass | fail | n/a` | |
| 已确定落点：项目文档、模板、Skill、Tool 或 Governance | `pass | fail | n/a` | |
| 已定义验证方式 | `pass | fail | n/a` | |

### Development To Skill Or Tool

| Check | Result | Notes |
|---|---|---|
| 已检查现有 Skill | `pass | fail | n/a` | |
| 流程有 trigger、inputs、procedure、verification、failure handling | `pass | fail | n/a` | |
| 如需要精确执行，已识别 Tool 或 Verification gate | `pass | fail | n/a` | |
| 用户 review 状态明确 | `pass | fail | n/a` | |

### Project Knowledge To Knowledge

| Check | Result | Notes |
|---|---|---|
| 已区分 Project Fact 和 Knowledge | `pass | fail | n/a` | |
| raw source、candidate、reviewed 或 reject/defer 路径明确 | `pass | fail | n/a` | |
| Source Trace 和 reviewAfter 已记录 | `pass | fail | n/a` | |
| 不写入通用 Harness Git | `pass | fail | n/a` | |

### Other Feedback

| Check | Result | Notes |
|---|---|---|
| Tool / Template / Governance / Verification / Observability / Architecture 是否适用 | `pass | fail | n/a` | |
| 需要用户审批的项已单独列出 | `pass | fail | n/a` | |
| deferred 或 rejected 项有明确理由 | `pass | fail | n/a` | |

## 5. Review Decision

| Item | Decision | Reviewer | Date | Notes |
|---|---|---|---|---|
| `<signalId>` | `approve | reject | revise | defer | no-action` | `<reviewer>` | `<date>` | |

## 6. Validation Summary

| Command Or Gate | Result | Evidence |
|---|---|---|
| `test-project-lifecycle-evidence.ps1` | `pass | fail | n/a` | |
| asset-specific gate | `pass | fail | n/a` | |
| `test-harness-governance.ps1` | `pass | fail | n/a` | |
| `git diff --check` | `pass | fail | n/a` | |

## 7. Non-Promotion Statement

```text
Signals listed in this triage record are not promoted until reviewed or explicitly approved.
Project facts, private knowledge, raw logs, credentials, local settings and runtime output are not General Harness assets.
```
