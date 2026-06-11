# Skill and Memory Governance

Status: draft
Version: v0.2.0-p11.7
Date: 2026-06-10

## Purpose

This policy defines how Harness manages Skill and Memory without polluting Knowledge or Project Facts.

## Distinctions

| Asset | Meaning | Not |
|---|---|---|
| Skill | Reusable workflow for a class of tasks. | Not a fact database. |
| Memory | Scoped experience, preference, repeated repair lesson, or operating note. | Not stable domain knowledge. |
| Knowledge | Reviewed, citable information. | Not one-session experience. |
| Project Fact | Authoritative fact inside one managed project. | Not root-wide memory. |

## Skill Lifecycle

```text
workflow evidence
-> skill improvement candidate
-> reviewed skill
-> deprecated or archived
```

Reviewed Skill must define:

- trigger conditions;
- input requirements;
- steps;
- required project facts or knowledge;
- stable tools;
- evidence output;
- acceptance criteria;
- failure handling;
- clarification triggers.

Skill candidates and reviewed skills should use:

```text
harness/templates/skill/SkillTemplate.md
```

Do not create one-session-one-skill assets. Prefer updating an existing skill, adding a template/reference, or listing a candidate for review.

## Memory Lifecycle

```text
workflow evidence
-> memory candidate
-> reviewed memory
-> archived or expired
```

Reviewed Memory must record:

- scope;
- source;
- confidence;
- staleness or expiry condition;
- review date;
- whether it may become Skill or Knowledge.

Memory candidates and reviewed memory should use:

```text
harness/templates/memory/MemoryTemplate.md
```

Memory must stay concise. Do not use Memory for raw logs, task transcripts, large source content, temporary paths, or facts already owned by Project Facts or reviewed Knowledge.

## P11 Rule

P11 may produce Skill/Memory candidates, but must not auto-promote them. Candidate promotion requires review or explicit user approval.

## Closeout Relationship

Task closeout may list Skill or Memory candidates through:

```text
harness/governance/promotion/GovernanceCloseoutPolicy.md
harness/templates/governance/GovernanceCloseoutTemplate.md
```

Closeout candidates must record source evidence, target asset, approval requirement and disposition.
