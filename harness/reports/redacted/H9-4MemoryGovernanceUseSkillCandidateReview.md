---
documentName: harness/reports/redacted/H9-4MemoryGovernanceUseSkillCandidateReview.md
version: v1.5.1-stage-doc-retired
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 记录 memory-governance-use Skill candidate 的创建背景、审核门禁、两轮 revise、Memory flow 全节点验证修复结果、M3 审核前 M2 复验结果、用户 approve 和 reviewed 晋升结果。
scope:
  - skill-candidate-review
  - skill-reviewed-promotion
  - memory-governance-use
  - h9-4-memory-loop
  - memory-validation-gate
  - memory-m2-revalidation
prerequisites:
  - AGENTS.md
  - harness/architecture/PLANS.md
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
relatedDocuments:
  - harness/architecture/PLANS.md
  - harness/skills/SkillIndex.md
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
  - harness/skills/reviewed/memory-governance-use/SKILL.md
  - harness/memory/MemoryIndex.md
  - harness/memory/MemoryPolicy.md
  - harness/governance/MemoryGovernance.md
  - harness/tools/scripts/stable/invoke-memory.ps1
outputTo:
  - harness/reports/redacted/H9-4MemoryGovernanceUseSkillCandidateReview.md
owner: agent
reviewAfter: 2026-07-11
supersededBy:
dependsOn:
  - harness/skills/reviewed/memory-governance-use/SKILL.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-05
  decision: approve-and-promote-reviewed-stage-doc-retired
---
# memory-governance-use Skill Review

## 1. Candidate And Promotion

| 字段 | 内容 |
|---|---|
| Skill | `memory-governance-use` |
| Reviewed 路径 | `harness/skills/reviewed/memory-governance-use/SKILL.md` |
| 类型 | user-directed Skill |
| 来源 | Memory 机制落地审核、只读 Memory validation gate、用户对 candidate Skill 的两轮 revise 和最终 approve |
| 当前状态 | reviewed，已由用户审核通过 |

## 2. Existing Skill 检查

已检查 Harness 当前 Skill 分工：

| Skill | 判断 |
|---|---|
| `simulation-failure-triage` | 负责仿真失败排查和真实项目算法问题定位；不覆盖 Memory candidate、review package 和 Memory store gate。 |
| `rag-knowledge-use` | 负责 reviewed Knowledge 查询、知识库治理和 RAG/LLM Wiki 机制验证；不覆盖 Memory 生命周期治理。 |
| `rag-structured-ingestion` | 负责 raw-to-candidate Knowledge ingestion；不覆盖 Memory 经验候选。 |
| `obsidian-skills/*` | 负责 Obsidian 辅助能力；不替代 Harness Memory policy 和 stable command gate。 |

结论：审核前没有已审核 Skill 能完整约束 Memory 触发、只读验证、候选审核包和用户决策收口，因此先新增独立 candidate，而不是 patch 现有 Skill。用户最终 approve 后，该 Skill 已晋升为 reviewed。

## 3. Skill 边界

该 Skill 只保留通用流程：

- 使用 `memory-flow-status` 将架构权威 Memory Update Flow 映射为可执行节点状态；
- 按每个流程节点的 `coverage`、`currentCommand` 和 `executionRule` 决定继续或停止；
- 使用 `invoke-memory.ps1` 运行 `validate-memory-store` 和 `candidate-review-package`；
- 读取用户 approve、reject、defer 或 revise 决策；
- 在未进入后续写入阶段前，只记录受控写入计划，不手动晋升或归档 Memory；
- 识别当前尚未由稳定命令强制执行的 Memory 生命周期动作；
- 收口时记录验证结果、未执行项和剩余风险。

候选 Skill 不保存：

- 项目私有事实；
- 真实业务数据；
- raw logs 或任务 transcript；
- 本机私有路径；
- settings、auth、token、secret 或凭据；
- 用户私有偏好；
- reviewed Memory 内容本身。

## 4. Review Gate

