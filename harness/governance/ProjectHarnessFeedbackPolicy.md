---
documentName: harness/governance/ProjectHarnessFeedbackPolicy.md
version: v1.0.0-project-feedback-policy
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 定义真实项目任务如何反向优化通用 Harness 的信号分类、候选落点、审核门禁、资产晋升和验证规则。
scope:
  - project-harness-feedback
  - governance
  - promotion-classification
  - memory-promotion-boundary
  - skill-promotion-boundary
  - knowledge-promotion-boundary
  - project-code-standards
  - tool-template-policy-feedback
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/governance/GovernanceIndex.md
  - harness/governance/ArtifactLifecycle.md
relatedDocuments:
  - harness/governance/GovernanceIndex.md
  - harness/governance/ArtifactLifecycle.md
  - harness/governance/MemoryGovernance.md
  - harness/governance/SkillGovernance.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md
  - harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
  - harness/tools/scripts/stable/test-harness-governance.ps1
outputTo:
  - harness/governance/ProjectHarnessFeedbackPolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/governance/ArtifactLifecycle.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: project-feedback-policy-created
---
# Project Harness Feedback Policy（项目反向优化 Harness 策略）

本文定义真实项目经验如何反向优化通用 Harness。它补充 `ArtifactLifecycle.md`：生命周期规则说明 candidate-first 和 review-first；本文说明真实项目信号应如何分类、落到哪类候选资产、哪些内容不得晋升。

## 1. 基本定位

真实项目任务可以暴露 Harness 的入口、工具、Skill、Memory、Knowledge、模板、验证和治理缺口，但项目事实不能直接进入通用 Harness。

反向优化的基本链路是：

```text
project task / project evidence
-> feedback signal
-> sensitivity and boundary check
-> target asset classification
-> candidate or triage record
-> asset-specific gate
-> human review or explicit approval
-> update target asset and indexes
-> validation and closeout
```

约束：

1. Workflow Evidence 和 Report 是来源证据，不是长期事实源。
2. 项目代码事实、项目业务事实、测试数据、私有日志和本机路径留在项目实例或本地边界。
3. 通用 Harness 只能吸收抽象后的流程、规则、模板、工具契约、治理门禁和非私有通用经验。
4. 任何跨 Knowledge、Memory、Skill、Project Fact、Tool、Template、Governance 或 Architecture 的晋升都必须记录来源、目标资产、审批要求和验证命令。

## 2. 信号分类矩阵

