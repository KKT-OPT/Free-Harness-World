---
documentName: docs/archive/design-history/architecture/HarnessEngineering-draft.md
title: Harness Engineering 项目自动化框架设计草稿
status: archived
version: v0.2.1-archived-post-p11-cleanup
createdAt: 2026-06-08
language: zh-CN
type: architecture-design
stage: P1
owner: human
absorbedBy:
  - docs/architecture/HarnessEngineering.md
  - docs/PLANS.md
sourceNote: Earlier temporary source drafts were absorbed and deleted during P11.8/Post-P11 cleanup.
externalReferences:
  - https://hermes-agent.nousresearch.com/docs/user-guide/security
---

# Harness Engineering 项目自动化框架设计草稿

## 1. 文档定位

本文是 P1 阶段的 `HarnessEngineering` 中文草稿，用于把当前框架从“沙盒脚本 + 旧 HarnessVault 文档治理”重构为面向智能体的项目自动化框架。

本文不执行目录迁移，不移动脚本，不创建真实项目实例，不替换 Hermes 或 Codex 的运行时实现。本文只定义目标架构、职责边界、资产模型、任务生命周期和后续落地标准。

本文采用三视图结构：

| 视图 | 中文含义 | 解决的问题 |
|---|---|---|
| Task Lifecycle View | 任务生命周期视图 | 用户任务如何从提示词走到执行、验证、验收和治理沉淀 |
| Asset Model View | 资产模型视图 | Harness 管理哪些稳定资产，以及这些资产的边界 |
| Directory Mapping View | 目录映射视图 | 这些资产最终如何落到 `<HARNESS_ROOT>` 目录 |

本文中的专业英文术语会尽量保留英文原词，并在首次出现或术语表中给出中文解释，防止语义偏移。

## 2. 旧口径修正

旧 HarnessVault 设计中成熟的资产治理思想需要保留，包括模板、RAG、Memory、Skill、workflow、reports、promotion、archive 等。

但是旧口径不再完整适用于当前目标。需要明确废弃或修正以下表述：

| 旧口径 | 新口径 |
|---|---|
| Harness 主要是文档资产治理系统 | Harness 是面向 agent 的项目自动化控制层、工具资产层和治理层 |
| Harness 不包含 sandbox 或脚本工具 | Harness 可以拥有本地沙盒设施、稳定脚本和命令门面 |
| Project Harness Instance 是复制通用 Harness 模板到项目 | 采用中央 Harness Root + 项目 Profile/入口，不复制整套 Harness |
| RAG、Memory、Skill、Project Facts 可以归为一层 | Skill、Knowledge、Memory、Project Facts、RAG Index 必须分开 |
| RAG 是知识库本身 | RAG Index 是可重建的检索索引，不是事实来源 |
| Governance 是流程末层 | Governance 是横切约束和任务收口机制 |

因此，当前目标不是修补旧文档，而是重写 `HarnessEngineering` 的总体定义和边界。

## 3. 术语表

