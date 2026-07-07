---
documentName: harness/governance/GovernanceIndex.md
version: v1.3.0-project-feedback-policy
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 作为 Harness Governance 的长期入口，路由 security、context、promotion、project feedback、archive 和 self-check，并说明通用治理机制与具体项目治理实例、Report、Verification、Observability 的边界。
scope:
  - governance
  - security
  - context
  - promotion
  - project-feedback
  - archive
  - self-check
  - report-instance-boundary
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/verification/VerificationIndex.md
  - harness/observability/ObservabilityIndex.md
  - harness/governance/ArtifactLifecycle.md
  - harness/governance/ProjectHarnessFeedbackPolicy.md
  - harness/governance/ReportArchivePolicy.md
  - harness/reports/ReportsIndex.md
  - harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md
  - harness/tools/scripts/stable/test-harness-governance.ps1
  - harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
outputTo:
  - harness/governance/GovernanceIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: project-feedback-policy-routed
---
# Governance 索引

本文是 `harness/governance/` 的长期治理入口。Governance，中文解释是治理，负责 review、promotion、archive、cleanup、approval boundary 和敏感边界，不直接替代 Verification 或 Observability。

旧 archive 目录中的治理索引只作为历史证据，不作为默认读取来源。

## 1. 治理区域

| 区域 | 文档 |
|---|---|
| Security | `harness/governance/security/SandboxRuntimeSecurityModel.md`, `GatewayAuthorizationPolicy.md`, `RuntimeApprovalPolicy.md`, `CredentialBoundaryPolicy.md`, `ContextFileSecurityPolicy.md`, `IsolationDecisionMatrix.md`, `LocalIdentityAndGitBoundaryPolicy.md` |
| Context | `harness/governance/context/ContextLoadingPolicy.md` |
| Artifact Lifecycle | `harness/governance/ArtifactLifecycle.md` |
| Project Feedback | `harness/governance/ProjectHarnessFeedbackPolicy.md`, `harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md` |
| Promotion | `harness/governance/KnowledgePromotionPolicy.md`, `MemoryGovernance.md`, `SkillGovernance.md` |
| Document and Index | `harness/governance/DocumentGovernance.md`, `IndexMaintenancePolicy.md` |
| Cleanup and Schedule | `harness/governance/CleanupPolicy.md`, `ScheduledGovernance.md` |
| Archive | `harness/governance/ReportArchivePolicy.md` |
| Self-Check | `harness/tools/scripts/stable/test-harness-governance.ps1`, `harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1`, `harness/tools/scripts/stable/invoke-memory.ps1`, `harness/tools/docs/script-index/ScriptIndex.md`, `harness/tools/docs/command-surfaces/StableToolSurfaceModel.md` |

## 2. 与 Verification / Observability 的边界

| 层 | 入口 | Governance 使用方式 |
|---|---|---|
| Verification | `harness/verification/VerificationIndex.md` | 引用 readiness、validation、regression 结果，决定是否需要 review、修复、延期或用户验收。 |
| Observability | `harness/observability/ObservabilityIndex.md` | 引用 trace summary 和 failure attribution 摘要，判断治理候选和敏感边界。 |
| Reports | `harness/reports/` 和 `projects/<project-id>/docs/project/reports/` | 保存脱敏报告证据；通用 Harness 报告和项目报告按所属边界分开存放。 |

Governance 不保存验证规则正文，不把 trace summary 当作事实源，不把 report suggestion 自动晋升为 Project Fact、Knowledge、Memory、Skill、Tool 或 Architecture。

## 3. Closeout 规则

每个完成的 Harness-managed task 可以产生候选更新，但候选必须保持 candidate 状态，直到经过 review 或用户明确批准。

候选分类使用：

```text
harness/governance/ArtifactLifecycle.md
harness/governance/ProjectHarnessFeedbackPolicy.md
harness/templates/governance/GovernanceCloseoutTemplate.md
harness/templates/governance/ProjectHarnessFeedbackTriageTemplate.md
```

候选类型包括 Project Fact、Knowledge、Memory、Skill、Tool、Template、Governance、Architecture、Report 或 RAG 更新。

如果候选来源于真实项目反向优化，必须先使用 `ProjectHarnessFeedbackPolicy.md` 判断信号类型和目标资产，避免把项目事实、私有知识或一次性任务历史误写入通用 Harness。

## 4. 具体实例落点规则

通用 Harness Governance 只保存可复用规则、机制、模板、门禁和命令面，不保存某个项目的具体治理实例作为默认入口。

具体治理和报告实例按所属对象落点：

| 实例类型 | 默认落点 | 说明 |
|---|---|---|
| 项目任务 workflow evidence | `projects/<project-id>/docs/project/workflow/` | 记录任务过程、Task Brief、执行和验证摘要。 |
| 项目级 report | `projects/<project-id>/docs/project/reports/` | 面向用户审核的项目验证、治理、故障分析或架构审查报告。 |
| 通用 Harness report | `harness/reports/` | 仅保存 Harness 自身机制、模板、工具、架构或发行相关的脱敏报告。 |
| 通用治理规则 | `harness/governance/` | 保存可复用治理规则、生命周期、审批和边界策略。 |

项目报告中的建议不能直接成为通用 Harness 规则；只有经过 review 并抽象为通用机制后，才可更新 `harness/governance/`、`harness/templates/`、`harness/tools/` 或其他长期资产。

真实项目任务的治理收口还应运行可执行门禁，而不只依赖 Mermaid 或人工描述：

```text
harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
```

该门禁只验证项目 workflow evidence 和项目 report 的结构与边界，不把具体项目报告复制到通用 Harness。

## 5. 索引维护

新增长期治理策略时：

1. 更新本文；
2. 如果是全局用户可见路由，同步更新 `INDEX.md`；
3. 如果是 General Harness 路由，同步更新 `harness/HarnessIndex.md`；
4. 记录来源证据到相关 redacted report 或 workflow evidence；
5. 运行 stale-route 和 sensitive-boundary 自检。

不要把 archived reports、旧 HarnessVault 目录、runtime logs、raw trace 或 raw status JSON 当作默认治理来源。

## 6. Governance Self-Check

治理自检入口：

```text
harness/tools/scripts/stable/test-harness-governance.ps1
```

该工具默认只读，输出 findings 和 repair suggestions。它不得检查 credential 正文、Maven settings XML、auth 文件或 raw runtime logs。historical scripts、runtime helpers 和 external tools 默认不进入稳定治理扫描。

`test-harness-governance.ps1` 必须至少运行 `test-project-lifecycle-evidence.ps1 -SelfTest`，保证真实项目生命周期证据门禁脚本本身可用；同时必须运行 `invoke-memory.ps1 -Command validate-memory-store` 和 `invoke-memory.ps1 -Command validate-memory-store -SelfTest`，保证 Memory store 当前状态和负向 fixture 门禁可用。具体项目任务收口时，应再对目标项目 workflow evidence 和项目 report 运行 `test-project-lifecycle-evidence.ps1`。
