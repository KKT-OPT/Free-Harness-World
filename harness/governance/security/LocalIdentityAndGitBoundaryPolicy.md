---
documentName: harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md
version: v1.0.0-pre-h8-git-boundary
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义本地身份、GitHub 信息、知识边界、仓库边界和 Git tracking 规则。
scope:
  - local-identity
  - git-boundary
  - user-knowledge-boundary
prerequisites:
  - AGENTS.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
  - harness/governance/security/CredentialBoundaryPolicy.md
outputTo:
  - harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: pre-h8-git-restore-decision
---
# 本地身份和 Git 边界策略

## 1. 目的

本文定义 Harness 如何处理本地机器身份、GitHub account information、repository boundaries、真实用户知识和 Git tracking。

Local Identity，中文解释是本地身份，包括本机绝对路径、用户目录、GitHub 账号、private repository URL、credential helper 状态、auth 文件位置、私有 Maven settings/profile 和其他只对当前机器或当前用户成立的信息。

Git Boundary，中文解释是 Git 管理边界，用于区分哪些 Harness Root 资产可以进入 Git，哪些必须保留在 `user/`、`var/`、`projects/` 或其他 ignored 区域。

## 2. 决策

Harness Root should be managed by a Git repository after the current root layout and sensitive-boundary checks pass review.

Do not initialize or connect a remote repository automatically. Repository creation, remote URL, GitHub account and publishing mode require explicit user approval.

## 3. 仓库分离

Harness Root and managed project work copies must remain separate repositories:

```text
<HARNESS_ROOT>                 -> Harness framework repository
<HARNESS_ROOT>/projects/<id>   -> project work copy, separate repository when needed
```

The same GitHub account may manage both repositories, but Git history, remotes, branches, issues and pull requests must stay separate.

## 4. 允许进入 Harness Root Git

| Area | Examples |
|---|---|
| Agent entry | `AGENTS.md`, `README.md` |
| Harness docs | `harness/architecture/`, `harness/governance/`, `harness/observability/`, `harness/verification/`, `harness/rag/`, `harness/memory/`, `harness/skills/` |
| Templates | `harness/templates/` |
| Skills and Memory rules | `harness/skills/`, `harness/memory/` without private user content |
| Adapter docs | `adapter/` |
| Tool source and docs | `harness/tools/scripts/stable/`, reviewed helper scripts, `harness/tools/docs/` |
| RAG policy/config examples | `harness/rag/manifests/*.example.yaml`, reviewed pipelines and eval templates |
| User examples | `user/registry/*.example.json`, local config examples without real values |
| Git ignore rules | `.gitignore` |

## 5. 禁止进入 Harness Root Git

| Area | Examples |
|---|---|
| Runtime state | `var/`, logs, cache, tmp, homes, evidence raw output |
| Local user settings | `user/settings/`, Maven settings XML, private Maven profile values |
| Local identity | `user/github/`, `user/auth/`, local GitHub account files |
| Local registry | `user/registry/*.local.json`, `user/registry/*.private.json` |
| User knowledge | `user/knowledge/**` except `user/knowledge/README.md` |
| External tools | `harness/tools/external/`, downloaded runtimes, binary tool installs |
| Project work copies | `projects/*/` |
| Obsidian runtime | workspace, graph and plugin runtime files |
| Concrete local paths | drive paths, user home paths, IDE workspace paths |
| Credentials | token, password, secret, auth files, key material |
| Private repository values | private URLs, deploy keys, credential helper state |

## 6. 本地值保存位置

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
  knowledge/
    raw/
    candidate/
    reviewed/
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

## 7. Git 管理恢复门禁

当前 Harness Root 已有 Git 仓库和 remote。H0-H7 重构期间发生大量路径迁移，GitHub 管理恢复应放在 H8 阶段执行，不在 H8 前置检查中自动 commit 或 push。

恢复 Git 管理前必须满足：

1. Governance self-check passes with `findingCount=0`.
2. Sensitive scan finds no concrete local paths or credential-like values in trackable assets.
3. `.gitignore` excludes `var/`, `user/settings/`, `user/github/`, `user/auth/`, `user/knowledge/**`, `user/registry/*.local.json`, `harness/tools/external/` and `projects/*/`.
4. User confirms whether the repository is local-only or connected to GitHub.
5. User confirms GitHub account/remote details, stored only under `user/` local files.

## 8. 发布规则

Commit and push are separate approvals:

```text
git status     -> allowed for review
git add/commit -> allowed only after user confirms commit scope
git remote add -> allowed only after user confirms remote and account boundary
git push       -> allowed only after user confirms publish target
```

Agent Runtime must not infer GitHub identity from local credential helpers or auth files.
