---
documentName: harness/verification/HarnessValidationPlan.md
version: v1.2.0-memory-governance-self-check
updatedAt: 2026-07-02 21:20:00.000 +08:00
status: active
purpose: 定义 Harness 生命周期验证计划，覆盖入口、任务接入、上下文、项目路由、工具、观测、验证、修复闭环、治理收口和 Memory store 门禁。
scope:
  - verification
  - validation-plan
  - harness-lifecycle
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/verification/VerificationIndex.md
relatedDocuments:
  - harness/verification/ReadinessCheckPolicy.md
  - harness/verification/RegressionPolicy.md
  - harness/verification/HarnessValidationCases.md
  - harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
  - harness/tools/scripts/stable/invoke-memory.ps1
  - harness/observability/TraceSchema.md
  - harness/observability/FailureAttribution.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/verification/HarnessValidationPlan.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/verification/VerificationIndex.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: memory-governance-self-check-added
---
# Harness 验证计划

本文定义 Harness 生命周期验证计划。它验证 Agent 是否能从任务接入走到可审查结果和治理收口，而不是只验证某一个项目或某一种技术栈。

## 1. 验证原则

1. Start from `AGENTS.md`, `INDEX.md`, `harness/HarnessIndex.md`, and `harness/architecture/PLANS.md`.
2. Use a controlled project under `projects/<project-id>`.
3. Use stable tool surfaces.
4. Produce workflow evidence.
5. Produce trace summary.
6. Produce validation report.
7. Produce failure attribution if anything fails.
8. Rerun or explicitly skip required regression after repair.
9. Return Common Task Result Contract.
10. Do not auto-promote candidates.
11. Do not expose credentials, settings, auth files or raw logs.
12. Classify governance candidates with disposition, target and approval requirement.
13. For real project lifecycle closeout, run `harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1` against the project workflow evidence and project report when a report is required.
14. For Harness governance self-check, run Memory store validation and Memory store self-test through `harness/tools/scripts/stable/invoke-memory.ps1`.

## 2. 验证范围

| Area | Question |
|---|---|
| Entry | Can an agent discover Harness Root and current plans? |
| Task Intake | Can a natural prompt become a Task Brief? |
| Readiness | Are missing or risky fields handled? |
| Context | Is context loaded with provenance and exclusions? |
| Project Routing | Does `projectId` resolve to a managed project? |
| Tooling | Are stable tools used instead of ad hoc command chains? |
| Observability | Is a trace summary produced? |
| Verification | Is validation repeatable and summarized? |
| Repair Loop | Are failed, partial or repaired results attributed and regressed before closure? |
| Reports | Is the result report-first and redacted? |
| Governance | Are candidates listed without auto-promotion? |
| Lifecycle Evidence Gate | Can a stable script verify task brief, project entry, design, development, validation, report, review and acceptance evidence? |
| Memory Gate | Can governance self-check verify current Memory store shape and Memory negative fixtures? |
| Closeout | Are candidate dispositions, approval requirements and deferred backlog clear? |

## 3. 输出位置

验证报告应进入：

```text
harness/reports/redacted/
```

项目 workflow evidence 应进入：

```text
projects/<project-id>/docs/project/workflow/
```

## 4. 失败处理

任何 failed、partial、blocked 或 repaired criterion 都必须关联：

```text
harness/observability/FailureAttribution.md
harness/verification/RegressionPolicy.md
```

并定义最小安全修复路径。

## 5. 修复关闭

任何 repaired result 必须记录：

- the original failed criterion;
- the attribution dimension;
- the repair action;
- the regression or explicit skip reason;
- residual risk;
- Common Task Result Contract output.

A repaired result may be marked `passed` only after the required regression passes or the skip reason is reviewed and recorded.
