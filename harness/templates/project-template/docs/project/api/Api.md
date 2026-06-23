---
documentName: harness/templates/project-template/docs/project/api/Api.md
version: v0.1.0-p12.1
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目 API 清单、契约归属和兼容性模板。
scope:
  - project-template
  - project-doc-template
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/README.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
outputTo:
  - harness/templates/project-template/docs/project/api/Api.md
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
# API Template（接口模板）

## 目的

Capture API surface, contract ownership, compatibility, integration dependencies and auth boundaries.

## 输入

- architecture facts
- repository facts
- API specifications or reviewed source facts
- integration constraints
- security boundaries

## 输出

- `projects/<project-id>/docs/project/api/Api.md`
- API inventory
- contract status table
- integration and compatibility notes

## 敏感边界

Do not include credentials, auth file content, private settings, unredacted logs, private paths, real private repository URLs, production tokens or secret endpoint details.

## 实例化规则

1. Copy this file to `projects/<project-id>/docs/project/api/Api.md`.
2. Use reviewed contract references rather than raw private endpoint dumps.
3. Keep examples redacted and synthetic unless explicitly approved.
4. Link API decisions to ADRs when compatibility or security policy changes.

## API Inventory

| API | Type | Owner | Status | Contract Source |
|---|---|---|---|---|
| `<api-name>` | `<rest-grpc-event-other>` | `<owner>` | `<status>` | `<source>` |

## Contract Summary

| Endpoint Or Operation | Input | Output | Compatibility | Notes |
|---|---|---|---|---|
| `<operation>` | `<input>` | `<output>` | `<compatibility>` | `<notes>` |

## Auth Boundary

```text
<auth-boundary-summary>
```

## Integration Dependencies

| Dependency | Direction | Contract | Failure Mode | Owner |
|---|---|---|---|---|
| `<dependency>` | `<inbound-outbound>` | `<contract>` | `<failure-mode>` | `<owner>` |

## Open Questions

| Question | Owner | Review Phase |
|---|---|---|
| `<question>` | `<owner>` | `<phase>` |
