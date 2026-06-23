---
documentName: sandbox/SandboxIndex.md
version: v1.0.0-pre-h8-structure
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 作为 sandbox 层入口，说明环境、隔离、profile 和 settings boundary 的长期边界。
scope:
  - sandbox
  - environment
  - isolation
  - profiles
  - settings-boundary
prerequisites:
  - AGENTS.md
  - INDEX.md
relatedDocuments:
  - harness/governance/security/SandboxRuntimeSecurityModel.md
  - harness/governance/security/IsolationDecisionMatrix.md
  - harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md
outputTo:
  - sandbox/SandboxIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-structure-aligned
---
# Sandbox 索引

`sandbox/` 保存沙盒环境边界说明、隔离模型、profile 约定和 settings boundary。运行态日志、cache、tmp、Maven local repo、RAG index 和临时证据进入 `var/`，不进入 `sandbox/`。

## 1. 目标分区

| 分区 | 说明 |
|---|---|
| `sandbox/environment/` | 环境要求、runtime 前置条件和平台说明。 |
| `sandbox/isolation/` | docker、vm、remote-worker 等隔离模型说明。 |
| `sandbox/profiles/` | sandbox profile 的结构和示例边界。 |
| `sandbox/settings-boundary/` | settings、auth、credential helper 的边界说明。 |

## 2. 维护规则

1. `sandbox/` 不保存真实 settings XML、token、password、auth 文件或私有仓库地址。
2. sandbox profile 不能绕过根 `AGENTS.md` 入口契约。
3. 运行态产物默认进入 `var/`，并由 `.gitignore` 保护。
4. 隔离策略变更应同步 `harness/governance/security/IsolationDecisionMatrix.md`。
