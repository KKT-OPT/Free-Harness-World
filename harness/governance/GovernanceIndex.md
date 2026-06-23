---
documentName: harness/governance/GovernanceIndex.md
version: v1.0.0-pre-h8-governance-mechanism
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 作为 Harness Governance 的长期入口，路由 security、context、promotion、archive 和 self-check，并说明 Governance 与 Verification、Observability 的边界。
scope:
  - governance
  - security
  - context
  - promotion
  - archive
  - self-check
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/verification/VerificationIndex.md
  - harness/observability/ObservabilityIndex.md
  - harness/governance/ArtifactLifecycle.md
  - harness/tools/scripts/stable/test-harness-governance.ps1
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
  reviewedAt: 2026-06-23
  decision: pre-h8-governance-mechanism-aligned
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
| Promotion | `harness/governance/KnowledgePromotionPolicy.md`, `MemoryGovernance.md`, `SkillGovernance.md` |
| Document and Index | `harness/governance/DocumentGovernance.md`, `IndexMaintenancePolicy.md` |
| Cleanup and Schedule | `harness/governance/CleanupPolicy.md`, `ScheduledGovernance.md` |
| Archive | `harness/governance/ReportArchivePolicy.md` |
| Self-Check | `harness/tools/scripts/stable/test-harness-governance.ps1`, `harness/tools/docs/script-index/ScriptIndex.md`, `harness/tools/docs/command-surfaces/StableToolSurfaceModel.md` |

## 2. 与 Verification / Observability 的边界

| 层 | 入口 | Governance 使用方式 |
|---|---|---|
| Verification | `harness/verification/VerificationIndex.md` | 引用 readiness、validation、regression 结果，决定是否需要 review、修复、延期或用户验收。 |
| Observability | `harness/observability/ObservabilityIndex.md` | 引用 trace summary 和 failure attribution 摘要，判断治理候选和敏感边界。 |
| Reports | `harness/reports/` | 保存脱敏结果和治理报告；报告建议必须 review 后才能进入长期资产。 |

Governance 不保存验证规则正文，不把 trace summary 当作事实源，不把 report suggestion 自动晋升为 Project Fact、Knowledge、Memory、Skill、Tool 或 Architecture。

## 3. Closeout 规则

每个完成的 Harness-managed task 可以产生候选更新，但候选必须保持 candidate 状态，直到经过 review 或用户明确批准。

候选分类使用：

```text
harness/governance/ArtifactLifecycle.md
harness/templates/governance/GovernanceCloseoutTemplate.md
```

候选类型包括 Project Fact、Knowledge、Memory、Skill、Tool、Template、Governance、Architecture、Report 或 RAG 更新。

## 4. 索引维护

新增长期治理策略时：

1. 更新本文；
2. 如果是全局用户可见路由，同步更新 `INDEX.md`；
3. 如果是 General Harness 路由，同步更新 `harness/HarnessIndex.md`；
4. 记录来源证据到相关 redacted report 或 workflow evidence；
5. 运行 stale-route 和 sensitive-boundary 自检。

不要把 archived reports、旧 HarnessVault 目录、runtime logs、raw trace 或 raw status JSON 当作默认治理来源。

## 5. Governance Self-Check

治理自检入口：

```text
harness/tools/scripts/stable/test-harness-governance.ps1
```

该工具默认只读，输出 findings 和 repair suggestions。它不得检查 credential 正文、Maven settings XML、auth 文件或 raw runtime logs。historical scripts、runtime helpers 和 external tools 默认不进入稳定治理扫描。
