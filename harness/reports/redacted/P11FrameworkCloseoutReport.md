---
documentName: P11FrameworkCloseoutReport.md
version: v1.0.0-pre-h8-report-archive
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: archived
purpose: 记录 P11 框架收口历史证据；当前阶段状态以 harness/architecture/PLANS.md 为准。
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
  - harness/reports/redacted/P11FrameworkCloseoutReport.md
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
# P11 Framework Closeout Report（P11 框架收口历史报告）

## 目的

This report is the single redacted P11 framework closeout report.

P11 must remain staged. This report accumulates P11 step outcomes instead of creating a new report for every sub-step.

The user explicitly requested P11 to begin on 2026-06-10, with these constraints:

- P11 contains many sub-steps and must not be completed in one pass.
- P11 completion must not be described as full completion of the whole sandbox or Harness automation framework.
- Stage updates must not be recorded in `AGENTS.md`; current phase state belongs in `docs/PLANS.md`.
- P11 evidence should be consolidated to avoid uncontrolled temporary document growth.

This report currently covers P11.0 through P11.8 User Acceptance and Post-P11 Backlog. It does not execute a broader production E2E scenario.

## Gate Interpretation

P10.5 has been reviewed enough by the user to authorize a stepwise P11 start.

This does not mean:

- P11 has passed complete production lifecycle validation;
- all old HarnessVault assets have been migrated;
- the current sandbox is production-ready;
- the RAG toolchain is installed;
- live Hermes WeCom delivery has been run;
- P11 has passed.

## Current P11 Scope

| Step | Name | Purpose | Status |
|---|---|---|---|
| P11.0 | Readiness and staged plan | Confirm gate transition, scope, evidence path and non-goals. | ready-for-review |
| P11.1 | Entry and context discovery | Validate root entry, index, plans, final architecture authority and context exclusion. | ready-for-review |
| P11.2 | Project package verification | Validate `projects/java-demo` against the standard project package. | ready-for-review |
| P11.3 | Task intake and routing | Convert a natural prompt into Task Brief, readiness state and project route. | ready-for-review |
| P11.3.5 | Legacy asset timing review | Decide which old HarnessVault assets should be absorbed before, during, or after P11. | ready-for-review |
| P11.3.6 | Architecture authority convergence | Converge `docs/architecture/` to a single final authority and archive competing design inputs. | ready-for-review |
| P11.4 | Stable tool validation | Exercise the documented Java/Maven command surface when explicitly selected for that step. | ready-for-review |
| P11.5 | Evidence and result contract | Produce workflow evidence, trace summary and Common Task Result Contract output. | ready-for-review |
| P11.6 | Failure attribution and repair loop | Classify failures or partials and define repair paths. | ready-for-review |
| P11.7 | Governance closeout | List candidate Project Facts, Knowledge, Memory, Skill, Tool or Governance updates without auto-promotion. | ready-for-review |
| P11.8 | User acceptance and post-P11 backlog | Record accepted scope, remaining gaps, future implementation backlog and expired temporary-document cleanup. | ready-for-review |

## Global P11 Non-Goals

P11 does not automatically:

- create or import a real business project;
- install MarkItDown, RapidOCR, Whisper, vector stores or other RAG tools;
- choose a final vector store;
- run live WeCom delivery;
- execute Java/Maven validation commands except when a specific P11 step explicitly activates stable tool validation;
- modify Java source or tests;
- copy old HarnessVault directories wholesale;
- treat P11 as full production acceptance for the whole Harness Root;
- claim full Harness or sandbox completion.

## Evidence Consolidation Rule

P11 should use these two accumulating evidence files by default:

```text
docs/reports/redacted/P11FrameworkCloseoutReport.md
projects/java-demo/docs/project/workflow/p11-framework-closeout.md
```

New P11 documents should be created only when a later step needs a distinct long-lived asset, such as a reusable policy, template, standard, or final acceptance artifact.

## Validation Basis

P11 uses these existing assets:

```text
AGENTS.md
docs/INDEX.md
docs/PLANS.md
docs/architecture/HarnessEngineering.md
docs/reports/redacted/P10_5FinalDesignLandingReport.md
docs/project-model/P11EntryChecklist.md
docs/project-model/StandardProjectPackage.md
docs/governance/verification/HarnessValidationPlan.md
docs/governance/verification/HarnessValidationCases.md
projects/java-demo/AGENTS.md
projects/java-demo/docs/project/ProjectIndex.md
```

Project workflow evidence for P11 lives at:

```text
projects/java-demo/docs/project/workflow/p11-framework-closeout.md
```

## Completion Standard For P11.0

P11.0 is ready for review when:

- `AGENTS.md`, `docs/INDEX.md` and `docs/PLANS.md` record P11 as stepwise-started;
- `docs/project-model/P11EntryChecklist.md` records that user authorization moved P11 from gated to staged start;
- this redacted report exists and is routed by `docs/INDEX.md`;
- project workflow evidence records the Task Brief and Harness Run Card;
- no P11 E2E, Java/Maven build, live gateway call, RAG installation or old HarnessVault bulk migration has been performed.

## P11.1 Entry And Context Discovery

Scope:

- validate Harness entry discovery;
- validate context routing and provenance;
- validate default context exclusions;
- confirm `AGENTS.md` is not a phase-state journal;
- confirm no runtime logs, raw status JSON, private settings, auth files or credentials were loaded.

Documents read for P11.1:

```text
AGENTS.md
docs/INDEX.md
docs/PLANS.md
docs/architecture/HarnessEngineering.md
docs/reports/redacted/P10_5FinalDesignLandingReport.md
docs/project-model/P11EntryChecklist.md
docs/governance/context/ContextLoadingPolicy.md
docs/governance/verification/HarnessValidationCases.md
projects/java-demo/AGENTS.md
projects/java-demo/docs/project/ProjectIndex.md
projects/java-demo/docs/project/SensitiveBoundaries.md
```

Default exclusions confirmed:

```text
var/**
raw logs
raw terminal transcripts
private settings
auth files
credentials
RAG indexes
embeddings
caches
archived reports unless explicitly requested
old HarnessVault raw reports
editor/runtime artifacts
generated build outputs
```

Validation result:

| Case | Result | Notes |
|---|---|---|
| Root entry discovery | pass | `AGENTS.md` defines Harness Root and required read order. |
| Phase-state routing | pass | Current phase state is routed through `docs/PLANS.md`; `AGENTS.md` now points there instead of carrying volatile status. |
| Index routing | pass | `docs/INDEX.md` routes final architecture authority, P11 gate, validation plan, context policy and P11 report. |
| Context policy | pass | `docs/governance/context/ContextLoadingPolicy.md` defines minimum sufficient context, provenance and exclusions. |
| Project entry discovery | pass | `projects/java-demo/AGENTS.md` and `ProjectIndex.md` define the controlled project route. |
| Sensitive context exclusion | pass | `SensitiveBoundaries.md` forbids settings content, paths, credentials, raw logs and unsafe status contents in tracked docs. |
| Runtime log handling | pass | P11.1 did not inspect `var/**` or raw logs and did not treat runtime state as facts. |
| Document proliferation control | pass | P11.1 reused this consolidated report and the consolidated project workflow evidence. |

