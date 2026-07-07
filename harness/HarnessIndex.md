---
documentName: harness/HarnessIndex.md
version: v1.4.0-project-feedback-policy
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 通用 Harness 资产分层索引，路由到架构、治理、模板、技能、记忆、RAG 机制、工具、验证、观测和报告，并记录 Memory governance gate 与项目反向优化 Harness 治理入口。
scope:
  - harness-document
prerequisites:
  - AGENTS.md
relatedDocuments:
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
  - harness/governance/ProjectHarnessFeedbackPolicy.md
  - harness/reports/ReportsIndex.md
  - harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md
  - harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
  - harness/tools/scripts/stable/invoke-memory.ps1
  - harness/skills/reviewed/memory-governance-use/SKILL.md
outputTo:
  - harness/HarnessIndex.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: project-feedback-policy-routed
---
# General Harness 索引

本文是 `harness/` 下 General Harness 资产的分层索引。全局入口是根目录 `INDEX.md`；本文不记录项目事实，不替代项目 `ProjectIndex.md`。

## 1. 权威入口

| 资产 | 目标路径 | 当前路由 |
|---|---|---|
| Architecture | `harness/architecture/HarnessEngineering.md` | 已落地。 |
| Architecture Plans | `harness/architecture/PLANS.md` | 已落地。 |
| Bootstrap | `harness/bootstrap/BootstrapIndex.md` | H8 已落地；负责 workspace 初始化、bootstrap foundation 和 agent-git GitHub 管理恢复入口。 |
| Governance | `harness/governance/GovernanceIndex.md` | 已落地；负责 artifact lifecycle、project feedback、review、promotion、archive、cleanup 和 approval boundary。 |
| Verification | `harness/verification/VerificationIndex.md` | H7 已落地；readiness、validation、regression 和 Harness validation cases 位于目标 verification 层。 |
| Observability | `harness/observability/ObservabilityIndex.md` | H7 已落地；trace summary 和 failure attribution schema 位于目标 observability 层。 |
| Templates | `harness/templates/` | 已落地；项目模板已在 H4 统一到 `harness/templates/project-template/`。 |
| Project Template | `harness/templates/project-template/README.md` | H4 已统一；旧项目模板路径已清理。 |
| Tools | `harness/tools/ToolsIndex.md` | H5 已落地；稳定工具、工具文档、manifest、候选、历史、runtime 和 external 边界由 `harness/tools/` 路由。 |
| RAG Mechanism | `harness/rag/RAGIndex.md` | H6 已落地；机制资产位于 `harness/rag/`，真实或候选知识位于 `user/knowledge/`，运行态位于 `var/rag/`。 |
| Memory | `harness/memory/MemoryIndex.md` | H9-4 Memory 已具备 `invoke-memory.ps1` 生命周期命令、reviewed Memory、store gate、self-test 和 governance self-check 集成，已由用户确认收口。 |
| Skills | `harness/skills/SkillIndex.md` | H8 前置已补齐；Skill policy、candidate、reviewed、archive 和 usage sidecar 由该入口路由。 |
| Reports | `harness/reports/ReportsIndex.md` | 已落地；定义通用 report 机制、模板、命令面和存放边界，项目具体 report 进入项目实例。 |

## 2. 推荐读取路径

### Harness 架构和落地

```text
harness/architecture/HarnessEngineering.md
-> harness/architecture/PLANS.md
-> harness/governance/GovernanceIndex.md
```

### Bootstrap 和初始化

```text
harness/bootstrap/BootstrapIndex.md
-> harness/tools/scripts/stable/bootstrap-harness-workspace.ps1
-> harness/tools/scripts/stable/test-harness-governance.ps1
```

### 任务接入

```text
adapter/task-intake/TaskIntakeWorkflowModel.md
-> harness/templates/task/TaskBriefTemplate.md
-> harness/templates/workflow/WorkflowTemplate.md
```

### 项目模板和项目实例

```text
harness/templates/project-template/README.md
harness/templates/project-template/AGENTS.md
harness/templates/project-template/docs/project/ProjectIndex.md
harness/templates/project-template/model/README.md
-> user/registry/projects.local.json
-> projects/<project-id>/AGENTS.md
-> projects/<project-id>/docs/project/ProjectIndex.md
```

### 工具资产

```text
harness/tools/ToolsIndex.md
harness/tools/docs/
harness/tools/manifests/
harness/tools/scripts/stable/
harness/tools/scripts/candidate/
harness/tools/scripts/runtime/
harness/tools/scripts/historical/
harness/tools/external/
```

### RAG / Knowledge

```text
harness/rag/RAGIndex.md
harness/rag/manifests/
harness/rag/pipelines/
harness/rag/evals/
harness/rag/policies/
user/knowledge/README.md
var/rag/
```

### 治理、验证和观测

```text
harness/governance/GovernanceIndex.md
-> harness/governance/security/
-> harness/governance/context/
-> harness/governance/ArtifactLifecycle.md
-> harness/governance/ProjectHarnessFeedbackPolicy.md
-> harness/governance/KnowledgePromotionPolicy.md
-> harness/governance/MemoryGovernance.md
-> harness/governance/SkillGovernance.md
-> harness/verification/VerificationIndex.md
-> harness/observability/ObservabilityIndex.md
```

### Memory 和 Skill

```text
harness/memory/MemoryIndex.md
harness/memory/MemoryPolicy.md
harness/skills/SkillIndex.md
harness/skills/SkillPolicy.md
harness/skills/usage/skill-usage.json
```

## 3. 当前落地状态摘要

| 领域 | 状态 | 说明 |
|---|---|---|
| 新架构权威 | landed | `HarnessEngineering.md` 已更新为 `v2.4.1-project-lifecycle-evidence-gate`。 |
| 导航入口 | landed | 根 `INDEX.md` 和本文已落地；旧导航兼容 stub 已删除。 |
| 架构计划 | landed | `harness/architecture/PLANS.md` 已落地；旧计划兼容 stub 已删除。 |
| Bootstrap | landed | H8 bootstrap foundation 已补齐，正式产品化发布推迟到 H9 真实项目验证之后。 |
| 目录布局 | partial | H3 目标骨架已落地，H4 project-template、H5 tools、H6 RAG/Knowledge、H7 verification/observability 和 H8 前置机制补齐已完成；后续按 `harness/architecture/PLANS.md` 处理 H8 bootstrap。 |
| 项目实例 | partial | 项目实例位于 `projects/<project-id>/`；项目根 `AGENTS.md` 是目标入口。 |
| 敏感边界 | active | `user/`、`var/`、`projects/` 和 credentials boundary 已有规则，需按目标 `.gitignore` 复核。 |
| 工具资产 | landed | H5 已完成；工具文档、manifest、stable/candidate/historical 脚本已迁移到 `harness/tools/`，runtime 和 external 由 local-only 边界保护。 |
| Project lifecycle evidence gate | landed | `test-project-lifecycle-evidence.ps1` 已成为真实项目任务收口前的只读证据门禁。 |
| RAG / Knowledge | landed | H6 已完成；旧顶层 `rag/` 已移除，机制、用户知识和运行态边界已拆分。 |
| Verification / Observability | landed | H7 已完成；验证规则位于 `harness/verification/`，观测 schema 位于 `harness/observability/`，Governance 只引用验证和观测结果。 |
| Memory / Skill | landed | Memory 已完成 candidate -> review -> reviewed 的真实闭环，`memory-governance-use` 已晋升 reviewed Skill，Memory store gate 已接入 governance self-check。 |
| Project Template | landed | `harness/templates/project-template/` 已成为唯一目标项目模板路径；旧兼容 stub 已进入删除流程。 |

## 4. 维护规则

1. 本文只路由 General Harness 资产，不保存项目事实。
2. 当前实现路径和目标路径冲突时，以 `HarnessEngineering.md` 的目标架构为最终方向，以 `PLANS.md` 决定落地顺序。
3. 新增或迁移 General Harness 长期资产后，必须同步本文。
4. 删除旧路径或历史输入前，必须确保根 `INDEX.md` 和本文已有新路由。
