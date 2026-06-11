# Candidate Knowledge Template

Status: template
Version: v0.2.0-p11.7
Date: 2026-06-10

## Source

```yaml
sourceRef: <source>
sourceType: raw | extracted | structured | workflow-evidence | project-fact | report | other
scope: global | domain | project-reviewed
projectId: null
domain: null
confidence: low | medium | high
reviewStatus: candidate
submittedBy: human | agent | unknown
usageRights: unknown | permitted | restricted
sensitiveRisk: none | low | medium | high
```

## Candidate Statement

Write the candidate knowledge here.

## Evidence

List source files, sections, hashes, or workflow evidence references.

## Applicability

Describe where this candidate may apply and where it must not apply.

## Review Notes

Record what must be checked before promotion to reviewed Knowledge.

## Promotion Decision

```yaml
decision: approve | reject | defer
targetAsset: <rag/knowledge/reviewed/path-or-null>
reviewer: <reviewer-or-null>
decisionDate: <date-or-null>
reason: <reason>
```
