---
name: memory-governance-use
description: 使用 Harness Memory 的“流程 + 稳定命令”状态机处理记忆候选。适用于需要按 HarnessEngineering Memory Update Flow 执行记忆治理、运行 memory-flow-status 对齐流程节点、运行 validate-memory-store 验证 Memory store、生成 candidate-review-package 审核包、读取用户 approve/reject/delete/defer/revise 决策，或在流程节点缺少稳定命令时停止并报告工具化缺口的场景。
metadata:
  short-description: Memory 候选治理与验证流程
  asset-state: reviewed
  review-state: approved-by-user
---
# Memory 治理使用流程

## 1. 笔记属性

`SKILL.md` 的 YAML frontmatter 只保留 Skill 校验器允许的元数据；Harness 文档治理所需的笔记属性和关联文档放在正文中维护。

| 属性 | 内容 |
|---|---|
| 文档 | `harness/skills/reviewed/memory-governance-use/SKILL.md` |
| 资产状态 | reviewed |
| 审核状态 | approved by user；后续语义修订仍需走 candidate / patch candidate review |
| 主题语言 | 中文；专业词、命令、路径、frontmatter key 和技术名词保留英文 |
| 适用对象 | Memory Update Flow 节点执行、Memory store 只读验证、candidate review package、用户决策记录和未工具化生命周期缺口识别 |
| 解决问题 | 把 Memory 机制从 agent 自行解释的文档流程收敛为稳定命令驱动的流程状态机；所有节点必须由命令执行或由命令报告边界，不能手工替代 |
| 输入来源 | Harness 入口文档、架构权威 Memory Update Flow、Memory policy、Memory governance、stable command status JSON、用户审核决策 |
| 输出结果 | `memory-flow-status` 流程覆盖报告、Memory store 验证结果、candidate 审核包、用户决策摘要、工具化缺口 |

## 2. 关联文档和读取路径

使用本 Skill 前，先按 Harness 入口规则读取全局入口、稳定 Memory 机制文档和命令文档，再根据任务读取目标 candidate 或 review package。不要把阶段性建设计划当作本 Skill 的执行依赖。

### 2.1 Harness 入口和 Skill 治理

| 文档 | 读取目的 |
|---|---|
| `AGENTS.md` | 获取 Harness Root 入口、读取顺序、敏感边界和文档治理规则。 |
| `INDEX.md` | 从全局索引路由到 Harness、项目实例、用户边界和运行态边界。 |
| `harness/HarnessIndex.md` | 确认 General Harness 资产分层和 Memory、Skill、Tool、Governance 入口。 |
| `harness/architecture/HarnessEngineering.md` | 确认 Memory 在 Harness 目标架构中的边界和冲突优先级。 |
| `harness/skills/SkillIndex.md` | 确认本 reviewed Skill 路由和是否存在可 patch 的同类 Skill。 |
| `harness/skills/SkillPolicy.md` | 确认 Skill 创建、更新、候选、审核、晋升和 Git 管理规则。 |
| `harness/governance/SkillGovernance.md` | 确认 Skill review gate、promotion gate 和 usage sidecar 要求。 |

### 2.2 Memory 机制和命令

| 文档 | 读取目的 |
|---|---|
| `harness/memory/MemoryIndex.md` | 确认 Memory candidate、reviewed、archive 和模板路由。 |
| `harness/memory/MemoryPolicy.md` | 确认哪些内容适合进入 Memory、哪些内容必须留在 workflow/report/project/knowledge。 |
| `harness/governance/MemoryGovernance.md` | 确认 Memory review gate、冲突检查、source evidence 和 review metadata 要求。 |
| `harness/templates/memory/MemoryTemplate.md` | 创建或审查 Memory candidate 时确认字段结构。 |
| `harness/tools/docs/script-index/ScriptIndex.md` | 查询 `invoke-memory.ps1` 稳定命令面和输出位置。 |
| `harness/tools/scripts/stable/invoke-memory.ps1` | 执行 Memory store 验证和 candidate review package。 |

## 3. 触发场景

在以下场景使用本 Skill：