P11.1 completion standard:

- entry discovery path is clear;
- context provenance is recorded;
- default exclusions are recorded;
- P11 evidence consolidation rule is recorded;
- no code, Maven command, live gateway, RAG installation or real project import was performed.

## P11.2 Project Package Verification

Scope:

- verify `projects/java-demo` against `docs/project-model/StandardProjectPackage.md`;
- verify project facts stay under `projects/java-demo/docs/project/`;
- verify workflow evidence is consolidated rather than spread across one file per P11 step;
- clean temporary placeholder-document pollution without deleting routed active phase documents;
- avoid Maven execution, source edits, live gateway calls, RAG installation or real project import.

Package result:

| Requirement | Result | Evidence |
|---|---|---|
| Project root exists | pass | `projects/java-demo/` |
| Project entry exists | pass | `projects/java-demo/AGENTS.md` |
| Project docs root exists | pass | `projects/java-demo/docs/project/` |
| Project index exists | pass | `projects/java-demo/docs/project/ProjectIndex.md` |
| Project profile exists | pass | `projects/java-demo/docs/project/ProjectProfile.yaml` |
| Source layout exists | pass | `projects/java-demo/docs/project/SourceLayout.md` |
| Validation profile exists | pass | `projects/java-demo/docs/project/Validation.md` |
| Test strategy exists | pass | `projects/java-demo/docs/project/TestStrategy.md` |
| Sensitive boundaries exist | pass | `projects/java-demo/docs/project/SensitiveBoundaries.md` |
| Acceptance document exists | pass | `projects/java-demo/docs/project/Acceptance.md`; current content records P9 flow acceptance. P11.8 later recorded the controlled closeout boundary and remaining Post-P11 backlog. |
| Decision directory exists | pass | `projects/java-demo/docs/project/decision/` |
| ADR template exists | pass | `projects/java-demo/docs/project/decision/ADR-0001-template.md` |
| Workflow directory exists | pass | `projects/java-demo/docs/project/workflow/` |
| Consolidated P11 workflow exists | pass | `projects/java-demo/docs/project/workflow/p11-framework-closeout.md` |

Project fact boundary result:

| Check | Result | Notes |
|---|---|---|
| Root registry does not duplicate full project facts | pass | Only example registry assets are routed; project facts remain in project docs. |
| Sensitive Maven profile boundary is documented | pass | Project docs record profile ID and redaction rules, not private settings paths or credentials. |
| P11.2 did not execute Maven | pass | Package verification is structural. Tool validation is deferred to P11.4 unless separately activated. |
| P11.2 did not modify Java source or tests | pass | Source tree was inspected for layout only. |
| P11.2 did not create a new per-step report | pass | This section was appended to the consolidated P11 report. |

Temporary document cleanup:

| Cleanup Item | Result | Notes |
|---|---|---|
| Non-empty `.gitkeep` placeholders | cleaned | Placeholder files that contained copied document bodies were reset to empty placeholders. |
| Routed `docs/_temporary` phase documents | retained at P11.2 | They were still referenced during P11.2. P11.8 later migrated routes and deleted the absorbed temporary Markdown. |
| P11 per-step temporary reports | not present | P11 now uses the consolidated closeout report and workflow evidence. |

P11.2 completion standard:

- all Standard Project Package required paths exist;
- project facts remain scoped to `projects/java-demo/docs/project/`;
- sensitive Maven/settings/auth/raw-log boundaries are documented;
- no new temporary P11 document is created;
- polluted `.gitkeep` placeholder contents are removed;
- no build, live gateway, RAG installation, real project import, or source edit is performed.

## P11.3 Task Intake And Routing

Scope:

- inspect architecture design documents that govern P11.3;
- convert the current natural-language user request into a Task Brief;
- perform readiness check;
- route the task to the controlled `java-demo` project;
- update architecture design if it contradicts current governance practice;
- avoid code changes, Maven execution, live gateway calls, RAG installation, real project import, or per-step temp documents.

Architecture design review:

| Finding | Result | Action |
|---|---|---|
| `AGENTS.md` responsibility | adjusted | `docs/architecture/HarnessEngineering.md` now states phase state belongs in `docs/PLANS.md`, not `AGENTS.md`. |
| P11 evidence growth | adjusted | Architecture now requires P11-like multi-step phases to prefer consolidated redacted reports and workflow evidence. |
| Temporary document cleanup | adjusted | Architecture now states `_temporary` docs must be deleted or archived after absorption, while active routed documents must not be removed prematurely. |
| `.gitkeep` pollution | adjusted | Architecture now states `.gitkeep` must remain empty placeholders. |
| Project routing model freshness | adjusted | P5 project registration model and example registry now describe `java-demo` as the controlled P11 demo project, not only its earlier P9-preflight state. |

Task Brief extracted from current prompt:

| Field | Value |
|---|---|
| rawPrompt | "检查架构设计文档，并完成P11.3" |
| channel | codex |
| runtime | codex |
| projectId | `java-demo` |
| projectIdSource | inferred from P11 checklist, validation plan, project profile and existing P11 closeout scope |
| goal | Review architecture design documents and complete P11.3 task intake and routing validation. |
| scope | Architecture docs, project routing model, example registry, P11 consolidated report, P11 project workflow, `docs/INDEX.md`, `docs/PLANS.md`. |
| acceptanceCriteria | Architecture design is aligned with current governance rules; Task Brief exists; readiness result is recorded; routing resolves to controlled `java-demo`; no new P11 temp document is created. |
| validationPlan | Static document review, route validation, stale-path scan, sensitive-boundary scan, no Maven execution. |
| riskLevel | medium |
| approvalRequired | No additional approval required for scoped documentation updates; later source edits, Maven validation, live gateway, tool installation or real project import still require step-specific activation. |

Readiness result:

| Check | Result | Notes |
|---|---|---|
| projectId known | pass | Inferred as `java-demo` with high confidence from P11 controlled project scope. |
| goal known | pass | User explicitly requested architecture review and P11.3 completion. |
| scope known | pass | Limited to architecture/routing/evidence docs and static validation. |
| acceptance criteria known | pass | P11.3 completion criteria are derived from Task Intake model and current user constraints. |
| validation plan known | pass | Static scans and evidence updates only. |
| sensitive boundary checked | pass | Private settings/auth/raw logs excluded. |
| approval requirement checked | pass | User authorized this P11.3 step; high-risk future steps remain separate. |
| readiness state | ready | No clarification required for this documentation/routing step. |

Routing result:

| Routing Item | Result | Evidence |
|---|---|---|
| Harness Root | pass | `<HARNESS_ROOT>` |
| Root entry | pass | `AGENTS.md` |
| Phase state | pass | `docs/PLANS.md` |
| Project model | pass | `docs/project-model/ProjectRegistrationModel.md` |
| Example registry | pass | `config/examples/projects.local.example.json` |
| Project root | pass | `projects/java-demo` |
| Project entry | pass | `projects/java-demo/AGENTS.md` |
| Project index | pass | `projects/java-demo/docs/project/ProjectIndex.md` |
| Project profile | pass | `projects/java-demo/docs/project/ProjectProfile.yaml` |
| Workflow evidence | pass | `projects/java-demo/docs/project/workflow/p11-framework-closeout.md` |

