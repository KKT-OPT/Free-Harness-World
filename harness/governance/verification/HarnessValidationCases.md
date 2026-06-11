# Harness Validation Cases

Status: draft
Version: v0.4.0-p11.7
Date: 2026-06-10

## Purpose

This document defines the P11 validation cases for the final Harness architecture authority.

## Case 1: Entry Discovery

Input:

```text
Start a Harness-managed task in java-demo.
```

Expected:

- reads `AGENTS.md`;
- reads `harness/INDEX.md`;
- reads `harness/PLANS.md`;
- identifies `harness/architecture/HarnessEngineering.md` as the final architecture authority and uses `harness/PLANS.md` for current phase state;
- does not treat runtime logs as facts.

## Case 2: Task Brief and Readiness

Expected:

- converts natural language prompt into Task Brief;
- records goal, projectId, scope, acceptance, validation and risk;
- asks clarification if high-risk critical fields are missing;
- records inferred fields with provenance.

## Case 3: Project Routing and Standard Package

Expected:

- routes to `projects/java-demo`;
- reads project `AGENTS.md` and `docs/project/ProjectIndex.md`;
- verifies the standard project package requirements;
- does not copy project facts into root registry.

## Case 4: Stable Tool Invocation

Expected:

- uses documented Java/Maven command surface;
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

- applies `harness/observability/failure-attribution/FailureAttributionPolicy.md`;
- applies `harness/governance/verification/RegressionPolicy.md`;
- records repair action, regression type, result, remaining risk and closure state;
- keeps repair evidence in consolidated workflow/report paths;
- does not auto-promote governance, tool, knowledge, memory or skill candidates.

Forbidden:

- use model confidence in place of rerun or validation;
- paste raw logs, private settings paths, private repository paths or status JSON contents;
- claim full project or Harness production readiness from one repaired demo validation.

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

## Pass Standard

P11 passes only when all cases pass or failures have explicit attribution, regression evidence and repair closure state.
