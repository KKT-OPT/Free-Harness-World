---
documentName: harness/governance/ReportArchivePolicy.md
version: v1.1.0-project-report-boundary
updatedAt: 2026-07-02 20:02:00.000 +08:00
status: active
purpose: 定义 Report 作为治理证据的归档、读取、项目实例落点、晋升和敏感边界规则。
scope:
  - governance
  - report-archive
  - report-boundary
prerequisites:
  - AGENTS.md
  - harness/governance/GovernanceIndex.md
relatedDocuments:
  - harness/reports/ReportsIndex.md
  - harness/reports/
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/governance/ReportArchivePolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: project-report-boundary-confirmed
---
# Report Archive Policy（报告归档策略）

Report 是治理、验证或观测输出证据，不是长期事实源。Report 中的建议必须经过 review 或用户明确批准，并写入目标资产后才成为正式事实。

## 1. Report 区域

| 区域 | 说明 |
|---|---|
| `harness/reports/redacted/` | Harness 自身机制、模板、工具、架构、发行或自检相关的脱敏报告。 |
| `harness/reports/archive/` | 历史报告，默认不加载。 |
| `projects/<project-id>/docs/project/workflow/` | 项目任务过程证据。 |
| `projects/<project-id>/docs/project/reports/` | 项目级验证、治理、故障分析、架构审查或测试报告，供项目用户审核。 |

项目相关的具体 report 实例应进入 `projects/<project-id>/docs/project/reports/`。通用 Harness 只保存 report 规则、格式、模板、命令面和 Harness 自身报告，不把具体项目 report 作为治理入口。

## 2. 晋升规则

Report conclusion 只有被吸收到以下目标资产后，才成为稳定事实：

- architecture document；
- governance policy；
- project fact；
- reviewed Knowledge；
- reviewed Memory；
- approved Skill；
- template；
- command-surface doc。

## 3. 禁止内容

Report 不得保存 raw logs、terminal transcripts、private settings paths、credentials、auth files、unredacted status JSON 或未经 review 的 raw vault reports。
