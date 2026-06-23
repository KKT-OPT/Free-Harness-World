---
documentName: harness/verification/ReadinessCheckPolicy.md
version: v1.0.0-h7-verification-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 定义 Harness 任务执行前的 readiness check 规则，判断任务是否可以执行、需要澄清或被策略阻断。
scope:
  - verification
  - readiness-check
  - task-intake
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/verification/VerificationIndex.md
relatedDocuments:
  - adapter/task-intake/TaskIntakeWorkflowModel.md
  - harness/templates/task/TaskBriefTemplate.md
  - harness/observability/TraceSchema.md
outputTo:
  - harness/verification/ReadinessCheckPolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/verification/VerificationIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Readiness Check Policy（就绪检查策略）

Readiness Check，中文解释是就绪检查，用于判断任务是否可以执行，还是必须先向用户澄清或因治理策略阻断。

## 1. 必检项

| 检查项 | Low Risk | Medium Risk | High Risk |
|---|---|---|---|
| projectId known | recommended | required | required |
| goal known | required | required | required |
| scope known | recommended | required | required |
| acceptance criteria known | recommended | required | required |
| validation plan known | optional | required | required |
| sensitive boundary checked | recommended | required | required |
| approval requirement checked | optional | required | required |

## 2. 必须澄清的情况

高风险执行前，如果出现以下情况，Agent 必须先向用户澄清：

- projectId is missing or conflicting;
- goal is missing or ambiguous;
- scope is missing or too broad;
- acceptance criteria are missing;
- validation plan is missing;
- the task touches sensitive boundaries;
- command execution, publishing, deployment, git history, or credential access is involved.

## 3. 可以带推断继续的情况

满足以下条件时，Agent 可以记录推断后继续：

- risk is low or medium;
- missing fields can be inferred from Project Facts with high confidence;
- the inference source is recorded in Task Brief;
- no hard governance constraint is violated.

## 4. Readiness Result

结果必须使用以下值之一：

```text
ready
needs-clarification
blocked-by-policy
blocked-by-missing-project
```

## 5. 输出位置

Readiness 结果应进入 Task Brief、workflow evidence 或验证报告摘要。不得把 raw logs、完整终端 transcript、私有 settings、auth 文件或未脱敏路径写入受 Git 管控文档。
