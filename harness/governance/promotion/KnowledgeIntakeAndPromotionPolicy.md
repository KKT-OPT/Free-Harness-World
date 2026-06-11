# Knowledge Intake and Promotion Policy

Status: draft
Version: v0.2.0-p11.7
Date: 2026-06-10

## Purpose

This policy defines how raw material becomes reviewed Knowledge and how RAG indexes are rebuilt from reviewed sources.

## Lifecycle

```text
raw source
-> extracted content
-> structured content
-> candidate knowledge
-> reviewed knowledge
-> rebuildable RAG index
-> archived or deprecated
```

## Asset Locations

| State | Location |
|---|---|
| raw | `rag/knowledge/raw/` |
| extracted | `rag/knowledge/extracted/` |
| candidate | `rag/knowledge/candidate/` |
| reviewed | `rag/knowledge/reviewed/` |
| archive | `rag/knowledge/archive/` |
| RAG manifest/pipeline/eval | `rag/` |
| rebuildable index/cache | `var/rag/` |

## Structured Ingestion

`MarkItDown + RapidOCR + Whisper` is the first offline structured ingestion candidate.

Allowed output states:

- extracted Markdown;
- metadata manifest;
- extraction report;
- chunks JSONL;
- candidate knowledge draft.

Forbidden automatic outputs:

- reviewed Knowledge;
- active Memory;
- active Skill;
- project facts;
- final vector store selection.

## Promotion Rules

Promotion to reviewed Knowledge requires:

- source provenance;
- scope: `global`, `domain`, or `project-reviewed`;
- sensitivity check;
- usage-rights or copyright risk check when external material is involved;
- conflict check against Project Facts and existing Knowledge;
- human review or explicit user approval;
- review date or staleness rule.

## Candidate Record

Candidate Knowledge should use:

```text
harness/templates/knowledge/CandidateKnowledgeTemplate.md
```

and record:

- source reference and source type;
- scope and project/domain boundary;
- confidence;
- usage rights when known;
- sensitive risk;
- applicability and non-applicability;
- promotion decision.

Reviewed Knowledge should use:

```text
harness/templates/knowledge/ReviewedKnowledgeTemplate.md
```

and record source trace, review date, reviewer and staleness rule.

## Closeout Relationship

Task closeout may list Knowledge candidates through:

```text
harness/governance/promotion/GovernanceCloseoutPolicy.md
harness/templates/governance/GovernanceCloseoutTemplate.md
```

Listing a candidate does not promote it. Promotion happens only after review or explicit user approval.

## Forbidden Paths

```text
raw log -> reviewed Knowledge
RAG chunk -> source of truth
agent guess -> reviewed Knowledge
workflow evidence -> reviewed Knowledge without review
private settings -> any knowledge asset
```
