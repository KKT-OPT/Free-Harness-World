---
documentName: harness/templates/project-template/model/ProjectRegistrationModel.md
version: v1.0.0-h4-consolidated
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 定义本地项目 registry 的路由字段、禁止内容和项目事实边界。
scope:
  - project-registry
  - local-routing
  - sensitive-boundary
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - user/registry/projects.local.example.json
  - harness/templates/project-template/model/ProjectInstanceModel.md
outputTo:
  - harness/templates/project-template/model/ProjectRegistrationModel.md
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
# Project Registration Model

The local project registry is a routing artifact. It helps an agent find a managed project instance, project entry file, project index, default validation profile and high-level safety summary.

It is not a project fact store.

## Registry Files

```text
user/registry/projects.local.example.json
user/registry/projects.local.json
```

The example file may be tracked. The local file is machine-specific and must remain local-only.

## Entry Shape

Use placeholders in examples:

```json
{
  "projectId": "<project-id>",
  "root": "projects/<project-id>",
  "entry": "AGENTS.md",
  "projectIndex": "docs/project/ProjectIndex.md",
  "defaultValidationProfile": "<validation-profile-id>",
  "knowledgeScopes": [
    "project-reviewed:<project-id>",
    "domain:<domain-id>",
    "global"
  ],
  "sensitiveBoundarySummary": [
    "credential-material-excluded",
    "private-settings-excluded",
    "auth-files-excluded",
    "unredacted-logs-excluded",
    "generated-output-excluded"
  ]
}
```

Allowed project entry fields:

```text
projectId
root
entry
projectIndex
defaultValidationProfile
knowledgeScopes
sensitiveBoundarySummary
```

## Forbidden Registry Content

The registry must not contain:

- source layout facts;
- architecture facts;
- API, data, PRD or test report content;
- raw validation output;
- real repository URLs;
- real branch names;
- real build commands;
- private settings paths;
- credentials, tokens, passwords or auth file content;
- git history;
- workflow evidence bodies;
- Memory, Skill or Knowledge bodies.

Detailed facts belong in:

```text
projects/<project-id>/docs/project/
```

Runtime and private execution configuration belongs outside the registry. The registry may name a validation profile ID, but must not include private path values or command bodies.
