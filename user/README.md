# User Local Boundary

Status: active
Version: v0.1.0-local-boundary
Date: 2026-06-12

`user/` is the local-only boundary for this Harness Root.

Tracked examples may live here, but concrete user values must stay in ignored files or ignored subdirectories.

## Local-Only Examples

```text
user/registry/projects.local.json
user/settings/
user/github/
user/auth/
```

Do not copy concrete GitHub account values, private repository URLs, Maven settings content, tokens, passwords, secrets, auth files, local machine paths or credential helper output into tracked Harness docs.
