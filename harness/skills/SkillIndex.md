---
documentName: harness/skills/SkillIndex.md
version: v2.7.0-batch-construction-tools
updatedAt: 2026-10-29
status: active
purpose: 作为 Harness Skill 入口，路由 Skill policy、candidate、reviewed、archive、usage sidecar、Memory governance、Code Review、Code Implementation、Algorithm Performance Analysis 和现有 Skill 包，并定义根目录规范。
scope:
  - skill
  - skill-index
  - skill-lifecycle
  - skill-usage
  - memory-governance-skill-reviewed
  - skill-root-normalization
  - code-review-reviewed
  - code-implementation-reviewed
  - algorithm-performance-analysis-reviewed
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/skills/SkillPolicy.md
  - harness/governance/SkillGovernance.md
  - harness/templates/skill/SkillTemplate.md
  - harness/skills/reviewed/memory-governance-use/SKILL.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/skills/reviewed/simulation-failure-triage/SKILL.md
  - harness/skills/reviewed/code-review/SKILL.md
  - harness/skills/reviewed/code-review/references/java-code-standards.md
  - harness/skills/reviewed/code-implementation/SKILL.md
  - harness/skills/reviewed/algorithm-performance-analysis/SKILL.md
  - harness/skills/reviewed/algorithm-performance-analysis/references/java-performance-analysis.md
outputTo:
  - harness/skills/SkillIndex.md
owner: mixed
reviewAfter: '2026-11-29'
supersededBy: null
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: user-requested-batch-tools-validated-and-reviewed
---

# Skill 索引

`harness/skills/` 保存可复用 workflow 或程序性经验。Skill 不是 Knowledge、不是 Memory、不是 Tool Asset，也不是一次性任务记录。

## 1. 目标结构

| 分区 | 路径 | 说明 |
|---|---|---|
| Skill Policy | `harness/skills/SkillPolicy.md` | Skill 边界、触发条件、创建/更新流程和晋升规则。 |
| Candidate Skills | `harness/skills/candidate/` | 等待 review 的新 skill 或 patch candidate。 |
| Reviewed Skills | `harness/skills/reviewed/` | 经 review 或用户明确批准的 skill；属于 Harness 长期资产，必须进入 Git 管理。 |
| Archived Skills | `harness/skills/archive/` | 被拒绝、过期或只具历史价值的 skill。 |
| Usage Sidecar | `harness/skills/usage/skill-usage.json` | Skill 动态使用统计；更新规则见 `SkillPolicy.md`。 |
| Skill Template | `harness/templates/skill/SkillTemplate.md` | Candidate / reviewed skill 的记录模板。 |

根目录只允许上述生命周期分区和 `SkillIndex.md`、`SkillPolicy.md`。未审核 Skill 包、占位 Skill 包和 patch candidate 必须放在 `candidate/` 下；外部克隆的第三方 Skill 语料不属于通用 Harness Skill 路径，应放在 `var/tmp/external-repos/` 或其他 local-only 外部参考边界。

## 2. 当前已知 Skill 包

| Skill | 当前路径 | 说明 |
|---|---|---|
| RAG Structured Ingestion | `harness/skills/candidate/rag-structured-ingestion/SKILL.md` | raw-to-candidate knowledge workflow；当前是 candidate Skill，后续需单独 review 后才能进入 reviewed。 |
| Algorithm Performance Analysis | `harness/skills/reviewed/algorithm-performance-analysis/SKILL.md` | 算法性能分析 reviewed Skill；用于建立可复现基线、拆分冷启动/预热/稳态、完成因果归因和优化验收，包含 Java/JVM reference 和确定性分段统计脚本，已由用户审核批准。 |
| Code Review | `harness/skills/reviewed/code-review/SKILL.md` | 代码审查 reviewed Skill；包含 Java 规范 reference，用于真实项目源码、diff、补丁、测试和规范沉淀审查，已通过真实项目 forward-test、用户 revise 和最终条件批准。 |
| Code Implementation | `harness/skills/reviewed/code-implementation/SKILL.md` | 代码实现 reviewed Skill；用于用户批准后的 code review finding 修复、功能实现、测试修复和实现后验证，必须更新项目 workflow evidence 并交回 code-review 复查，已与 code-review 一起通过用户审核。 |
| Memory Governance Use | `harness/skills/reviewed/memory-governance-use/SKILL.md` | Memory Update Flow 到稳定命令的流程状态机、Memory store 只读验证、candidate review package、用户决策记录和未工具化生命周期缺口识别；已由用户 approve 并晋升为 reviewed Skill。 |
| RAG Knowledge Use | `harness/skills/reviewed/rag-knowledge-use/SKILL.md` | 来源绑定草稿与封印晋升、副本审核、已知用例回归及证据归档；保留纯库/混合查询和整轮记录审计边界。 |
| Simulation Failure Triage | `harness/skills/reviewed/simulation-failure-triage/SKILL.md` | 用户指定触发并经完整 candidate、revise、approve、promotion 流程审核通过的仿真失败排查流程；正文包含笔记属性和关联文档读取路径。 |

占位候选目录包括 `architecture-design/`、`failure-attribution/` 和 `java-feature-implementation/`。这些目录只表示可能的候选方向；没有 `SKILL.md` 前不视为 active Skill。

现有 candidate skill 包在后续 review 时可迁入 `reviewed/<skill-name>/` 或治理批准的分类路径。新增或自动创建 skill 必须先进入 candidate flow，不得绕过 review。

## 3. 本轮晋升与增量合入

| 资产 | 路径 | 审核边界 |
|---|---|---|
| 有状态算法验证 | `harness/skills/reviewed/stateful-algorithm-validation/SKILL.md` | 用户授权测试通过后晋升；因果回放、独立参考和序列/生命周期验证，不替代项目引擎 |
| 已合入补丁 | 三个reviewed Skill的reliability-checks/runtime-contracts reference | 配置、状态、参考、指标、清理和计时边界按需加载；原候选已归档，无同名活跃副本 |

审核和验证证据见`harness/reports/redacted/H9-5EngineeringReliabilityFeedback.md`；
补丁来源只留`harness/skills/archive/engineering-reliability-patches/PATCH.md`，不再作为候选入口。

## 4. 维护规则

1. 新增 Skill 前必须检查现有 Skill 是否可 patch。
2. 用户指定触发和自动触发必须分开记录；用户指定触发不等于自动化创建，也不跳过 candidate 和 review。
3. `SKILL.md` frontmatter 只保存静态治理信息；动态使用统计进入 usage sidecar。
4. Skill 不能保存项目事实、用户私有知识、raw logs、settings、auth 或私有路径。
5. Reviewed Skill 是 Harness 长期资产，晋升后必须以限定路径纳入 Git 管理，不得作为 untracked 文件遗留。