| 术语 | 中文解释 |
|---|---|
| Agent | 智能体。能够理解任务、调用工具、读写文件、执行命令并与用户交互的执行主体。 |
| Agent Runtime | 智能体运行时。指 Hermes、Codex 或未来其他 agent 的会话、推理、工具调用和用户交互执行环境。 |
| Harness | 本框架。面向 agent 的项目自动化控制层、工具资产层和治理层。 |
| Harness Root | Harness 根目录。当前统一为 `<HARNESS_ROOT>`，也是本地沙盒位置。 |
| Sandbox | 沙盒。用于限制 agent 执行范围、隔离运行态和降低误操作风险的环境。当前是本地沙盒，未来可升级为 Docker 或虚拟机。 |
| Task Lifecycle | 任务生命周期。从用户提示词到任务执行、验证、验收、修复和治理沉淀的完整过程。 |
| Task Brief | 任务简报。agent 从自然语言提示词中整理出的结构化任务理解，记录目标、范围、验收标准、推断和缺失项。 |
| Readiness Check | 就绪检查。执行前判断任务信息是否足够、风险是否可接受、是否需要先向用户澄清。 |
| Project Profile | 项目配置画像。根注册表中的轻量配置，记录 projectId、项目入口、默认验证 profile、知识作用域、命令门面和敏感边界。 |
| Project Facts | 项目事实。某个受管项目内部的权威事实，包括架构、源码位置、测试命令、验收标准、项目决策等。 |
| Skill | 技能。面向某类任务的可复用工作流，例如架构设计 skill、代码审查 skill、故障归因 skill。Skill 是流程，不是知识事实。 |
| Knowledge | 知识。经过整理、结构化和审核的稳定信息，可以被引用和检索。 |
| Memory | 记忆。具体经验、偏好、修复路径、测试窍门等，具有作用域、置信度和过期风险。 |
| RAG | Retrieval-Augmented Generation，检索增强生成。中文含义是模型回答前先检索相关资料，再基于资料生成结果。 |
| RAG Index | RAG 索引。由知识、项目事实和元数据派生出的检索结构，例如 chunks、embedding、关键词索引、向量库集合。它不是事实来源。 |
| Tool Assets | 工具资产。稳定脚本、命令门面和 helper scripts，用于让 agent 以可重复方式执行验证、构建、检查等动作。 |
| Evidence | 证据。任务执行过程中产生的 Task Brief、命令记录、验证结果、日志路径、失败归因和验收记录。 |
| Harness Run Card | Harness 运行卡。一次任务运行的披露记录，描述 runtime、入口版本、工具表面、sandbox/approval profile、上下文来源、验证协议和证据路径。 |
| Handoff Contract | 交接合同。agent、tool、human 或 runtime 之间转交任务时必须携带的意图、约束、权限、证据、预算、风险和未决问题。 |
| Governance | 治理。安全、审批、归档、晋升、清理、git 边界、运行态边界和任务收口规则。 |
| Structured Ingestion | 结构化摄取。把 PDF、网页、图片、DOCX 等原始非结构化资料解析为带来源、结构和元数据的候选语料。 |
| Profile | 配置画像。描述某个项目、工具或验证场景的默认配置集合。 |
| tracked | 被 git 跟踪。表示文件默认应进入版本管理。 |
| ignored | 被 git 忽略。表示文件默认不进入版本管理，通常用于缓存、日志、运行态目录或敏感内容。 |
| front matter | 文档头部结构化元数据。通常放在 Markdown 文件顶部，用 YAML 描述文档状态、标签、来源等。 |
| JSONL | 一行一个 JSON 对象的文本格式。适合保存批量 chunk、事件或评估样本。 |
| chunk | 文档切片。把长文档拆成较小片段，供检索或索引使用。 |
| embedding | 向量表示。把文本、图片等内容转为数值向量，用于相似度检索。 |
| vector store | 向量库。保存 embedding 并支持相似度搜索的数据库或本地组件。 |
| rerank | 重排序。检索出候选结果后，再用额外模型或规则重新排序，提高相关性。 |
| Docker | 容器隔离技术。可作为未来生产网关执行环境，用较轻量的方式隔离 agent 命令。 |
| Virtual Machine | 虚拟机。比容器更强的隔离边界，成本更高，但适合高风险或强隔离场景。 |

## 4. 总体定义

Harness 是一个面向 agent 的项目自动化控制与资产治理框架。

它的核心目标是：让 Hermes、Codex 或未来其他 agent 在真实项目中执行任务时，能够从统一入口发现约束，理解任务，定位项目上下文，调用稳定工具，产出验证报告，并把可复用经验通过治理流程沉淀为长期资产。

Harness 拥有：

- 入口协议和发现规则；
- 任务理解、Task Brief 和就绪检查规则；
- 项目注册、Project Profile 和项目实例规范；
- 项目模板、项目事实结构和工作流证据规范；
- 稳定脚本、命令门面和工具资产；
- Skill、Knowledge、Memory、Project Facts 和 RAG Index 的资产边界；
- 验证报告、失败归因、修复闭环和验收记录；
- 安全、审批、凭据、git 边界、运行态边界和归档治理。

Harness 不拥有：

- 大模型调用内核；
- agent 的会话循环；
- Hermes、Codex 或其他 agent runtime 的内部状态；
- 用户私密凭据；
- 未脱敏原始终端日志；
- 原始模型上下文；
- 真实业务项目的完整事实副本。

一句话边界：

```text
Harness 定义 agent 如何安全、稳定、可审计地自动化项目。
Agent Runtime 负责推理、交互、工具调用和具体执行。
Sandbox 提供受控运行环境。
```

## 5. 总体架构原则

1. 任务生命周期是主架构。
2. 资产模型是支撑体系，不等于流程层级。
3. 目录结构是落地映射，不等于架构本身。
4. `<HARNESS_ROOT>` 是 Harness Root，也是当前本地沙盒位置。
5. `AGENTS.md` 是根入口，但不能变成知识大杂烩。
6. 详细规则必须通过索引路由到对应文档。
7. 用户提示词不要求符合固定模板，agent 用模板做语义理解标尺。
8. 高风险任务缺少目标、范围、验收标准或风险边界时，必须先澄清。
9. 高置信推断可以执行，但必须记录推断来源。
10. 真实项目以受管工作副本形式放入 `projects/<project-id>`。
11. 真实业务项目保持独立 git 边界，不混入 Harness 根仓库。
12. Governance 是横切约束，不是普通流程末层。
13. RAG 优先本地、免费或开源、私人化、安全和成熟方案。
14. 任何 workflow evidence 不会自动成为长期事实，必须经过 review 或 promotion。
15. Harness policy，中文解释是运行策略，应尽量和 deterministic mechanism，中文解释是确定性机制，分离；策略可读、可审计，机制可重复、可验证。
16. ETCLOVG，中文解释是 Execution、Tooling、Context、Lifecycle、Observability、Verification、Governance 七层检查镜头，可用于检查 Harness 覆盖面，但不替代当前任务生命周期主架构。
17. 长任务的上下文、记忆和摘要必须带 provenance，中文解释是来源追踪，以及 staleness，中文解释是陈旧性，不能把压缩上下文当作事实。
18. workflow evidence 应披露 Harness Run Card，避免把模型能力、工具能力和 Harness 配置混在一起评价。
19. 结构化摄取工具可以帮助 RAG 建库，但其输出只能先进入 extracted/candidate 状态，不能自动成为 reviewed Knowledge。

