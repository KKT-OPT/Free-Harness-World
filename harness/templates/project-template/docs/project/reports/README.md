---
documentName: harness/templates/project-template/docs/project/reports/README.md
version: v1.1.0-report-mechanism-link
updatedAt: 2026-07-02 20:05:00.000 +08:00
status: active
purpose: 项目实例 reports 目录模板，定义项目级报告证据边界、审核规则和通用 Harness report 机制链接。
scope:
  - project-reports-template
  - report-boundary
  - project-review-report
prerequisites:
  - projects/<project-id>/AGENTS.md
  - projects/<project-id>/docs/project/ProjectIndex.md
relatedDocuments:
  - harness/reports/ReportsIndex.md
  - harness/governance/ReportArchivePolicy.md
  - harness/templates/report/ValidationReportTemplate.md
  - harness/templates/report/E2EValidationReportTemplate.md
  - harness/templates/report/FailureAttributionTemplate.md
  - harness/templates/governance/GovernanceCloseoutTemplate.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
  - harness/templates/project-template/docs/project/workflow/README.md
outputTo:
  - harness/templates/project-template/docs/project/reports/README.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/templates/project-template/README.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-02
  decision: h9-3-report-boundary-aligned
---
# 项目 Reports 目录模板

本目录在项目实例化后对应：

```text
projects/<project-id>/docs/project/reports/
```

该目录用于保存面向项目用户审核的脱敏项目级报告。Report，中文解释是报告，是验证、治理、观测或问题分析的输出证据，不是项目事实源。

## 1. 可保存的报告类型

- validation report，中文解释是验证报告；
- governance report，中文解释是治理报告；
- architecture review report，中文解释是架构审查报告；
- test report，中文解释是测试报告；
- failure attribution report，中文解释是失败归因报告。

## 2. 审核和晋升规则

1. 项目级 report 应优先存放在项目实例中，通用 Harness 只保存格式、规则、模板、命令面和边界。
2. report 中的建议不会自动成为项目事实；只有经过 review，并显式更新目标 Project Fact、ADR、Skill、Template、Tool 或 Governance Rule 后，才成为稳定资产。
3. report 可以被 workflow evidence、PLANS 或治理收口引用为证据，但不得替代项目事实文档。
4. 如果 report 提出通用 Harness 改进，应先进入 governance review，再更新 `harness/reports/`、`harness/governance/`、`harness/templates/` 或 `harness/tools/`。

## 3. 推荐模板

| 场景 | 模板 |
|---|---|
| 验证报告 | `harness/templates/report/ValidationReportTemplate.md` |
| 端到端验证报告 | `harness/templates/report/E2EValidationReportTemplate.md` |
| 失败归因报告 | `harness/templates/report/FailureAttributionTemplate.md` |
| 治理收口报告 | `harness/templates/governance/GovernanceCloseoutTemplate.md` |

## 4. 敏感边界

不得保存 raw logs、raw terminal transcript、完整 request/response、完整 status JSON、credential、auth、token、password、private settings path、本机绝对路径、私有仓库真实 URL 或未经用户批准的客户/项目私有数据。
