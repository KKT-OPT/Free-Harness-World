---
documentName: harness/tools/docs/command-surfaces/JavaMavenCommandCookbook.md
version: v1.1.0-h9-java-main-working-directory
updatedAt: 2026-06-23 18:54:52.291 +08:00
status: active
purpose: 提供 Java/Maven 稳定命令门面的可复用调用示例，避免 Agent 为不同项目临时拼接命令。
scope:
  - java-maven-command-examples
  - stable-tool-usage
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
  - harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
outputTo:
  - harness/tools/docs/command-surfaces/JavaMavenCommandCookbook.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/tools/ToolsIndex.md
  - harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h9-java-main-working-directory
---
# Java/Maven 命令示例

本文记录 Java/Maven 稳定工具的复用示例。示例只使用占位符，不保存真实项目路径、真实 profile、私有仓库 URL、settings 正文或运行日志正文。

## 1. 查看 Java/Maven Profile

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -CheckVersion
```

适用场景：

- 验证 profile 是否可用；
- 查看 Java、Maven、settings path 和 local repository path 的安全摘要；
- 不输出 Maven settings XML 或 credential 正文。

## 2. 单模块 Maven 验证

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Goals test
```

期望输出：

- status JSON 路径；
- redacted log path；
- Maven goals、profile、exitCode 和 state 的状态摘要。

## 3. 多模块 Maven 验证

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Module <module-name> `
  -AlsoMake `
  -Goals test-compile
```

## 4. 运行单个测试类

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Module <module-name> `
  -AlsoMake `
  -Goals test `
  -- -Dtest=<test-class-name>
```

## 5. 运行 Java Main

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Module <module-name> `
  -MainClass <package.MainClass> `
  -JavaWorkingDirectory module-root `
  -PassMarker <pass-marker>
```

`-JavaWorkingDirectory project-root` 可用于需要复现 IDE 项目根工作目录语义的 E2E program；场景级 pass marker 和业务输出判断只写入 workflow evidence。

## 6. 运行带兄弟模块 classpath 的 Java Main

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-java-main.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Module <module-name> `
  -MainClass <package.MainClass> `
  -ReactorClasspathModules <module-a>,<module-b> `
  -PassMarker <pass-marker>
```

## 7. 使用 Harness 管理的 Maven 本地仓库

当私有 Maven profile 的默认 local repository 对当前 sandbox runtime 不可写时，Agent 应继续使用稳定工具，并把 local repository 指向 Harness 管理的运行态路径：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Goals test `
  -LocalRepo <HARNESS_ROOT>\var\m2\<run-id>
```

记录要求：

- 可以记录 profile ID；
- 可以记录 `var/m2/<run-id>` 这类 Harness runtime 路径；
- 不得记录私有 settings 路径、私有仓库路径、credential、raw log 或 status JSON 正文；
- local repository 不可写导致的第一次失败应归因为 `tool/execution`，不是项目源码失败。

## 8. Agent 最终回执格式

完成 Java/Maven 验证后，Agent 应在 workflow evidence 中记录稳定工具输出摘要：

```text
state: <passed|failed|partial|blocked>
statusJson: <path>
log: <path>
summary: <short safe result>
repairSuggestion: <safe repair suggestion when needed>
```
