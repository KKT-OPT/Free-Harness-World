---
documentName: user/README.md
version: v1.0.0-pre-h8-user-boundary
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 user 目录作为本地用户、私有配置、本地 registry 和本地知识边界的说明。
scope:
  - user-boundary
  - local-only
  - registry
  - settings
  - auth
prerequisites:
  - AGENTS.md
  - INDEX.md
relatedDocuments:
  - user/registry/projects.local.example.json
  - user/registry/knowledge.local.example.json
  - user/knowledge/README.md
  - harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md
outputTo:
  - user/README.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-user-boundary-aligned
---
# User Local Boundary

`user/` 是当前 Harness Root 的本地用户边界。tracked examples 可以放在这里，但真实用户值必须留在 ignored files 或 ignored subdirectories。

## Local-Only Examples

```text
user/registry/projects.local.json
user/registry/knowledge.local.json
user/settings/
user/github/
user/auth/
user/identity/
user/knowledge/
```

不要把具体 GitHub 账号、私有仓库 URL、Maven settings 内容、token、password、secret、auth 文件、本机绝对路径或 credential helper 输出写入 tracked Harness docs。
