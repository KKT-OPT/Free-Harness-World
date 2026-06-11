# Harness 任务接入与 Workflow 模型

Status: draft
Version: v0.1.0-p6
Date: 2026-06-08

## 1. 文档定位

本文是 P6 阶段交付物，用于定义自然语言任务如何进入 Harness，并如何形成 Task Brief、readiness check 和 workflow evidence。

专业术语说明：

- Task Brief：任务简报。agent 对用户自然语言任务的结构化理解。
- Workflow：工作流。记录任务从理解、计划、执行、验证、验收到治理沉淀的证据链。
- Readiness Check：就绪检查。判断任务是否具备执行条件，以及是否必须先向用户澄清。
- Evidence：证据。包括 Task Brief、执行计划、命令记录、验证结果、失败归因和验收结论。
- Harness Run Card：运行卡。记录一次任务运行的 runtime、入口版本、工具表面、sandbox/approval profile、上下文来源、验证协议和证据路径。
- Handoff Contract：交接合同。记录 agent、tool、human 或 runtime 之间交接任务时携带的意图、约束、权限、证据和未决问题。

本文不执行真实项目任务，不修改项目源码。

## 2. 核心口径

用户提示词是自然语言，不要求用户填写固定模板。

模板是 agent 的语义标尺，不是用户表单。

任务进入 Harness 后，agent 必须生成 Task Brief，并在项目任务的 workflow evidence 开头保存。

workflow evidence 应在 Task Brief 后记录 Harness Run Card，用于披露本次任务运行的 Harness 配置。

高风险任务在关键字段缺失、冲突或低置信时必须先澄清。

## 3. P6 交付物

| 交付物 | 路径 | 用途 |
|---|---|---|
| Task Brief 模板 | `harness/templates/task/TaskBriefTemplate.md` | 记录 agent 对任务的结构化理解 |
| Workflow 模板 | `harness/templates/workflow/WorkflowTemplate.md` | 保存 Task Brief、计划、执行、验证、验收和治理候选 |
| 复杂任务提示词指导 | `harness/templates/task/ComplexTaskPromptGuidance.md` | 指导 agent 从自由提示词生成 Task Brief |
| Readiness policy | `harness/governance/verification/ReadinessCheckPolicy.md` | 定义澄清规则和执行前门槛 |

## 4. Task Brief 字段

Task Brief 最少包含：

```yaml
taskId: <generated-task-id>
rawPrompt: <原始提示词摘要>
channel: wecom | codex | hermes-cli | other
runtime: hermes | codex | other
projectId:
  value: <project-id-or-unknown>
  source: explicit | inferred | missing
goal:
  value: <任务目标>
  source: explicit | inferred | missing
scope:
  allowedPaths: []
  forbiddenPaths: []
acceptanceCriteria:
  items: []
  source: explicit | inferred | missing
validationPlan:
  commands: []
  source: project-facts | inferred | missing
contextAndKnowledge:
  projectFacts: []
  knowledgeScopes: []
  memoryRefs: []
  ragIndexes: []
provenance:
  sourceDocuments: []
  externalSources: []
  sensitiveSourcesExcluded: []
risk:
  level: low | medium | high
  reasons: []
  boundary: <risk boundary summary>
approvalRequired: true | false
missingCriticalFields: []
inferredFields:
  - field: <字段名>
    value: <推断值>
    source: <依据文档或用户提示词>
    confidence: low | medium | high
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

## 5. 字段来源规则

| 来源 | 中文解释 | 可用于 |
|---|---|---|
| `explicit` | 用户明确说出 | goal、projectId、scope、acceptanceCriteria |
| `inferred` | agent 从项目事实或上下文推断 | projectId、validationPlan、scope |
| `project-facts` | 来自项目事实 | validationPlan、source layout、test strategy |
| `missing` | 缺失 | 触发 readiness check |

推断字段必须记录：

- 推断值；
- 来源；
- 置信度；
- 如果推断错误，如何修复。

上下文、知识和交接字段必须记录：

- Project Facts 来源；
- Knowledge scope；
- Memory 引用；
- RAG index 引用，如果没有则显式记为 none；
- 被排除的敏感来源，例如 credential、auth、private settings 或未脱敏 raw log；
- Handoff Contract，如果任务需要跨 agent、tool、human 或 runtime 交接。

## 6. 高风险任务

高风险任务包括：

- 修改源码；
- 修改测试；
- 执行会改变项目状态的命令；
- 变更项目事实；
- 变更治理规则；
- 访问敏感边界；
- 发布、部署、推送或修改 git 历史。

高风险任务如果缺少以下字段，必须先澄清：

- `projectId`；
- `goal`；
- `scope`；
- `acceptanceCriteria`；
- `validationPlan`；
- `risk boundary`，中文解释是风险边界；
- 用户是否允许写文件或执行命令。

## 7. Workflow Evidence 要求

项目任务的 workflow evidence 必须从 Task Brief 开始。

推荐路径：

```text
projects/<project-id>/docs/project/workflow/<taskId>.md
```

在项目 workflow 模型尚未落地前，可以先把模板作为规范，不创建实际 workflow 文件。

Workflow 必须记录：

1. Task Brief；
2. Harness Run Card；
3. Readiness Check；
4. 执行计划；
5. 文件变更摘要；
6. 工具调用记录；
7. 验证结果；
8. 失败归因；
9. 用户验收；
10. 治理沉淀候选。

## 8. P6 完成标准自检

P6 原完成标准：

```text
1. Accept a natural-language prompt without requiring the user to fill a form.
2. Extract explicit fields.
3. Infer fields from project facts when confidence is high.
4. Mark missing critical fields.
5. Ask for clarification before high-risk execution.
6. Save Task Brief at the start of workflow evidence.
7. Record inferred fields and their sources.
```

自检结果：

| 检查项 | 结果 | 证据 |
|---|---|---|
| 接受自然语言提示词，不要求用户填表 | pass | 第 2 节、`harness/templates/task/ComplexTaskPromptGuidance.md` |
| 能提取显式字段 | pass | 第 4、5 节、Task Brief 模板 |
| 可从项目事实高置信推断字段 | pass | 第 5 节、Readiness policy |
| 可标记缺失关键字段 | pass | 第 4、6 节、Task Brief 模板 |
| 高风险执行前必须澄清 | pass | 第 6 节、Readiness policy |
| Task Brief 保存到 workflow evidence 开头 | pass | 第 7 节、Workflow 模板 |
| 推断字段记录来源 | pass | 第 4、5 节、Task Brief 模板 |

P6 当前结论：

```text
P6 draft deliverable is complete for review.
No real project workflow has been created.
No project source has been modified.
```
