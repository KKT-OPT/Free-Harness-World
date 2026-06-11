# Agent Sandbox / Harness Root

`<HARNESS_ROOT>` 是当前 Harness Root，也是本地执行沙盒。它按 template-inspired 形态组织为：

```text
AGENTS.md
README.md
adapter/
harness/
projects/
rag/
sandbox/
tools/
user/
var/
docs/              # short compatibility stubs only
```

Harness 是 agent 维护和读取的通用文档系统知识库，同时也是项目自动化控制层、工具资产层和治理层。Codex、Hermes 等 Agent Runtime 负责执行；Harness 负责入口、规则、路由、工具、证据和治理。

## Current Authority

当前唯一最终架构权威：

```text
harness/architecture/HarnessEngineering.md
```

当前长期索引和阶段计划：

```text
harness/INDEX.md
harness/PLANS.md
```

`docs/` 只保留短期兼容入口，后续 review 通过后应删除。

## Stable Layout

- `adapter/`: 用户、gateway、Codex/Hermes runtime adapter、Task Brief 和结果契约。
- `harness/`: 通用 Harness 文档系统，包括架构、治理、记忆、观测、项目模板、报告、skills 和 templates。
- `projects/`: 真实或 demo 项目实例。项目事实只进入 `projects/<project-id>/docs/project/`。
- `rag/`: 用户知识库和 RAG 结构化摄取层；`rag/knowledge/` 是人类可读知识分层。
- `sandbox/`: 沙盒环境、隔离、profile 和 settings 边界说明。
- `tools/`: 供 agent 使用的工具，包括 `tools/scripts/`、`tools/docs/`、`tools/external/` 和 manifests。
- `user/`: 用户本地信息和设置边界，包括项目 registry、私有 Maven profile、settings、GitHub 说明和本地配置。
- `var/`: logs、tmp、homes、m2、cache、evidence、rag indexes 等运行态。

## Project Registry

本地项目注册表：

```text
user/registry/projects.local.json
```

安全校验：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\test-project-registry.ps1 `
  -Root <HARNESS_ROOT> `
  -Registry user/registry/projects.local.json
```

registry 只保存路由 metadata。项目事实留在 `projects/<project-id>/docs/project/`。

## Governance Self-Check

P12.4 后的 dry-run 治理自检：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\test-harness-governance.ps1 `
  -Root <HARNESS_ROOT> `
  -Registry user/registry/projects.local.json
```

该检查覆盖入口路由、兼容 stub、架构权威、敏感边界、生成物、项目 registry 和仓库边界。默认不删除文件。

## Java/Maven Profiles

默认本地 profile：

```text
real-local-maven
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
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -CheckVersion
```

## Maven Validation

普通 Maven 验证：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Goals test
```

运行 Java main：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent codex `
  -Profile real-local-maven `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Module module-name `
  -MainClass package.MainClass `
  -PassMarker PASS
```

## Cleanup

预览 runtime cleanup：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\clean-sandbox.ps1
```

实际清理需要明确授权：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\clean-sandbox.ps1 -Apply
```

## GitHub Boundary

Harness Root 应作为一个独立 Git 仓库管理，但 `git init`、remote、commit 和 push 都需要用户明确确认。

复制进 `projects/<project-id>` 的真实项目必须作为另一个独立 Git 仓库管理，即使使用同一个 GitHub 账号，也不得混合 git history。

本机路径、GitHub 账号、私有仓库 URL、auth、settings 和私有 Maven 信息属于 `user/` local boundary，不进入 tracked docs。

## Obsidian Boundary

Harness 文档可以采用 Obsidian-friendly Markdown：frontmatter、wikilink、Mermaid、可选 Bases/Canvas。`.obsidian` workspace、graph、plugin runtime code 不是事实源，不进入默认上下文，也不作为 Git 维护机制。
