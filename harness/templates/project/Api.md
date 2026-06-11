# API Template

Status: template
Version: v0.1.0-p12.1
Date: 2026-06-10

## Purpose

Capture API surface, contract ownership, compatibility, integration dependencies and auth boundaries.

## Inputs

- architecture facts
- repository facts
- API specifications or reviewed source facts
- integration constraints
- security boundaries

## Outputs

- `projects/<project-id>/docs/project/api/Api.md`
- API inventory
- contract status table
- integration and compatibility notes

## Sensitive Boundary

Do not include credentials, auth file content, private settings, unredacted logs, private paths, real private repository URLs, production tokens or secret endpoint details.

## Instantiation Rules

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