| 检查项 | 结果 |
|---|---|
| 触发模式 | 通过；本次是用户指定执行 H9-4 Memory 阶段，不是自动化 Skill 创建。 |
| Candidate-first | 通过；Skill 先位于 `harness/skills/candidate/`，经用户 approve 后才晋升 reviewed。 |
| 可复用性 | revise 后通过；流程以架构权威 Memory Update Flow 为主线，并由 `memory-flow-status` 程序化输出节点覆盖和缺口。 |
| 临时表述 | revise 后通过；Skill 正文不再把 `PLANS.md` 或阶段性 Memory 计划文档作为执行依赖，也不以阶段编号作为流程主题。 |
| Frontmatter | 通过；YAML 只保留 Skill 校验器允许的 `name`、`description` 和 `metadata`，Harness 笔记属性放入正文。 |
| 关联文档 | revise 后通过；正文列出 AGENTS、INDEX、HarnessIndex、HarnessEngineering、SkillIndex、SkillPolicy、SkillGovernance、MemoryIndex、MemoryPolicy、MemoryGovernance、MemoryTemplate、ScriptIndex 和 `invoke-memory.ps1`。 |
| 敏感边界 | 通过；Skill 不保存本机路径、私有配置、凭据、raw logs 或项目私有事实。 |

## 5. Revise 记录

用户第一轮 revise 意见：

| 用户意见 | 处理 |
|---|---|
| Skill 中存在临时性说明或文档指引，例如把 `PLANS.md` 和阶段性 Memory 计划文档作为读取路径。 | 已处理；Skill 正文删除阶段计划作为执行依赖，仅保留稳定入口、架构权威、Memory policy/governance、Skill policy/governance、ScriptIndex 和 `invoke-memory.ps1`。 |
| Skill 中提到的 Memory 大部分机制仍靠文档约束，不是脚本或程序保障。 | 已处理；Skill 新增“可执行能力边界”，明确当前只有 store shape / metadata / source evidence / duplicate / sensitive scan / review package 由脚本保障；candidate 创建、reviewed 晋升、archive/defer 写入和语义冲突检测仍不得手工替代，必须等待稳定命令或用户审核。 |

用户第二轮 revise 意见：

| 用户意见 | 处理 |
|---|---|
| 需要对比 `HarnessEngineering.md` 中 Memory 流程 Mermaid 再检查 Skill。 | 已处理；新增 `memory-flow-status`，以 `HarnessEngineering.md#22.2-memory-update-flow` 为架构来源，输出 A-Q 共 17 个流程节点的命令覆盖状态。 |
| Memory Skill 的核心定位应是“流程 + 脚本/程序”，每个子步骤应该通过脚本或程序精确执行。 | 已处理；Skill 执行流程改为先运行 `memory-flow-status`，每个节点只能执行 `currentCommand`，`missing` 节点必须停止并报告 `requiredCommand` 缺口。当前命令覆盖结果为 implemented = 2，partial = 4，missing = 11，因此该 Skill 不能声明 Memory 生命周期闭环已完成。 |

全节点验证修复：

| 问题 | 修复 |
|---|---|
| `memory-flow-status` 只能报告 partial，导致 `memory-governance-use` 无法通过全部流程验证。 | 已补齐 A-Q 17 个 Memory Update Flow 节点对应的稳定命令：`verify-source-evidence`、`detect-from-workflow`、`classify-candidate-suitability`、`record-no-memory-disposition`、`create-candidate`、`classify-memory-type`、`validate-memory-store`、`detect-memory-duplicate-conflict`、`reject-or-merge-candidate`、`conflict-review-package`、`candidate-review-package`、`apply-review-decision`、`promote-reviewed`、`archive-candidate`、`revise-candidate`、`sync-memory-index`。 |
| 生命周期命令可能误写真实 Memory。 | 已设置默认 dry-run / report-only；写入 candidate、reviewed、archive 或 candidate 修订必须显式 `-Apply`，并提供 reviewer、approval note 和 reason。 |

## 6. Validation

M3 已执行以下验收命令：

