---
documentName: harness/reports/redacted/H9-2SimulationFailureTriageSkillCandidateReview.md
version: v1.1.0-skill-mechanism-closeout
updatedAt: 2026-07-02 18:20:00.000 +08:00
status: active
purpose: 记录 H9-2 simulation-failure-triage Skill candidate 的审核、修订、用户批准、晋升结果和对 Harness Skill 机制的反向优化。
scope:
  - h9-2
  - skill-candidate-review
  - simulation-failure-triage
  - skill-mechanism-feedback
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
  - harness/skills/reviewed/simulation-failure-triage/SKILL.md
  - projects/lfms-decision/docs/project/test/simulation/SimulationFailureTriage.md
  - projects/lfms-decision/docs/project/test/simulation/SimulationManual.md
  - projects/lfms-decision/docs/project/workflow/20260702-h9-1-duplicate-history-reuse-fix.md
outputTo:
  - harness/reports/redacted/H9-2SimulationFailureTriageSkillCandidateReview.md
owner: agent
reviewAfter: 2026-07-16
supersededBy:
dependsOn:
  - harness/skills/reviewed/simulation-failure-triage/SKILL.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: approved-promoted-and-mechanism-closeout
---
# H9-2 Skill Candidate Review

## 1. Candidate

| 字段 | 内容 |
|---|---|
| Candidate | `simulation-failure-triage` |
| 路径 | `harness/skills/reviewed/simulation-failure-triage/SKILL.md` |
| 类型 | new Skill candidate |
| 来源 | H9-1 真实任务和项目级 `SimulationFailureTriage.md` |
| 当前状态 | approved，已晋升为 reviewed Skill |

## 2. Existing Skill 检查

已检查 `harness/skills/` 下现有 Skill：

- `rag-structured-ingestion`
- `rag-knowledge-use`
- `obsidian-skills/*`

结论：现有 Skill 聚焦 RAG、Knowledge 和 Obsidian，不覆盖 Java/服务仿真失败排查、连续调用状态分析、算法流水线归因、诊断 main 和最小回归验证。因此本轮创建 new Skill candidate，而不是 patch candidate。

## 3. Candidate 边界

候选 Skill 只保留通用流程：

- 建立任务口径；
- 使用稳定命令面复现；
- 判读 summary、call records、state transitions、timeline、anomalies 和结构化日志；
- 按 API/Gateway、Governance、Timeline、Strategy、Solver、Plugin Binding、Pipeline、Projection、Response 分层归因；
- 必要时编写脱敏诊断 main；
- 修复后执行合成最小回归和用户相关仿真复跑；
- 更新 workflow evidence 和治理候选。

候选 Skill 不保存：

- 真实 CSV 内容；
- 未脱敏日志；
- 完整请求响应或 `newStateJson`；
- 本机 Maven settings、本机绝对路径或凭据；
- 项目私有业务结论。

## 4. Validation

| 检查 | 结果 |
|---|---|
| `quick_validate.py` | passed，使用 `PYTHONUTF8=1` 避免 Windows 默认编码误读 UTF-8。 |
| `git diff --check` | passed。 |
| 敏感路径扫描 | passed，未命中本机绝对路径、私有 Maven settings 或凭据模式。 |
| 临时表述扫描 | passed，Skill candidate 目录未命中阶段号、运行体名称或无关 Skill 主题词。 |
| 关联文档路径检查 | passed，`SkillPolicy.md`、`SkillGovernance.md`、项目级 `SimulationFailureTriage.md` 和 `SimulationManual.md` 存在。 |
| SkillIndex 路由 | passed，已新增 candidate 路由。 |
| H9-2 计划 | complete，用户已审核通过并完成 reviewed 晋升。 |

## 5. 用户决策项

用户最终审核决策：`approve`。

第一次 revise 要求：