## 6. 三视图总览

### 6.1 Task Lifecycle View

任务生命周期是主架构：

```text
用户提示词
-> Agent Runtime 接收任务
-> Harness 入口发现
-> Task Brief 语义化校验
-> Readiness Check 与澄清
-> 上下文和知识路由
-> 项目实例定位
-> 执行计划
-> 稳定工具调用
-> 验证报告
-> 用户验收或修复请求
-> Governance 沉淀
```

### 6.2 Asset Model View

资产模型回答 Harness 管理什么：

```text
Entry Assets
Policy Assets
Template Assets
Skill Assets
Knowledge Assets
Memory Assets
Project Fact Assets
Tool Assets
Evidence Assets
RAG Index Assets
Governance Assets
```

### 6.3 Directory Mapping View

目录映射回答这些资产放在哪里：

```text
<HARNESS_ROOT>\
  AGENTS.md
  docs\
  skills\
  knowledge\
  memory\
  templates\
  scripts\
  config\
  projects\
  var\
  tools\
  settings\
```

### 6.4 ETCLOVG 检查镜头

ETCLOVG 是从近期 agent harness 文献中吸收的检查镜头，用于防止设计只覆盖文档和目录，而遗漏真实运行系统中的关键层：

| Layer | 中文解释 | 当前 Harness 对应面 |
|---|---|---|
| Execution | 执行环境和 sandbox | `sandbox/`、`var/`、P8 安全模型 |
| Tooling | 工具接口和协议 | `scripts/`、`tools/`、`docs/tools/` |
| Context | 上下文、知识、记忆和 RAG | `knowledge/`、`memory/`、`rag/`、Project Facts |
| Lifecycle | 任务生命周期和状态流转 | Task Brief、Workflow、Project Profile |
| Observability | 可观测性、trace、失败归因 | workflow evidence、`docs/observability/` |
| Verification | 验证、评估和回归 | validation profile、稳定工具输出 |
| Governance | 审批、权限、审计和晋升 | `docs/governance/security/`、`docs/governance/` |

该镜头只作为 completeness check，中文解释是完整性检查。Harness 的主结构仍然是任务生命周期；资产模型和目录映射仍然是支撑体系。

## 7. 任务生命周期视图

### 7.1 生命周期表

| 阶段 | Harness 职责 | Agent Runtime 职责 | 产物 | 完成标准 |
|---|---|---|---|---|
| 用户提示词 | 定义提示词理解规则 | 接收自然语言任务 | 原始提示词摘要 | 保留用户真实意图 |
| 入口发现 | 提供 `AGENTS.md`、索引和读取顺序 | 从 `HARNESS_ROOT` 或 cwd 读取入口 | 入口读取记录 | 找到 Harness Root |
| Task Brief | 提供模板和字段语义 | 提取目标、范围、验收、风险和缺失项 | Task Brief | 明确显式项、推断项和缺失项 |
| Readiness Check | 定义澄清规则 | 判断是否可执行或需提问 | 就绪检查记录 | 高风险缺失项不被跳过 |
| 上下文路由 | 定义读取优先级和知识作用域 | 加载最小必要上下文 | 上下文清单 | 没有盲目加载全部资料 |
| 项目定位 | 提供项目注册表和 Profile | 定位 `projects/<project-id>` | projectId 与项目入口 | 项目事实来自项目根 |
| 执行计划 | 定义计划记录格式 | 规划文件、命令、验证和回滚路径 | 执行计划 | 用户或 workflow 可审计 |
| 稳定工具调用 | 提供命令门面和脚本规范 | 调用稳定工具并记录结果 | status JSON、log path | 不手搓不稳定命令链 |
| 验证报告 | 定义报告格式和证据要求 | 汇总验证结果和失败归因 | 验证报告 | 可判断通过、失败或部分完成 |
| 用户验收 | 定义验收记录 | 回复用户并接收反馈 | 验收结果 | 用户能继续修复任务 |
| 治理沉淀 | 定义 promotion 和 archive | 提交候选沉淀项 | 候选 Project Fact、Memory、Skill、Knowledge | 不自动污染长期资产 |

### 7.2 用户提示词

用户可以通过企业微信、Hermes CLI、Codex 会话或未来其他入口提交任务。用户不需要填写固定表单。

示例：

```text
给 java-demo 项目新增 multiply 功能，补充测试，跑完验证后告诉我结果。
```

agent 必须把自然语言任务转成 Task Brief，而不是要求用户先学习模板。

### 7.3 Harness 入口发现

