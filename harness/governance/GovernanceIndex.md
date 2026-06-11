# Governance Index

Status: active
Version: v0.3.0-local-identity-git-boundary
Date: 2026-06-12

## Purpose

This index routes durable Harness governance policies.

It is the active governance entry under `harness/governance/`. The older P9-preflight governance index under `harness/governance/archive/` is historical evidence only.

## Stable Governance Areas

| Area | Documents |
|---|---|
| Security | `harness/governance/security/SandboxRuntimeSecurityModel.md`, `GatewayAuthorizationPolicy.md`, `RuntimeApprovalPolicy.md`, `CredentialBoundaryPolicy.md`, `ContextFileSecurityPolicy.md`, `IsolationDecisionMatrix.md`, `LocalIdentityAndGitBoundaryPolicy.md` |
| Context | `harness/governance/context/ContextLoadingPolicy.md` |
| Promotion | `harness/governance/promotion/KnowledgeIntakeAndPromotionPolicy.md`, `SkillMemoryGovernance.md`, `GovernanceCloseoutPolicy.md` |
| Verification | `harness/governance/verification/ReadinessCheckPolicy.md`, `HarnessValidationPlan.md`, `HarnessValidationCases.md`, `RegressionPolicy.md` |
| Archive | `harness/governance/archive/ReportArchivePolicy.md` |
| Self-Check | `tools/scripts/stable/test-harness-governance.ps1`, `tools/docs/script-index/ScriptIndex.md`, `tools/docs/command-surfaces/StableToolSurfaceModel.md` |

## Closeout Rule

Every completed Harness-managed task may produce candidate updates, but candidates remain candidates until reviewed or explicitly approved.

P11.7 uses:

```text
harness/governance/promotion/GovernanceCloseoutPolicy.md
harness/templates/governance/GovernanceCloseoutTemplate.md
```

to classify candidate Project Facts, Knowledge, Memory, Skill, Tool, Template, Governance, Architecture, Report or RAG updates.

## Index Maintenance

When a new durable governance policy is added:

1. add it to this index;
2. add it to `harness/INDEX.md` if it is a user-facing route;
3. record source evidence in the relevant redacted report or workflow;
4. run a stale-route and sensitive-boundary scan.

Do not use archived reports, old HarnessVault directories, runtime logs or raw status files as default governance sources.

## P12.3 Governance Self-Check

P12.3 rewrites the old HarnessVault cleanup and index-maintenance ideas into a current dry-run stable tool:

```text
tools/scripts/stable/test-harness-governance.ps1
```

The tool is read-only by default and reports findings with repair suggestions. It must not inspect credential bodies, Maven settings XML, auth files or raw runtime logs. Historical scripts and runtime helper candidates remain outside the default stable governance scan until explicitly reviewed.