- 用户要求处理记忆治理、候选记忆审核、Memory store 验证或 Memory candidate review package。
- 真实任务完成后，需要判断某条经验是否是通用、非私有、未来可复用的 Memory candidate。
- 需要为现有 `harness/memory/candidate/` 下的候选生成用户审核包。
- 需要确认 candidate、reviewed、archive 状态是否互斥，是否存在重复 `memoryId`、缺失 `sourceEvidence`、缺失 review metadata 或敏感模式。
- 用户已经给出 approve、reject、delete、defer 或 revise 决策，需要判断是否存在可用稳定命令；没有命令时只记录缺口，不手工改 Memory。

不要在以下场景使用本 Skill 作为事实源：

- 回答项目业务事实、真实数据、代码行为或用户私有偏好。
- 读取或总结 raw logs、task transcript、settings、auth、token、secret 或本机私有路径。
- 替代 reviewed Knowledge、Project Facts、Skill、workflow evidence 或 report。

## 4. 边界规则

- Memory 只保存通用化、非私有、未来可复用的经验。
- 一次性任务过程、项目事实、用户私有偏好、raw logs、未脱敏日志、私有配置和凭据不得进入 Memory。
- 冲突优先级为：用户当前明确指令 > Project Fact / 正式文档 > reviewed Knowledge > active Memory > candidate Memory > archived Memory。
- Candidate Memory 不是 active Memory；未获 review 或用户明确批准前，不得当作长期规则使用。
- 本 Skill 已由用户 approve 并晋升为 reviewed Skill；后续修改本 Skill 的语义内容时，必须走 candidate / patch candidate review，不得直接绕过审核。
- 只有 `invoke-memory.ps1` 或其他稳定命令实际执行过的节点，才能称为程序门禁结果。
- `HarnessEngineering.md` 中的 Memory Mermaid 是流程权威；本 Skill 不重新解释 Mermaid，而是先运行 `memory-flow-status` 获取程序化节点覆盖表。
- 流程节点必须在 `memory-flow-status` 中标记为 `implemented` 才能继续；如果未来出现 `missing` 或 `partial`，必须停止并报告工具缺口，不得用手工移动、复制、临时脚本或自由裁量替代。

## 5. 可执行能力边界

当前脚本已经强制执行的能力：

| 能力 | 程序保障 |
|---|---|
| 流程节点覆盖状态 | `memory-flow-status` 按架构权威 Memory Update Flow 输出每个节点的 required command、current command、coverage 和 execution rule。 |
| Source evidence 验证 | `verify-source-evidence` 确认 workflow evidence 或用户反馈来源存在。 |
| 候选信号检测 | `detect-from-workflow` 从 source evidence 中生成只读候选信号，不写 candidate。 |
| 候选适用性分类 | `classify-candidate-suitability` 根据候选 Review Notes 和敏感边界输出 `ready-for-review`、`needs-review` 或 blocking 状态。 |
| no-memory 处置 | `record-no-memory-disposition` 把不进入 Memory 的判断写为 runtime disposition report。 |
| 创建 candidate | `create-candidate` 默认 dry-run；只有 `-Apply` 且输入完整时写入 `harness/memory/candidate/`。 |
| Memory 类型分类 | `classify-memory-type` 验证候选 scope 是否属于允许的 Memory scope。 |
| Store shape 和基础字段检查 | `validate-memory-store` 检查 candidate、reviewed、archive 结构、frontmatter、review metadata、source evidence、状态、重复 `memoryId` 和敏感模式。 |
| 重复和冲突检测 | `detect-memory-duplicate-conflict` 做确定性的 memoryId、statement、source evidence 重复检查；语义冲突仍进入 review package。 |
| 冲突审核包 | `conflict-review-package` 输出冲突审核输入和优先级规则。 |
| 负向 fixture 自测 | `validate-memory-store -SelfTest` 验证门禁能检出典型坏样本。 |
| 候选审核包 | `candidate-review-package` 为单个 candidate 生成只读审核输入。 |
| 用户决策路由 | `apply-review-decision` 根据 approve/reject/delete/defer/revise 路由到受控命令，默认 dry-run。 |
| 晋升 reviewed | `promote-reviewed` 默认 dry-run；只有 `-Apply`、reviewer、approval note 和 reason 齐备时才移动 candidate。 |
| 归档 candidate | `archive-candidate` 默认 dry-run；只有 `-Apply`、reviewer、approval note 和 reason 齐备时才归档。 |
| 删除 candidate | `delete-candidate` 默认 dry-run；只有用户明确要求删除，并且 `-Apply`、reviewer、approval note 和 reason 齐备时才删除 candidate。 |
| 修订 candidate | `revise-candidate` 默认 dry-run；只有 `-Apply` 且审核输入齐备时才修改候选。 |
| 索引同步状态 | `sync-memory-index` 输出 MemoryIndex 同步状态报告。 |