| 项目信号来源 | 需要回答的问题 | 默认候选类型 | 默认目标资产 | 必需门禁 | 禁止事项 |
|---|---|---|---|---|---|
| workflow evidence 中反复出现的操作经验 | 是否短小、通用、未来可复用，且不是事实或流程手册 | `Memory` | `harness/memory/candidate/`，审核后进入 `harness/memory/reviewed/` | `memory-governance-use` Skill，`invoke-memory.ps1 validate-memory-store`，用户 review | 把一次性任务历史、项目业务事实、用户私有偏好写成 Memory |
| workflow evidence 中可复用的多步骤流程 | 是否能成为一类任务的执行方法 | `Skill` | `harness/skills/candidate/`，审核后进入 `harness/skills/reviewed/` | `SkillGovernance.md`，现有 Skill 去重，用户 approve，usage sidecar 更新 | 把项目私有路径、真实数据、未脱敏日志写入 Skill |
| 项目代码暴露出的稳定规范 | 是项目专属规范，还是跨项目代码规范 | `ProjectFact` 或 `Template` / `Governance` / `Skill` | 项目规范进入项目文档；跨项目规范进入项目模板、治理策略或 code review Skill | 项目代码证据、适用范围说明、冲突检查、用户 review | 直接把真实项目源码或私有实现复制到通用 Harness |
| 项目开发、调试、测试方式 | 是否能形成测试 Skill、开发 Skill、稳定工具或验证门禁 | `Skill` 或 `Tool` / `Verification` | `harness/skills/candidate/`、`harness/tools/`、`harness/verification/` | 可执行命令、失败模式、脱敏日志、self-test 或真实项目验证 | 只写文档不提供可执行入口却声称已形成工具机制 |
| 项目领域知识或外部材料 | 是否是人类和 Agent 需要长期阅读的知识 | `Knowledge` 或 `ProjectFact` | 用户知识库 `user/knowledge/` 或外部 private knowledge repo；项目事实进入项目文档 | `KnowledgePromotionPolicy.md`，raw -> candidate -> reviewed，source trace，用户 review | 把用户知识正文或项目领域事实写入通用 Harness Git |
| 项目文档结构缺口 | 是否说明项目模板不完整 | `Template` | `harness/templates/project-template/` | 模板通用化、占位符化、无项目事实、索引同步 | 把某个项目的具体内容写入模板 |
| 项目执行中的治理缺口 | 是否需要新增审批、清理、晋升或边界规则 | `Governance` 或 `Verification` | `harness/governance/`、`harness/verification/`、稳定脚本 | policy 更新、必要时脚本门禁、governance self-check | 只用 Mermaid 或口头规则替代关键门禁 |
| 重复使用的临时命令或脚本 | 是否需要稳定命令面 | `Tool` | `harness/tools/scripts/stable/` 与工具文档 | 输入输出契约、dry-run 或 self-test、脱敏日志、ScriptIndex 同步 | 未稳定的一次性脚本直接进入 stable |
| 通用架构边界变化 | 是否改变 Harness 长期设计 | `Architecture` | `harness/architecture/HarnessEngineering.md` | 单独列为用户审批项，更新索引和计划 | 未经用户明确批准直接改写架构权威 |
| 只用于说明一次任务结果 | 是否只是证据或报告 | `Report` | 项目 report 或通用 redacted report | 报告边界、敏感信息检查、后续候选分离 | 把 report 结论自动当作事实源 |

## 3. 用户意见的治理解释

### 3.1 从 workflow 沉淀通用 Memory

成立，但只适用于“短小、通用、非私有、未来可复用”的经验。若内容是多步骤流程，应优先成为 Skill；若内容是项目事实，应留在项目文档；若内容是知识，应进入 Knowledge。

### 3.2 从项目代码沉淀代码规范

成立，但需要先判断规范层级：

| 层级 | 落点 |
|---|---|
| 项目专属规范 | `projects/<project-id>/docs/project/` 下的项目规范、测试或仓库文档 |
| 可复制项目模板规范 | `harness/templates/project-template/` |
| 跨项目评审规则 | code review Skill 或 Governance policy |
| 可执行检查 | stable tool 或 Verification gate |

代码规范沉淀必须基于代码事实和测试反馈，不复制真实业务源码，不把项目业务策略伪装成通用规范。

### 3.3 从项目开发沉淀测试 Skill、开发 Skill 等

成立。触发条件包括：

1. 同一类开发、调试、测试或排障步骤在多个任务中重复出现；
2. 已有 Skill 不能覆盖；
3. 过程有明确输入、步骤、产物、验证和失败处理；
4. 可以脱离单个项目私有上下文复用。

如果流程依赖可执行命令，应同时判断是否需要稳定工具或验证门禁。Skill 说明流程，Tool 保证精确执行。

### 3.4 从项目知识沉淀知识库

成立，但知识正文默认进入 `user/knowledge/` 或外部 private knowledge repo，不进入通用 Harness Git。项目事实进入项目文档；跨项目通用知识经 raw -> candidate -> reviewed 后进入知识库；RAG index 仍是可重建运行态产物。

### 3.5 其他可反向优化项

真实项目还可能沉淀：