当前发现规则：

```text
cwd = <HARNESS_ROOT>
HARNESS_ROOT = <HARNESS_ROOT>
```

根入口：

```text
<HARNESS_ROOT>\AGENTS.md
```

推荐读取顺序：

```text
1. AGENTS.md
2. docs/INDEX.md
3. docs/PLANS.md
4. task-specific policy / template / skill
5. project registry
6. project-level AGENTS.md
7. project docs/project/ProjectIndex.md
```

`AGENTS.md` 只保留最高优先级硬约束、读取顺序和少量关键稳定记忆。大部分规则、模板、Skill、Knowledge 和治理政策必须通过索引文档路由。

### 7.4 Task Brief 语义化校验

Task Brief 是 agent 对任务的结构化理解。它不是用户输入格式。

建议字段：

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
risk:
  level: low | medium | high
  reasons: []
approvalRequired: true | false
missingCriticalFields: []
inferredFields:
  - field: <字段名>
    value: <推断值>
    reason: <推断依据>
```

Task Brief 必须保存到项目 workflow 开始处。

### 7.5 Readiness Check 与澄清

高风险任务包括：

- 修改源码；
- 执行会改变项目状态的命令；
- 变更项目事实；
- 变更治理规则；
- 触碰凭据、私有配置或敏感目录；
- 修改 git 历史；
- 发布、推送或部署。

以下关键字段缺失或冲突时，高风险任务必须先向用户澄清：

- 目标；
- 范围；
- 项目；
- 验收标准；
- 风险边界；
- 是否允许写文件或执行命令。

高置信推断可以执行，但必须记录推断依据。例如从项目 Profile 推断默认 Maven 验证命令。

### 7.6 上下文和知识路由

上下文优先级：

```text
当前用户指令
> Harness 硬约束和治理硬约束
> Project Facts
> approved Skill
> reviewed Knowledge
> relevant Memory
> workflow evidence
> active reports
> archived reports
```

当前用户指令不能覆盖安全、隐私、git 边界、审批和治理硬停止规则。

RAG Index 只能帮助检索上下文，不能作为事实来源。回答必须能追溯到 reviewed Knowledge、Project Facts 或明确的源文件。

### 7.7 项目实例定位

受管项目位于：

```text
<HARNESS_ROOT>\projects\<project-id>
```

每个受管项目必须包含：

```text
projects/<project-id>/AGENTS.md
projects/<project-id>/docs/project/ProjectIndex.md
```

项目事实存放在项目工作副本内。Harness 根注册表只保存路由元数据，不复制项目事实正文。

### 7.8 执行计划

执行前，agent 应在 workflow 中记录计划：

- 预计修改的文件或模块；
- 使用的 Skill；
- 使用的 Tool Assets；
- 验证命令；
- 预期证据；
- 失败后的修复路径；
- 需要用户审批的动作。

计划可以简短，但不能完全缺失。

### 7.9 稳定工具调用

Harness 暴露稳定命令门面，而不是让 agent 每次临时拼命令。

当前 Java/Maven 工具资产：

```text
scripts/stable/show-java-maven-config.ps1
scripts/stable/invoke-maven-project.ps1
scripts/stable/invoke-java-main.ps1
scripts/stable/clean-sandbox.ps1
```

后续应在 P7 阶段建立脚本索引和稳定命令门面。

工具输出至少包含：

- pass/fail 状态；
- status JSON 路径；
- log 路径；
- 关键命令参数；
- 敏感信息处理说明。

### 7.10 验证报告

验证报告必须说明：

- 做了什么；
- 改了哪些文件；
- 执行了哪些验证；
- 哪些验收标准通过；
- 哪些失败；
- 失败归因；
- 剩余风险；
- 下一步动作。

原始日志不是最终报告。未脱敏原始日志默认不进入 git。

验证报告之前或 workflow evidence 开头应记录 Harness Run Card，至少包含：

- runtime 和 channel；
- 入口文档版本；
- projectId 和 Project Profile；
- sandbox/approval profile；
- 使用的 Skill、Tool Assets 和命令表面；
- context sources，中文解释是上下文来源；
- knowledge scopes，中文解释是知识作用域；
- validation profile；
- evidence paths；
- 敏感信息处理说明。

Harness Run Card 的目的不是增加表格负担，而是让后续评价能区分模型、工具、上下文、sandbox 和治理配置对结果的影响。

### 7.11 用户验收和修复闭环

用户判断是否接受结果。

如果用户不接受，下一轮任务必须读取上一轮 workflow evidence 和失败归因，不得丢弃既有验收标准。

修复任务也是完整生命周期，不是随意补丁。

### 7.12 治理沉淀

任务完成后，agent 可以提出候选沉淀：

- Project Fact 更新；
- Memory 更新；
- Skill 更新；
- Knowledge 更新；
- Template 更新；
- Tool Asset 改进；
- Governance 修正规则。

候选不等于生效。长期资产必须经过 review 或明确用户批准。

## 8. 运行时边界

### 8.1 职责矩阵

| 主体 | 拥有 | 不拥有 |
|---|---|---|
| 用户 | 目标、验收判断、授权、风险接受 | agent 内部推理细节 |
| Agent Runtime | 推理、会话、工具调用、文件编辑、命令执行、用户交互 | Harness 资产事实、治理规则最终归属 |
| Harness | 入口、约束、项目路由、稳定工具、资产治理、验证报告规范 | 模型调用内核、agent 会话存储、私密凭据 |
| Sandbox | 受控文件系统、运行态目录、隔离路径、工具执行环境 | 长期知识事实、用户验收结论 |
| Project | 项目源码、项目事实、项目 workflow、项目级约束 | 根 Harness 通用治理规则 |

### 8.2 修正后的边界声明

```text
Harness owns stable control contracts, stable tool assets, project routing, validation policy, and governance.
```

中文解释：Harness 拥有稳定控制契约、稳定工具资产、项目路由、验证策略和治理规则。

```text
Agent runtime owns reasoning, tool invocation, session execution, and user interaction.
```

中文解释：agent runtime 拥有推理、工具调用、会话执行和用户交互。

```text
Local sandbox facilities under Harness Root provide the controlled environment where stable tools operate.
```

中文解释：Harness Root 下的本地沙盒设施提供稳定工具运行的受控环境。

## 9. 项目模型

### 9.1 中央 Harness Root + 项目 Profile

当前采纳的项目植入模型：

```text
Central Harness Root
-> project registry
-> project Profile
-> project root AGENTS.md
-> project docs/project/ProjectIndex.md
-> project facts, source, validation, workflow
```

中文解释：不把整套 Harness 复制到每个项目，而是由中央 Harness Root 管理通用规则，项目通过 Profile、项目入口和项目事实完成定制。

### 9.2 Project Profile 示例

```yaml
projectId: java-demo
root: projects/java-demo
entry: AGENTS.md
projectIndex: docs/project/ProjectIndex.md
defaultValidationProfile: isolated-sandbox-maven
knowledgeScopes:
  - project-reviewed:java-demo
  - domain:java
  - global