| 修改点 | 处理 |
|---|---|
| 主题语言改为中文，专业词和程序命名保留英文。 | 已处理；`description`、正文标题、步骤、表格和 UI metadata 已改为中文表达。 |
| 删除临时性表述。 | 已处理；Skill 正文不再使用阶段号、运行体名称或现有 Skill 对比作为主题内容。 |
| 明确使用场景和解决的问题。 | 已处理；Skill 以“仿真、回放式验证、CSV 驱动测试或连续 API 调用失败，且表层错误码不能解释根因”的场景作为触发条件。 |

第二次 revise 要求：

| 修改点 | 处理 |
|---|---|
| Skill 本体缺少笔记属性。 | 已处理；`SKILL.md` 正文新增“笔记属性”，说明资产状态、审核状态、适用对象、解决问题、输入来源和输出结果。 |
| Skill 本体缺少关联文档反向链接。 | 已处理；`SKILL.md` 正文新增“关联文档和读取路径”，包含 `AGENTS.md`、`SkillIndex.md`、`SkillPolicy.md`、`SkillGovernance.md`、`SimulationFailureTriage.md`、`SimulationManual.md` 等。 |
| 不能破坏 Skill 校验器的 frontmatter 规则。 | 已处理；YAML frontmatter 只保留 Skill 校验器允许的键，Harness 文档治理属性放在正文维护。 |

最终处置：

| 项目 | 结果 |
|---|---|
| 晋升路径 | `harness/skills/reviewed/simulation-failure-triage/SKILL.md` |
| Candidate 处置 | 从 candidate 路径移除，避免同一 Skill 在 candidate 和 reviewed 中重复路由。 |
| SkillIndex | 已同步 reviewed 路由。 |
| Usage sidecar | 已记录 `simulation-failure-triage` 的 reviewed 状态、使用次数、修订次数和批准时间。 |
| Git 管理 | 已按限定路径纳入 Git staging，等待后续 commit。 |
| H9-2 | 满足完成门禁，可标记 complete。 |

## 6. 机制反向优化结论

本次流程暴露并补齐了 Harness Skill 机制的几个落地点：

| 经验 | 机制调整 |
|---|---|
| 本次 Skill 是用户指定触发，不是自动化创建。 | `SkillPolicy.md` 区分 user-directed flow 和 auto-triggered flow；用户指定触发仍需 candidate-first 和 review-first。 |
| 用户批准后，reviewed Skill 仍可能停留为 untracked 文件。 | `SkillPolicy.md` 和 `SkillGovernance.md` 新增 Git 管理门禁：reviewed Skill 必须用限定路径纳入 Git 管理。 |
| Skill 校验器 frontmatter 与 Harness Markdown frontmatter 规则不同。 | Skill 本体保留校验器允许的 YAML；Harness 笔记属性和关联文档链接放入正文维护。 |
| `revise` 是真实审核流程中的常态，不是异常状态。 | 审核记录保留两轮 revise 要求和处理结果，作为 candidate 修订闭环证据。 |
| Skill 资产不能只写入索引，还要能被执行者找到依赖文档。 | reviewed Skill 正文包含 `AGENTS.md`、`SkillIndex.md`、`SkillPolicy.md`、`SkillGovernance.md`、`SimulationFailureTriage.md`、`SimulationManual.md` 等关联文档读取路径。 |
| 晋升后需要避免 candidate 和 reviewed 双路由。 | Promotion gate 要求清理同名活跃 candidate 路由，并由 `SkillIndex.md` 指向 reviewed 路径。 |

本次对 Harness Skill 机制的更新范围：

- `harness/skills/SkillPolicy.md`：新增用户指定触发、自动触发、review 决策、Git 管理门禁。
- `harness/governance/SkillGovernance.md`：新增 Promotion Gate 和 Git Management Gate。
- `harness/skills/SkillIndex.md`：明确 reviewed Skill 是 Harness 长期资产，晋升后必须进入 Git 管理。
- `harness/architecture/PLANS.md`：H9-2 记录为 complete，下一阶段进入 Governance 闭环验证。
