---
documentName: harness/templates/project-template/model/StandardProjectPackage.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 定义标准受管项目包的目录、必需文档、可选模块和边界。
scope:
  - standard-project-package
  - managed-project-layout
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/model/ProjectTemplateGuide.md
  - harness/templates/project-template/model/ProjectInstanceModel.md
outputTo:
  - harness/templates/project-template/model/StandardProjectPackage.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/templates/project-template/README.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: h4-consolidated
---
# Standard Project Package

The standard Harness-managed project package separates reusable templates from instantiated project facts.

Reusable templates live in:

```text
harness/templates/project-template/
```

Instantiated project facts live in:

```text
projects/<project-id>/
```

## Formal Layout

```text
projects/<project-id>/
  AGENTS.md
  docs/project/
    ProjectIndex.md
    ProjectProfile.yaml
    ValidationProfile.yaml
    SourceLayout.md
    Validation.md
    TestStrategy.md
    SensitiveBoundaries.md
    Acceptance.md
    prd/PRD.md
    architecture/Architecture.md
    dictionary/SemanticDictionary.md
    git/Repository.md
    api/Api.md
    data/Data.md
    test/Test.md
    decision/ADR-0001.md
    workflow/README.md
    model/README.md
    reports/README.md
```

## 必需事实

| File Or Directory | Purpose |
|---|---|
| `AGENTS.md` | Project-local entry rules, technical stack summary, global constraints and important rules. |
| `ProjectIndex.md` | Project identity, fact inventory and routing. |
| `ProjectProfile.yaml` | Project routing profile and high-level metadata. |
| `ValidationProfile.yaml` | Validation profile identifiers and non-private command references. |
| `SourceLayout.md` | Source, test, resource, generated-output and forbidden path layout. |
| `Validation.md` | Stable validation surfaces, evidence rules and known gaps. |
| `TestStrategy.md` | Test strategy and quality gate policy. |
| `SensitiveBoundaries.md` | Project-specific sensitive classes and handling rules. |
| `Acceptance.md` | Acceptance criteria, review gates and current completion boundary. |
| `prd/PRD.md` | Product requirements, scope and non-goals. |
| `architecture/Architecture.md` | Architecture positioning, modules, boundaries and constraints. |
| `dictionary/SemanticDictionary.md` | Canonical terminology and semantic drift control. |
| `git/Repository.md` | Repository reference, branch policy and agent git rules. |
| `api/Api.md` | API inventory and compatibility notes when applicable. |
| `data/Data.md` | Data entities, privacy class and lifecycle notes when applicable. |
| `test/Test.md` | Test scope details and evidence policy. |
| `decision/` | ADR-style durable decisions. |
| `workflow/` | Task evidence, trace summaries and governance candidates. |
| `model/` | Project-local model notes and onboarding assumptions. |
| `reports/` | Redacted validation, governance or analysis reports. |

## Boundary

The standard package must not include:

- real repository URLs;
- real branch names;
- real build or deployment commands;
- private settings paths;
- credentials, tokens, passwords or auth files;
- raw logs or raw terminal transcripts;
- local absolute paths;
- customer or production data;
- concrete account or organization identifiers.

Use placeholders and reviewed redacted references until the project owner approves concrete facts in the instantiated project.
