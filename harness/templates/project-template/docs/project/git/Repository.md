---
documentName: harness/templates/project-template/docs/project/git/Repository.md
version: v0.3.0-formal-project-package
updatedAt: 2026-06-18 10:30:00.000 +08:00
status: active
purpose: 项目仓库、分支策略和 agent Git 边界模板。
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
  - harness/templates/project-template/docs/project/git/Repository.md
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
# Repository Template（仓库治理模板）

## 目的

Capture repository, branch, build, test, pull request and agent git boundary facts for a managed project.

## 输入

- project profile
- local worktree boundary
- reviewed repository reference or redacted repository reference
- GitHub owner/account reference placeholder
- stable command surfaces
- branch and review policy

## 输出

- `projects/<project-id>/docs/project/git/Repository.md`
- repository routing facts
- branch policy
- build/test command references
- agent git operation boundaries

## 敏感边界

Do not include credentials, auth files, private settings, unredacted logs, real local paths, concrete GitHub account values or real private repository URLs.

Use `<repository-ref>` and `<github-account-ref>` until a reviewed redacted reference is approved. Concrete local GitHub account details belong under `user/` local files.

## 实例化规则

1. Copy this file to `projects/<project-id>/docs/project/git/Repository.md`.
2. Use stable command IDs instead of long ad hoc command bodies when possible.
3. Keep raw git logs and terminal output out of tracked docs unless redacted.
4. Do not record credentials, deploy keys or auth file content.

## Repository Information

| Field | Value |
|---|---|
| Project ID | `<project-id>` |
| Repository Reference | `<repository-ref>` |
| GitHub Owner Or Org Reference | `<github-owner-or-org-ref>` |
| GitHub Account Reference | `<github-account-ref>` |
| Default Branch | `<default-branch>` |
| Development Branch | `<development-branch>` |
| Release Branch Pattern | `<release-branch-pattern>` |
| Owner | `<owner>` |
| Review Rule | `<review-rule>` |

## Branch Strategy

| Branch Type | Naming Rule | Purpose | Merge Policy |
|---|---|---|---|
| default | `<default-branch>` | stable baseline | `<merge-policy>` |
| development | `<development-branch>` | daily integration | `<merge-policy>` |
| feature | `<feature-pattern>` | feature work | `<merge-policy>` |
| fix | `<fix-pattern>` | bug fix | `<merge-policy>` |
| docs | `<docs-pattern>` | docs work | `<merge-policy>` |

## Command Surfaces

| Scenario | Stable Command ID | Acceptance |
|---|---|---|
| Install dependencies | `<install-command-id>` | `<acceptance>` |
| Build | `<build-command-id>` | `<acceptance>` |
| Run | `<run-command-id>` | `<acceptance>` |
| Unit test | `<unit-test-command-id>` | `<acceptance>` |
| Integration test | `<integration-test-command-id>` | `<acceptance>` |
| Docs check | `<docs-check-command-id>` | `<acceptance>` |

## Pull Request Rules

1. Major architecture or governance changes require review.
2. Direct writes to protected branches require explicit user approval.
3. PR descriptions must include scope, validation and risk.
4. Generated files must state their source.
5. Harness doc changes must update the corresponding index when routing changes.

## GitHub Boundary

| Item | Handling |
|---|---|
| GitHub account name | Store concrete value under `user/`; tracked docs use `<github-account-ref>`. |
| Private repository URL | Store concrete value under `user/`; tracked docs use `<repository-ref>`. |
| Credential helper or auth state | Never read, copy or summarize into tracked docs. |
| Public repository URL | May be tracked only after review confirms it is not sensitive. |
| Harness Root repo | Separate repository from any project work copy. |
| Project repo | May use the same account, but remains a separate Git repository. |

## Agent Git Boundary

Before git operations, the agent must know:

| Question | Answer |
|---|---|
| Is write access allowed? | `<yes-no-unknown>` |
| Is commit allowed? | `<yes-no-unknown>` |
| Is PR creation allowed? | `<yes-no-unknown>` |
| Is protected branch modification forbidden? | `<yes-no-unknown>` |
| Is this task read-only? | `<yes-no-unknown>` |
