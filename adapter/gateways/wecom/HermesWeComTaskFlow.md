---
documentName: adapter/gateways/wecom/HermesWeComTaskFlow.md
version: v0.1.0-p10
updatedAt: 2026-06-17 18:30:00.000 +08:00
status: draft
purpose: 维护 Hermes WeCom Task Flow 的长期文档说明、入口边界或目标骨架，供 Harness 路由、治理或后续阶段重构使用。
scope:
  - adapter-contract
  - agent-runtime-routing
  - task-flow
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/PLANS.md
outputTo:
  - adapter/gateways/wecom/HermesWeComTaskFlow.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-17
  decision: frontmatter-aligned
---
# Hermes WeCom Task Flow

## 1. Purpose

This document defines the Harness-facing task flow for Hermes WeCom usage.

WeCom is a user interaction channel. It must not become the source of project facts, runtime policy, or credentials.

## 2. Flow

```text
WeCom user prompt
-> Hermes gateway authorization
-> Hermes runtime adapter
-> Harness Root entry
-> Task Brief
-> project routing
-> workflow evidence
-> stable tool invocation
-> Common Task Result Contract
-> WeCom user-facing reply
```

## 3. Required Entry Instruction

The Hermes gateway should pass or preserve this Harness orientation:

```text
Start from <HARNESS_ROOT>.
Read AGENTS.md, INDEX.md, harness/HarnessIndex.md, and harness/architecture/PLANS.md.
Use project entry documents and stable Harness tools.
Write workflow evidence before returning the result.
Use the Common Task Result Contract.
Do not include credentials, auth files, private settings, private repository paths, or raw logs.
```

## 4. Authorization and Approval

Before project execution, the gateway flow must satisfy:

- the WeCom user is authorized for the requested Harness/project scope;
- dangerous commands require approval according to runtime policy;
- credential passthrough is explicit allowlist only;
- context files are treated as untrusted input until checked;
- ordinary managed-project automation does not default to YOLO/off approval mode.

Policies:

```text
harness/governance/security/GatewayAuthorizationPolicy.md
harness/governance/security/RuntimeApprovalPolicy.md
harness/governance/security/CredentialBoundaryPolicy.md
harness/governance/security/ContextFileSecurityPolicy.md
```

## 5. Workflow Evidence

The WeCom flow must create the same project evidence shape as Codex:

```text
projects/<project-id>/docs/project/workflow/<task-id>.md
```

The workflow may record:

- channel: `wecom`;
- runtime: `hermes`;
- authorization check result as a redacted summary;
- redacted validation evidence paths.

The workflow must not record:

- WeCom auth state or tokens;
- private settings paths;
- raw chat transcripts if they contain sensitive data;
- raw runtime logs.

## 6. WeCom Reply Shape

Recommended compact reply:

```text
Result: <passed|failed|partial|blocked>
Project: <project-id>
Summary: <short summary>
Workflow: <workflow path>
Status: <status JSON path or none>
Next: <next action>
```

When message length is constrained, keep at least:

```text
Result: <status>
Workflow: <path>
Next: <next action>
```

## 7. P10 Scope Boundary

P10 documents the WeCom flow and result contract. It does not perform a live WeCom send, install Hermes, or migrate gateway secrets.
