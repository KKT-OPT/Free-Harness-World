---
documentName: harness/governance/ScheduledGovernance.md
version: v1.0.0-pre-h8-scheduled-governance
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Harness 定期治理检查、reviewAfter 复核、stale 文档处理和自检报告规则。
scope:
  - governance
  - scheduled-review
  - self-check
  - review-after
prerequisites:
  - AGENTS.md
  - harness/governance/GovernanceIndex.md
relatedDocuments:
  - harness/tools/scripts/stable/test-harness-governance.ps1
  - harness/governance/DocumentGovernance.md
  - harness/governance/IndexMaintenancePolicy.md
outputTo:
  - harness/governance/ScheduledGovernance.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-scheduled-governance-aligned
---
# Scheduled Governance

Scheduled Governance，中文解释是定期治理，负责按 reviewAfter、路径变更、Git 边界变更或用户要求触发 Harness 自检。

## 1. 触发条件

- 进入 H8 bootstrap 或发布前；
- 大规模路径迁移后；
- `.gitignore` 或 GitHub 管理策略变更后；
- 重要文档 reviewAfter 到期；
- governance self-check 出现 warning 或 error；
- 用户要求进行架构健康检查。

## 2. 检查内容

- required routes；
- stale route candidates；
- compatibility stubs；
- architecture authority boundary；
- frontmatter 和文档状态；
- sensitive boundary；
- Git ignore 和 project repo boundary；
- Memory、Skill、Knowledge promotion gate；
- runtime / generated output 是否误入 Git。

## 3. 输出

自检结果可以进入 redacted report 或 `harness/architecture/PLANS.md` 的阶段验收记录。自检报告不是事实源，必须通过治理吸收后才能更新长期资产。
