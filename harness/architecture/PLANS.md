---
documentName: harness/architecture/PLANS.md
version: v1.3.1-h9-0-precondition-complete
updatedAt: 2026-06-23 18:54:52.291 +08:00
status: active
purpose: 记录 Harness 目标架构落地阶段、重构计划、验收标准、H8 bootstrap foundation 结果，以及 H9 真实项目验证的分阶段计划。
scope:
  - architecture-landing-plan
  - harness-refactor-plan
  - stage-acceptance
  - h8-bootstrap-foundation
  - h9-real-project-validation
  - h9-subphase-acceptance
  - h9-0-precondition
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
  - harness/templates/project-template/model/StandardProjectPackage.md
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
  decision: h9-0-precondition-complete
---
# Harness 架构落地计划

本文是 Harness 目标架构的落地计划、重构路线和验收标准来源。架构权威以 `harness/architecture/HarnessEngineering.md` 为准；本文不替代架构正文，不记录项目任务过程证据。

## 1. 当前状态

```text
currentStage = H9-0 Real Project Fact Baseline
status = ready-for-H9-0
lastCompletedStage = H8
architectureAuthority = harness/architecture/HarnessEngineering.md
targetArchitectureVersion = v2.4.0-target-architecture
h9ValidationAnchor = projects/lfms-decision
h9Precondition = java-maven-profile-and-e2e-main-commandline-validation-complete
```

当前目标架构口径：

- `INDEX.md` 是全局导航入口。
- `harness/HarnessIndex.md` 是 General Harness 资产分层索引。
- `harness/architecture/PLANS.md` 是架构落地、重构和验收计划。
- `projects/<project-id>/AGENTS.md` 是项目级 Agent 入口。
- `projects/<project-id>/docs/project/ProjectIndex.md` 是项目事实入口。
- `harness/tools/`、`harness/rag/`、`harness/verification/`、`harness/observability/` 是目标一级分区。
- `harness/templates/project-template/` 是唯一目标项目模板路径。
- `user/knowledge/` 或外部 private repo 是真实用户知识目标边界。
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
| H8-pre | H8 前置检查和完善 | complete | 结构检查、兼容清理、Governance/Memory/Skill/Knowledge 机制补齐、Git 管理恢复决策。 |
| H8 | GitHub agent 分支恢复和 Bootstrap Foundation | complete | 已恢复 `agent-git` 分支 GitHub 管理；install/uninstall 和非沙盒 clone 验证已通过；README 和 MIT LICENSE 已完成产品化基础补齐。 |
| H9 | 真实项目验证总阶段 | in-progress | 以 `projects/lfms-decision` 为验证锚点，分阶段验证项目事实、真实任务、Skill、Governance、Knowledge、Memory 和工具闭环。 |
| H9-0 | 真实项目文档和事实基线 | ready | 补齐 `projects/lfms-decision/docs/project/` 项目事实文档、ProjectIndex 路由和用户审阅结论。 |
| H9-1 | 至少一个真实任务全流程验证 | pending | 完成一个真实 Java 项目的分析、设计、执行、测试、验收和 workflow evidence 闭环。 |
| H9-2 | Skill 闭环验证 | pending | 从真实任务产生 Skill candidate 或已有 Skill patch candidate，并完成 review 决策。 |
| H9-3 | Governance 闭环验证 | pending | 至少一个真实任务完成 candidate-first、review-first、human approval 的治理收口。 |
| H9-4 | Knowledge 和 Memory 闭环验证 | pending | 验证 Knowledge 晋升边界和 Memory candidate -> review -> active/rejected/archive 路径。 |
| H9-5 | H9 汇总和 H10 门禁判定 | pending | 汇总 H9 验收结果、架构反向优化项和 release readiness 风险，判断是否进入 H10。 |
| H10 | Release Readiness 和 main 发布门禁 | pending | H9 全部子阶段验收后再判断是否具备 release candidate；`main` 合并、tag、正式发布只能由用户执行。 |

## 3. 当前沙盒 Harness 落地现状