Inferred fields:

| Field | Value | Source | Confidence |
|---|---|---|---|
| projectId | `java-demo` | `docs/project-model/P11EntryChecklist.md`, `docs/governance/verification/HarnessValidationPlan.md`, `projects/java-demo/docs/project/ProjectIndex.md` | high |
| validation mode | static document/routing validation | P11.3 scope and user request | high |
| no Maven execution | true | P11 staging plan and P11.4 boundary | high |
| no new P11 temp doc | true | P11 evidence consolidation rule | high |

P11.3 completion standard:

- a natural language request has been converted to Task Brief;
- readiness is recorded as ready;
- project routing resolves to `projects/java-demo`;
- architecture design documents are checked and adjusted for current governance rules;
- no source edit, Maven execution, live gateway, RAG installation, real project import, or per-step temporary document is performed.

## P11.3.5 Legacy Asset Timing Review

Reason:

The user correctly identified a risk before P11.4: P11.2 proved only that `java-demo` satisfies the Standard Project Package minimum layout. It did not prove that the current `templates/project/` set is final, nor that old HarnessVault project templates have been fully absorbed.

Legacy sources inspected:

```text
<legacy-HarnessVault-root>\harness\docs\project-template\
<legacy-HarnessVault-root>\harness\templates\
<legacy-HarnessVault-root>\harness\docs\governance\
<legacy-HarnessVault-root>\harness\docs\observability\
<legacy-HarnessVault-root>\harness\docs\verification\
<legacy-HarnessVault-root>\harness\docs\agent\
<legacy-HarnessVault-root>\harness\docs\rag\
```

P11.2 interpretation correction:

| Statement | Correct Interpretation |
|---|---|
| `java-demo` conforms to Standard Project Package | It conforms to the minimum project package required for controlled P11 validation. |
| Current `templates/project/` is sufficient for P9/P11 demo flow | It is not the final real-project onboarding template set. |
| Old project-template has value | Yes. It should be selectively rewritten into the new model, not copied wholesale. |
| P11.4 can run stable tool validation | Yes, after recording this timing decision, because P11.4 validates tool surfaces, not final project-template completeness. |

Legacy absorption timing:

| Legacy Asset Area | Value | Timing | Action |
|---|---|---|---|
| `docs/project-template/ProjectIndex.md` and `README.md` | Mature project-template indexing and instantiation rules. | P11.8 or P12 template hardening | Rewrite into `docs/project-model/ProjectTemplateGuide.md` and `templates/project/` guidance after P11 validation evidence is available. |
| `docs/project-template/architecture/ARCHITECTURE.md` | Real project architecture fact-source template. | P12 or first real-project onboarding | Rewrite as `templates/project/Architecture.md`; do not require before P11.4. |
| `docs/project-template/dictionary/SemanticDictionary.md` | Prevents semantic drift in long-running projects. | P12 or first real-project onboarding | Rewrite as `templates/project/SemanticDictionary.md`; candidate for real-project package, not demo minimum. |
| `docs/project-template/git/Repository.md` | Captures repo, branch, build, test and agent git boundaries. | Post-P11/P12; before real business project onboarding | Rewrite as `templates/project/Repository.md`; must adapt to Harness Root plus separate project git boundary. |
| `docs/project-template/test/README.md` | Test strategy/report/acceptance structure. | P11.5/P11.8 or P12 | Partly absorb into validation/evidence templates; current `TestStrategy.md` remains enough for P11.4. |
| `docs/project-template/workflow/README.md` | Workflow partition rules and anti-duplication rule. | P11.5 | Merge into workflow evidence/result-contract refinement. Current consolidated P11 evidence already follows this idea. |
| `docs/project-template/decision/ADR-0001-template.md` | Richer ADR structure than current minimal template. | P11.7/P11.8 | Rewrite into `templates/project/ADR-0001-template.md`; keep governance review before replacing. |
| `docs/project-template/prd/`, `api/`, `data/` | Useful optional sections for real projects. | P12 or project onboarding | Do not add to mandatory Standard Project Package before P11; make optional template modules. |
| Old `templates/WorkflowTemplate.md` | Has useful metadata/context/trace/promotion sections. | P11.5 | Compare and merge into `templates/workflow/WorkflowTemplate.md` if it improves evidence/result-contract flow. |
| Old `templates/ReportTemplate.md` | Report shape candidate. | P11.5/P11.8 | Rewrite into report templates only if redaction/evidence boundaries are preserved. |
| Old `templates/GovernancePolicyTemplate.md` | Governance template candidate. | P11.7 | Rewrite into `templates/governance/`, not before tool validation. |
| Old `templates/MemoryTemplate.md`, `SkillTemplate.md`, knowledge templates | Mature candidate templates for asset promotion. | P11.7 core absorbed; broader hardening P12 | Core templates are rewritten by P11.7; do not auto-promote. |
| Old governance cleanup/index policies | Strong lifecycle and cleanup ideas. | P11.7/P11.8 | Rewrite into governance backlog or policies after P11 evidence shows actual cleanup needs. |
| Old observability/verification docs | Already partly absorbed in P10.5. | P11.5/P11.6 only if gaps appear | Use as reference, not wholesale migration. |
| Old RAG docs | Useful knowledge lifecycle ideas but old RAG/index boundary differs. | After structured ingestion PoC, likely P12 | Do not migrate before MarkItDown/RapidOCR/Whisper ingestion lifecycle is validated. |

Decision:

- P11.4 is not blocked by full old project-template migration.
- P11.4 is blocked if the plan continues to imply current `templates/project/` is final.
- This P11.3.5 review removed that implication: at P11 time, project templates were minimum/demo-ready, while old project-template absorption was still a deferred rewrite task.
- P12.1 later completed reusable project-template hardening for real-project onboarding preparation. This still does not equal real business project onboarding validation.

Governance candidate:

```text
Create a post-P11 project-template hardening task:
rewrite old HarnessVault project-template into new Harness templates/project and docs/project-model guidance,
using optional modules for architecture, dictionary, repository, prd, api, data, test, workflow and decision.
```

## P11.3.6 Architecture Authority Convergence

Reason:

The user identified the root drift correctly: while the Harness design was being built in phases, `docs/architecture/` still contained multiple design inputs. That made it too easy for later work to treat an old draft, a RAG strategy note, or a temporary template assumption as final architecture.

Scope:

- converge `docs/architecture/` to one final architecture document;
- absorb valuable old HarnessVault design ideas into that final document;
- move earlier architecture inputs into archive as history;
- update entry routing and phase interpretation;
- avoid creating a new temporary report.

Architecture result:

