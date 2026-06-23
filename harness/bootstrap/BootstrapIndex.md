---
documentName: harness/bootstrap/BootstrapIndex.md
version: v1.1.0-h8-install-uninstall
updatedAt: 2026-06-23 10:05:00.000 +08:00
status: active
purpose: 定义 Harness Workspace 首次初始化、局部安装、自检和 GitHub agent 分支恢复管理的 H8 目标入口。
scope:
  - bootstrap
  - workspace-initialization
  - workspace-install
  - workspace-uninstall
  - distribution-foundation
  - agent-branch-git-management
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
relatedDocuments:
  - README.md
  - harness/tools/scripts/stable/bootstrap-harness-workspace.ps1
  - harness/tools/scripts/stable/test-harness-governance.ps1
  - harness/tools/scripts/stable/publish-harness-agent-branch.ps1
  - projects/README.md
  - user/registry/projects.local.example.json
  - user/registry/knowledge.local.example.json
outputTo:
  - harness/bootstrap/BootstrapIndex.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h8-install-uninstall-added
---
# Bootstrap 索引

本文是 H8 的 bootstrap 入口。H8 的目标不是正式产品化发布，而是让 `agent-git` 分支具备可下载、可初始化、可自检和可审查提交的基础能力。

正式产品化发布必须等待 H9 真实项目验证及后续 release gate 通过后，由用户在 `main` 分支完成。

## 1. H8 Bootstrap 范围

H8 Bootstrap 覆盖：

- Harness Root 入口和索引可读；
- `LICENSE`、`README.md`、`AGENTS.md`、`INDEX.md` 和 `harness/HarnessIndex.md` 存在；
- `user/registry/*.example.json` 可作为本地 registry 初始化来源；
- `projects/README.md` 提供项目实例挂载边界；
- `harness/tools/scripts/stable/bootstrap-harness-workspace.ps1` 提供本地初始化命令；
- `harness/tools/scripts/stable/test-harness-governance.ps1` 提供治理自检；
- `harness/tools/scripts/stable/publish-harness-agent-branch.ps1` 用于恢复 `agent-git` 分支 GitHub 管理。

H8 不声明：

- Harness 已达到正式 release；
- `main` 分支可由 agent 发布；
- Memory、Skill、Knowledge 和 Governance 已经过真实项目闭环验证；
- 当前架构已完成全部产品化成熟度。

## 2. 首次初始化流程

```powershell
git clone git@github.com:KKT-OPT/Free-Harness-World.git <HARNESS_ROOT>
cd <HARNESS_ROOT>
git checkout agent-git

powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode status
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode install
```

`-Mode install` 只创建缺失的本地目录和空的本地 registry 文件。用户需要后续按真实项目和知识源填写本地 registry。脚本不覆盖已有文件，不写入凭据，不导入真实项目。`-Mode init` 是兼容别名。

## 2.1 卸载流程

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode uninstall
```

`-Mode uninstall` 只删除 install 生成的本地 registry 文件和空的 `var/` 运行态目录。它不删除 Git clone 本身，不删除 tracked 文档，不删除真实项目目录。

## 3. 初始化产物

| 产物 | Git 边界 | 说明 |
|---|---|---|
| `user/registry/projects.local.json` | ignored | 空本机项目路由，需要用户按真实项目修改。 |
| `user/registry/knowledge.local.json` | ignored | 空本机知识源路由，需要用户按真实知识源修改。 |
| `projects/` | tracked mount README only | 真实项目目录默认 ignored，项目 Git 独立。 |
| `var/` | ignored | 运行态 logs、tmp、cache、rag index 等。 |

## 4. 自检流程

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-harness-governance.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-project-registry.ps1 -SelfTest
```

通过自检只表示 H8 bootstrap 基础设施可用，不表示正式产品化发布。

## 5. GitHub 管理恢复

H8 只恢复 `agent-git` 分支的 GitHub 管理。

允许：

- agent 在 `agent-git` 分支提交和推送经自检通过的 Harness 架构落地资产；
- 用户在 GitHub 上审查 `agent-git` 分支；
- 后续由用户决定是否合并或重做到 `main`。

禁止：

- agent 直接修改或推送 `main`；
- agent 创建正式 release tag；
- 把真实项目源码、用户私有知识、运行态产物、auth、settings 或未脱敏日志提交到 Harness Distribution Repo。

## 6. H8 验收标准

| 标准 | 期望 |
|---|---|
| Bootstrap 入口 | `harness/bootstrap/BootstrapIndex.md` 存在并被索引路由。 |
| Install 命令 | `bootstrap-harness-workspace.ps1 -Mode install` 可运行并创建本地 registry 和运行态目录。 |
| Uninstall 命令 | `bootstrap-harness-workspace.ps1 -Mode uninstall` 可运行并删除 install 生成的本地文件，不破坏 Git clone。 |
| 本地边界 | `.gitignore` 阻止 `var/`、`projects/*/`、用户私有配置和运行态工具进入 Git。 |
| 自检 | governance self-check 和 registry self-test 通过。 |
| Clone 验证 | 在非当前 Harness Root 的独立本地路径完成 clone、install、status、uninstall 流程验证。 |
| GitHub 恢复 | 当前分支为 `agent-git`，远端为 `KKT-OPT/Free-Harness-World`，变更提交并推送到 `origin/agent-git`。 |
| Release 边界 | 文档明确正式产品化发布在 H9 真实项目验证之后，由用户在 `main` 分支完成。 |
