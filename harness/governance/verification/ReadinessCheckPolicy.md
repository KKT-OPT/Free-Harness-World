# Readiness Check Policy

Status: draft
Version: v0.1.0-p6
Date: 2026-06-08

## 1. Purpose

Readiness Check，中文解释是就绪检查，用于判断任务是否可以执行，还是必须先向用户澄清。

## 2. Required Checks

| Check | Low Risk | Medium Risk | High Risk |
|---|---|---|---|
| projectId known | recommended | required | required |
| goal known | required | required | required |
| scope known | recommended | required | required |
| acceptance criteria known | recommended | required | required |
| validation plan known | optional | required | required |
| sensitive boundary checked | recommended | required | required |
| approval requirement checked | optional | required | required |

## 3. Must Clarify

The agent must ask the user before high-risk execution when:

- projectId is missing or conflicting;
- goal is missing or ambiguous;
- scope is missing or too broad;
- acceptance criteria are missing;
- validation plan is missing;
- the task touches sensitive boundaries;
- command execution, publishing, deployment, git history, or credential access is involved.

## 4. May Proceed With Recorded Inference

The agent may proceed when:

- risk is low or medium;
- missing fields can be inferred from Project Facts with high confidence;
- the inference source is recorded in Task Brief;
- no hard governance constraint is violated.

## 5. Readiness Result

Use one of:

```text
ready
needs-clarification
blocked-by-policy
blocked-by-missing-project
```
