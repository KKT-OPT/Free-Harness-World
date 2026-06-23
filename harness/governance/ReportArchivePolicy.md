---
documentName: harness/governance/ReportArchivePolicy.md
version: v1.0.0-pre-h8-report-archive
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Report 作为治理证据的归档、读取、晋升和敏感边界规则。
scope:
  - governance
  - report-archive
  - report-boundary
prerequisites:
  - AGENTS.md
  - harness/governance/GovernanceIndex.md
relatedDocuments:
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
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-report-archive-aligned
---
# Report Archive Policy（报告归档策略）

Report 是治理、验证或观测输出证据，不是长期事实源。Report 中的建议必须经过 review 或用户明确批准，并写入目标资产后才成为正式事实。

## 1. Report 区域

| 区域 | 说明 |
|---|---|
| `harness/reports/redacted/` | 可在相关任务中读取的脱敏报告。 |
| `harness/reports/archive/` | 历史报告，默认不加载。 |
| `projects/<project-id>/docs/project/workflow/` | 项目任务过程证据。 |
| `projects/<project-id>/docs/project/reports/` | 项目级报告。 |

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
