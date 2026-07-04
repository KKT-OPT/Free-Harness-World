---
documentName: harness/reports/ReportsIndex.md
version: v1.1.0-project-lifecycle-evidence-gate
updatedAt: 2026-07-02 21:20:00.000 +08:00
status: active
purpose: 定义 Harness Report 的通用机制入口，路由报告格式、规则、模板、命令面、应用场景和存放边界。
scope:
  - reports
  - report-mechanism
  - report-template
  - report-boundary
  - command-surface
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/governance/ReportArchivePolicy.md
  - harness/templates/report/ValidationReportTemplate.md
  - harness/templates/report/E2EValidationReportTemplate.md
  - harness/templates/report/FailureAttributionTemplate.md
  - harness/templates/governance/GovernanceCloseoutTemplate.md
  - harness/templates/project-template/docs/project/reports/README.md
  - harness/tools/scripts/stable/test-harness-governance.ps1
  - harness/tools/scripts/stable/test-project-registry.ps1
  - harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
outputTo:
  - harness/reports/ReportsIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/governance/ReportArchivePolicy.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: report-mechanism-boundary-and-lifecycle-gate-confirmed
---
# Report 索引

`harness/reports/` 是通用 Harness 报告机制入口和 Harness 自身脱敏报告边界。Report，中文解释是报告，是验证、治理、观测或问题分析的输出证据，不是事实源。

## 1. 存放边界

| 报告类型 | 默认位置 | 说明 |
|---|---|---|
| Harness 自身报告 | `harness/reports/redacted/` | Harness 架构、机制、工具、模板、发行或自检相关脱敏报告。 |
| Harness 历史报告 | `harness/reports/archive/` | 历史证据，默认不作为读取入口。 |
| 项目级报告 | `projects/<project-id>/docs/project/reports/` | 项目验证、治理、失败分析、架构审查或测试报告，面向项目用户审核。 |
| 项目任务过程证据 | `projects/<project-id>/docs/project/workflow/` | Task Brief、执行记录、验证摘要和候选列表。 |
| 运行态报告 | `var/` 下对应运行目录 | 可重建或含运行态上下文的报告，不进入 tracked docs，除非已脱敏并经过 review。 |

规则：

1. 具体项目 report 不放入 `harness/reports/`，应放入项目实例。
2. 通用 Harness 不把项目 report 当作机制权威，只能引用其脱敏结论作为阶段证据。
3. Report 中的建议必须经过 review，并写入目标事实文档或目标资产后，才成为稳定事实。

## 2. 格式模板

| 场景 | 模板 |
|---|---|
| 验证报告 | `harness/templates/report/ValidationReportTemplate.md` |
| 端到端验证报告 | `harness/templates/report/E2EValidationReportTemplate.md` |
| 失败归因报告 | `harness/templates/report/FailureAttributionTemplate.md` |
| 治理收口报告 | `harness/templates/governance/GovernanceCloseoutTemplate.md` |
| 项目 reports 目录说明 | `harness/templates/project-template/docs/project/reports/README.md` |

## 3. 应用场景

| 场景 | 报告用途 |
|---|---|
| Verification | 记录验证命令、结果、失败归因、残余风险和验收结论。 |
| Governance | 记录候选识别、review、approval、disposition、follow-up 和 non-promotion statement。 |
| Observability | 汇总 trace、failure attribution 和运行摘要，不复制 raw logs。 |
| Project review | 给项目用户审核具体项目任务的治理、验证或失败分析结论。 |
| Harness readiness | 给 Harness 维护者审核通用机制、工具、模板或阶段发布状态。 |

## 4. 命令面

当前稳定命令面：

| 命令 | 用途 | 输出 |
|---|---|---|
| `harness/tools/scripts/stable/test-harness-governance.ps1` | Harness 治理自检。 | dry-run findings 和 repair suggestions。 |
| `harness/tools/scripts/stable/test-project-registry.ps1` | 项目 registry 自检。 | registry findings。 |
| `harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1` | 真实项目任务生命周期证据检查。 | workflow/report lifecycle findings。 |

其他验证、仿真或 RAG 工具可以生成运行态报告，但只有脱敏、review 后才可进入 `harness/reports/` 或项目 `docs/project/reports/`。

## 5. 敏感边界

Report 不得保存：

- raw logs；
- raw terminal transcript；
- 完整 request/response；
- 完整 status JSON；
- private settings path；
- credential、auth、token、password；
- 本机绝对路径；
- 私有仓库真实 URL；
- 未经用户批准的客户或项目私有数据。

## 6. 维护规则

1. 新增通用 report 模板时，同步更新本文。
2. 新增稳定 report 相关命令面时，同步更新本文和 `harness/tools/ToolsIndex.md`。
3. 项目级 report 目录规则应优先进入项目模板和项目实例，不写成某个项目的 Harness 通用规则。
4. 阶段性 report 可以被 `PLANS.md` 引用为证据，但不得替代架构权威、治理策略或项目事实文档。
