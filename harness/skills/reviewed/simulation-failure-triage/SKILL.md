---
name: simulation-failure-triage
description: 排查和验证 Java 或服务类仿真失败、真实数据回放失败、CSV 驱动测试失败、连续 API 调用状态异常等问题。适用于表层错误码可能只是包装错误，而真实原因需要结合仿真产物、输入数据画像、状态迁移、时间轴、策略、求解计划、Plugin Binding、StateProjection、Response、诊断 main program、最小回归验证和用户验收共同定位的场景。
metadata:
  short-description: 仿真失败排查与验证流程
  asset-state: reviewed
  review-state: approved-by-user
---
# 仿真失败排查

## 1. 笔记属性

`SKILL.md` 的 YAML frontmatter 只保留 Skill 校验器允许的元数据；Harness 文档治理所需的笔记属性和关联文档放在正文中维护。

| 属性 | 内容 |
|---|---|
| 文档 | `harness/skills/reviewed/simulation-failure-triage/SKILL.md` |
| 资产状态 | reviewed |
| 审核状态 | approved，用户已审核通过 |
| 主题语言 | 中文；专业词、命令、路径、类名和程序标识保留英文 |
| 适用对象 | 仿真失败、真实数据回放失败、CSV 驱动测试失败、连续 API 调用状态异常 |
| 解决问题 | 表层错误码不能直接说明根因时，按证据完成复现、输入画像、流水线归因、诊断、修复验证和证据关闭 |
| 输入来源 | 项目入口文档、测试策略、仿真手册、仿真产物、结构化日志摘要、workflow evidence |
| 输出结果 | 经过验证的根因摘要、修复或处置建议、回归验证结果、workflow evidence 更新建议 |

## 2. 关联文档和读取路径

使用本 Skill 前，先按 Harness 入口规则读取全局和项目入口文档，再读取目标项目的仿真和验证文档。以下链接是本 Skill 的反向依赖和参考路径。

### 2.1 Harness 入口和 Skill 治理

| 文档 | 读取目的 |
|---|---|
| `AGENTS.md` | 获取 Harness Root 入口、读取顺序、敏感边界和文档治理规则。 |
| `INDEX.md` | 从全局索引路由到 Harness、项目实例、用户边界和运行态边界。 |
| `harness/HarnessIndex.md` | 确认 General Harness 资产分层和 Skill、Tool、Governance 入口。 |
| `harness/skills/SkillIndex.md` | 确认当前 Skill 状态、候选路径和是否存在可复用或可 patch 的已有 Skill。 |
| `harness/skills/SkillPolicy.md` | 确认 Skill 创建、更新、候选、审核、晋升和敏感信息边界。 |
| `harness/governance/SkillGovernance.md` | 确认候选 Skill 的 review gate、用户决策和晋升门禁。 |

### 2.2 项目级仿真和验证参考

以下文档来自 `lfms-decision` 的真实项目沉淀，是本 Skill 的项目级来源示例。处理该项目时必须读取；处理其他项目时，应通过该项目的 `AGENTS.md` 和 `ProjectIndex.md` 查找等价文档，不要把该项目事实套用到其他项目。

| 文档 | 读取目的 |
|---|---|
| `projects/lfms-decision/AGENTS.md` | 获取项目级入口、限制和读取顺序。 |
| `projects/lfms-decision/docs/project/ProjectIndex.md` | 路由到项目事实、测试、验证和 workflow evidence。 |
| `projects/lfms-decision/docs/project/test/simulation/SimulationFailureTriage.md` | 读取项目级仿真失败排查流程、产物判读顺序和证据记录要求。 |
| `projects/lfms-decision/docs/project/test/simulation/SimulationManual.md` | 读取仿真程序使用方法、输入输出、summary、call records、timeline 和 anomalies 的含义。 |
| `projects/lfms-decision/docs/project/Validation.md` | 确认稳定命令面、Java/Maven profile 和项目验证方式。 |
| `projects/lfms-decision/docs/project/TestStrategy.md` | 确认测试层级、最小回归和真实数据复跑的选择规则。 |

## 3. 适用场景

当任务满足以下特征时，使用本 Skill：