sensitiveBoundaries:
  - .env
  - settings*.xml
  - secrets/**
defaultCommands:
  validate: invoke-maven-project
```

Project Profile 只记录路由和默认值，不保存完整项目事实。

### 9.3 Project Facts

项目事实包括：

- 业务目标和范围；
- 源码目录；
- 模块边界；
- 构建系统；
- 测试策略；
- 默认验证命令；
- 敏感边界；
- 架构决策；
- workflow 历史；
- 已接受的项目约束。

项目事实优先级高于通用知识，但不能覆盖 Harness 根安全和治理硬约束。

## 10. 资产模型视图

### 10.1 资产分类

| 资产类 | 中文解释 | 典型位置 | Git 策略 |
|---|---|---|---|
| Entry Assets | 入口资产 | `AGENTS.md`、`docs/INDEX.md` | tracked |
| Policy Assets | 策略资产 | `docs/governance/` | tracked |
| Template Assets | 模板资产 | `templates/` | tracked |
| Skill Assets | 技能工作流资产 | `skills/`、`docs/skills/` | reviewed 后 tracked |
| Knowledge Assets | 知识资产 | `knowledge/`、`docs/knowledge/` | reviewed tracked，raw selective |
| Memory Assets | 经验记忆资产 | `memory/`、`docs/memory/` | reviewed 后 tracked |
| Project Fact Assets | 项目事实资产 | `projects/<project-id>/docs/project/` | 在项目仓库中 tracked |
| Tool Assets | 工具资产 | `scripts/`、`tools/` | stable tracked |
| Evidence Assets | 证据资产 | project workflow、`docs/reports/` | redacted tracked |
| RAG Index Assets | 检索索引资产 | `var/rag/`、`knowledge/indexes/` | 默认 ignored |
| Governance Assets | 治理资产 | `docs/governance/`、`docs/governance/verification/` | tracked |

### 10.2 Skill Assets

Skill 是可复用任务工作流，不是知识事实。

Skill 应包含：

- 适用场景；
- 输入要求；
- 执行步骤；
- 使用的 Tool Assets；
- 需要读取的 Project Facts 或 Knowledge；
- 验收标准；
- 输出格式；
- 失败处理；
- 何时必须向用户澄清。

示例：

```text
architecture-design skill
code-review skill
failure-attribution skill
java-feature-implementation skill
knowledge-promotion skill
```

### 10.3 Knowledge Assets

知识是稳定、结构化、可引用的信息。

知识作用域：

| Scope | 中文解释 | 示例 |
|---|---|---|
| global | 全局知识，跨领域和项目复用 | 通用代码审查规则 |
| domain | 领域知识，在某个领域内复用 | Java/Maven 规范、飞行器机型参数 |
| project-reviewed | 项目审核知识，只对某项目稳定 | 某项目模块边界、验收命令 |

不是所有项目稳定知识都进入 global。只有跨项目可复用、已审核、无敏感内容的信息才可晋升。

### 10.4 Memory Assets

Memory 是经验，不是稳定领域事实。

Memory 应记录：

- 来源；
- 适用范围；
- 置信度；
- 失效条件；
- review 时间；
- 是否可推广为 Skill 或 Knowledge。

示例：

```text
java-demo 的某个测试经常因为本地时区失败，应优先检查 timezone 配置。
```

这类信息是经验，不能直接当作领域知识。

### 10.5 RAG Index Assets

RAG Index 是派生产物，可重建。

来源可以是：

- reviewed Knowledge；
- Project Facts；
- approved metadata；
- redacted reports；
- reviewed Memory。

RAG Index 必须保留 metadata：

```yaml
sourceRef: <源文档>
scope: global | domain | project-reviewed
projectId: <optional>
domain: <optional>
status: reviewed | candidate | archived
chunkId: <stable-chunk-id>
reviewedAt: <date-or-null>
```

## 11. 知识库和 RAG 策略

### 11.1 知识生命周期

```text
raw source
-> extracted content
-> structured content
-> candidate knowledge
-> reviewed knowledge
-> indexed retrieval artifact
-> deprecated or archived
```

中文解释：

- raw source：原始资料，例如 PDF、图片、Markdown、网页导出、代码片段；
- extracted content：提取后的文本、表格、OCR、元数据；
- structured content：结构化内容，例如章节树、表格块、图片引用、source coordinates 和 metadata；
- candidate knowledge：候选知识，尚未成为权威事实；
- reviewed knowledge：审核后的稳定知识；
- indexed retrieval artifact：检索索引产物；
- deprecated or archived：废弃或归档内容。

### 11.2 本地优先 RAG 原则

当前 RAG 方案优先考虑：

- 免费或开源；
- 本地运行；
- 私人化和数据可控；
- 安全；
- 成熟文档和生态；
- 可重建索引；
- metadata filter，中文解释是按元数据过滤；
- hybrid retrieval，中文解释是向量检索和关键词检索结合；
- citation，中文解释是回答必须能引用来源；
- evaluation，中文解释是用测试集评估检索质量。

### 11.3 推荐落地路径

| 阶段 | 方案 | 目标 |
|---|---|---|
| v0 | Markdown + YAML front matter + `rg` | 先把知识结构和来源追踪做对 |
| v1 | raw inventory + extracted content + `chunks.jsonl` | 让索引可重建 |
| v2 | 本地向量库 PoC | 比较 Qdrant、Chroma、pgvector |
| v3 | hybrid retrieval + rerank | 提升召回和排序质量 |
| v4 | RAG eval + governance | 检查 context precision、recall、groundedness |

候选技术栈：

```text
Document parsing: Docling 或 Unstructured
Corpus format: Markdown + YAML front matter + JSONL chunks
RAG orchestration: LlamaIndex、LangChain 或 Haystack
Vector store: Qdrant 或 Chroma 优先；引入 PostgreSQL 时考虑 pgvector
Evaluation: Ragas 或 TruLens
```

本文不做最终选型。最终选型应通过本地 PoC 和安全评估完成。

Structured ingestion 工具，例如文档解析、OCR、版面解析和结构化导出工具，应作为 RAG v1 的候选组件评估。它们解决的是原始资料到可治理语料的转换，不解决知识审核、事实权威、向量库选择或检索评估问题。

## 12. 目录映射视图

目标 Harness Root：

```text
<HARNESS_ROOT>\
  AGENTS.md
  README.md
  docs\
    INDEX.md
    PLANS.md
    HarnessEngineering.md
    governance\
    verification\
    observability\
    reports\
  skills\
  knowledge\
    raw\
    extracted\
    reviewed\
    indexes\
  memory\
  templates\
  scripts\
  config\
    projects.local.example.json
  projects\
    <project-id>\
      AGENTS.md
      docs\
        project\
          ProjectIndex.md
          workflow\
  var\
    logs\
    tmp\
    status\
    cache\
    rag\
    homes\
    m2\
  tools\
  settings\
```

### 12.1 默认进入 git

```text
AGENTS.md
README.md
docs/**
skills/**
knowledge/reviewed/**
memory/**
templates/**
scripts/**
config/*.example.json
projects/java-demo/**
```

### 12.2 默认不进入 git

```text
var/**
knowledge/indexes/**
logs/**
tmp/**
home-*/**
m2-*/**
downloads/**
auth files
private settings
raw terminal transcripts
unredacted external outputs
real business project repositories
```

`knowledge/raw/**` 是否进入 git 需要单独判断，取决于资料大小、敏感性和授权情况。

## 13. 安全和隔离模型

### 13.1 安全原则

Harness 必须默认保守：

- 不默认转发凭据；
- 不默认信任项目上下文文件；
- 不允许未审批高风险命令；
- 不把 YOLO 或关闭审批作为普通自动化默认模式；
- 不把真实业务项目和 Harness 根仓库混成一个 git 历史；
- 不把 raw logs 当成事实或报告；
- 不让消息网关对未授权用户开放。

### 13.2 Hermes 安全建议的吸收边界

Hermes 官方安全文档强调 defense-in-depth，中文解释是纵深防御。与 Harness 相关的边界包括：

- User authorization：用户授权，消息网关必须有 allowlist 或配对机制；
- Dangerous command approval：危险命令审批，破坏性命令必须有人在环；
- Hardline blocklist：硬阻断列表，灾难性命令不可通过普通审批绕过；
- Container isolation：容器隔离，生产网关建议使用 Docker、Modal、Daytona 等隔离后端；
- Credential filtering：凭据过滤，环境变量和凭据文件必须显式 allowlist；
- Context file scanning：上下文文件扫描，检查 prompt injection 和凭据外泄风险；
- Network isolation：网络隔离，高安全场景可使用独立机器或虚拟机。

Harness 不复制 Hermes 的实现细节，但应把这些原则转成 Harness 的安全政策。

参考：

```text
https://hermes-agent.nousresearch.com/docs/user-guide/security
```

### 13.3 本地沙盒、Docker 和虚拟机

| 隔离方式 | 中文解释 | 优点 | 风险 | 建议阶段 |
|---|---|---|---|---|
| Local Sandbox | 本地沙盒，当前 `<HARNESS_ROOT>` | 简单、开发快、便于调试 | 与主机隔离弱 | 设计和早期 PoC |
| Docker | 容器隔离 | 成本低、可重复、适合网关执行 | Windows 路径、卷挂载和凭据转发需要谨慎 | P8 后重点评估 |
| Virtual Machine | 虚拟机隔离 | 隔离强、适合高风险任务 | 成本高、启动慢、运维复杂 | 真实业务或强安全场景 |
| Remote Worker | 远程工作机 | 可与主机隔离，适合专用执行节点 | 需要 SSH、网络和凭据治理 | 后续生产化 |

当前不直接选择 Docker 或虚拟机。P8 阶段应产出正式 decision matrix，中文解释是决策矩阵。

## 14. 工具资产和 Java/Maven 示例

### 14.1 Tool Assets 要求

稳定工具必须具备：

- 明确用途；
- 输入参数说明；
- 输出格式说明；
- 状态 JSON；
- 日志路径；
- 敏感信息处理；
- 可重复调用；
- 失败码和失败归因说明。

### 14.2 Java/Maven 命令门面

当前脚本先作为 Execution Tool Assets，中文解释是执行工具资产。

```text
scripts/stable/show-java-maven-config.ps1
scripts/stable/invoke-maven-project.ps1
scripts/stable/invoke-java-main.ps1
scripts/stable/clean-sandbox.ps1
```

后续 P7 需要把它们包装为稳定命令门面，例如：

```text
harness validate --project java-demo --profile isolated-sandbox-maven
harness run-main --project java-demo --class com.example.Main
```

上述命令只是目标形态示意，不代表当前已实现。

## 15. Runtime Adapter

Runtime Adapter 中文解释是运行时适配流程，不是把 runtime 纳入 Harness 内核。

目标是让 Hermes、Codex 和未来其他 agent 都遵循相同的 Harness 入口和证据规范。

### 15.1 Hermes WeCom 流程

```text
企业微信用户提示词
-> Hermes gateway
-> Harness Root 发现
-> Task Brief
-> 项目 Profile
-> 项目事实
-> 执行和验证
-> workflow evidence
-> 企业微信验收回复
```

### 15.2 Codex 流程

```text
Codex 用户提示词
-> 当前 workspace
-> Harness Root 发现
-> Task Brief
-> 项目 Profile
-> 项目事实
-> 执行和验证
-> workflow evidence
-> Codex final response
```

两种 runtime 的用户交互方式不同，但 Harness 资产、项目事实、Task Brief、验证报告和治理收口应保持一致。

## 16. Java/Maven 端到端示例

用户任务：

```text
给 java-demo 项目新增 multiply 功能，补充测试，跑完验证后告诉我结果。
```

预期流程：

1. Hermes 收到企业微信任务。
2. Hermes 从 `HARNESS_ROOT=<HARNESS_ROOT>` 或 cwd 发现 Harness。
3. Hermes 读取根 `AGENTS.md`、`docs/INDEX.md` 和任务相关文档。
4. Hermes 生成 Task Brief。
5. Hermes 通过项目注册表定位 `projects/java-demo`。
6. Hermes 读取项目 `AGENTS.md` 和 `docs/project/ProjectIndex.md`。
7. Hermes 读取 Project Facts，确认源码目录、测试目录和默认验证命令。
8. Hermes 生成执行计划。
9. Hermes 修改源码和测试。
10. Hermes 调用稳定 Java/Maven 工具。
11. 工具输出 status JSON 和 log path。
12. Hermes 生成验证报告。
13. Hermes 通过企业微信回复用户。
14. 如果用户不接受，下一轮任务从 workflow evidence 和失败归因继续。

## 17. Governance

Governance 是横切约束，贯穿任务前、中、后。

### 17.1 任务前

- 入口读取；
- 安全边界检查；
- Task Brief；
- Readiness Check；
- 高风险澄清。

### 17.2 任务中

- 工具调用记录；
- 文件变更记录；
- 命令审批；
- 凭据保护；
- 失败归因。

### 17.3 任务后

- 验证报告；
- 用户验收；
- 修复任务入口；
- promotion candidates；
- archive；
- 清理 runtime state。

### 17.4 Promotion 规则

Promotion 中文解释是晋升，把临时证据或候选经验提升为长期资产。

允许的晋升路径：

```text
workflow evidence -> Project Fact candidate -> reviewed Project Fact
workflow evidence -> Memory candidate -> reviewed Memory
workflow evidence -> Skill improvement candidate -> approved Skill
workflow evidence -> Knowledge candidate -> reviewed Knowledge
```

禁止路径：

```text
raw log -> active Memory
failed report -> Project Fact
agent guess -> reviewed Knowledge
RAG chunk -> source of truth
```

## 18. 文档格式规范

为了防止后续文档混乱，Harness 文档应遵循：

- Markdown 为主；
- 结构化字段优先使用 YAML front matter；
- 机器交换结果优先使用 JSON；
- 批量知识 chunk 优先使用 JSONL；
- XML 只在生态要求时使用，例如 Maven `pom.xml`；
- 图示可以使用 Mermaid；
- 专业英文术语首次出现应加中文解释；
- 文档中的代码块必须标明格式；
- 资产状态必须明确是 `draft`、`candidate`、`reviewed`、`deprecated` 或 `archived`。

## 19. 非目标

本文不做：

- 不迁移目录；
- 不移动脚本；
- 不创建根 `AGENTS.md`；
- 不创建 `docs/INDEX.md`；
- 不创建项目注册表；
- 不选择最终 RAG 技术栈；
- 不实现 Docker 或虚拟机隔离；
- 不把 Hermes/Codex runtime 内核纳入 Harness；
- 不改真实业务项目。

## 20. P1 验收标准

P1 草稿可以被接受，当它能够说明：

1. Harness 是什么；
2. Harness 拥有什么；
3. Agent Runtime 拥有什么；
4. 为什么任务生命周期是主架构；
5. 为什么资产模型和目录映射不是生命周期层级；
6. `AGENTS.md` 如何作为权威入口；
7. 自然语言提示词如何转成 Task Brief；
8. 高风险任务何时必须澄清；
9. 如何定位 Project Profile、Project Facts、源码和验证命令；
10. Skill、Knowledge、Memory、Project Facts、RAG Index 的区别；
11. 为什么 RAG Index 不是事实来源；
12. Harness 如何拥有稳定脚本和本地沙盒设施；
13. Hermes/Codex 如何作为外部 runtime 被 Harness 约束；
14. 哪些内容进入 git，哪些保持 runtime-only；
15. Java/Maven 示例如何走完整生命周期；
16. 后续 P2 到 P11 如何继续落地。

## 21. 近期文献吸收后的候选优化

本轮阅读的 agent harness 相关文献给当前设计带来以下候选优化。这些内容是设计输入，不自动成为 reviewed Knowledge。

1. 用 ETCLOVG 做完整性检查，防止只做文档组织而遗漏 execution、observability、verification 和 governance。
2. 在 workflow evidence 中加入 Harness Run Card，披露 runtime、工具、sandbox、approval、context 和 validation 配置。
3. 把 handoff 从普通文本摘要升级为 Handoff Contract，明确 intent、constraints、permissions、artifacts、provenance、budget、risk 和 unresolved decisions。
4. 采用 NLAH，中文解释是自然语言 Harness 策略文档，的写法经验：任务合同优先、阶段和机制分离、状态和证据显式、模块边界可替换、语言短而可执行。
5. 把 context management 视为状态估计问题，而不是简单压缩问题；摘要、记忆、检索和候选知识都必须带来源、置信度和陈旧性。
6. 把 RAG 结构化摄取作为 v1 层，而不是等到向量库选型后才处理原始资料。
7. 暂缓吸收 self-evolving harness、自动 harness 搜索和大规模协议标准化实现；这些应在 P10/P11 或 RAG PoC 后再评估。

## 22. 待决策问题

以下问题留到后续阶段继续对齐：

1. `skills/`、`knowledge/`、`memory/` 是否采用顶层目录，还是统一放入 `docs/` 下。
2. 真实业务项目在 `projects/<project-id>` 下如何与 Harness 根 git 仓库隔离。
3. RAG v2 阶段优先 PoC Qdrant 还是 Chroma。
4. Docker 和虚拟机隔离在 Windows 本地环境中的实施成本。
5. 是否需要实现统一 `harness` CLI，中文解释是命令行入口。
6. Project Profile 使用 JSON、YAML 还是二者并存。
7. Workflow evidence 是否每个项目独立入库，还是同步生成根级 redacted reports。
