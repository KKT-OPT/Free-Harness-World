---
documentName: TaskBriefTemplate.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '提供 Agent 将用户自然语言任务整理为 Task Brief 的标准模板。'
scope:
  - task-brief-template
  - task-intake
  - workflow-evidence-template
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/templates/TemplateIndex.md
  - adapter/task-intake/TaskIntakeWorkflowModel.md
outputTo:
  - harness/templates/task/TaskBriefTemplate.md
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
# Task Brief Template（任务简报模板）

> Task Brief，中文解释是任务简报。它由 agent 根据用户自然语言提示词生成，不要求用户直接填写。

```yaml
taskId: <generated-task-id>
createdAt: <iso-8601-time>
channel: wecom | codex | hermes-cli | other
runtime: hermes | codex | other
rawPrompt: <原始提示词摘要，不粘贴敏感信息>

projectId:
  value: <project-id-or-unknown>
  source: explicit | inferred | missing
  confidence: low | medium | high

goal:
  value: <任务目标>
  source: explicit | inferred | missing
  confidence: low | medium | high

scope:
  allowedPaths: []
  forbiddenPaths: []
  source: explicit | inferred | missing

acceptanceCriteria:
  items:
    - <验收标准>
  source: explicit | inferred | missing

validationPlan:
  commands:
    - <稳定工具或验证命令>
  source: project-facts | inferred | missing

contextAndKnowledge:
  projectFacts:
    - <project fact ref>
  knowledgeScopes:
    - global | domain:<domain-id> | project-reviewed:<project-id>
  memoryRefs:
    - <memory ref or empty>
  ragIndexes:
    - <index ref or none>
  source: explicit | inferred | missing

provenance:
  sourceDocuments:
    - <path-or-url>
  externalSources:
    - <url-or-none>
  sensitiveSourcesExcluded:
    - <credential/auth/settings/raw-log source excluded>

risk:
  level: low | medium | high
  reasons: []
  boundary: <risk boundary summary>

approvalRequired: true

missingCriticalFields:
  - <缺失字段>

inferredFields:
  - field: <字段名>
    value: <推断值>
    source: <推断依据>
    confidence: low | medium | high

clarification:
  required: true | false
  questions:
    - <需要问用户的问题>

handoff:
  required: true | false
  target: agent | tool | human | runtime | none
  contract:
    intent: <handoff intent>
    constraints: []
    permissions: []
    artifacts: []
    unresolvedDecisions: []
```

## 人类可读摘要

- Goal:
- Project:
- Scope:
- Acceptance:
- Validation:
- Context:
- Risk:
- Clarification required:
