---
documentName: INDEX.md
version: v1.0.0-pre-h8-readiness-complete
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: 全局导航入口，路由到 General Harness、项目实例、本地用户边界、运行态边界和架构落地计划。
scope:
  - workspace-index
  - global-routing
  - harness-boundaries
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - harness/HarnessIndex.md
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
outputTo:
  - INDEX.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-readiness-complete
---
# Harness 工作区索引

本文是 `<HARNESS_ROOT>` 的全局导航入口。`AGENTS.md` 只保存入口契约、硬约束和读取顺序；本文负责把人和 Agent 路由到 General Harness、项目实例、本地用户边界和运行态边界。

## 1. 必须入口链路

处理任何非简单任务时，按以下顺序读取：

```text
1. AGENTS.md
2. INDEX.md
3. harness/HarnessIndex.md
4. harness/architecture/PLANS.md
5. 当前任务相关 Policy / Template / Skill / Tool / Project 文档
6. user/registry/projects.local.json 或 Project Profile（如果任务涉及项目）
7. projects/<project-id>/AGENTS.md
8. projects/<project-id>/docs/project/ProjectIndex.md
```

## 2. 全局权威

| 资产 | 路径 | 说明 |
|---|---|---|
| Agent Entry | `AGENTS.md` | 唯一 Agent 入口契约、硬约束和读取顺序。 |
| Workspace Index | `INDEX.md` | 全局导航入口。 |
| General Harness Index | `harness/HarnessIndex.md` | General Harness 资产分层索引。 |
| Architecture Authority | `harness/architecture/HarnessEngineering.md` | Harness 长期目标架构权威。 |
| Architecture Plans | `harness/architecture/PLANS.md` | 新架构落地阶段、重构计划和验收标准。 |
| Human Entry | `README.md` | 人类阅读入口和常用命令说明。 |

## 3. 顶层边界

| 边界 | 路径 | 说明 |
|---|---|---|
| Adapter | `adapter/AdapterIndex.md` | 用户、gateway 和 Agent Runtime 的交互契约层。 |
| General Harness | `harness/` | 架构、治理、模板、技能、记忆、报告、验证、观测和目标工具/RAG 机制。 |
| Project Instances | `projects/<project-id>/` | 真实或 demo 项目实例；项目事实只进入项目实例。 |
| Sandbox | `sandbox/SandboxIndex.md` | 沙盒环境、隔离、profile 和 settings boundary 说明。 |
| User Boundary | `user/` | 本地 registry、settings、auth、identity 和用户私有边界。 |
| Runtime State | `var/` | logs、tmp、cache、m2、homes、evidence、rag index 等运行态。 |

## 4. 常见任务路由

| 任务类型 | 读取路径 |
|---|---|
| Harness 架构设计或架构更新 | `AGENTS.md` -> `INDEX.md` -> `harness/architecture/HarnessEngineering.md` -> `harness/architecture/PLANS.md` |
| Harness 落地和重构计划 | `AGENTS.md` -> `INDEX.md` -> `harness/architecture/PLANS.md` |
| General Harness 资产查找 | `AGENTS.md` -> `INDEX.md` -> `harness/HarnessIndex.md` |
| Bootstrap 和初始化 | `harness/bootstrap/BootstrapIndex.md` -> `harness/tools/scripts/stable/bootstrap-harness-workspace.ps1` |
| 任务接入和 Task Brief | `adapter/task-intake/TaskIntakeWorkflowModel.md` -> `harness/templates/task/TaskBriefTemplate.md` |
| 项目路由 | `user/registry/projects.local.json` -> `projects/<project-id>/AGENTS.md` -> `projects/<project-id>/docs/project/ProjectIndex.md` |
| 安全和凭据边界 | `harness/governance/security/CredentialBoundaryPolicy.md` -> `harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md` |
| 治理和晋升 | `harness/governance/GovernanceIndex.md` -> `harness/governance/ArtifactLifecycle.md` |
| Memory | `harness/memory/MemoryIndex.md`；Memory policy、candidate、reviewed 和 archive 边界由该入口路由。 |
| Skill | `harness/skills/SkillIndex.md`；Skill policy、candidate、reviewed、archive 和 usage sidecar 由该入口路由。 |
| 验证和 readiness | `harness/verification/VerificationIndex.md`；readiness、validation、regression 和 Harness validation cases 均由该入口路由。 |
| 观测和 failure attribution | `harness/observability/ObservabilityIndex.md`；trace summary 和 failure attribution schema 由该入口路由。 |
| Tool assets | `harness/tools/ToolsIndex.md`；H5 已完成迁移，稳定脚本位于 `harness/tools/scripts/stable/`。 |
| RAG / Knowledge | `harness/rag/RAGIndex.md` 保存机制入口，`user/knowledge/README.md` 保存真实知识和候选知识边界说明，`var/rag/` 保存运行态索引和提取产物。 |

## 5. 本地和敏感边界

以下内容不得作为稳定事实源，不得写入 prompt、Task Brief、workflow summary、Knowledge、Memory、Skill 或 tracked docs：

- `var/**` 运行态、缓存、日志、临时证据和索引；
- `user/settings/**`、`user/auth/**`、`user/identity/**`、`user/github/**`；
- `user/registry/*.local.json` 中的本机路由细节；
- 真实 settings XML、token、password、auth 文件、credential helper 状态；
- 本机绝对路径、私有仓库 URL、私有 Maven server 细节；
- 未脱敏 trace、raw runtime transcript、raw logs。

## 6. 索引维护规则

1. 新增长期 user-facing route 时必须更新本文。
2. General Harness 分区内的长期资产必须更新 `harness/HarnessIndex.md`。
3. 阶段状态、重构计划和验收标准只写入 `harness/architecture/PLANS.md`。
4. 项目事实只写入项目实例，不写入本文。
5. 历史报告和归档可作为证据背景，但不得成为默认上下文来源。
