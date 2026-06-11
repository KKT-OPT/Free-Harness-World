# Sensitive Boundaries Template

Status: template
Version: v0.3.0-formal-project-package
Date: 2026-06-12

## Purpose

Define what the agent may read, summarize, pass by path, or never touch for this managed project.

## Outputs

- `projects/<project-id>/docs/project/SensitiveBoundaries.md`
- project-specific sensitive boundary map
- prompt and evidence exclusion rules

## Sensitive Classes

| Class | Examples | Default Handling |
|---|---|---|
| Credential | token, password, key, auth file, Maven server credential | Never read or track |
| Local machine path | drive paths, user home paths, local IDE paths | Keep in `user/` local files |
| GitHub identity | account name, private org, credential helper state | Keep in `user/` local files |
| Private repository | private URL, deploy key, remote auth | Use redacted reference only |
| Private Maven | settings XML, server id mapping, local repository path | Pass path only through allowed tools |
| Raw log | terminal output, stack traces with paths or secrets | Runtime state unless redacted |
| Customer or production data | personal data, business data, production snapshots | Use synthetic or redacted examples |

## Project-Specific Rules

| Source | Access Mode | May Enter Prompt | May Enter Tracked Docs | Notes |
|---|---|---|---|---|
| `<path-or-source>` | `<read-summary-pass-path-only-forbidden>` | `<yes-no>` | `<yes-no>` | `<notes>` |

## Allowed Local References

Concrete local references must live under:

```text
user/
```

Tracked project docs may use only reviewed placeholders:

```text
<local-project-root>
<private-repository-ref>
<github-account-ref>
<private-maven-profile-id>
<settings-path-ref>
```

## Blocking Conditions

1. Task requires reading credential contents.
2. Task asks to write local absolute paths into tracked docs.
3. Tool output contains token, password, secret or auth material and is about to be recorded.
4. Project fact cannot be stated without private repository or account details.
5. User has not approved handling of sensitive project material.