| 领域 | 当前状态 | 下一步 |
|---|---|---|
| 架构权威 | `harness/architecture/HarnessEngineering.md` 是 active 权威。 | 不写入阶段性内容。 |
| 全局索引 | `INDEX.md` 和 `harness/HarnessIndex.md` 已落地；旧兼容 stub 已清理。 | H9 只在必要时同步阶段路由，不记录项目事实。 |
| Adapter | `adapter/AdapterIndex.md` 已补齐。 | 用真实任务验证入口和 Task Brief 交接是否足够。 |
| Sandbox | `sandbox/SandboxIndex.md` 已补齐。 | H9 真实项目验证不得破坏 Harness Root。 |
| Governance | 目标治理机制文档已补齐到 `harness/governance/`。 | H9-3 用真实任务验证治理闭环。 |
| Memory | `harness/memory/MemoryIndex.md` 和 `MemoryPolicy.md` 已补齐。 | H9-4 验证 candidate/review/active 或 reject/archive 路径。 |
| Skills | `harness/skills/SkillIndex.md`、`SkillPolicy.md` 和 usage sidecar 已补齐。 | H9-2 用真实任务验证 Skill candidate 或 patch candidate。 |
| Knowledge / RAG | `harness/governance/KnowledgePromotionPolicy.md`、`harness/rag/`、`user/knowledge/` 和 `var/rag/` 边界已对齐。 | H9-4 验证 Knowledge 晋升边界，不污染 RAG index 或通用事实。 |
| Project Template | 目标路径为 `harness/templates/project-template/`；旧项目模板兼容 stub 已清理。 | H9-0 使用模板补齐真实项目文档基线。 |
| Tool assets | 目标路径为 `harness/tools/`。 | H9-1 验证真实任务是否优先使用 stable tools。 |
| Verification / Observability | 目标路径为 `harness/verification/` 和 `harness/observability/`。 | H9-1 验证真实任务的测试、验收和证据链记录。 |
| Distribution | `README.md`、`LICENSE`、`projects/README.md`、`harness/bootstrap/BootstrapIndex.md` 已存在。 | H10 前不得宣称正式 release；H9 验证结果决定是否进入 release readiness。 |

## 4. H0-H8 验收摘要

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
| H8-pre | H8 前置结构检查、兼容文件清理、机制补齐和 Git 管理恢复决策已完成。 |
| H8 | `agent-git` GitHub 管理已恢复；bootstrap status/install/uninstall 支持已完成；独立 clone 安装卸载验证已通过；顶层 README 和标准 MIT LICENSE 已补齐。 |

## 5. H8 完成结果

H8 的目标是完成 bootstrap foundation，并恢复 `agent-git` 分支的 GitHub 管理。H8 不是正式产品化发布阶段。

| 项目 | 结果 |
|---|---|
| Bootstrap 入口 | `harness/bootstrap/BootstrapIndex.md` 已建立并接入索引。 |
| Bootstrap 命令 | `harness/tools/scripts/stable/bootstrap-harness-workspace.ps1` 支持 `status`、`install`、`uninstall`；`init` 保留为兼容别名。 |
| Clean Install Registry | `install` 生成空的本地 project/knowledge registry，不自动引用不存在的示例项目。 |
| Clone 验证 | 已在非当前 Harness Root 的独立本地路径完成 clone、status、install、self-check、uninstall、status 流程验证。 |
| 自检 | governance self-check、registry self-test、`git diff --check` 已通过。 |
| GitHub 恢复 | H0-H8 变更已提交并推送到 `origin/agent-git`；H8 README/LICENSE 优化后最新提交为 `cb9d69b`。 |
| Release 边界 | H8 未发布正式版本，`main` 未被 agent 修改；正式 release 推迟到 H9 真实项目验证和 H10 release readiness 之后。 |

## 6. H9 重新拆分判断

用户建议成立：H9 作为真实项目验证、问题反向优化和机制闭环验证阶段，不能在一次任务中完成完整闭环。原因如下：

1. 真实项目验证依赖具体任务、代码事实、用户领域知识、测试环境和验收反馈，不是单纯文档更新。
2. Skill、Governance、Knowledge、Memory 都需要通过真实任务产生候选、审查和处置记录；只存在 policy 文档不能证明机制已闭环。
3. `projects/lfms-decision` 是已有 Java 项目，项目事实应先基于代码事实和用户知识补齐，再进入真实任务验证。
4. H9 的每个机制验证都需要可审阅证据，适合拆成子阶段分批验收。

因此，H9 改为多子阶段模型。只有 H9-0 到 H9-5 全部验收通过，才能把 H9 标记为 complete，并进入 H10 release readiness 判断。

## 7. H9 边界和口径

H9 验证锚点：

```text
projectId = lfms-decision
projectPath = projects/lfms-decision
projectType = existing-java-project
```

边界规则：

1. H9 使用 `projects/lfms-decision` 作为真实项目验证锚点；本文不记录该项目的私有业务事实。
2. 用户主导业务事实、领域语义和验收判断；agent 负责读取代码事实、整理文档、执行验证、提出候选改进。
3. 项目事实文档落地到 `projects/lfms-decision/docs/project/`，不写入 General Harness 文档。
4. 真实任务证据落地到项目 workflow evidence；本计划只记录阶段验收状态和摘要。
5. 未经用户明确要求，不直接修改真实项目业务源码。
6. 私有 settings、auth、密钥、未脱敏日志、私有仓库细节和本机绝对路径不得进入 tracked Harness 文档。
7. 从项目经验反向优化 Harness 时，只能先形成 candidate；进入长期 Harness 资产前必须 review 或用户批准。

