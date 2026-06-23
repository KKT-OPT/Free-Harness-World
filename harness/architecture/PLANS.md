---
documentName: harness/architecture/PLANS.md
version: v1.2.0-h8-install-uninstall-validation
updatedAt: 2026-06-23 10:05:00.000 +08:00
status: active
purpose: 记录新架构方案的落地阶段、当前沙盒 Harness 现状、重构计划、阶段验收标准、H8 bootstrap foundation 和后续真实项目验证/release gate。
scope:
  - architecture-landing-plan
  - harness-refactor-plan
  - stage-acceptance
  - pre-h8-readiness
  - h8-bootstrap-foundation
  - github-agent-branch-management
  - h8-install-uninstall-validation
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/HarnessEngineering.md
  - harness/governance/GovernanceIndex.md
outputTo:
  - harness/architecture/PLANS.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h8-reopened-for-install-uninstall-validation
---
# Harness 架构落地计划

本文是 Harness 目标架构的落地计划、重构路线和验收标准来源。架构权威以 `harness/architecture/HarnessEngineering.md` 为准；本文不替代架构正文，不记录项目任务过程证据。

## 1. 当前状态

```text
currentStage = H8 Install/Uninstall Clone Validation
status = h8-supplemental-validation-in-progress
lastCompletedStage = H8-bootstrap-foundation
architectureAuthority = harness/architecture/HarnessEngineering.md
targetArchitectureVersion = v2.4.0-target-architecture
```

当前目标架构口径：

- `INDEX.md` 是全局导航入口；
- `harness/HarnessIndex.md` 是 General Harness 资产分层索引；
- `harness/architecture/PLANS.md` 是架构落地、重构和验收计划；
- `projects/<project-id>/AGENTS.md` 是项目级 Agent 入口；
- `projects/<project-id>/docs/project/ProjectIndex.md` 是项目事实入口；
- `harness/tools/`、`harness/rag/`、`harness/verification/`、`harness/observability/` 是目标一级分区；
- `harness/templates/project-template/` 是唯一目标项目模板路径；
- `user/knowledge/` 或外部 private repo 是真实用户知识目标边界；
- `var/rag/` 是 RAG index、embedding、cache 等运行态边界。

## 2. 阶段总览

| 阶段 | 名称 | 状态 | 主要输出 |
|---|---|---|---|
| H0 | 架构权威审批 | complete | `HarnessEngineering.md` v2.4 active。 |
| H1 | 导航权威迁移 | complete | `INDEX.md`、`harness/HarnessIndex.md`、`harness/architecture/PLANS.md`。 |
| H2 | 入口和活跃路由对齐 | complete | 根入口、README、adapter、governance、templates 的活跃路由已对齐。 |
| H3 | 目标骨架和边界脚手架 | complete | `harness/tools/`、`harness/rag/`、`harness/verification/`、`user/knowledge/`、`LICENSE`、`projects/README.md`。 |
| H4 | 项目模板统一 | complete | `harness/templates/project-template/` 成为唯一目标项目模板路径。 |
| H5 | 工具资产层迁移 | complete | 工具资产已分类并路由到 `harness/tools/`。 |
| H6 | RAG 和 Knowledge 边界迁移 | complete | RAG 机制、用户知识和运行态索引边界已拆分。 |
| H7 | Verification、Observability 和 Governance 对齐 | complete | 验证规则、观测 schema 和治理 linkage 已对齐目标路径。 |
| H8-pre | H8 前置检查和完善 | complete | 结构检查、兼容清理、治理/Memory/Skill/Knowledge 机制补齐、Git 管理恢复决策。 |
| H8 | GitHub agent 分支恢复和 Bootstrap Foundation | supplemental-validation | 已恢复 `agent-git` 分支 GitHub 管理；补充 install/uninstall 和非沙盒 clone 验证后才可完成验收。 |
| H9 | 目标布局后的真实项目验证 | pending | 用真实项目 workflow 验证 Skill、Governance、Knowledge、Memory 和工具闭环，不晋升私有事实。 |
| H10 | Release Readiness 和 main 发布门禁 | pending | H9 验证后再判断是否具备 release candidate；`main` 合并、tag、正式发布只能由用户执行。 |

