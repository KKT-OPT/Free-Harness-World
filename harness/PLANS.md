---
documentName: harness/PLANS.md
title: Harness Phase Plans
aliases:
  - Harness Plans
  - Harness 阶段计划
tags:
  - harness
  - plans
version: v0.14.0-formal-template-git-boundary
status: active
updatedAt: 2026-06-12
---

# Harness 阶段计划

本文是 Harness Root 的阶段状态、下一步和 Post-P11 / P12 backlog 来源。架构权威以 `harness/architecture/HarnessEngineering.md` 为准。

## 1. 当前状态

```text
currentStage = P12.4.1 Formal Project Template And Git Boundary Hardening
status = p12.4.1-complete-ready-for-review
```

P12.4 已完成 template-inspired root layout 重构和最终架构文档重构。P12.4.1 补齐正式项目模板、INDEX 职责边界、本地身份敏感边界和 Git 管理判断。P12.4.1 不代表 Harness 生产化完成。

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

## 3. P12.4 完成内容

完成项：

- 最终架构权威迁移并重写为 `harness/architecture/HarnessEngineering.md`。
- `docs/` 改为短期兼容 stub，不再承载正文。
- 旧顶层 `interaction/` 迁移为 `adapter/`。
- 旧顶层 `scripts/` 迁移为 `tools/scripts/`。
- `tools/docs/` 迁移为 `tools/docs/`。
- 旧顶层 `templates/`、`skills/`、`memory/` 迁移到 `harness/`。
- 旧顶层 `knowledge/` 迁移到 `rag/knowledge/`。
- `settings/` 和本地 config 迁移到 `user/`。
- `AGENTS.md` 和 `README.md` 已更新为新入口。
- `tools/scripts/stable/` 默认路径已更新。
- 非稳定 historical/runtime 脚本已去除本机绝对路径默认值，改为参数或环境变量输入。
- `.gitignore` 已更新为新用户、工具、项目和 Obsidian 边界。

本阶段不做：

- 不导入真实 Java 项目；
- 不安装 RAG 工具；
- 不选择 vector store；
- 不创建完整 `.obsidian` 运行配置；
- 不复制旧 HarnessVault 整目录；
- 不删除 `projects/java-demo` 或 `var/` 历史运行态。

## 4. P12.4 验收标准

| 标准 | 期望 |
|---|---|
| PowerShell 语法检查 | `tools/scripts/stable/*.ps1` 全部 parse ok |
| Governance self-check | `status=passed`, `findingCount=0` |
| Project registry check | normal 和 `-SelfTest` 均 `status=passed` |
| `docs/` 兼容层 | 只包含 stub，不保存真实架构/计划/治理正文 |
| 旧路径引用 | active docs 中旧路径仅允许兼容说明或 historical report 命中 |
| 敏感扫描 | tracked docs 中无具体私有路径、settings 正文、token、password、secret 值 |
| 项目导入 | 未新增真实项目，`projects/` 只保留当前既有项目 |
| 架构权威 | `harness/architecture/` 只有 `HarnessEngineering.md` |

## 5. 后续阶段顺延

原 P12.4 RAG Structured Ingestion PoC 顺延为 P12.5。

### P12.4.1 补充完成内容

- `harness/templates/project/` 补齐正式项目包模板：SourceLayout、Validation、TestStrategy、SensitiveBoundaries、Acceptance、PRD、Architecture、Repository、API、Data、Test、ADR、Workflow。
- `StandardProjectPackage.md` 将真实项目口径调整为正式项目包，`java-demo` 仅保留 flow-proof / contract-proof 定位。
- `AGENTS.md` 收敛为入口和硬约束，长期路由由 `harness/INDEX.md` 承担。
- 本机绝对路径、GitHub 账号、私有仓库和私有 Maven 信息统一定义为 `user/` local boundary。
- 新增 Git 管理边界策略，结论为：Harness Root 应创建独立 Git 仓库，但 `git init`、remote、commit、push 均需用户确认后执行。

### P12.5 RAG Structured Ingestion PoC

目标：验证离线 structured ingestion，而不是先选择 vector store。

进入条件：

- 用户明确批准安装或使用本地 MarkItDown、RapidOCR、Whisper 相关工具；
- 使用合成样例或已脱敏样例；
- 明确不调用云端 LLM API。

验收标准：

- `network: disabled`；
- `llmApiRequired: false`；
- OCR 和 Whisper 可离线运行或明确记录未安装阻塞；
- 输出进入 `rag/knowledge/extracted` 或 `rag/knowledge/candidate`；
- 不选择 vector store；
- 不处理真实敏感材料。

### P12.6 RAG Policy And Old RAG Docs Migration

目标：在 P12.5 之后，选择性重写旧 HarnessVault RAG 文档到新版 Knowledge/RAG 生命周期。

### P12.7 Unified Harness CLI Facade

目标：把成熟稳定脚本和 self-check 包成统一 CLI 表面，但不把 agent runtime 内核纳入 Harness。

### P12.8 Isolation Implementation Path

目标：实现或验证 Docker/VM/远程 worker 的最小可行隔离方案。

### P12.9 Live Gateway Validation

目标：单独授权后验证 Hermes/WeCom live delivery 的任务入口、审批、证据和结果契约。

### P12.10 Real Project Onboarding Pilot

目标：在模板、registry、安全和 self-check 成熟后，接入一个真实业务项目的受管工作副本。

进入条件：

- P12.4 已 review 通过；
- 用户指定项目和边界；
- 真实项目只进入 `projects/<project-id>`；
- Harness Root 和真实项目保持两个 GitHub 仓库。

## 6. 仍不启动

在用户明确进入对应阶段前，不启动：

- RAG 工具安装；
- vector store 选择；
- live gateway；
- real project onboarding；
- Docker/VM 实施；
- unified CLI 实现；
- 旧 HarnessVault 整包迁移；
- Knowledge、Memory、Skill 或 Project Fact 自动晋升。
