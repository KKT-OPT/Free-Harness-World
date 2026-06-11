# Hermes Runtime Adapter Flow

Status: active-contract
Version: v0.1.1-post-p11-cleanup
Date: 2026-06-09

## 1. Purpose

This document defines how Hermes consumes Harness Root for managed project automation.

Hermes remains an external agent runtime. Harness does not own the Hermes runtime kernel, messaging implementation, auth subsystem, or session manager.

## 2. Harness Start Prompt

A Hermes task can be prompted to start from Harness Root with this minimal instruction:

```text
HARNESS_ROOT is <HARNESS_ROOT>.
Start from AGENTS.md, then harness/INDEX.md and harness/PLANS.md.
For project work, resolve projectId, read projects/<project-id>/AGENTS.md
and projects/<project-id>/docs/project/ProjectIndex.md.
Use Harness stable tool surfaces when executing validation.
Write workflow evidence under projects/<project-id>/docs/project/workflow/.
Return the Common Task Result Contract with result, evidence paths, and next action.
Do not include credentials, auth files, private settings, private repository paths, or raw logs.
```

This prompt is an adapter instruction. It is not a replacement for Harness documents.

## 3. Flow

1. Receive task through Hermes CLI, WeCom, or another gateway.
2. Apply gateway authorization and runtime approval policy before execution.
3. Read Harness Root entry documents.
4. Build Task Brief from the user prompt.
5. Resolve project and read project entry documents.
6. Create workflow evidence in the project work copy.
7. Invoke stable Harness tool surfaces when needed.
8. Produce a Common Task Result Contract.
9. Send a concise user-facing reply through the originating channel.

## 4. Workflow Evidence Requirements

Hermes workflow evidence must match the Codex evidence shape:

```text
projects/<project-id>/docs/project/workflow/<task-id>.md
```

Required sections:

- Task Brief;
- Harness Run Card;
- readiness check;
- execution plan;
- execution record;
- validation summary;
- acceptance state;
- governance candidates.

Gateway metadata may be summarized in the Run Card, but runtime-specific prompts, channel implementation details, and auth state must not become project facts.

## 5. Security Boundary

Hermes must observe:

```text
harness/governance/security/GatewayAuthorizationPolicy.md
harness/governance/security/RuntimeApprovalPolicy.md
harness/governance/security/CredentialBoundaryPolicy.md
harness/governance/security/ContextFileSecurityPolicy.md
harness/governance/security/IsolationDecisionMatrix.md
```

Ordinary managed-project automation must not default to YOLO/off approval mode unless an intentionally isolated environment has been approved.

## 6. Result Contract

Hermes final replies must follow:

```text
adapter/result-contracts/CommonTaskResultContract.md
```

For Hermes CLI:

```yaml
runtime: hermes
channel: cli
```

For Hermes WeCom:

```yaml
runtime: hermes
channel: wecom
```

## 7. P10 Acceptance Mapping

| P10 Criterion | Hermes Flow |
|---|---|
| Hermes can be prompted from Harness Root | Harness Start Prompt provides the minimal adapter instruction. |
| Comparable workflow evidence | Writes the same workflow shape as Codex. |
| User replies include result, evidence paths, next action | Uses Common Task Result Contract. |
| Runtime details do not leak into project facts | Runtime/channel details stay in Run Card/result, not facts. |

## 8. P10 Scope Boundary

P10 defines the adapter flow and contract. It does not install Hermes, change Hermes auth, prove live WeCom delivery, or complete the full Harness framework.

P11 later completed controlled framework closeout. Live gateway execution remains a separate Post-P11 / P12 task that requires explicit user authorization.
