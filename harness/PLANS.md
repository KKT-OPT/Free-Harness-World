---
documentName: harness/PLANS.md
title: Harness Phase Plans
aliases:
  - Harness Plans
  - Harness 阶段计划
tags:
  - harness
  - plans
version: v0.15.0-real-project-first-order
status: active
updatedAt: 2026-06-12
---

# Harness 阶段计划

本文是 Harness Root 的阶段状态、下一步和 Post-P11 / P12 backlog 来源。架构权威以 `harness/architecture/HarnessEngineering.md` 为准。

## 1. 当前状态

```text
currentStage = P12.5 Real Project Onboarding Gate
status = p12.5-agent-branch-prepared-ready-for-review
```

P12.4 已完成 template-inspired root layout 重构和最终架构文档重构。P12.4.1 已补齐正式项目模板、INDEX 职责边界、本地身份敏感边界和 Git 管理判断。

当前根据真实项目接入经验调整 P12 后续顺序：先补齐真实项目接入闸门和 workflow/trace tooling，再继续真实 Java 项目 pilot、治理/记忆闭环和 RAG structured ingestion。

重要边界：

- `projects/lfms-decision` 是真实项目的沙盒工作副本，项目 Git 仓库与 Harness Root Git 仓库分离。
- `agent-harness-onboarding` 是 agent 维护分支；`new_architecture` 是用户/项目基线分支，agent 不直接提交或推送。
- `E2eScenarioS3Program` 的一次命令行运行结果只是 workflow evidence 中的临时链路验证，不是完整业务验收，不自动晋升为 Project Fact、Memory、Skill、Knowledge 或 Harness 通用规则。
- 本轮不更新 `harness/architecture/HarnessEngineering.md`；工具和流程经验先进入 P12.6 tooling 计划。

## 2. 阶段总览

| 阶段 | 名称 | 状态 | 当前证据 |
|---|---|---|---|
| P0-P1 | 早期架构设计 | absorbed-into-final-architecture | `harness/archive/design-history/architecture/` |
| P2 | 根入口和索引 | active | `AGENTS.md`, `harness/INDEX.md`, `harness/PLANS.md` |
| P3-P8 | 资产模型、任务接入、工具和安全 | absorbed-or-active | `harness/architecture/HarnessEngineering.md`, `adapter/`, `tools/`, `harness/governance/` |
| P9 | Java demo 流程证明 | flow-proof-complete | `projects/java-demo/` |
| P10 | Runtime adapter 契约证明 | contract-complete | `adapter/result-contracts/`, `adapter/runtime-adapters/`, `adapter/gateways/` |
| P10.5 | Final design landing | superseded-by-final-architecture-authority | `harness/architecture/HarnessEngineering.md`, `harness/reports/redacted/P10_5FinalDesignLandingReport.md` |
| P11 | Framework closeout | p11.8-ready-for-review | `harness/reports/redacted/P11FrameworkCloseoutReport.md`, `projects/java-demo/docs/project/workflow/p11-framework-closeout.md` |
| P12.0 | Plan baseline and cleanup | complete-ready-for-review | old path cleanup and P12 backlog baseline |
| P12.1 | Project template hardening | complete-ready-for-review | `harness/templates/project/`, `harness/project-template/model/` |
| P12.2 | Local project registry landing | complete-ready-for-review | `user/registry/projects.local.json`, `tools/scripts/stable/test-project-registry.ps1` |
| P12.3 | Governance self-check tooling | complete-ready-for-review | `tools/scripts/stable/test-harness-governance.ps1` |
| P12.4 | Harness architecture and root layout refactor | complete-ready-for-review | `harness/architecture/HarnessEngineering.md`, template-inspired root layout |
| P12.4.1 | Formal project template and Git boundary hardening | complete-ready-for-review | `harness/templates/project/`, `harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md` |
| P12.5 | Real Project Onboarding Gate | agent-branch-prepared-ready-for-review | `projects/lfms-decision/docs/project/workflow/20260612-real-project-onboarding.md` |
| P12.6 | Workflow/Trace Evidence Tooling | next | `tools/scripts/stable/invoke-java-main.ps1` repair candidate, workflow validator backlog |
| P12.7 | Real Java Project Pilot | pending-after-p12.6 | `projects/lfms-decision` pilot work copy |
| P12.8 | Governance + Memory Closeout Pilot | pending-after-p12.7 | project workflow evidence candidates |
| P12.9 | RAG Structured Ingestion PoC | pending-after-p12.8 | `rag/manifests/offline-markitdown-rapidocr-whisper.profile.example.yaml` |

## 3. P12.5 Real Project Onboarding Gate

目标：明确真实项目接入边界，只做接入准备和低风险链路验证，不急着改业务代码。

已确认：

- projectId：`lfms-decision`。
- 沙盒位置：`projects/lfms-decision`。
- 项目仓库：独立 Git 仓库，与 Harness Root 仓库分离。
- 基线分支：`new_architecture`。
- agent 分支：`agent-harness-onboarding`。
- 旧 in-source agent docs 路径：用户授权在 agent 分支删除。
- 私有 Maven/settings：只进入 ignored 的 `user/` 本地边界，不写入 tracked docs。
- S3 命令行运行：只作为临时链路验证 workflow evidence。