当前仍需要人工审核的边界：

| 能力 | 当前处理 |
|---|---|
| 是否足够通用 | 命令只能输出候选信号和 review notes，不能替用户批准。 |
| 语义冲突 | 命令做确定性重复检查；跨 Project Fact、reviewed Knowledge 和 active Memory 的语义冲突必须进入 review package。 |
| reviewed / archive / delete / revise 写入 | 命令已支持受控写入或删除，但必须有用户明确决策、reviewer、approval note、reason 和 `-Apply`。 |

## 6. 稳定命令

统一使用 stable wrapper：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-memory.ps1 -Root <HARNESS_ROOT> -Command <command>
```

当前可用 commands：

| Command | 用途 | 写入边界 |
|---|---|---|
| `memory-flow-status` | 对照 `HarnessEngineering.md` 的 Memory Update Flow 输出流程节点、当前命令覆盖、缺口和停止规则。 | 只写 `var/memory/evals/` report 和 `var/memory/status/` JSON。 |
| `verify-source-evidence` | 校验 source evidence 路径存在。 | 只写 runtime report。 |
| `detect-from-workflow` | 从 source evidence 中抽取候选信号。 | 只写 runtime report，不创建 candidate。 |
| `classify-candidate-suitability` | 判断候选是否 ready / needs-review / blocked。 | 只写 runtime report。 |
| `record-no-memory-disposition` | 记录不进入 Memory 的处置。 | 只写 runtime report。 |
| `create-candidate` | 从 statement 和 source evidence 创建 candidate。 | 默认 dry-run；`-Apply` 后写 `harness/memory/candidate/`。 |
| `classify-memory-type` | 校验 Memory scope 类型。 | 只写 runtime report。 |
| `validate-memory-store` | 检查 `harness/memory/candidate/`、`reviewed/`、`archive/` 的 frontmatter、review metadata、source evidence、状态互斥、重复 `memoryId` 和敏感模式。 | 只写 `var/memory/` runtime report / status JSON。 |
| `detect-memory-duplicate-conflict` | 检查 memoryId、statement、source evidence 的确定性重复和冲突输入。 | 只写 runtime report。 |
| `reject-or-merge-candidate` | 将 reject / merge 处置路由到后续命令。 | 默认 report-only。 |
| `conflict-review-package` | 生成冲突审核包。 | 只写 runtime report。 |
| `validate-memory-store -SelfTest` | 使用临时 fixture 验证门禁能检出缺 frontmatter、缺 review 字段、缺 source evidence、重复 `memoryId`、非法 `assetState` 和 credential-like 敏感模式。 | 只写 `var/tmp/` 和 `var/memory/` runtime 产物。 |
| `candidate-review-package -CandidateId <id>` | 为指定 candidate 生成用户审核包，列出 source evidence、当前状态、风险、建议决策和 approve/reject/delete/defer/revise 输入。 | 只写 `var/memory/reviews/` runtime report。 |
| `apply-review-decision` | 根据用户决策路由到 promote/archive/delete/revise。 | 默认 dry-run；写入必须满足对应命令要求。 |
| `promote-reviewed` | 晋升 candidate 到 reviewed。 | 默认 dry-run；`-Apply` 且审核字段齐备后才写 `reviewed/`。 |
| `archive-candidate` | 归档 candidate。 | 默认 dry-run；`-Apply` 且审核字段齐备后才写 `archive/`。 |
| `delete-candidate` | 删除被用户明确要求删除的 candidate。 | 默认 dry-run；`-Apply` 且审核字段齐备后才删除 `candidate/` 内目标文件；普通 reject 默认仍使用 `archive-candidate`。 |
| `revise-candidate` | 修订 candidate statement 或决策。 | 默认 dry-run；`-Apply` 且审核字段齐备后才修改 candidate。 |
| `sync-memory-index` | 输出 MemoryIndex 同步状态。 | 当前 report-only。 |

后续 mutation commands 只能在工具实现、reviewer、approval note 和用户决策齐备后使用；如果当前阶段尚未落地对应命令，只记录计划，不手写移动或复制 Memory 文件。

## 7. 执行流程

1. 运行 `memory-flow-status`，读取 `steps[]` 中每个 Memory Update Flow 节点的 `coverage`、`currentCommand` 和 `executionRule`。
2. 如果目标动作对应的节点不是 `implemented`，立即停止；在回复或审核包中报告缺失的 `requiredCommand`，不要继续手工执行。
3. 如果目标动作对应的节点为 `implemented`，只执行 `currentCommand` 指定的命令。
4. 运行 `validate-memory-store`，确认当前 Memory store 没有 blocking issues。
5. 如任务涉及指定 candidate，只能运行 `candidate-review-package -CandidateId <id>` 生成审核输入，不替用户假设 approve/reject/delete/defer/revise。
6. 用户给出决策后，再次查看 `memory-flow-status`，然后用 `apply-review-decision` dry-run 预览；普通 reject 默认归档，用户明确说删除时才使用 `delete-candidate`；只有用户明确要求 apply 且审核字段齐备，才允许带 `-Apply` 执行。
7. 收口前再次运行 `validate-memory-store`，并记录 `memory-flow-status` 的 coverage 摘要、执行过的命令、未执行节点和剩余风险。

## 8. 验收清单

- 已运行 `invoke-memory.ps1 -Command memory-flow-status`，并按 `steps[]` 决定是否继续。
- 每个继续执行的 Memory flow 节点都有 `currentCommand`；没有命令的节点已停止并报告缺口。
- 已运行 `invoke-memory.ps1 -Command validate-memory-store`，且无 blocking issues。
- 如涉及候选审核，已运行 `candidate-review-package -CandidateId <id>`。
- 已把用户决策区分为 approve、reject、delete、defer 或 revise；没有由 agent 自行假设。
- 未经用户明确批准，未写入 `harness/memory/reviewed/`、`harness/memory/archive/` 或删除 candidate。
- 如批准后的动作尚无稳定命令，已记录工具缺口，没有用手工文件操作替代。
- 未把 raw logs、task transcript、本机私有路径、settings、auth、token、secret 或项目私有事实写入 Memory 或 Skill。
- 本 Skill 已处于 reviewed 状态；收口时确认 `SkillIndex.md` 和 usage sidecar 已指向 reviewed 路径。

## 9. 治理

| 检查项 | 规则 |
|---|---|
| 文档 | `harness/skills/reviewed/memory-governance-use/SKILL.md` |
| 状态 | reviewed |
| 触发模式 | user-directed，当用户要求处理 Memory 治理、候选审核或 Memory store 验证时触发 |
| 关联文档 | 已在正文列出 AGENTS、INDEX、HarnessIndex、HarnessEngineering、SkillIndex、SkillPolicy、SkillGovernance、MemoryIndex、MemoryPolicy、MemoryGovernance、MemoryTemplate、ScriptIndex 和 `invoke-memory.ps1`。 |
| 事实边界 | 本 Skill 只约束 Memory 治理流程，不保存项目事实、用户私有知识、raw logs 或任务过程细节。 |
| 敏感边界 | 不保存未脱敏日志、本机绝对路径、settings、auth、token、secret、私有仓库 URL 或凭据。 |
| 晋升规则 | 已由用户 approve 后晋升为 reviewed Skill，并同步 SkillIndex 和 usage sidecar；后续修订继续遵守 candidate-first 和 review-first。 |