## 8. H9 子阶段设计

| 子阶段 | 目标 | 主要输出 | 验收标准 | 进入下一阶段门禁 |
|---|---|---|---|---|
| H9-0 | 建立真实项目文档和事实基线 | 项目 ProjectIndex、PRD、API、Architecture、Repository、SourceLayout、Validation、TestStrategy、Acceptance、SensitiveBoundaries 等文档 | 文档按模板落地；事实有来源；未知项标记待确认；用户完成基线审阅 | 用户确认项目事实基线可用于真实任务验证 |
| H9-1 | 完成至少一个真实任务全流程 | Task Brief、执行计划、代码或配置变更、测试结果、验收记录、workflow evidence | 任务从入口、分析、设计、执行、测试到验收形成完整证据链 | 真实任务完成并经用户验收 |
| H9-2 | 验证 Skill 闭环 | Skill candidate 或已有 Skill patch candidate、review 结论、usage sidecar 更新候选 | candidate-first；与既有 Skill 去重；完成 approve/reject/archive 决策 | 至少一个真实任务驱动的 Skill 决策闭环完成 |
| H9-3 | 验证 Governance 闭环 | Governance candidates、风险判断、人工审批记录、治理收口记录 | candidate-first、review-first、human approval 被真实任务触发并完成处置 | 至少一个真实任务的治理收口通过 |
| H9-4 | 验证 Knowledge 和 Memory 闭环 | Knowledge candidate/review 记录、Memory candidate/review/active 或 reject/archive 记录 | 项目事实不污染通用知识；Memory 只晋升通用化经验；RAG index 只作为可重建产物 | Knowledge 和 Memory 至少各完成一次符合边界的闭环验证，或记录明确不适用原因 |
| H9-5 | 汇总 H9 验收并判断 H10 | H9 验收摘要、反向优化清单、残余风险、H10 go/no-go 建议 | H9-0 到 H9-4 证据齐备；未完成项有明确处置；用户决定是否进入 H10 | 用户批准进入 H10 或要求继续 H9 迭代 |

### 8.1 H9-0 真实项目文档和事实基线

目标：先补齐 `projects/lfms-decision` 的项目级文档闭环，让后续真实任务有稳定的项目事实入口。

输入来源：

- 项目代码事实。
- 已存在的项目文档或配置。
- 用户掌握的业务事实和验收口径。
- `harness/templates/project-template/docs/project/` 下的标准模板。

建议输出：

| 文档 | 目标路径 |
|---|---|
| 项目事实入口 | `projects/lfms-decision/docs/project/ProjectIndex.md` |
| PRD | `projects/lfms-decision/docs/project/prd/PRD.md` |
| API | `projects/lfms-decision/docs/project/api/Api.md` |
| 架构说明 | `projects/lfms-decision/docs/project/architecture/Architecture.md` |
| 仓库说明 | `projects/lfms-decision/docs/project/git/Repository.md` |
| 源码布局 | `projects/lfms-decision/docs/project/SourceLayout.md` |
| 测试策略 | `projects/lfms-decision/docs/project/TestStrategy.md` |
| 验证说明 | `projects/lfms-decision/docs/project/Validation.md` |
| 验收标准 | `projects/lfms-decision/docs/project/Acceptance.md` |
| 敏感边界 | `projects/lfms-decision/docs/project/SensitiveBoundaries.md` |
| 语义词典 | `projects/lfms-decision/docs/project/dictionary/SemanticDictionary.md` |
| 数据说明 | `projects/lfms-decision/docs/project/data/Data.md`，仅在项目确有数据模型或数据边界需要记录时落地。 |

H9-0 验收标准：

1. 项目根 `AGENTS.md` 和 `docs/project/ProjectIndex.md` 能作为项目入口和事实入口。
2. 重要项目 Markdown 文档具备 YAML frontmatter。
3. 每条重要事实标注来源：代码事实、配置事实、用户确认、待确认或推断。
4. 待确认事实不能伪装成已确认事实。
5. 文档不写入密钥、auth、私有 settings、未脱敏日志或本机绝对路径。
6. 用户完成项目事实基线审阅，明确哪些内容可用于 H9-1 真实任务验证。

H9-0 前置环境闭环结果：