## 3. 当前沙盒 Harness 落地现状

| 领域 | 当前状态 | 下一步 |
|---|---|---|
| 架构权威 | `harness/architecture/HarnessEngineering.md` 是 active 权威。 | 不写入阶段性内容。 |
| 全局索引 | `INDEX.md` 和 `harness/HarnessIndex.md` 已落地；旧兼容 stub 已清理。 | H8 纳入 bootstrap self-check。 |
| Adapter | `adapter/AdapterIndex.md` 已补齐。 | H8 纳入 bootstrap self-check。 |
| Sandbox | `sandbox/SandboxIndex.md` 已补齐。 | H8 继续完善 bootstrap 初始化说明。 |
| Governance | 目标治理机制文档已补齐到 `harness/governance/`。 | H8 继续强化 self-check；真实闭环验证进入 H9。 |
| Memory | `harness/memory/MemoryIndex.md` 和 `MemoryPolicy.md` 已补齐。 | 后续只按 review 流程新增 candidate/reviewed memory。 |
| Skills | `harness/skills/SkillIndex.md`、`SkillPolicy.md` 和 usage sidecar 已补齐。 | 后续 review 现有 skill 包是否迁入 reviewed 分区。 |
| Knowledge / RAG | `harness/governance/KnowledgePromotionPolicy.md`、`harness/rag/`、`user/knowledge/` 和 `var/rag/` 边界已对齐。 | 后续 reviewed Knowledge 仍需 human review 或用户明确批准。 |
| Project Template | 目标路径为 `harness/templates/project-template/`；旧项目模板兼容 stub 已清理。 | H8 检查实例化说明和发布包边界。 |
| Tool assets | 目标路径为 `harness/tools/`。 | H8 复核 runtime/external Git 边界。 |
| Verification / Observability | 目标路径为 `harness/verification/` 和 `harness/observability/`。 | H8 self-check 纳入 required routes。 |
| Distribution | `README.md`、`LICENSE`、`projects/README.md`、`harness/bootstrap/BootstrapIndex.md` 已存在。 | H8 完成 bootstrap foundation；正式 release readiness 推迟到 H9 真实项目验证之后。 |

## 4. H0-H7 验收摘要

| 阶段 | 验收摘要 |
|---|---|
| H0 | 架构权威已升级为 `v2.4.0-target-architecture`，状态 active。 |
| H1 | 新导航入口和架构计划路径已落地。 |
| H2 | 活跃文档不再依赖旧索引和旧计划路径作为主入口。 |
| H3 | 目标一级目录和产品化必需文件已建立。 |
| H4 | 项目模板正文已统一到目标项目模板路径。 |
| H5 | 工具资产已迁移到 `harness/tools/`，稳定工具契约已补齐。 |
| H6 | RAG 机制、用户知识和运行态边界已拆分。 |
| H7 | Verification、Observability 和 Governance 边界已对齐。 |

## 5. H8 前置检查范围

本轮 H8 前置检查至少覆盖：

1. 根据 `harness/architecture/HarnessEngineering.md` 检查顶层目录、General Harness 分区和关键文档是否已经建立。
2. 阅读兼容文件，确认无风险后删除。
3. 检查 Governance、Memory、Knowledge Promotion 和 Skill Creation 机制是否符合架构文档中的 Mermaid 流程。
4. 判断 GitHub 管理恢复应在 H8 前还是 H8 阶段执行。

本轮结论：

```text
H8-pre = complete
nextStage = H8
gitManagementRestore = H8 stage, user approval required before stage/commit/push
```

## 6. H8 前置完成标准和结果

