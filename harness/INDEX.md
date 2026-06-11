---
documentName: harness/INDEX.md
title: Harness Root Index
aliases:
  - Harness Index
  - Harness 文档索引
tags:
  - harness
  - index
version: v0.14.0-total-index
status: active
updatedAt: 2026-06-12
---

# Harness 文档索引

本文是 `<HARNESS_ROOT>` 的长期总索引，帮助 agent 快速找到相关文档内容。`AGENTS.md` 只保留入口发现和硬约束；具体架构、计划、治理、模板、工具、RAG 和项目模型均由本文路由。

`docs/` 只保留短期兼容入口，正文以 `harness/`、`adapter/`、`tools/`、`rag/`、`user/` 和 `projects/` 为准。

## 1. 必须入口链路

```text
1. AGENTS.md
2. harness/INDEX.md
3. harness/PLANS.md
4. 当前任务相关 Harness 文档、模板、Skill 或 Policy
5. user/registry/projects.local.json 或 Project Profile
6. projects/<project-id>/AGENTS.md
7. projects/<project-id>/docs/project/ProjectIndex.md
```

## 2. 核心资产

| 资产 | 路径 | 说明 |
|---|---|---|
| Agent Entry | `AGENTS.md` | 唯一 agent 入口、硬约束和读取顺序。 |
| Human Entry | `README.md` | 人类阅读的架构说明和常用命令。 |
| Architecture | `harness/architecture/HarnessEngineering.md` | 唯一最终架构权威。 |
| Plans | `harness/PLANS.md` | 阶段状态、验收状态和后续计划。 |
| Adapter | `adapter/` | task intake、runtime adapter、gateway 和 result contract。 |
| Governance | `harness/governance/` | 安全、上下文、晋升、验证、归档和治理规则。 |
| Observability | `harness/observability/` | trace、failure attribution 和 workflow observability。 |
| Project Template | `harness/project-template/`, `harness/templates/project/` | 正式项目包模型、模板说明和可复制项目模板。 |
| Templates | `harness/templates/` | 唯一可复用模板源。 |
| Memory | `harness/memory/` | Memory 规则、模板和 reviewed/candidate/archive 分区。 |
| Skills | `harness/skills/` | 可复用 Skill 资产和 Obsidian-related skills。 |
| Reports | `harness/reports/` | 脱敏报告和历史证据。 |
| Tools | `tools/scripts/`, `tools/docs/` | 稳定脚本、候选脚本、历史脚本和工具文档。 |
| User Boundary | `user/` | 本地 registry、私有 Maven profile、settings 和用户配置边界。 |
| RAG / Knowledge | `rag/knowledge/`, `rag/manifests/` | 用户知识库和 structured ingestion 配置。 |
| Project Instances | `projects/<project-id>/` | 项目事实和 workflow evidence。 |
| Runtime State | `var/` | logs、tmp、homes、m2、cache、evidence 和 RAG 运行态。 |
| Compatibility Stubs | `docs/` | 短期跳转入口，最终目标是删除。 |

## 3. 推荐读取路径

框架设计任务：

```text
harness/architecture/HarnessEngineering.md
-> harness/PLANS.md
-> harness/governance/GovernanceIndex.md
-> harness/project-template/model/StandardProjectPackage.md
```

任务接入和 adapter 任务：

```text
adapter/task-intake/TaskIntakeWorkflowModel.md
-> harness/templates/task/TaskBriefTemplate.md
-> harness/templates/workflow/WorkflowTemplate.md
-> harness/governance/verification/ReadinessCheckPolicy.md
```

项目路由任务：

```text
harness/project-template/model/ProjectRegistrationModel.md
-> user/registry/projects.local.json
-> user/registry/projects.local.example.json
-> tools/scripts/stable/test-project-registry.ps1
```

工具任务：

```text
tools/docs/command-surfaces/StableToolSurfaceModel.md
-> tools/docs/script-index/ScriptIndex.md
-> tools/scripts/stable/
```

治理自检：

```text
harness/governance/GovernanceIndex.md
-> tools/docs/script-index/ScriptIndex.md
-> tools/scripts/stable/test-harness-governance.ps1
```

RAG / Knowledge 任务：

```text
harness/architecture/HarnessEngineering.md
-> rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml
-> harness/templates/knowledge/StructuredIngestionManifestTemplate.md
-> rag/knowledge/
```

安全和用户配置任务：

```text
harness/governance/security/CredentialBoundaryPolicy.md
-> harness/governance/security/ContextFileSecurityPolicy.md
-> user/
```

## 4. 常见问题路由

| 问题 | 读取位置 |
|---|---|
| 当前最终架构是什么 | `harness/architecture/HarnessEngineering.md` |
| 当前阶段和下一步是什么 | `harness/PLANS.md` |
| agent 如何接入任务 | `AGENTS.md`, `adapter/task-intake/TaskIntakeWorkflowModel.md` |
| runtime 最终回复应包含什么 | `adapter/result-contracts/CommonTaskResultContract.md` |
| 如何校验项目注册表 | `tools/scripts/stable/test-project-registry.ps1`, `harness/project-template/model/ProjectRegistrationModel.md` |
| 如何运行 Harness Root 治理自检 | `tools/scripts/stable/test-harness-governance.ps1`, `harness/governance/GovernanceIndex.md` |
| Java/Maven 项目如何验证 | `tools/docs/command-surfaces/JavaMavenCommandSurface.md`, `tools/scripts/stable/invoke-maven-project.ps1`, `tools/scripts/stable/invoke-java-main.ps1` |
| 项目模板如何实例化 | `harness/project-template/model/ProjectTemplateGuide.md`, `harness/templates/project/` |
| Knowledge/Memory/Skill 如何晋升 | `harness/governance/promotion/KnowledgeIntakeAndPromotionPolicy.md`, `harness/governance/promotion/SkillMemoryGovernance.md` |
| RAG structured ingestion 如何评估 | `rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml`, `harness/architecture/HarnessEngineering.md` |
| 凭据、settings 和 auth 文件如何处理 | `harness/governance/security/CredentialBoundaryPolicy.md`, `user/` |
| 本机路径、GitHub 账号和 Git 管理边界如何处理 | `harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md`, `.gitignore`, `user/` |
| Obsidian 边界是什么 | `harness/architecture/HarnessEngineering.md`, `harness/skills/obsidian-skills/` |

## 5. 索引维护规则

1. 新增长期资产时必须更新本文。
2. 阶段状态只写入 `harness/PLANS.md`，本文只提供路由。
3. 具体本机路径、GitHub 账号、私有仓库 URL、settings 和 auth 信息只放在 `user/` local files。
4. 历史报告和归档可保留事实背景，但不得成为默认读取路线。
