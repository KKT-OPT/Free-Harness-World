# Local Identity And Git Boundary Policy

Status: active
Version: v0.1.0-git-boundary
Date: 2026-06-12

## Purpose

This policy defines how Harness handles local machine identity, GitHub account information, repository boundaries and Git tracking.

Local Identity，中文解释是本地身份，包括本机绝对路径、用户目录、GitHub 账号、private repository URL、credential helper 状态、auth 文件位置、私有 Maven settings/profile 和其他只对当前机器或当前用户成立的信息。

Git Boundary，中文解释是 Git 管理边界，用于区分哪些 Harness Root 资产可以进入 Git，哪些必须保留在 `user/`、`var/`、`projects/` 或其他 ignored 区域。

## Decision

Harness Root should be managed by a Git repository after the current root layout and sensitive-boundary checks pass review.

Do not initialize or connect a remote repository automatically. Repository creation, remote URL, GitHub account and publishing mode require explicit user approval.

## Repository Separation

Harness Root and managed project work copies must remain separate repositories:

```text
<HARNESS_ROOT>                 -> Harness framework repository
<HARNESS_ROOT>/projects/<id>   -> project work copy, separate repository when needed
```

The same GitHub account may manage both repositories, but Git history, remotes, branches, issues and pull requests must stay separate.

## Allowed In Harness Root Git

| Area | Examples |
|---|---|
| Agent entry | `AGENTS.md`, `README.md` |
| Harness docs | `harness/architecture/`, `harness/governance/`, `harness/project-template/`, `harness/observability/` |
| Templates | `harness/templates/` |
| Skills and Memory rules | `harness/skills/`, `harness/memory/` without private user content |
| Adapter docs | `adapter/` |
| Tool source and docs | `tools/scripts/stable/`, reviewed helper scripts, `tools/docs/` |
| RAG policy/config examples | `rag/manifests/*.example.yaml`, reviewed pipelines and eval templates |
| User examples | `user/registry/*.example.json`, local config examples without real values |
| Compatibility stubs | `docs/` while the compatibility period is active |
| Git ignore rules | `.gitignore` |

## Forbidden In Harness Root Git

| Area | Examples |
|---|---|
| Runtime state | `var/`, logs, cache, tmp, homes, evidence raw output |
| Local user settings | `user/settings/`, Maven settings XML, private Maven profile values |
| Local identity | `user/github/`, `user/auth/`, local GitHub account files |
| Local registry | `user/registry/*.local.json`, `user/registry/*.private.json` |
| External tools | `tools/external/`, downloaded runtimes, binary tool installs |
| Project work copies | `projects/*/` |
| Obsidian runtime | workspace, graph and plugin runtime files |
| Concrete local paths | drive paths, user home paths, IDE workspace paths |
| Credentials | token, password, secret, auth files, key material |
| Private repository values | private URLs, deploy keys, credential helper state |

## Where Local Values Go

Concrete local values belong under `user/`:

```text
user/
  registry/
    projects.local.json
  settings/
    maven/
      java-maven.local.json
      settings-sandbox.xml
  github/
    account.local.yaml
    remotes.local.yaml
  auth/
    <local auth references>
```

Tracked docs may use placeholders:

```text
<HARNESS_ROOT>
<github-account-ref>
<private-repository-ref>
<private-maven-profile-id>
<settings-path-ref>
<local-project-root>
```

## Git Initialization Gate

Before running `git init` for Harness Root:

1. Governance self-check passes with `findingCount=0`.
2. Sensitive scan finds no concrete local paths or credential-like values in trackable assets.
3. `.gitignore` excludes `var/`, `user/settings/`, `user/github/`, `user/auth/`, `user/registry/*.local.json`, `tools/external/` and `projects/*/`.
4. User confirms whether the repository is local-only or connected to GitHub.
5. User confirms GitHub account/remote details, stored only under `user/` local files.

## Publishing Rule

Commit and push are separate approvals:

```text
git init       -> allowed only after review
git add/commit -> allowed only after user confirms commit scope
git remote add -> allowed only after user confirms remote and account boundary
git push       -> allowed only after user confirms publish target
```

Agent Runtime must not infer GitHub identity from local credential helpers or auth files.