| Check | Result | Notes |
|---|---|---|
| Single architecture authority | pass | `docs/architecture/HarnessEngineering.md` is now the only active architecture document. |
| Earlier architecture draft | archived | The earlier HarnessEngineering draft was moved to design history and is no longer routed as an active architecture source. |
| Asset ontology/RAG strategy note | archived | Its core ideas are absorbed into the Knowledge/RAG, Memory, Skill and structured ingestion sections of the final architecture. |
| Old HarnessVault value absorbed | pass | Entry, project template, governance, context, knowledge intake, Memory, Skill, reports, observability and verification concepts are captured in the final architecture. |
| P11-time project templates clarified | pass | Final architecture stated the P11-time project templates were minimum/demo-ready, not final real-project onboarding templates. P12.1 later hardened reusable templates without claiming real-project onboarding validation. |
| Phase state separated from architecture | pass | `docs/PLANS.md` and this report carry status; architecture carries durable rules. |

Legacy design ideas absorbed into the final architecture:

| Area | Absorbed Rule |
|---|---|
| Entry/navigation | `AGENTS.md`, `INDEX.md` and `PLANS.md` responsibilities stay separated. |
| Templates | `templates/**` is the only reusable template source. |
| Project template | Project Template and Project Instance remain distinct; richer real-project modules are optional until hardening. |
| Knowledge/RAG | raw -> extracted -> structured -> candidate -> reviewed -> index lifecycle. |
| Memory | Candidate/reviewed/archive states with scope, source, confidence and staleness. |
| Skill | Reusable procedure, not knowledge or one-session workflow history. |
| Governance | dry-run, report-first, human approval for promotions and cleanup auditability. |
| Reports | reports are evidence and archived reports are excluded by default. |
| Observability | trace summary and failure attribution without raw runtime transcript leakage. |
| Verification | lifecycle validation rather than only Java behavior testing. |

Decision:

- P11.4 may proceed after review because architecture authority is now stable enough to govern tool validation.
- P11.4 still must not imply real-project template finalization, full old HarnessVault migration, RAG installation or full Harness production readiness.
- Future architecture changes must update `docs/architecture/HarnessEngineering.md`; reports and workflow evidence may propose changes but cannot become architecture by themselves.

## P11.4 Stable Tool Validation

Scope:

- validate that the controlled `java-demo` project can be tested through the documented stable Java/Maven command surface;
- use the private Maven profile requested by the user only through the profile ID;
- avoid manual Maven classpath assembly or historical smoke scripts;
- record only redacted evidence paths and safe status fields;
- judge whether old HarnessVault content should be absorbed in this stage.

Task Brief for this step:

| Field | Value |
|---|---|
| rawPrompt | "继续完成P11.4，并且每个阶段都要判断当前阶段是否要迁入旧版harness的文档内容。" |
| projectId | `java-demo` |
| goal | Complete P11.4 stable tool validation and record the legacy-asset migration judgment for this stage. |
| scope | Stable Java/Maven command surface, `projects/java-demo`, P11 consolidated report/workflow, tool docs and relevant old HarnessVault tool/verification governance references. |
| acceptanceCriteria | Stable tool invocation is used; result is recorded with redacted evidence; failure/repair is attributed if needed; old HarnessVault content decision is recorded; no raw logs or private settings paths enter tracked docs. |
| validationPlan | Run `scripts/stable/invoke-maven-project.ps1` with `test`; if tool/environment failure occurs, repair through stable documented parameters and rerun. |
| riskLevel | medium |
| approvalRequired | The user explicitly activated P11.4; live gateway, RAG installation, real project import and destructive cleanup remain out of scope. |

Legacy HarnessVault stage judgment:

| Legacy Area | P11.4 Decision | Reason |
|---|---|---|
| old `RuntimeBoundaryPolicy` | Do not migrate as a separate doc in P11.4. Use its idea in evidence. | Final architecture and security docs already define runtime/Harness separation. |
| old `RegressionPolicy` | Deferred at P11.4; completed in P11.6 as current `RegressionPolicy.md`. | P11.4 encountered a tool/environment failure and repaired by rerunning stable validation. Full regression policy belongs to failure/repair loop. |
| old `TraceSchema` | Do not migrate now. Already absorbed into current `docs/observability/traces/TraceSchema.md`. | P11.4 only needs a compact trace summary. |
| old `scripts/README.md` and `check_harness_docs.py` | Do not migrate now. | P11.4 validates runtime command surfaces, not document self-check scripts. P11.7 absorbed route/index governance; automated dry-run tooling remains P12. |
| old project-template/test docs | Do not migrate now. | Current project `Validation.md` and `TestStrategy.md` are sufficient for stable tool validation; richer templates remain Post-P11/P12 work. |
| current tool docs | Rewrite now. | P11.4 exposed a real stable-surface rule: private profile validation may need a Harness-managed writable local repo under `var/m2`. |

Tool invocation result:

| Run | Result | Attribution | Evidence |
|---|---|---|---|
| Initial stable invocation | failed | `tool/execution`: configured local repository was not writable by the sandbox runtime. | `var/logs/last-p11-stable-tool-codex.json`, `var/logs/p11-stable-tool-codex-20260610-022030.log` |
| Repaired stable invocation | passed | Reused stable script and private profile ID; added Harness-managed `var/m2` local repository override. | `var/logs/last-p11-stable-tool-repair-codex.json`, `var/logs/p11-stable-tool-repair-codex-20260610-022132.log` |

Safe status summary:

| Field | Value |
|---|---|
| commandSurface | `scripts/stable/invoke-maven-project.ps1` |
| projectRoot | `projects/java-demo` |
| profile | `real-local-maven` |
| goals | `test` |
| finalState | `passed` |
| finalExitCode | `0` |
| statusJson | `var/logs/last-p11-stable-tool-repair-codex.json` |
| redactedLog | `var/logs/p11-stable-tool-repair-codex-20260610-022132.log` |

Tool documentation updated:

```text
docs/tools/command-surfaces/JavaMavenCommandSurface.md
docs/tools/command-surfaces/StableToolSurfaceModel.md
docs/tools/script-index/ScriptIndex.md
```

P11.4 completion standard:

- stable Java/Maven command surface was used;
- historical smoke scripts were not used;
- private profile ID was used without exposing private settings or credentials;
- first failure was attributed and repaired;
- repaired validation passed;
- status JSON and log path were recorded as runtime evidence only;
- old HarnessVault migration judgment was recorded for this stage;
- no Java source, test source, live gateway, RAG tool, real business project or old directory bulk copy was changed.

## P11.5 Evidence And Result Contract

Scope:

- convert P11.4 stable tool validation into reusable workflow evidence;
- produce a compact trace summary without raw trace or raw terminal transcript;
- produce Common Task Result Contract output;
- judge whether old HarnessVault workflow/report template content should be rewritten into current assets.

Task Brief for this step:

| Field | Value |
|---|---|
| rawPrompt | "继续完成P11.5，并且每个阶段都要判断当前阶段是否要迁入旧版harness的文档内容。" |
| projectId | `java-demo` |
| goal | Complete P11.5 evidence and result contract using the P11.4 validation result. |
| scope | Consolidated P11 report, project workflow evidence, Common Task Result Contract, workflow/report templates, trace summary and legacy template judgment. |
| acceptanceCriteria | P11.5 records trace summary, validation summary, result contract output, legacy migration judgment and sensitive handling without creating per-step temp docs. |
| validationPlan | Static evidence review and template/contract update; no Maven rerun. |
| riskLevel | medium |
| approvalRequired | User explicitly activated P11.5. Promotion of candidates remains review-only. |