| 标准 | 结果 | 证据 |
|---|---|---|
| 顶层结构 | pass | 顶层目标目录为 `adapter/`、`harness/`、`projects/`、`sandbox/`、`user/`、`var/`；架构外空目录已清理。 |
| General Harness 分区 | pass | `harness/architecture/`、`governance/`、`memory/`、`observability/`、`rag/`、`reports/`、`skills/`、`templates/`、`tools/`、`verification/` 已建立。 |
| 分区索引 | pass | Adapter、Harness、Governance、Memory、Skills、RAG、Verification、Observability、Sandbox 均有入口或索引。 |
| 兼容清理 | pass | 已删除旧索引/计划 stub、旧项目模板 stub、旧 promotion policy 路径和 v2.3 设计输入；active route 不再依赖旧路径。 |
| 治理机制 | pass | `ArtifactLifecycle.md`、`DocumentGovernance.md`、`IndexMaintenancePolicy.md`、`CleanupPolicy.md`、`ScheduledGovernance.md`、`ReportArchivePolicy.md` 已建立。 |
| Knowledge Promotion | pass | `KnowledgePromotionPolicy.md` 明确 raw -> extracted -> candidate -> review -> reviewed -> RAG index / archive 流程。 |
| Memory | pass | `MemoryPolicy.md` 明确 task evidence -> candidate -> conflict/review -> active memory / archive 流程。 |
| Skill | pass | `SkillPolicy.md` 明确 workflow evidence/user request -> candidate -> existing skill check -> review -> reviewed/archive -> usage sidecar 流程。 |
| Git 管理恢复决策 | pass | GitHub 管理恢复放在 H8 阶段执行；commit、push、branch rewrite 或 remote 变更必须用户审批。 |
| 自检 | pass | governance self-check、registry self-test、frontmatter scan、stale route scan 和 `git diff --check` 已通过。 |

