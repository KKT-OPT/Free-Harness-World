---
documentName: adapter/AdapterIndex.md
version: v1.0.0-pre-h8-structure
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 作为 adapter 层入口，路由任务接入、runtime adapter、gateway、result contract 和 agent profile contract。
scope:
  - adapter
  - task-intake
  - runtime-adapter
  - gateway
  - result-contract
prerequisites:
  - AGENTS.md
  - INDEX.md
relatedDocuments:
  - adapter/task-intake/TaskIntakeWorkflowModel.md
  - adapter/runtime-adapters/codex/CodexRuntimeAdapterFlow.md
  - adapter/runtime-adapters/hermes/HermesRuntimeAdapterFlow.md
  - adapter/gateways/wecom/HermesWeComTaskFlow.md
  - adapter/result-contracts/CommonTaskResultContract.md
outputTo:
  - adapter/AdapterIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-structure-aligned
---
# Adapter 索引

`adapter/` 是用户、gateway 和 Agent Runtime 的交互契约层。它只定义接入模型、runtime flow、gateway flow、结果契约和 agent profile contract，不保存运行态实现、会话记录、auth、settings 或私有配置。

## 1. 当前入口

| 资产 | 路径 | 说明 |
|---|---|---|
| Task Intake | `adapter/task-intake/TaskIntakeWorkflowModel.md` | 自然语言任务到 Task Brief 和 workflow evidence 的接入模型。 |
| Codex Runtime Adapter | `adapter/runtime-adapters/codex/CodexRuntimeAdapterFlow.md` | Codex runtime flow 契约。 |
| Hermes Runtime Adapter | `adapter/runtime-adapters/hermes/HermesRuntimeAdapterFlow.md` | Hermes runtime flow 契约。 |
| WeCom Gateway | `adapter/gateways/wecom/HermesWeComTaskFlow.md` | WeCom 到 Hermes/Codex 的 gateway flow 契约。 |
| Result Contract | `adapter/result-contracts/CommonTaskResultContract.md` | 任务结果返回字段和证据路径契约。 |

## 2. 维护规则

1. Adapter 文档只描述契约，不保存 gateway token、cookie、auth 文件或会话 transcript。
2. 新增 runtime 或 gateway 契约后，必须更新本文和 `INDEX.md` 中的相关任务路由。
3. 任务证据进入项目 workflow evidence 或 redacted report，不进入 adapter 文档。