Legacy HarnessVault stage judgment:

| Legacy Area | P11.5 Decision | Reason |
|---|---|---|
| old `templates/WorkflowTemplate.md` | Rewrite selected ideas into current workflow template. | Metadata, context loaded, execution trace, promotion candidates and final output improve reusable evidence. |
| old `templates/ReportTemplate.md` | Rewrite selected structure into current validation report template. | Summary, scope, findings, recommended actions, approval and follow-up sections improve report-first governance. |
| old `docs/project-template/workflow/README.md` | Absorb rule, not file. | Current model keeps workflow templates in `templates/workflow/` and project instances under `docs/project/workflow/`. |
| old validation cases | Do not migrate now. | Current `HarnessValidationCases.md` already covers P11 cases; deeper case expansion can wait until Post-P11/P12. |
| old failure attribution docs | Deferred at P11.5; completed in P11.6. | P11.5 only references the repaired failure; full repair-loop formalization belongs to the next step. |

Assets updated in P11.5:

```text
interaction/result-contracts/CommonTaskResultContract.md
templates/workflow/WorkflowTemplate.md
templates/report/ValidationReportTemplate.md
```

Trace summary:

| Field | Value |
|---|---|
| traceId | `p11-java-demo-stable-tool-validation` |
| taskId | `p11-framework-closeout` |
| runtime | `codex` |
| channel | `codex` |
| projectId | `java-demo` |
| status | `passed` |
| workflow | `projects/java-demo/docs/project/workflow/p11-framework-closeout.md` |
| report | `docs/reports/redacted/P11FrameworkCloseoutReport.md` |
| entryDocs | `AGENTS.md`, `docs/INDEX.md`, `docs/PLANS.md`, `docs/architecture/HarnessEngineering.md` |
| projectDocs | `projects/java-demo/AGENTS.md`, `projects/java-demo/docs/project/ProjectIndex.md`, `Validation.md`, `SensitiveBoundaries.md` |
| toolsUsed | `scripts/stable/invoke-maven-project.ps1` |
| validationResult | Initial tool/execution failure repaired; final Maven `test` validation passed. |
| sensitiveHandling | Private settings paths, private repository paths, credentials, raw logs and status JSON contents excluded. |

Operation event summary:

| Event | Type | Target | Result | Evidence |
|---|---|---|---|---|
| p11.5-01 | read | Root and project P11 evidence | passed | This report and project workflow evidence |
| p11.5-02 | rewrite | Result contract and evidence templates | passed | Contract/template paths listed above |
| p11.5-03 | report | Trace summary and result contract output | passed | This P11.5 section |
| p11.5-04 | validation | Stale state and sensitive-boundary scan | passed | Tool output summary in final assistant response |

Common Task Result Contract output:

```yaml
taskId: p11-framework-closeout
runtime: codex
channel: codex
projectId: java-demo
status: passed
workflow: projects/java-demo/docs/project/workflow/p11-framework-closeout.md
traceSummary: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.5-Evidence-And-Result-Contract
statusJson: var/logs/last-p11-stable-tool-repair-codex.json
log: var/logs/p11-stable-tool-repair-codex-20260610-022132.log
validationReport: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.4-Stable-Tool-Validation
failureAttribution: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.4-Stable-Tool-Validation
summary: P11.5 produced trace summary and result contract evidence for the repaired P11.4 stable Java/Maven validation.
nextAction: review-needed
governanceCandidates:
  - type: Tool
    action: review
  - type: Verification
    action: defer
  - type: Template
    action: review
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```

P11.5 completion standard:

- consolidated workflow evidence contains P11.5 result contract content;
- trace summary is recorded without raw logs or raw trace;
- result contract output points to evidence paths and next action;
- old HarnessVault workflow/report template value is selectively rewritten, not copied wholesale;
- no Maven rerun, live gateway call, RAG installation, real project import or old HarnessVault bulk copy occurred.

## P11.6 Failure Attribution And Repair Loop

Scope:

- turn the P11.4 repaired stable-tool failure into a reusable failure attribution and repair-loop pattern;
- selectively rewrite useful old HarnessVault failure/regression ideas into current Harness assets;
- update validation standards so repaired work cannot close without attribution and regression evidence;
- avoid Maven rerun, live gateway call, RAG installation, real project import, old directory bulk copy or new temporary report creation.

Task Brief for this step:

| Field | Value |
|---|---|
| rawPrompt | "继续完成P11.6，并且每个阶段都要判断当前阶段是否要迁入旧版harness的文档内容。" |
| projectId | `java-demo` |
| goal | Complete P11.6 failure attribution and repair loop formalization using the repaired P11.4 validation as the concrete case. |
| scope | Failure attribution policy, regression policy, failure attribution template, validation plan/cases, consolidated P11 report and project workflow evidence. |
| acceptanceCriteria | P11.6 records old Harness migration judgment, failure attribution record, regression closure, updated policy/template assets and redacted validation evidence. |
| validationPlan | Static document update and scans; reuse the existing P11.4 repaired validation evidence; no Maven rerun. |
| riskLevel | medium |
| approvalRequired | User explicitly activated P11.6. Tool installation, live gateway, real project import and high-risk cleanup remain out of scope. |

Legacy HarnessVault stage judgment:

| Legacy Area | P11.6 Decision | Reason |
|---|---|---|
| old `FailureAttributionPolicy` | Rewrite selected structure into current `docs/observability/failure-attribution/FailureAttributionPolicy.md`. | The old multidimensional attribution model and evidence requirements directly match this stage. |
| old `RegressionPolicy` | Rewrite selected policy into new `docs/governance/verification/RegressionPolicy.md`. | P11.6 is the first stage explicitly responsible for repair-loop closure and rerun rules. |
| old `HarnessValidationCases` | Partially absorb repair-loop expectations into current validation cases. | Current cases already exist; only the repair/regression expectations need expansion now. |
| old `TraceSchema` | Do not migrate now. | Current trace schema already covers compact trace summaries and failure summary fields. |
| old runtime boundary and governance docs | Do not migrate in P11.6. | Current security/governance docs already carry these boundaries; deeper governance promotion belongs to P11.7. |
| old raw reports, logs and runtime outputs | Exclude. | They are not stable facts and may contain sensitive or stale runtime state. |

Assets updated in P11.6:

```text
docs/observability/failure-attribution/FailureAttributionPolicy.md
docs/governance/verification/RegressionPolicy.md
templates/report/FailureAttributionTemplate.md
docs/governance/verification/HarnessValidationPlan.md
docs/governance/verification/HarnessValidationCases.md
```

Failure attribution record:

| Field | Value |
|---|---|
| failureId | `p11.4-stable-tool-initial-failure` |
| taskId | `p11-framework-closeout` |
| projectId | `java-demo` |
| failedCriterion | Stable Java/Maven validation should pass through the documented command surface. |
| failureStage | stable tool validation |
| affectedAsset | `scripts/stable/invoke-maven-project.ps1` |
| errorSummary | Initial invocation failed because the configured local repository was not writable by the sandbox runtime. |
| primaryDimension | `execution` |
| secondaryDimensions | `tool` |
| reproducible | `unknown` |
| retryable | `conditional` |
| repairAction | Rerun the same stable tool surface with a Harness-managed writable local repository override. |
| regressionRequired | Rerun stable Java/Maven validation. |
| repairResult | `passed` |
| remainingRisk | Current result validates the controlled demo repair pattern only; it does not prove full Java project landing or full Harness production readiness. |
| closureState | `repaired` |

Regression record:

| Field | Value |
|---|---|
| regressionId | `p11.4-stable-tool-repair-regression` |
| trigger | repaired stable-tool validation failure |
| scope | controlled `java-demo` Maven `test` validation through stable command surface |
| type | `tool-regression`, `workflow-regression`, `security-regression` |
| runtime | `codex` |
| commandSurface | `scripts/stable/invoke-maven-project.ps1` |
| result | `passed` |
| evidence | `var/logs/last-p11-stable-tool-repair-codex.json`, `var/logs/p11-stable-tool-repair-codex-20260610-022132.log` |
| remainingRisk | demo-scope only |
| nextAction | `review-needed` |

Repair-loop closure:

| Check | Result | Notes |
|---|---|---|
| Original failed criterion preserved | pass | Failure record keeps the stable-tool validation criterion. |
| Attribution dimension recorded | pass | Primary `execution`, secondary `tool`. |
| Repair action scoped | pass | Repair used the existing stable command surface with a writable Harness-managed local repo override. |
| Regression evidence exists | pass | Repaired P11.4 stable validation passed. |
| Residual risk recorded | pass | Demo-scope only; no full Harness production claim. |
| Result contract linked | pass | P11.5 and P11.6 sections point to consolidated report/workflow evidence. |
| Governance candidates not auto-promoted | pass | Candidates remain listed for later review. |

Operation event summary:

| Event | Type | Target | Result | Evidence |
|---|---|---|---|---|
| p11.6-01 | read | Current failure, validation and result-contract assets | passed | This report and routed policy/template docs |
| p11.6-02 | read | Old Harness failure/regression references | passed | Selectively rewritten ideas only; no bulk copy |
| p11.6-03 | write | Failure attribution and regression assets | passed | Asset paths listed above |
| p11.6-04 | report | Failure attribution and repair-loop closure | passed | This P11.6 section |
| p11.6-05 | validation | Stale state and sensitive-boundary scan | passed | Tool output summary in final assistant response |

Common Task Result Contract output:

```yaml
taskId: p11-framework-closeout
runtime: codex
channel: codex
projectId: java-demo
status: passed
workflow: projects/java-demo/docs/project/workflow/p11-framework-closeout.md
traceSummary: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.6-Failure-Attribution-And-Repair-Loop
statusJson: var/logs/last-p11-stable-tool-repair-codex.json
log: var/logs/p11-stable-tool-repair-codex-20260610-022132.log
validationReport: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.6-Failure-Attribution-And-Repair-Loop
failureAttribution: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.6-Failure-Attribution-And-Repair-Loop
summary: P11.6 formalized the failure attribution and repair-loop closure for the repaired P11.4 stable Java/Maven validation.
nextAction: review-needed
governanceCandidates:
  - type: Verification
    action: review
  - type: Template
    action: review
  - type: Tool
    action: review
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```

P11.6 completion standard:

- old Harness failure/regression value is selectively rewritten into current assets;
- repaired P11.4 failure has an explicit attribution record;
- regression closure is recorded without rerunning Maven in this step;
- validation plan/cases now require attribution and regression evidence for repaired work;
- no raw logs, private settings paths, private repository paths, credentials or status JSON contents are copied into tracked docs;
- no new temporary P11 report is created.

## P11.7 Governance Closeout

Scope:

- classify P11.0-P11.6 durable update candidates without auto-promotion;
- selectively rewrite old HarnessVault governance, Knowledge, Memory, Skill and template ideas needed for closeout;
- judge whether `docs/architecture/HarnessEngineering.md` needs an update;
- keep P11 staged and avoid full E2E, RAG tool installation, live gateway use, real project import or old HarnessVault bulk copy.

Task Brief for this step:

| Field | Value |
|---|---|
| rawPrompt | "继续完成P11.7，并且每个阶段都要判断当前阶段是否要迁入旧版harness的文档内容，以及当前的新版架构设计方案 HarnessEngineering.md 是否要更新。" |
| projectId | `java-demo` |
| goal | Complete P11.7 governance closeout and classify durable candidates without auto-promotion. |
| scope | Governance index, closeout policy/template, Knowledge/Memory/Skill promotion rules/templates, report archive rule, ADR governance fields, final architecture closeout rules, consolidated P11 report/workflow. |
| acceptanceCriteria | P11.7 records legacy migration judgment, architecture update judgment, candidate dispositions, updated governance/template assets and redacted validation evidence. |
| validationPlan | Static document updates and scans; no Maven rerun. |
| riskLevel | medium |
| approvalRequired | User explicitly activated P11.7 and requested architecture update judgment. Promotions remain review-only. |

Architecture update judgment:

| Question | Judgment | Action |
|---|---|---|
| Does final architecture already say candidates do not auto-promote? | yes | Existing principle preserved. |
| Does final architecture define closeout disposition states and candidate record fields? | not enough | Updated `docs/architecture/HarnessEngineering.md` with P11.7 closeout disposition and record fields. |
| Does this change create competing architecture? | no | The single architecture authority remains the same file. |
| Does this update claim full Harness production readiness? | no | It only defines governance closeout rules. |

Legacy HarnessVault stage judgment:

| Legacy Area | P11.7 Decision | Reason |
|---|---|---|
| old `ArtifactLifecycle` | Partially absorb now. | Candidate/review/archive states and forbidden direct transitions are core to governance closeout. |
| old `KnowledgePromotionPolicy` | Absorb now into current closeout and Knowledge promotion policies. | P11.7 must prevent workflow/report/RAG candidates from becoming reviewed Knowledge without review. |
| old `MemoryPolicy` and `MemoryTemplate` | Absorb now into current Skill/Memory governance and memory template. | Memory candidate/review/source/staleness rules are needed for candidate classification. |
| old `SkillPolicy` and `SkillTemplate` | Absorb now into current Skill/Memory governance and skill template. | Skill candidate trigger/input/procedure/verification rules are needed for candidate classification. |
| old `GovernancePolicyTemplate` | Absorb now into `templates/governance/GovernancePolicyTemplate.md`. | Future governance policies need consistent owner, scope and review fields. |
| old `IndexMaintenancePolicy` | Partially absorb now. | Active `docs/governance/GovernanceIndex.md` and route update rules are needed now; full automated self-check remains later tooling. |
| old `CleanupPolicy` | Partially absorb now. | Report-before-mutation and no silent deletion inform closeout; no cleanup execution occurs in P11.7. |
| old ADR template | Partially absorb now into current ADR template. | Status, impact, risks and follow-up improve governance decision records; full project-template hardening remains Post-P11/P12. |
| old `AgentContextManifest.yaml` | Do not migrate now. | Architecture already treats machine-readable manifest as a future helper; Markdown entry remains authoritative. |
| old RAG docs | Defer. | RAG docs should wait until structured ingestion PoC and corpus lifecycle are validated. |
| old raw reports, logs, `.obsidian`, indexes and caches | Exclude. | They are not stable facts and may contain stale or sensitive runtime/editor state. |