| 项目 | 结果 |
|---|---|
| 本机 Java/Maven profile | `real-local-maven` 可被稳定工具发现，Maven version check 通过；真实 settings 和本地仓库只保存在 ignored local user boundary。 |
| 真实 E2E main 程序运行 | `invoke-java-main` 可自动编译并运行 `lfms-decision` 的选定 E2E main program。 |
| 用户验收 | S7 命令行输出已由用户确认通过；场景级固定输出不晋升为通用 Harness 规则。 |
| 下一步 | 下一轮可正式进入 H9-0 项目事实文档补齐。 |

### 8.2 H9-1 至少一个真实任务全流程验证

目标：以真实 Java 项目任务验证 Harness 的任务入口、证据链、工具调用、测试和验收流程。

验收标准：

1. 任务有 Task Brief，包含目标、projectId、范围、验收标准、验证计划、风险等级和是否需要审批。
2. 任务从项目 `AGENTS.md` 和 `ProjectIndex.md` 进入，不绕过项目事实入口。
3. 执行前有设计或实施计划；执行后有变更摘要、测试结果和验收记录。
4. 优先使用 stable tools；如必须使用临时命令，需要说明原因且不自动晋升为工具资产。
5. 任务证据保存到项目 workflow evidence。
6. 用户完成真实任务验收或明确退回原因。

### 8.3 H9-2 Skill 闭环验证

目标：用真实任务判断是否需要新增 Skill 或修补已有 Skill，并完成候选、审查和处置。

验收标准：

1. Skill 变更来源于 H9-1 或后续真实任务证据，不凭空创建。
2. 先检查已有 Skill 和工具资产，避免重复创建。
3. 产物先进入 candidate 或 patch candidate，不直接晋升 reviewed。
4. review 结论明确为 approve、reject、archive 或 revise。
5. 如果 approve，需要同步 usage sidecar 或相应索引；如果 reject/archive，需要记录原因。

### 8.4 H9-3 Governance 闭环验证

目标：用真实任务验证治理机制是否能处理风险、候选资产、审批和收口。

验收标准：

1. 真实任务中产生的治理事项先作为 candidate 进入 review。
2. 高风险或边界不清事项必须有人类审批，不由 agent 自行晋升长期资产。
3. Governance closeout 记录包含风险、证据、决策、处置和后续责任。
4. Report 仍不是事实源；Workflow Evidence 只产生候选，不直接成为长期事实。

### 8.5 H9-4 Knowledge 和 Memory 闭环验证

目标：验证 Knowledge 晋升和 Memory 晋升的边界，不让项目私有事实污染 General Harness。

验收标准：

1. Knowledge 只按 raw -> extracted -> candidate -> review -> reviewed 或 archive 流程晋升。
2. RAG index 只作为可重建检索产物，不作为权威事实源。
3. Memory 只保存通用化经验，不保存用户私有偏好、项目私有业务事实或敏感上下文。
4. 至少完成一次 Memory candidate -> review -> active/rejected/archive 路径验证。
5. 如果某类晋升在真实任务中不适用，需要记录不适用原因和后续触发条件。

### 8.6 H9-5 汇总和 H10 门禁判定

目标：把 H9 的真实项目验证结果转化为可审阅的阶段结论，并判断是否进入 H10。

验收标准：

1. H9-0 到 H9-4 的验收结果齐备。
2. 真实项目验证发现的问题形成 Harness 反向优化清单。
3. 需要修改架构权威的事项单独列为用户审批项，不直接写入 `HarnessEngineering.md`。
4. 残余风险、未完成项和建议下一步明确。
5. 用户决定进入 H10、继续 H9 迭代，或退回某个 H9 子阶段。

## 9. H10 目标

目标：H9 全部子阶段验收通过后，再判断是否进入 release readiness。H10 不默认发生，必须由用户审批。

验收标准：

| 标准 | 期望 |
|---|---|
| Release Candidate | H9 真实项目验证报告通过，残余风险可接受。 |
| 文档一致性 | Architecture、INDEX、HarnessIndex、README、Bootstrap、Tools、Verification、Governance 口径一致。 |
| GitHub 分支 | `agent-git` 已完成审查；是否合入 `main` 由用户决定。 |
| 发布动作 | `main` 合并、tag、release note 和正式发布只能由用户执行。 |

## 10. 计划维护规则

1. 阶段状态只写入本文。
2. 架构规则只写入 `HarnessEngineering.md`。
3. 路由入口同步写入 `INDEX.md` 和 `harness/HarnessIndex.md`。
4. 任一阶段完成前，必须记录验收结果和未完成项。
5. 任何涉及 Knowledge、Memory、Skill、Project Fact 或 Governance 晋升的结果，必须经过 review 或用户明确批准。
6. 真实项目事实和真实任务证据写入项目文档或项目 workflow evidence；本文只记录阶段计划和验收摘要。
