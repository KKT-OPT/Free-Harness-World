# Project Registration Model

Status: active
Version: v0.3.0-p12.2
Date: 2026-06-10

## Purpose

This document defines the Harness Root project registration model.

The registry is a routing artifact. It helps an agent find a managed project instance, its entry file, project index, default validation profile and high-level safety summary. It is not a project fact store.

## Source Priority And Legacy Boundary

For old HarnessVault inputs, concrete directory organization and file content outrank the old standalone architecture narrative.

P12.2 reviewed the old HarnessVault tree and found no durable local project registry equivalent. The useful old ideas are:

| Old HarnessVault fact | P12.2 interpretation |
|---|---|
| Top-level `INDEX.md` routes to layer indexes. | The new registry must route only to project entries, not duplicate project facts. |
| `AgentContextManifest.yaml` is auxiliary and says Markdown facts remain authoritative. | The new registry is machine-checkable auxiliary routing; project `docs/project` remains authoritative for facts. |
| `docs/project-template/ProjectIndex.md` separates templates from instantiated project docs. | The registry points to `projects/<project-id>/docs/project/ProjectIndex.md` after instantiation. |

No old registry directory or old manifest is copied into the current Harness Root.

## Registry Files

Current P12.2 files:

```text
user/registry/projects.local.json
user/registry/projects.local.example.json
tools/scripts/stable/test-project-registry.ps1
```

`user/registry/projects.local.json` is the local routing registry for this Harness Root. It may contain only reviewed routing metadata and safety summaries.

`user/registry/projects.local.example.json` is a schema-like example. It must not contain real project facts, real repository URLs, branch names, credentials, private settings paths or git history.

## Entry Shape

Each project entry must use this minimal shape:

```json
{
  "projectId": "java-demo",
  "root": "projects/java-demo",
  "entry": "AGENTS.md",
  "projectIndex": "docs/project/ProjectIndex.md",
  "defaultValidationProfile": "real-local-maven",
  "knowledgeScopes": [
    "project-reviewed:java-demo",
    "domain:java",
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

Top-level registry fields:

```text
schemaVersion
registryKind
projects
```

## Forbidden Registry Content

The registry must not contain:

- source layout facts;
- architecture facts;
- API, data, PRD or test report content;
- raw validation output;
- real repository URLs;
- branch names;
- private settings paths;
- credential, token, password or auth file content;
- git history;
- workflow evidence bodies;
- Memory, Skill or Knowledge bodies.

Detailed facts belong in:

```text
projects/<project-id>/docs/project/
```

Runtime and private execution configuration belongs outside the registry. The registry may name a validation profile ID, but must not include the profile's private path values.

## Validation Rules

Use the scoped registry validator:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/scripts/stable/test-project-registry.ps1 -Root . -Registry user/registry/projects.local.json
```

The validator checks:

| Check | Rule |
|---|---|
| Missing project | `root`, `entry` and `projectIndex` must exist. |
| Duplicate project ID | `projectId` must be unique. |
| Out-of-bound root | `root` must remain under `projects/`. |
| Allowed fields | Project entries must use only the minimal registry fields. |
| Relative paths | `root`, `entry` and `projectIndex` must be relative and must not contain traversal. |
| Sensitive summary | `sensitiveBoundarySummary` must stay as a summary, not path/glob/detail content. |

Negative checks can be exercised without writing temporary files:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/scripts/stable/test-project-registry.ps1 -Root . -SelfTest
```

`-SelfTest` must detect:

```text
missingProjectRoot
duplicateProjectId
rootOutOfBounds
```

## Current Managed Project

Current local registry:

```text
user/registry/projects.local.json
```

Current project:

```text
projectId = java-demo
root = projects/java-demo
entry = AGENTS.md
projectIndex = docs/project/ProjectIndex.md
defaultValidationProfile = real-local-maven
```

`projects/java-demo` remains a controlled demo project. It proves routing, workflow evidence, stable tool invocation and governance closeout patterns for a controlled project. It does not prove real business project onboarding.

## Future Real Project Rule

Future real projects must still follow these rules:

1. The project work copy must live under `projects/<project-id>`.
2. Root registry entries must contain only routing metadata and safety summary.
3. Project facts must stay inside `projects/<project-id>/docs/project/`.
4. Real business git history must not be mixed into the Harness Root repository.
5. The user must explicitly approve real project onboarding before a new local registry entry is added.