| 验证项 | 命令或证据 | 结果 |
|---|---|---|
| Skill frontmatter sanity | 只读 PowerShell 检查 `harness/skills/reviewed/memory-governance-use/SKILL.md` 的 YAML 顶层键 | passed；顶层键仅为 `name`、`description`、`metadata`。 |
| 临时计划依赖扫描 | `rg "PLANS|H9_4_MEMORY_LOOP_PLANS|H9-4|M2|M3|阶段计划|临时性" harness/skills/reviewed/memory-governance-use/SKILL.md` | passed，Skill 本体无命中。 |
| Memory flow status | `invoke-memory.ps1 -Command memory-flow-status` | passed；stepCount = 17，implementedStepCount = 17，partialStepCount = 0，missingStepCount = 0，flowCoverageState = complete。 |
| Flow command smoke | 对 A-Q 节点对应命令执行 dry-run / 只读 smoke | passed；所有命令返回 state = passed。 |
| Memory store gate | `invoke-memory.ps1 -Command validate-memory-store` | passed；entryCount = 1，candidateCount = 1，reviewedCount = 0，archiveCount = 0，blockingIssues = 0。 |
| 当前 Memory candidate 状态 | `validate-memory-store` status JSON | `java-maven-real-project-validation` 仍为 `assetState=candidate`、frontmatter decision = `pending`、promotion decision = `defer`、targetState = `candidate`。 |
| Memory gate self-test | `invoke-memory.ps1 -Command validate-memory-store -SelfTest` | passed；负向 fixture 能检出缺 frontmatter、缺 review 字段、缺 source evidence、重复 `memoryId`、非法 `assetState` 和 credential-like 敏感模式。 |
| Source evidence | `invoke-memory.ps1 -Command verify-source-evidence -CandidateId java-maven-real-project-validation` | passed；source evidence 文件存在。 |
| Duplicate / conflict check | `invoke-memory.ps1 -Command detect-memory-duplicate-conflict -CandidateId java-maven-real-project-validation` | passed；duplicate id = 0、duplicate statement = 0、duplicate source = 0、conflict = 0。 |
| Candidate review package | `invoke-memory.ps1 -Command candidate-review-package -CandidateId java-maven-real-project-validation` | passed；仅写 runtime review package，decision options = approve / reject / defer / revise。 |
| Python syntax | `python -m py_compile harness/tools/scripts/stable/memory_tool/commands.py harness/tools/scripts/stable/memory_tool/cli.py` | passed。 |
| 审核前写入边界 | 检查 `harness/memory/reviewed/`、`harness/memory/archive/` 和 `harness/skills/reviewed/memory-governance-use/SKILL.md` | passed；审核前 reviewed/archive Memory 仍只有 `.gitkeep`，reviewed Skill 尚不存在。 |
| 审核后晋升边界 | 用户 approve 后迁入 reviewed 路径并同步 `SkillIndex.md`、`skill-usage.json` | passed；只晋升 Skill，不修改 Memory candidate/reviewed/archive。 |
| Git diff whitespace | `git diff --check` | passed。 |
| 敏感扫描 | 针对本轮新增/更新的 Skill、审核包、计划和索引执行本机路径与 credential-like 模式扫描 | passed，未命中。 |
| Governance self-check | `test-harness-governance.ps1` | passed；finding 为既有 architecture legacy warning 和嵌套项目 Git info。M3 不要求接入 Memory gate 到 governance self-check，接入属于后续阶段。 |

说明：当前仓库没有稳定 `quick_validate.py` 入口，因此本报告不再把它作为 Skill 验收依据；本轮以 stable Memory command、frontmatter sanity、文本扫描、语法检查和 governance self-check 作为 M2/M3 审核前验证证据。

M3 审核通过前，已按用户要求使用更新后的 `memory-governance-use` 重新验证 M2。结论是：M2 只读门禁仍通过，当前 Memory 候选仍为 `candidate/defer`，审核前未发生 reviewed/archive Memory 写入、candidate 修改或 reviewed Skill 晋升。用户 approve 后，仅执行 Skill 晋升和索引同步。

## 7. 用户决策和处置

用户已审核 `memory-governance-use` candidate，并给出：

| 决策 | 含义 | 处置 |
|---|---|---|
| `approve` | 认可该 Skill 可作为 reviewed Memory 治理流程。 | 已晋升到 `harness/skills/reviewed/memory-governance-use/`，并同步 `SkillIndex.md` 和 usage sidecar。 |

## 8. 当前结论

M3 已完成：`memory-governance-use` 已由用户 approve 并晋升为 reviewed Skill。该动作只处理 Skill 生命周期，不执行 Memory promotion、archive 或 defer 写入；Memory 候选 `java-maven-real-project-validation` 的生命周期决策进入 M4。