验收标准：

| 标准 | 期望 |
|---|---|
| 项目位置 | 真实项目只位于 `projects/<project-id>` |
| Git 边界 | Harness Root 和真实项目是两个仓库；agent 只操作 agent 分支 |
| 敏感边界 | 本机路径、settings、auth、GitHub 账号、私有 Maven 信息不进入 tracked docs |
| 项目模板 | 正式 project package 已实例化到项目仓库 |
| 旧文档 | 旧 in-source docs 不作为事实源；迁移需后续 review |
| 低风险验证 | 可做一次命令行/私有 Maven/settings 链路验证，但只记录为 workflow evidence |
| 不做事项 | 不声明完整业务验证，不修改用户基线分支，不更新通用架构 |

## 4. P12.6 Workflow/Trace Evidence Tooling

目标：把真实项目开发中会反复发生的验证工作流固化为稳定工具，避免每次靠临时命令探索。

必须完成：

- 新增或完善 Task Brief、Harness Run Card、Trace Summary、Validation、Governance Candidates 的生成脚本。
- 新增 workflow evidence validator，检查项目 workflow 是否包含：
  - Task Brief；
  - Harness Run Card；
  - Trace；
  - Validation；
  - Governance Candidates。
- 完善 Java/Maven 主类验证工具，要求 agent 不再手工组装 classpath。
- 明确运行日志、status JSON、classpath 文件、argfile 只属于 runtime evidence，默认进入 `var/` 或项目 ignored 输出。

验收标准：

| 标准 | 期望 |
|---|---|
| 脚本可用 | `invoke-java-main.ps1` 能执行 Maven 编译、classpath 构建和 main class 运行 |
| stderr 处理 | Java/SLF4J 等 stderr 警告不应中断成功进程 |
| workflow validator | 缺少必需 evidence section 时返回明确失败 |
| 敏感边界 | validator 不读取 settings/auth 内容，不把 raw logs 写入 tracked docs |
| 文档同步 | `tools/docs/script-index/ScriptIndex.md` 和 command surface 文档说明稳定用法 |

## 5. P12.7 Real Java Project Pilot

目标：在 P12.6 tooling 成熟后，继续以 `lfms-decision` 做真实 Java 项目 pilot。

范围：

- 使用 agent 分支，不提交到 `new_architecture`。
- 继续完善正式 project package。
- 跑只读或低风险验证：结构识别、Maven profile、测试命令、敏感扫描。
- 若需要改项目代码，只允许在 agent 分支，并记录为 project-local workflow evidence。

验收标准：

| 标准 | 期望 |
|---|---|
| 结构识别 | module/source/test/resource/generated-output 边界清晰 |
| 验证命令 | 通过稳定脚本运行，不使用一次性手工 classpath |
| 证据 | 每次任务有 workflow evidence，且 validator 通过 |
| 口径 | 单个测试通过不等于全项目通过 |
| Git | agent 分支可提交/推送；合并到基线必须由用户确认 |

## 6. P12.8 Governance + Memory Closeout Pilot

目标：基于真实项目任务产出 candidates，由用户判断哪些晋升为长期资产。

候选类型：

- Project Fact；
- Memory；
- Skill；
- Knowledge；
- Harness 通用规则；
- Tool improvement。

验收标准：

| 标准 | 期望 |
|---|---|
| 候选清单 | 每个候选包含来源 workflow evidence 和建议归属 |
| 晋升规则 | 未经 review 或用户批准不得自动晋升 |
| 边界 | 项目经验不默认变成通用 Harness 规则 |
| 旧资产 | 旧 in-source docs 只做 source-led review 后的迁移候选 |

## 7. P12.9 RAG Structured Ingestion PoC

目标：用脱敏真实项目文档或合成样例验证离线 structured ingestion。

候选工具：

- MarkItDown；
- RapidOCR；
- Whisper。

验收标准：

| 标准 | 期望 |
|---|---|
| 网络 | `network: disabled` |
| LLM API | `llmApiRequired: false` |
| 输入 | 只使用合成样例或已脱敏样例 |
| 输出 | 进入 `rag/knowledge/extracted` 或 `rag/knowledge/candidate` |
| 晋升 | 不自动进入 reviewed knowledge |
| 不做事项 | 不选择 vector store，不处理真实敏感材料 |

## 8. 延后阶段

以下阶段顺延到 P12.9 之后重新排期：

- RAG policy and old RAG docs migration；
- Unified Harness CLI facade；
- Isolation implementation path；
- Live gateway validation；
- 旧 HarnessVault 整包迁移。

## 9. 仍不启动

在用户明确进入对应阶段前，不启动：

- RAG 工具安装；
- vector store 选择；
- live gateway；
- Docker/VM 实施；
- unified CLI 实现；
- 旧 HarnessVault 整包迁移；
- Knowledge、Memory、Skill 或 Project Fact 自动晋升；
- 真实项目 agent 分支向用户基线分支合并。
