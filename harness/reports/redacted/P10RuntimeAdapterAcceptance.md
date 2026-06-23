---
documentName: P10RuntimeAdapterAcceptance.md
version: v1.0.0-pre-h8-report-archive
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: archived
purpose: 记录 P10 Runtime Adapter 验收历史证据；该报告不是当前架构事实源。
scope:
  - redacted-historical-report
  - non-authoritative-evidence
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/governance/ReportArchivePolicy.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/reports/redacted/P10RuntimeAdapterAcceptance.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/governance/ReportArchivePolicy.md
review:
  reviewedBy: mixed
  reviewedAt: 2026-06-23
  decision: pre-h8-report-archive-frontmatter-alignment
---
# P10 Runtime Adapter Acceptance（P10 运行时适配验收历史报告）

## 1. Decision

Framework closeout should remain outside P9/P10.

P9 and P10 are controlled validation slices:

- P9 proves a Java/Maven demo flow can start from Harness Root, use a project instance, invoke stable tools, and record workflow evidence.
- P10 defines the runtime adapter and common result contract so Codex, Hermes, and Hermes WeCom can consume the same Harness assets.

They do not prove that the complete Harness framework is finished.

## 2. Why P11 Owns Framework Completion

Moving full framework completion before P9/P10 would make these phases too broad and brittle. The current root has many intentional placeholders, old HarnessVault assets are not fully migrated, and the standard project package is not complete enough to treat one Java demo as a real project-landing proof.

P11 later closed the controlled framework closeout gap. At the time of P10, the required P11 work was:

- accepted final architecture entry;
- old HarnessVault migrate/rewrite/archive decisions executed or explicitly deferred;
- standard project docs and templates completed;
- project registry and project package made repeatable;
- governance, promotion, report, observability, and repair-loop assets completed;
- runtime adapter flows exercised through controlled evidence;
- validation and failure attribution reports produced.

Post-P11 / P12 now owns production hardening: real project templates, registry landing, governance self-check tooling, RAG structured ingestion PoC, unified CLI, stronger isolation, live gateway validation and real project onboarding.

## 3. P10 Deliverables

| Deliverable | Path | Status |
|---|---|---|
| Common task result contract | `interaction/result-contracts/CommonTaskResultContract.md` | complete |
| Codex adapter flow | `interaction/runtime-adapters/codex/CodexRuntimeAdapterFlow.md` | complete |
| Hermes adapter flow | `interaction/runtime-adapters/hermes/HermesRuntimeAdapterFlow.md` | complete |
| Hermes WeCom task flow | `interaction/gateways/wecom/HermesWeComTaskFlow.md` | complete |
| P10 acceptance report | `docs/reports/redacted/P10RuntimeAdapterAcceptance.md` | complete |

## 4. P10 Acceptance Check

| Criterion | Result | Evidence |
|---|---|---|
| Hermes can be prompted to start from Harness Root | pass at contract level | `interaction/runtime-adapters/hermes/HermesRuntimeAdapterFlow.md` |
| Codex can use the same root entry and project registry | pass at contract level | `interaction/runtime-adapters/codex/CodexRuntimeAdapterFlow.md` |
| Both runtimes produce comparable workflow evidence | pass at contract level | common workflow path pattern in adapter docs |
| User-facing replies include result, evidence paths, and next action | pass | `interaction/result-contracts/CommonTaskResultContract.md` |
| Runtime-specific details do not leak into project facts | pass | adapter docs require runtime details to stay in Run Card/result |

## 5. P9 Correction

P9 should be recorded as flow-proof complete, not as a full Java project landing validation.

The P9 demo is useful because it proves a controlled task lifecycle slice, including project routing, stable Java/Maven tool invocation, workflow evidence, and redacted result handling.

It is not sufficient to prove the full framework because the standard project package, governance closeout, old asset migration, observability, final architecture, and reusable project onboarding flow are still incomplete.

## 6. P10 Non-Goals

P10 does not:

- install or modify Hermes;
- perform live WeCom delivery;
- create or import a real business project;
- migrate old HarnessVault assets;
- complete the final `HarnessEngineering.md`;
- implement a unified `harness` CLI;
- choose or validate a vector store;
- install RAG tools;
- change runtime approval settings.

## 7. Sensitive Boundary

This report contains only redacted Harness paths and design status. It does not include private Maven settings, credential material, auth files, unredacted logs, or private repository paths.