- 仿真、回放式验证、CSV 驱动测试或连续 API 调用出现失败。
- 表层错误码不能直接解释真实根因，可能只是 Gateway、Solver 或包装层收口后的错误。
- 需要比较失败调用与前序成功调用的输入、状态、时间轴和输出差异。
- 需要沿算法或服务流水线逐层定位：`API / Gateway -> Governance -> Timeline -> Strategy -> Solver -> Plugin Binding -> Pipeline -> StateProjection -> Response`。
- 修复后需要同时完成最小合成回归和用户相关的真实数据仿真复跑。

不适用：

- 单个普通 unit test 失败，且不涉及连续调用状态或仿真产物。
- 只需要解释某个独立异常栈，不需要复现、归因和验证闭环。
- 外部生产系统连接、权限、消息订阅或环境不可用问题；这类问题应先按项目敏感边界和环境故障处理。

## 4. 边界规则

- 先读取目标项目的入口文档、测试策略、验证命令面和相关测试说明书。
- 不把最终错误码直接当作根因；必须定位第一个错误决策点或第一个错误数据归类点。
- 不把运行态日志、完整请求响应、完整状态 JSON、原始 CSV、私有配置、本机路径或凭据写入 tracked docs。
- 项目事实保留在项目文档或 workflow evidence 中；本 Skill 只保留可复用流程。
- 如果排查过程产生可复用经验，先形成候选资产，再由用户或治理流程决定是否晋升。

## 5. 标准流程

### 5.1 明确任务口径

在执行命令前确认并记录：

| 字段 | 要求 |
|---|---|
| 目标 | 说明是复现、定位根因、修复问题，还是验证修复。 |
| 数据边界 | 确认样本来源、可读范围、脱敏要求和是否允许写入摘要。 |
| 验收标准 | 明确成功响应、错误码变化、WARN 日志、状态不变、预测为空等业务期望。 |
| 修改边界 | 明确是否允许改生产代码、测试代码、文档，或只允许诊断。 |
| 验证计划 | 说明使用哪些稳定工具、main class、测试层级和回归方式。 |
| 证据位置 | 任务过程写入 workflow evidence，运行态输出只记录安全摘要。 |

### 5.2 使用稳定命令面复现

优先使用项目已有的稳定脚本或命令面。Java/Maven main program 常见模板：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-java-main.ps1 `
  -ProjectRoot <PROJECT_ROOT> `
  -Agent <agent-id> `
  -Profile <profile-id> `
  -Module <module> `
  -AlsoMake `
  -MavenGoals test-compile `
  -MainClass <main-class> `
  -JavaWorkingDirectory project-root `
  -RunName <task-specific-run-name>
```

记录摘要即可：

- command surface；
- profile ID；
- module；
- main class；
- run name；
- exit code；
- status JSON 路径；
- log 路径；
- 任务级关键断言结果。

不要粘贴未脱敏日志正文。

### 5.3 建立输入数据画像

复现后先确认失败是否源自输入事实：

| 检查项 | 目的 |
|---|---|
| 数据源组成 | 避免把多来源混合数据误判为单来源问题。 |
| 调用数量 | 确认 planned、executed、success、failed、aborted 等整体状态。 |
| 失败调用位置 | 定位具体 seq、requestId 或 traceKey 摘要。 |
| 前后调用差异 | 比较失败调用与最近成功调用的业务时间、上报时间、source、速度字段和 optional 字段。 |
| 历史状态 | 判断 previous state 是否存在、是否可解析、是否包含可用历史点或模型状态。 |
| 重复或回退 | 检查同批或相邻调用是否存在业务时间重复、回退、无新增业务时间。 |

### 5.4 判读仿真产物

优先按以下顺序查看安全摘要：

| 产物 | 用途 |
|---|---|
| summary | 判断整体调用数、成功失败数、是否完整处理输入。 |
| call records | 判断 wrapper、snapshot、状态摘要和语义断言。 |
| state transitions | 判断 previous/new state、锚点、时间轴和新增业务时间。 |
| timeline records | 判断业务时间轴、预测时间轴、裁剪和回退。 |
| anomalies | 判断输入时序、无新增业务时间、语义警告和慢调用。 |
| structured logs | 判断 service、method、stage、event、errorCode 和安全 message 摘要。 |

