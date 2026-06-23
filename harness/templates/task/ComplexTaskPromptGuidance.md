---
documentName: ComplexTaskPromptGuidance.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '指导 Agent 从复杂自由提示词中提取目标、范围、验收、验证、风险和澄清项。'
scope:
  - complex-task-intake
  - task-brief-generation
  - clarification-rules
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/templates/task/TaskBriefTemplate.md
  - adapter/task-intake/TaskIntakeWorkflowModel.md
outputTo:
  - harness/templates/task/ComplexTaskPromptGuidance.md
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
# Complex Task Prompt Guidance（复杂任务提示词整理指南）

## 1. Purpose

本文指导 agent 如何从用户自由提示词生成 Task Brief。

用户不需要按本文格式提问。

## 2. Agent Rules

1. 保留用户真实意图。
2. 优先提取明确字段。
3. 只有来源清晰且置信度高时才进行推断。
4. 记录每一项推断及其来源。
5. 标记缺失的关键字段。
6. 高风险执行前如有必要必须先澄清。
7. 不要把本指南变成要求用户填写的表单。

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

以下情况需要向用户澄清：

- the target project is unknown;
- the requested change is high-risk but acceptance criteria are missing;
- the prompt asks to edit code but does not say how to validate;
- the task touches secrets, credentials, private settings, publishing, deployment, or git history;
- the inferred scope conflicts with project facts.

## 5. High-Confidence Inference Examples

Agent 可以推断：

- default validation command from Project Profile;
- source and test directories from Project Facts;
- projectId from an unambiguous project name;
- acceptance criteria from established project validation rules.

Agent 必须记录推断来源。
