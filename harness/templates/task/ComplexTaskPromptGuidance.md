# Complex Task Prompt Guidance

Status: draft
Version: v0.1.0-p6

## 1. Purpose

本文指导 agent 如何从用户自由提示词生成 Task Brief。

用户不需要按本文格式提问。

## 2. Agent Rules

1. Preserve the user's actual intent.
2. Extract explicit fields first.
3. Infer only when the source is clear and confidence is high.
4. Record every inference and source.
5. Mark missing critical fields.
6. Ask clarification before high-risk execution when required.
7. Do not turn this guidance into a user-facing form.

## 3. Field Extraction Order

```text
projectId
goal
scope
acceptanceCriteria
validationPlan
risk
approvalRequired
```

## 4. Clarification Examples

Ask the user when:

- the target project is unknown;
- the requested change is high-risk but acceptance criteria are missing;
- the prompt asks to edit code but does not say how to validate;
- the task touches secrets, credentials, private settings, publishing, deployment, or git history;
- the inferred scope conflicts with project facts.

## 5. High-Confidence Inference Examples

The agent may infer:

- default validation command from Project Profile;
- source and test directories from Project Facts;
- projectId from an unambiguous project name;
- acceptance criteria from established project validation rules.

The agent must record the inference source.