验证命令摘要：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File harness\tools\scripts\stable\test-harness-governance.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File harness\tools\scripts\stable\test-project-registry.ps1 -SelfTest
git diff --check
```

验证结果：

- `test-harness-governance.ps1`：passed；仅有 `managedProjectSeparateGit` info，说明受管项目拥有独立 `.git`，符合 Harness 根仓库和项目仓库分离原则。
- `test-project-registry.ps1 -SelfTest`：passed，3 个 self-test case 全部符合预期。
- PowerShell parser：`test-harness-governance.ps1` 和 `test-project-registry.ps1` 均 parse ok。
- frontmatter scan：active Harness Markdown 文档均已具备 YAML frontmatter；外部工具源码、用户私有 settings、local knowledge candidate 和 archived reports 不作为 active authority 扫描对象。
- stale route scan：剩余旧路径命中只存在于 self-check legacy detector 和 Status JSON 占位符，不属于 active route。
- `git diff --check`：无 whitespace error；仅提示 `harness/architecture/HarnessEngineering.md` 后续 Git 触碰时 CRLF 将转为 LF。

## 7. Git 管理恢复决策

当前仓库已有 Git remote：

```text
origin = git@github.com:KKT-OPT/Free-Harness-World.git
currentBranch = agent-git
```

H0-H7 重构期间发生大量路径迁移、删除和新增。H8 的职责是恢复 `agent-git` 分支的 GitHub 管理，让重构后的架构资产重新被 GitHub 审查和追踪。

决策：

```text
Git management restore timing = H8 stage
remote = git@github.com:KKT-OPT/Free-Harness-World.git
agentWritableBranch = agent-git
humanOwnedReleaseBranch = main
```

用户已确认：agent 可以在 `agent-git` 分支提交、修改和推送；`main` 分支只能由用户提交、修改和发布。

H8 中执行：

```text
git status review
bootstrap foundation
governance self-check
git add reviewed scope
git commit
git push origin agent-git
```

禁止：

- 推送或修改 `main`；
- 创建正式 release tag；
- 把真实项目源码、用户私有知识、运行态产物、auth、settings 或未脱敏日志提交到 Harness Distribution Repo；
- 将 H8 描述为正式产品化发布。

## 8. H8 目标

目标：完成 H8 bootstrap foundation，并恢复 `agent-git` 分支的 GitHub 管理。H8 不是正式产品化发布阶段。

范围：

- `harness/bootstrap/BootstrapIndex.md`；
- bootstrap status/install/uninstall 稳定脚本；
- root README 更新；
- `.gitignore` 按目标边界复核；
- governance self-check 支持目标路径；
- validation cases 覆盖 bootstrap、索引、目录、Git 边界、敏感边界；
- `agent-git` 分支 commit/push；
- 明确正式产品化发布推迟到 H9 真实项目验证之后。

验收标准：

| 标准 | 期望 |
|---|---|
| Bootstrap | `bootstrap-harness-workspace.ps1 -Mode status` 可运行；`-Mode install` 可创建缺失本地 registry 和运行态目录且不覆盖已有文件；`-Mode uninstall` 可删除安装态本地文件且不破坏 Git clone。 |
| Self-check | governance self-check 可发现旧路径、缺失索引、敏感边界和 Git 边界风险。 |
| Git ignore | `var/`、local user data、projects、runtime/external assets 默认不进入通用 Git。 |
| Distribution foundation | `LICENSE`、`projects/README.md` 和 `harness/bootstrap/BootstrapIndex.md` 存在。 |
| Git 恢复 | 当前分支为 `agent-git`，H0-H8 变更提交并推送到 `origin/agent-git`。 |
| Release 边界 | H8 文档明确不发布正式版本，`main` 分支和正式 release 由用户控制。 |
| Clone 验证 | 在非当前 Harness Root 的独立本地路径 clone `origin/agent-git`，完成 status、install、self-check、uninstall、status 流程。 |

H8 完成结果：

| 项目 | 结果 |
|---|---|
| Bootstrap 入口 | `harness/bootstrap/BootstrapIndex.md` 已建立并接入索引。 |
| Bootstrap 命令 | `harness/tools/scripts/stable/bootstrap-harness-workspace.ps1 -Mode status` 通过。 |
| 自检 | governance self-check 通过；registry self-test 通过；`git diff --check` 无 whitespace error。 |
| GitHub 恢复 | H0-H8 变更已提交并推送到 `origin/agent-git`，commit `1786664`。 |
| Release 边界 | H8 未发布正式版本，`main` 未被 agent 修改，正式 release 推迟到 H9 真实项目验证之后。 |
| 补充要求 | 用户要求 H8 增加 install/uninstall，并在非当前 Harness Root 的独立本地路径做 clone/install/uninstall 验证。 |

## 9. H9 目标

目标：在目标布局落地后，用真实受管项目实例验证 Harness 任务工作流、Skill、Governance、Knowledge、Memory 和工具闭环。

验收标准：

| 标准 | 期望 |
|---|---|
| 项目入口 | Agent 从项目根 `AGENTS.md` 和 `docs/project/ProjectIndex.md` 进入。 |
| 证据链 | 每个复杂任务有 Task Brief、Trace、Validation、Governance Candidates。 |
| 工具调用 | 使用 stable tools，不依赖一次性手工命令。 |
| Skill 闭环 | 至少一个真实任务产生 Skill candidate 或已有 Skill patch candidate，并经过 review 决策。 |
| Governance 闭环 | 至少一个真实任务经过 candidate-first、review-first、human approval 的治理收口。 |
| Knowledge 闭环 | 真实项目或知识任务只生成 candidate/reviewed 流程证据，不直接污染 RAG index 或通用事实。 |
| Memory 闭环 | Memory 不再只有占位符；至少验证一次 candidate -> review -> active/rejected/archive 路径。 |
| 晋升边界 | 项目经验只产生 candidates，不自动进入通用 Harness。 |
| 隐私边界 | 不写入私有 settings、auth、raw logs、私有仓库细节。 |

## 10. H10 目标

目标：H9 真实项目验证通过后，再判断是否进入 release readiness。H10 不默认发生，必须由用户审批。

验收标准：

| 标准 | 期望 |
|---|---|
| Release Candidate | H9 真实项目验证报告通过，残余风险可接受。 |
| 文档一致性 | Architecture、INDEX、HarnessIndex、README、Bootstrap、Tools、Verification、Governance 口径一致。 |
| GitHub 分支 | `agent-git` 已完成审查；是否合入 `main` 由用户决定。 |
| 发布动作 | `main` 合并、tag、release note 和正式发布只能由用户执行。 |

## 11. 计划维护规则

1. 阶段状态只写入本文。
2. 架构规则只写入 `HarnessEngineering.md`。
3. 路由入口同步写入 `INDEX.md` 和 `harness/HarnessIndex.md`。
4. 任何迁移阶段完成前，必须记录验收结果和未完成项。
5. 任何涉及 Knowledge、Memory、Skill、Project Fact 或 Governance 晋升的结果，必须经过 review 或用户明确批准。