| 类型 | 典型触发 | 目标 |
|---|---|---|
| Tool | 临时命令反复使用，且需要固定输入输出 | 稳定脚本、工具文档、manifest |
| Template | 项目文档结构重复缺口 | 项目模板或报告模板 |
| Governance | 审批、清理、归档、晋升边界不稳定 | Governance policy 或验证脚本 |
| Verification | 测试、报告、验收证据缺少可执行检查 | Verification policy 或 stable gate |
| Observability | 失败归因、日志结构、状态码不足 | Observability schema 或 failure attribution 模板 |
| Architecture | 长期边界需要调整 | 单独用户审批后的架构权威更新 |

## 4. 标准执行流程

真实项目任务收口时，按以下顺序处理反向优化：

1. 读取项目入口和 workflow evidence，确认来源证据完整。
2. 列出项目任务暴露的反馈信号，不立即改写通用资产。
3. 对每个信号做敏感边界检查，排除 credentials、settings、未脱敏日志、本机路径、真实业务数据和私有仓库细节。
4. 使用本文的信号分类矩阵选择候选类型。
5. 检查现有 Memory、Skill、Knowledge、Tool、Template、Governance 和 Verification 是否已经覆盖。
6. 使用 `ProjectHarnessFeedbackTriageTemplate.md` 或项目 report 记录 triage 结论。
7. 对目标资产运行对应门禁：Memory 用 Memory gate，Skill 用 Skill review，Knowledge 用 Knowledge promotion gate，Tool 用工具 self-test，项目证据用 project lifecycle evidence gate。
8. 需要用户审批的事项保持 candidate 或 needs-user-review，不自行晋升。
9. 获批后更新目标资产、索引、usage sidecar、reviewAfter 和必要的验证文档。
10. 运行治理自检和目标资产自检，记录结果。

## 5. 候选输出规则

| 候选类型 | 最小输出 |
|---|---|
| Memory | memory candidate、source evidence、suitability、duplicate/conflict 检查、review package |
| Skill | candidate Skill、trigger、inputs、procedure、verification、failure handling、现有 Skill 去重 |
| Knowledge | raw source、candidate、review package、promotion plan、source trace、reviewed page 或 reject/defer 记录 |
| Tool | 稳定命令或候选命令、输入输出契约、脱敏日志、失败模式、自测或真实验证 |
| Template | 通用模板改动、占位符、实例化规则、索引更新 |
| Governance | policy 改动、适用范围、审批边界、必要时脚本门禁 |
| Architecture | 用户审批项、设计差异、影响范围、索引同步 |
| Project Fact | 项目文档更新、来源、review 状态、项目验收记录 |

## 6. 必须保留的边界

禁止路径：

```text
project source code -> General Harness Git
private project fact -> Memory
private project knowledge -> General Harness Git
workflow evidence -> reviewed asset without review
report conclusion -> architecture authority without approval
runtime log -> Knowledge / Memory / Skill
temporary script -> stable tool without contract and validation
project-specific command output -> universal test rule without abstraction
```

## 7. 验证和收口

项目反向优化收口至少需要：

1. 项目任务证据通过项目生命周期证据检查，或说明该任务不是项目执行任务。
2. 每个反馈信号都有 disposition：absorbed、candidate、defer、reject、archive、no-action 或 needs-user-review。
3. 每个 absorbed 或 promoted 项都有目标资产、索引更新和验证命令。
4. 每个 deferred 项都有后续触发条件。
5. 每个 rejected 项都有理由。
6. 运行 `test-harness-governance.ps1`，确保通用 Harness 边界未被污染。

当前最低可执行门禁：

```text
harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
harness/tools/scripts/stable/test-harness-governance.ps1
harness/tools/scripts/stable/invoke-memory.ps1
harness/tools/scripts/stable/invoke-rag-knowledge.ps1
```

如果后续需要把项目反向优化 triage 本身变为一键检查，应新增稳定脚本检查 triage 表、候选落点、审批状态、索引更新和资产自检结果。在该脚本落地前，不能声称项目反向优化已经完全自动化。