Assets updated in P11.7:

```text
docs/architecture/HarnessEngineering.md
docs/project-model/P11EntryChecklist.md
docs/governance/GovernanceIndex.md
docs/governance/promotion/GovernanceCloseoutPolicy.md
docs/governance/promotion/KnowledgeIntakeAndPromotionPolicy.md
docs/governance/promotion/SkillMemoryGovernance.md
docs/governance/archive/ReportArchivePolicy.md
docs/governance/verification/HarnessValidationPlan.md
docs/governance/verification/HarnessValidationCases.md
templates/governance/GovernanceCloseoutTemplate.md
templates/governance/GovernancePolicyTemplate.md
templates/memory/MemoryTemplate.md
templates/skill/SkillTemplate.md
templates/knowledge/CandidateKnowledgeTemplate.md
templates/knowledge/ReviewedKnowledgeTemplate.md
templates/project/ADR-0001-template.md
templates/report/E2EValidationReportTemplate.md
```

Governance closeout candidate disposition:

| candidateId | Type | Proposal | Disposition | Target | Next Action |
|---|---|---|---|---|---|
| `p11-architecture-closeout-record` | Architecture | Add closeout disposition states and record fields. | absorbed | `docs/architecture/HarnessEngineering.md` | review |
| `p11-governance-index` | Governance | Add active governance index. | absorbed | `docs/governance/GovernanceIndex.md` | review |
| `p11-governance-closeout-policy` | Governance | Add closeout policy and template. | absorbed | `docs/governance/promotion/GovernanceCloseoutPolicy.md`, `templates/governance/GovernanceCloseoutTemplate.md` | review |
| `p11-knowledge-template-hardening` | Template | Add source trace, rights/sensitivity and promotion decision fields. | absorbed | `templates/knowledge/` | review |
| `p11-memory-template` | Template | Add memory candidate/review/staleness template. | absorbed | `templates/memory/MemoryTemplate.md` | review |
| `p11-skill-template` | Template | Add skill candidate/review template. | absorbed | `templates/skill/SkillTemplate.md` | review |
| `p11-adr-governance-fields` | Template | Add status, impact, risks and follow-up fields. | absorbed | `templates/project/ADR-0001-template.md` | review |
| `p11-staged-closeout-operating-rule` | Governance | Keep P11 staged and evidence-led. | absorbed | `docs/PLANS.md`, this report, project workflow | review |
| `p11-private-maven-local-repo-lesson` | Tool | Keep local repo override as tool guidance, not Memory. | no-action | already handled in P11.4 tool docs | none |
| `p11-project-template-hardening` | Template | Rewrite old project-template optional modules. | defer | Post-P11/P12 | review later |
| `p11-rag-docs-migration` | RAG | Rewrite old RAG docs after structured ingestion PoC. | defer | P12 or ingestion PoC task | review later |
| `p11-live-gateway-validation` | Verification | Validate live Hermes/WeCom delivery. | defer | separate approved task | review later |
| `p11-real-project-onboarding` | ProjectFact | Import or onboard real business project. | defer | separate approved task | review later |

Promotion boundary:

- no Project Facts were promoted;
- no reviewed Knowledge was created;
- no Memory was promoted;
- no Skill was activated;
- no RAG tools were installed;
- no vector store was selected;
- no runtime logs or status JSON contents were copied into tracked docs;
- no old HarnessVault directory was copied wholesale.

Operation event summary:

| Event | Type | Target | Result | Evidence |
|---|---|---|---|---|
| p11.7-01 | read | Current architecture and governance assets | passed | routed Harness docs |
| p11.7-02 | read | Old governance, Memory, Skill and template references | passed | selected ideas only |
| p11.7-03 | write | Governance closeout assets and templates | passed | asset paths listed above |
| p11.7-04 | write | Final architecture closeout rule | passed | `docs/architecture/HarnessEngineering.md` |
| p11.7-05 | report | Candidate disposition and non-promotion statement | passed | this section |
| p11.7-06 | validation | Stale state and sensitive-boundary scan | passed | Tool output summary in final assistant response |

Common Task Result Contract output:

```yaml
taskId: p11-framework-closeout
runtime: codex
channel: codex
projectId: java-demo
status: passed
workflow: projects/java-demo/docs/project/workflow/p11-framework-closeout.md
traceSummary: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.7-Governance-Closeout
statusJson: null
log: null
validationReport: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.7-Governance-Closeout
failureAttribution: null
summary: P11.7 classified governance candidates, selectively rewrote governance/template assets and updated the architecture authority with closeout disposition rules.
nextAction: review-needed
governanceCandidates:
  - type: Governance
    action: review
  - type: Template
    action: review
  - type: Architecture
    action: review
  - type: RAG
    action: defer
  - type: ProjectTemplate
    action: defer
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```

P11.7 completion standard:

- candidate dispositions are recorded;
- old governance/Memory/Skill/Knowledge/template value is selectively rewritten or deferred;
- final architecture update judgment is recorded and implemented where needed;
- closeout assets are routed through current indexes;
- no candidate is auto-promoted to reviewed Knowledge, Memory, Skill or Project Fact;
- no Maven rerun, live gateway call, RAG installation, real project import or old HarnessVault bulk copy occurred.

## P11.8 User Acceptance And Post-P11 Backlog

Scope:

- record the P11 acceptance boundary without claiming production completeness;
- judge whether old HarnessVault content should be migrated in this stage;
- judge whether `docs/architecture/HarnessEngineering.md` needs a durable update;
- remove default routes to absorbed temporary phase documents;
- delete expired temporary Markdown after references are migrated;
- keep remaining work as explicit Post-P11/P12 backlog.

Task Brief for this step:

| Field | Value |
|---|---|
| rawPrompt | "继续完成P11.8，判断当前阶段是否要迁入旧版harness的文档内容以及当前的新版架构设计方案 HarnessEngineering.md 是否要更新，同时删除已过期的内容和文档" |
| projectId | `java-demo` |
| goal | Complete P11.8 acceptance boundary, backlog and expired temporary-document cleanup. |
| scope | Final architecture authority, root index/plans, project model gates, consolidated P11 report, project workflow evidence and temporary Markdown cleanup. |
| acceptanceCriteria | P11.8 records legacy migration judgment, architecture update judgment, cleanup decisions, Post-P11 backlog, route migration and validation evidence. |
| validationPlan | Static route scan, stale temporary path scan, sensitive-boundary scan, temporary Markdown inventory, architecture directory check and no-git check. |
| riskLevel | medium |
| approvalRequired | User explicitly activated P11.8 and requested expired content deletion. No approval is granted for RAG installation, real project import, live gateway execution or old HarnessVault bulk copy. |

