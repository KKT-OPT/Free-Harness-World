---
documentName: ValidationReportTemplate.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '提供 Harness 管理任务验证报告的标准结构和敏感信息排除规则。'
scope:
  - validation-report-template
  - verification-evidence
  - sensitive-handling
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/templates/TemplateIndex.md
  - harness/verification/VerificationIndex.md
outputTo:
  - harness/templates/report/ValidationReportTemplate.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: mixed
  reviewedAt: 2026-06-23
  decision: pre-h8-frontmatter-alignment
---
# Validation Report Template（验证报告模板）

## 概要

说明验证对象以及是否通过。

## 范围

列出项目、文件、命令和验证 profile。

## 命令

```text
<command>
```

## 结果

```yaml
status: pass | fail | partial
statusJson: <path>
logPath: <path>
traceSummary: <path-or-workflow-section>
resultContract: <path-or-workflow-section>
```

## 失败归因

如果失败，摘要说明可能原因和下一步修复动作。

## 发现

列出重要发现，包括部分通过、已修复失败、残余风险和证据缺口。

## 建议动作

列出下一步动作、审查需求、修复任务或延后迁移决策。

## 审批要求

说明在晋升、破坏性清理、真实 gateway 执行、真实项目导入或策略/模板变更前是否需要用户审批。

## 后续任务

列出后续任务，不把它们视为已完成工作。

## Sensitive Handling

确认凭据、私有 settings、auth 文件和未脱敏日志没有复制到受管文档。

不要把原始日志、原始 Status JSON 内容、私有 settings 路径、私有仓库路径、凭据或 auth 文件正文粘贴进本报告。
