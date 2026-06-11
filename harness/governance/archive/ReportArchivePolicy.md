# Report Archive Policy

Status: draft
Version: v0.2.0-p11.7
Date: 2026-06-10

## Purpose

Reports are governance evidence. They are not long-term facts until absorbed into an accepted asset.

## Report Areas

| Area | Purpose |
|---|---|
| `harness/reports/redacted/` | Current redacted reports that may be read by default when relevant. |
| `harness/reports/archive/` | Historical reports, not default context. |
| `projects/<project-id>/docs/project/workflow/` | Project task evidence. |

## Default Rule

Archived reports are not loaded by default. They may be read only when the user asks for history, audit, or legacy context.

## Promotion Rule

A report conclusion becomes a stable fact only after being written into one of:

- accepted architecture document;
- governance policy;
- project fact;
- reviewed Knowledge;
- reviewed Memory;
- approved Skill;
- template or command-surface doc.

## Forbidden

Do not archive into tracked docs:

- raw logs;
- terminal transcripts;
- private settings paths;
- credentials or auth files;
- unredacted status JSON;
- old HarnessVault raw reports without review.

## P10.5 Rule

`harness/reports/redacted/P10_5FinalDesignLandingReport.md` is the active redacted report for final design landing. It records decisions but does not replace the final architecture document.

## P11 Closeout Rule

`harness/reports/redacted/P11FrameworkCloseoutReport.md` is accumulated redacted evidence for P11 staged closeout.

It may list governance candidates, failure attribution, repair closure and acceptance evidence, but it does not promote candidates by itself. Any durable result must be absorbed into the correct target asset and routed by `harness/INDEX.md` or the relevant project index.