### 5.5 按流水线归因

按流水线顺序定位第一个错误决策点：

```text
API / Gateway
-> Governance
-> Timeline
-> Strategy
-> Solver planning
-> Plugin Binding
-> Pipeline execution
-> StateProjection
-> Response
```

求解或插件绑定类问题要区分：

- 没有候选插件；
- 候选插件存在，但能力标签不满足；
- 能力标签满足，但 `supports(...)` 拒绝当前 runtime context；
- 上游策略本应跳过或降级某个 stage，却继续进入必需 stage；
- 最终错误码只是绑定层或 Gateway 层包装后的结果。

连续状态类问题要检查：

- 历史融合点是否可用；
- motion/predict state 是否存在；
- 业务时间轴和预测时间轴是否符合语义；
- prediction reference 是否被误用；
- `StateProjection` 是否应更新，还是应沿用历史。

### 5.6 必要时编写诊断 main program

当仿真产物不足以解释根因时，编写项目内诊断 main program。

诊断程序应满足：

- 只读取已批准数据，或构造最小合成输入；
- 输出脱敏摘要，不输出完整原始数据、完整请求响应或完整状态 JSON；
- 明确打印 Governance、Timeline、Strategy、Solver、Plugin Binding、StateProjection 中与根因相关的摘要；
- 放在项目约定的测试目录；
- 使用同一稳定命令面执行和验证。

### 5.7 修复后验证

修复后至少覆盖两层验证：

1. 最小合成回归：不依赖真实私有数据，保护具体 bug 行为。
2. 用户相关仿真复跑：使用用户批准的数据或场景，证明真实问题已解决。

回归断言应围绕业务契约，而不是偶然日志文本。若 WARN 是契约的一部分，优先断言结构化字段、reason code 或可稳定识别的摘要。

### 5.8 关闭证据

完成前检查：

- workflow evidence 记录 Task Brief、计划、执行摘要、验证结果、验收结论和治理候选。
- 失败或跳过的验证被如实记录。
- 可复用流程进入项目级文档或候选 Skill，而不是停留在临时 workflow evidence。
- 未经用户审核，不把候选经验晋升为 reviewed Skill、Memory、Knowledge 或 Tool Asset。

## 6. 验收清单

- 已使用稳定命令面复现，或说明未使用原因。
- 已定位失败调用的 seq、requestId 或 traceKey 摘要。
- 已核对输入数据源组成和失败前后调用差异。
- 已按流水线定位第一个错误决策点。
- 如新增诊断代码，代码位于测试区域并只输出脱敏摘要。
- 修复后包含最小合成回归和用户相关仿真复跑，或说明无法覆盖的原因。
- workflow evidence 记录命令摘要、状态、结果、残余风险和用户验收。
- 沉淀为候选资产时不包含项目私有事实或敏感数据。

## 7. 常见误区

- 只看最终错误码，不检查上游治理、策略和绑定上下文。
- 未先统计数据源组成，就把混合数据结论套用到单一数据源。
- 把 workflow evidence 当作长期操作手册，而不是抽取为项目文档或候选 Skill。
- 业务语义要求沿用历史时，仍然更新状态投影或推进时间轴。
- 用户审核未完成时，提前标记晋升完成。

## 8. 治理

| 检查项 | 规则 |
|---|---|
| 文档 | `harness/skills/reviewed/simulation-failure-triage/SKILL.md` |
| 版本 | `v1.0.0-reviewed` |
| 状态 | `active` |
| 资产状态 | reviewed |
| 关联文档 | 已在正文列出 Harness 入口、SkillIndex、SkillPolicy、SkillGovernance、SimulationFailureTriage 和 SimulationManual。 |
| 事实边界 | 项目事实留在项目文档或 workflow evidence；本 Skill 只保留通用流程。 |
| 敏感边界 | 不保存原始数据、完整日志、完整请求响应、本机路径、私有配置或凭据。 |
| 晋升记录 | 用户已在 2026-07-02 审核通过，由 candidate 晋升为 reviewed Skill。 |
