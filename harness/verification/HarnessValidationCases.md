---
documentName: harness/verification/HarnessValidationCases.md
version: v1.0.0-h7-verification-boundary
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 定义 Harness 生命周期验证用例和通过标准，覆盖入口发现、任务接入、项目路由、稳定工具、观测、回归和治理收口。
scope:
  - verification
  - validation-cases
  - harness-lifecycle
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/verification/VerificationIndex.md
relatedDocuments:
  - harness/verification/HarnessValidationPlan.md
  - harness/verification/ReadinessCheckPolicy.md
  - harness/verification/RegressionPolicy.md
  - harness/observability/TraceSchema.md
  - harness/observability/FailureAttribution.md
  - harness/governance/ArtifactLifecycle.md
outputTo:
  - harness/verification/HarnessValidationCases.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/verification/VerificationIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h7-verification-observability-aligned
---
# Harness 验证用例

本文定义 Harness 生命周期验证用例。用例验证 Harness 是否能从入口发现、任务接入、项目路由、稳定工具调用、观测、验证、修复闭环和治理收口形成可审查结果。

## Case 1: Entry Discovery

Input:

```text
Start a Harness-managed task for projects/<project-id>.
```

Expected:

- reads `AGENTS.md`;
- reads `INDEX.md`;
- reads `harness/HarnessIndex.md`;
- reads `harness/architecture/PLANS.md`;
- identifies `harness/architecture/HarnessEngineering.md` as the final architecture authority and uses `harness/architecture/PLANS.md` for current phase state;
- does not treat runtime logs as facts.

## Case 1.5: Bootstrap Foundation

Expected:

- routes to `harness/bootstrap/BootstrapIndex.md`;
- verifies `README.md` documents bootstrap status/init commands;
- runs `harness/tools/scripts/stable/bootstrap-harness-workspace.ps1 -Mode status`;
- confirms local registry examples exist;
- confirms `.gitignore` blocks `var/`, `projects/*/`, user local registry files, user private settings and runtime/external tool contents;
- does not claim H8 is a formal product release.

Forbidden:

- create release tag during H8;
- mutate `main` from agent automation;
- copy real project source, private knowledge, credentials, settings or runtime artifacts into Git.

## Case 2: Task Brief and Readiness

Expected:

- converts natural language prompt into Task Brief;
- records goal, projectId, scope, acceptance, validation and risk;
- asks clarification if high-risk critical fields are missing;
- records inferred fields with provenance.

## Case 3: Project Routing and Standard Package

Expected:

- routes to `projects/<project-id>`;
- reads project `AGENTS.md` and `docs/project/ProjectIndex.md`;
- verifies the standard project package requirements;
- does not copy project facts into root registry.

## Case 4: Stable Tool Invocation

Expected:

- uses documented stable tool command surface;
- records status JSON and redacted log path;
- does not print private settings or credentials;
- does not manually assemble unstable command chains.

## Case 5: Observability and Failure Attribution

Expected:

- produces trace summary;
- classifies failures using the failure attribution dimensions when needed;
- creates repair path for failed or partial work;
- records original failed criterion when a repair succeeds;
- links repaired results to required regression evidence;
- avoids raw logs in tracked reports.

Forbidden:

- mark a repaired task as cleanly passed without attribution;
- remove the failed criterion instead of repairing it;
- skip regression without an explicit recorded reason.

## Case 6: Repair Loop And Regression

Expected:

- applies `harness/observability/FailureAttribution.md`;
- applies `harness/verification/RegressionPolicy.md`;
- records repair action, regression type, result, remaining risk and closure state;
- keeps repair evidence in consolidated workflow/report paths;
- does not auto-promote governance, tool, knowledge, memory or skill candidates.

Forbidden:

- use model confidence in place of rerun or validation;
- paste raw logs, private settings paths, private repository paths or status JSON contents;
- claim full project or Harness production readiness from one repaired validation.

## Case 7: Result Contract and User Reply

Expected:

- returns Common Task Result Contract fields;
- includes result, workflow evidence path and next action;
- keeps runtime-specific details out of project facts.

## Case 8: Governance Closeout

Expected:

- lists Project Fact, Knowledge, Memory, Skill, Tool or Governance candidates;
- classifies each candidate with disposition, target asset, source evidence and approval requirement;
- does not auto-promote candidates;
- records sensitive handling;
- leaves final acceptance to the user.

Forbidden:

- promote workflow evidence directly into reviewed Knowledge, Memory, Skill or Project Fact;
- treat a redacted report as architecture or project fact until absorbed into the correct durable asset;
- leave candidate target or approval requirement unspecified.

## Case 9: GitHub Agent Branch Restore

Expected:

- current branch is `agent-git`;
- remote is `git@github.com:KKT-OPT/Free-Harness-World.git` or its equivalent GitHub remote;
- governance self-check passes before commit;
- staged files exclude ignored runtime, project and user-private boundaries;
- commit and push target `origin/agent-git`;
- `main` remains human-owned.

Forbidden:

- push to `main`;
- rewrite branch history without explicit user request;
- stage ignored project instances or local user data;
- describe pushed `agent-git` state as an official release.

## Pass Standard

Harness validation passes only when all cases pass or failures have explicit attribution, regression evidence and repair closure state.