Architecture update judgment:

| Question | Judgment | Action |
|---|---|---|
| Does final architecture already state temporary materials should be deleted or archived after absorption? | partly | Existing rule preserved. |
| Does it clearly separate P11 controlled closeout acceptance from whole-Harness production acceptance? | not enough | Updated final architecture with P11 acceptance boundary and Post-P11 backlog rule. |
| Does it define that expired temporary docs must be removed from default routing after absorption? | not enough | Updated final architecture with route cleanup rule. |
| Does this create another architecture source? | no | The single architecture authority remains `docs/architecture/HarnessEngineering.md`. |

Legacy HarnessVault stage judgment:

| Legacy Area | P11.8 Decision | Reason |
|---|---|---|
| old project-template `README` and `ProjectIndex` | Defer to Post-P11/P12 template hardening. | Valuable for real-project onboarding, but P11.8 is acceptance/backlog/cleanup. Migrating now would open a new design subproject. |
| old project-template architecture, dictionary, repository, prd, api, data and test sections | Defer to Post-P11/P12 or first real-project onboarding. | These are optional real-project modules, not required for P11 controlled closeout. |
| old RAG workflow/policy/index docs | Defer until structured ingestion PoC. | RAG migration should follow MarkItDown + RapidOCR + Whisper corpus lifecycle validation, not precede it. |
| old cleanup policy | Partially absorb now as operating rule. | P11.8 uses report-before-mutation, no silent deletion and keep indexes consistent. |
| old governance, Knowledge, Memory and Skill core policies | Already absorbed in P11.7. | No duplicate migration needed. |
| old raw reports, logs, indexes, caches, real user knowledge, credentials and editor/runtime artifacts | Exclude. | They are not stable facts and may be sensitive or stale. |

Expired content cleanup decision:

| Item | Decision | Evidence |
|---|---|---|
| Active routing to absorbed temporary phase drafts | removed | `docs/INDEX.md` and `docs/PLANS.md` now route to long-term assets. |
| Absorbed temporary Markdown | deleted | Deleted after route migration and report entry. |
| Generated Maven text reports under project `target/` | deleted | Removed regenerable surefire and compiler-status text outputs that can contain local absolute paths. Binary class outputs are not routed as evidence. |
| Empty temporary directory skeleton | retained | `.gitkeep` placeholders remain for future short-lived work. |
| Long-term architecture/history assets | retained | `docs/architecture/HarnessEngineering.md` remains the only architecture authority; archived design-history assets remain out of default route. |
| P11 evidence | retained | Consolidated report and project workflow evidence remain the audit trail. |

Deleted expired temporary Markdown:

```text
docs/_temporary/drafts/generic-agent-sandbox-design.md
docs/_temporary/drafts/harness-project-automation-framework-design-draft.md
docs/_temporary/migration/harness-asset-migration-plan.md
docs/_temporary/migration/harness-root-directory-runtime-boundary-plan.md
docs/_temporary/phases/p0/harness-implementation-roadmap.md
docs/_temporary/phases/p5/harness-project-registration-instance-model.md
docs/_temporary/phases/p8/harness-p8-implementation-plan.md
docs/_temporary/reviews/harness-root-reorganization-review-plan.md
docs/_temporary/status/harness-current-status-alignment-review.md
```

Post-P11 backlog:

| Backlog | Disposition |
|---|---|
| Project-template hardening from old HarnessVault | defer to P12 or dedicated template task |
| RAG structured ingestion PoC | defer to RAG PoC task; no tool installation in P11.8 |
| Vector store selection | defer until structured corpus lifecycle and evaluation pass |
| Automated governance self-check tooling | defer to P12 tooling |
| Local project registry landing | defer until user asks to onboard real projects |
| Live Hermes/WeCom delivery | defer to separate approved live-gateway task |
| Docker or virtual machine isolation | defer to isolation implementation task |
| Real business project onboarding | defer until templates, registry and security gates are ready |

Promotion boundary:

- no Project Facts were promoted;
- no reviewed Knowledge, Memory or Skill was created;
- no RAG tools were installed;
- no vector store was selected;
- no live gateway call was made;
- no real business project was imported;
- no old HarnessVault directory was copied wholesale;
- regenerable Maven text reports under project `target/` were removed from the workspace because they are runtime/build outputs, not stable evidence;
- no private settings, auth files, credentials, raw logs or status JSON contents were copied into tracked docs.

Operation event summary:

| Event | Type | Target | Result | Evidence |
|---|---|---|---|---|
| p11.8-01 | read | Current entry, plans, architecture, report and workflow evidence | passed | routed Harness docs |
| p11.8-02 | read | Old project-template, RAG and cleanup references | passed | selected ideas only; no bulk copy |
| p11.8-03 | write | Architecture acceptance/cleanup rule | passed | `docs/architecture/HarnessEngineering.md` |
| p11.8-04 | write | Root index/plans and project model gates | passed | `docs/INDEX.md`, `docs/PLANS.md`, `docs/project-model/` |
| p11.8-05 | cleanup | Absorbed temporary Markdown | passed | cleanup list above |
| p11.8-06 | validation | Route, temporary Markdown and sensitive-boundary scans | passed | Tool output summary in final assistant response |

Common Task Result Contract output:

```yaml
taskId: p11-framework-closeout
runtime: codex
channel: codex
projectId: java-demo
status: passed
workflow: projects/java-demo/docs/project/workflow/p11-framework-closeout.md
traceSummary: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.8-User-Acceptance-And-Post-P11-Backlog
statusJson: null
log: null
validationReport: docs/reports/redacted/P11FrameworkCloseoutReport.md#P11.8-User-Acceptance-And-Post-P11-Backlog
failureAttribution: null
summary: P11.8 recorded the controlled acceptance boundary, Post-P11 backlog, legacy migration timing, architecture update judgment and expired temporary Markdown cleanup.
nextAction: user-review-needed
governanceCandidates:
  - type: ProjectTemplate
    action: defer
  - type: RAG
    action: defer
  - type: Tooling
    action: defer
  - type: Architecture
    action: review
sensitiveHandling:
  rawLogsIncluded: false
  privateSettingsIncluded: false
  credentialsIncluded: false
  authFilesIncluded: false
```

P11.8 completion standard:

- P11 acceptance boundary is explicit;
- Post-P11/P12 backlog is explicit;
- old HarnessVault migration judgment is recorded;
- final architecture update judgment is recorded and implemented where needed;
- default routes no longer point to absorbed temporary phase Markdown;
- expired temporary Markdown is deleted after route migration;
- no RAG installation, live gateway call, real project import or old HarnessVault bulk copy occurred.

## 敏感边界

This report intentionally uses only Harness-relative paths except for the known Harness Root identity. It does not include private Maven settings paths, repository paths, credentials, auth files, raw logs or status JSON contents.

## Next Step

P11.8 is ready for user review. If accepted, the next work should move to Post-P11/P12 backlog items rather than treating P11 as full production completion.
