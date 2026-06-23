---
documentName: README.md
version: v1.1.0-h8-install-uninstall
updatedAt: 2026-06-23 10:05:00.000 +08:00
status: active
purpose: 作为人类读者的 Harness Root 入口，说明当前权威文档、稳定布局、registry 和治理自检命令。
scope:
  - human-entry
  - bootstrap-orientation
  - workspace-summary
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/PLANS.md
outputTo:
  - README.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h8-install-uninstall-added
---
# Harness Root 人类入口

`<HARNESS_ROOT>` 是 Harness Workspace，也是本地执行沙盒。长期目标是作为可下载、可植入、跨机器复用的 Harness Distribution Repo checkout。

```text
AGENTS.md
INDEX.md
README.md
LICENSE
adapter/
harness/
projects/
sandbox/
user/
var/
```

Harness 是 agent 维护和读取的通用文档系统知识库，同时也是项目自动化控制层、工具资产层和治理层。Codex、Hermes 等 Agent Runtime 负责执行；Harness 负责入口、规则、路由、工具、证据和治理。

## 当前权威

当前唯一最终架构权威：

```text
harness/architecture/HarnessEngineering.md
```

当前长期索引和阶段计划：

```text
INDEX.md
harness/HarnessIndex.md
harness/architecture/PLANS.md
```

旧兼容入口在确认无风险后删除；长期入口以本文、`AGENTS.md`、`INDEX.md` 和 `harness/HarnessIndex.md` 为准。

## Bootstrap

H8 当前目标是完成 bootstrap foundation 和 `agent-git` 分支 GitHub 管理恢复，不是正式产品化发布。正式产品化发布需要等待 H9 真实项目验证及后续 release gate，并由用户在 `main` 分支完成。

检查 bootstrap 状态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 `
  -Root <HARNESS_ROOT> `
  -Mode status
```

安装本机 workspace 状态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 `
  -Root <HARNESS_ROOT> `
  -Mode install
```

`-Mode install` 只创建缺失的本地 registry 和运行态目录，其中本地 registry 是空 registry，需要用户后续按真实项目填写；脚本不覆盖已有文件，不写入凭据，不导入真实项目。`-Mode init` 是兼容别名。

卸载本机 workspace 安装态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 `
  -Root <HARNESS_ROOT> `
  -Mode uninstall
```

`-Mode uninstall` 只删除 install 生成的本地 registry 文件和空的 `var/` 运行态目录，不删除 Git clone、不删除 tracked 文档、不删除真实项目目录。

## 稳定布局

- `adapter/`: 用户、gateway、Codex/Hermes runtime adapter、Task Brief 和结果契约。
- `harness/`: 通用 Harness 文档系统，包括架构、治理、记忆、观测、项目模板、报告、skills、templates、目标 RAG 机制、目标工具资产和目标 verification。
- `projects/`: 真实或 demo 项目实例。项目事实只进入 `projects/<project-id>/docs/project/`。
- `sandbox/`: 沙盒环境、隔离、profile 和 settings 边界说明。
- `user/`: 用户本地信息和设置边界，包括项目 registry、私有 Maven profile、settings、auth、identity 和真实用户知识边界。
- `var/`: logs、tmp、homes、m2、cache、evidence、rag indexes 等运行态。

H8 前置检查后，工具资产、RAG、Verification、Observability、Memory 和 Skill 机制均已迁移或补齐到目标路径：工具资产位于 `harness/tools/`，RAG 机制位于 `harness/rag/`，真实或候选知识位于 `user/knowledge/` 或外部 private repo，运行态索引和提取产物位于 `var/rag/`，验证规则位于 `harness/verification/`，观测 schema 位于 `harness/observability/`，Memory 位于 `harness/memory/`，Skill 位于 `harness/skills/`。

## 项目 Registry

本地项目注册表：

```text
user/registry/projects.local.json
```

安全校验：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\test-project-registry.ps1 `
  -Root <HARNESS_ROOT> `
  -Registry user/registry/projects.local.json
```

registry 只保存路由 metadata。项目事实留在 `projects/<project-id>/docs/project/`。

## 治理自检

dry-run 治理自检：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\test-harness-governance.ps1 `
  -Root <HARNESS_ROOT> `
  -Registry user/registry/projects.local.json
```

该检查覆盖入口路由、历史路径回流、架构权威、敏感边界、生成物、项目 registry 和仓库边界。默认不删除文件。

## Java/Maven Profile

本地 profile ID 应来自用户设置或 Project Profile，例如：

```text
<profile-id>
```

profile 文件：

```text
user/settings/maven/java-maven.local.json
```

sandbox settings 示例：

```text
user/settings/maven/settings-sandbox.xml
```

不要把 settings XML 正文、server 用户名、密码、token、auth 文件或私有仓库细节写入 prompt、Task Brief、workflow summary 或 tracked docs。

安全查看 profile：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -CheckVersion
```

## Maven 验证

普通 Maven 验证：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Goals test
```

运行 Java main：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Module <module-name> `
  -MainClass <package.MainClass> `
  -PassMarker <pass-marker>
```

## 清理

预览 runtime cleanup：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\clean-sandbox.ps1
```

实际清理需要明确授权：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\clean-sandbox.ps1 -Apply
```

## GitHub 边界

Harness Root 应作为一个独立 Git 仓库管理。当前 GitHub 仓库是 `KKT-OPT/Free-Harness-World`。

分支边界：

- `agent-git`：agent 可以提交、修改和推送，用于架构落地、bootstrap foundation 和 H8 后续验证。
- `main`：用户拥有，正式产品化发布、合并和 release tag 只能由用户执行。

复制进 `projects/<project-id>` 的真实项目必须作为另一个独立 Git 仓库管理，即使使用同一个 GitHub 账号，也不得混合 git history。

本机路径、GitHub 账号、私有仓库 URL、auth、settings 和私有 Maven 信息属于 `user/` local boundary，不进入 tracked docs。

## Obsidian 边界

Harness 文档可以采用 Obsidian-friendly Markdown：frontmatter、wikilink、Mermaid、可选 Bases/Canvas。`.obsidian` workspace、graph、plugin runtime code 不是事实源，不进入默认上下文，也不作为 Git 维护机制。
