---
documentName: harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
version: v1.1.0-h9-java-main-discovery
updatedAt: 2026-06-23 18:54:52.291 +08:00
status: active
purpose: 定义 Java/Maven 项目的稳定命令门面、证据输出和敏感信息边界。
scope:
  - java-maven-command-surface
  - stable-tool-contract
  - workflow-evidence
  - real-project-validation-discovery
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/tools/docs/command-surfaces/JavaMavenCommandCookbook.md
  - harness/governance/security/CredentialBoundaryPolicy.md
outputTo:
  - harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/tools/ToolsIndex.md
  - harness/tools/scripts/stable/invoke-maven-project.ps1
  - harness/tools/scripts/stable/invoke-java-main.ps1
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h9-java-main-discovery-and-working-directory
---
# Java/Maven 命令门面

本文定义 Java/Maven 项目的 Command Surface，中文解释是命令门面。Agent 执行 Java/Maven 验证时，应优先调用这里列出的稳定脚本，不在任务中临时拼接复杂 classpath、settings 解析或 Maven 调用规则。

## 1. 稳定命令

| 命令 | 稳定脚本 | 用途 |
|---|---|---|
| 查看 profile | `harness/tools/scripts/stable/show-java-maven-config.ps1` | 输出 Java/Maven profile 的安全摘要。 |
| Maven 验证 | `harness/tools/scripts/stable/invoke-maven-project.ps1` | 运行 Maven goals，输出 status JSON 和 redacted log path。 |
| Java main 验证 | `harness/tools/scripts/stable/invoke-java-main.ps1` | 编译、构建 classpath、运行 main class，并输出证据路径。 |
| 清理运行态 | `harness/tools/scripts/stable/clean-sandbox.ps1` | dry-run 清理 `var/logs` 和 `var/tmp`；`-Apply` 需要用户授权。 |

## 2. 真实项目验证发现顺序

Agent 执行真实 Java/Maven 项目验证时，必须先从项目事实入口发现验证契约，再调用稳定工具。推荐顺序：

```text
projects/<project-id>/AGENTS.md
-> projects/<project-id>/docs/project/ProjectIndex.md
-> projects/<project-id>/docs/project/ValidationProfile.yaml
-> projects/<project-id>/docs/project/Validation.md
-> projects/<project-id>/docs/project/TestStrategy.md 或 docs/project/test/Test.md
-> harness/tools/scripts/stable/show-java-maven-config.ps1
-> harness/tools/scripts/stable/invoke-maven-project.ps1 或 invoke-java-main.ps1
```

规则：

1. 项目文档只保存 profile ID、module、main class、测试范围、是否需要 pass marker、可忽略 warning 类型和证据位置。
2. 本机 Java、Maven、settings 和 local repository 的真实路径只保存在 ignored local profile，例如 `user/settings/maven/java-maven.local.json`。
3. Agent 不应在任务中手工搜索 Maven 安装、读取 settings XML 或拼接复杂 classpath；若稳定工具能力不足，应先修复工具或形成 tool patch candidate。
4. 单个 E2E program 的业务字段、固定输出值和场景级判断只写入本次 workflow evidence，不写入通用 Harness 文档。

## 3. 查看 Profile

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile <profile-id>
```

默认行为：

- 输出 JSON 安全摘要；
- 检查 Maven、Java、settings path 和 local repository path 是否存在；
- 不解析 Maven settings XML；
- 不输出凭据材料、口令或 settings 正文。

## 4. Maven 验证

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Agent codex `
  -Profile <profile-id> `
  -Goals test
```

标准输出：

- status summary；
- status JSON path；
- redacted log path；
- failure mode；
- repair suggestion。

## 5. Java Main 验证

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-java-main.ps1 `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -MainClass <package.MainClass> `
  -JavaWorkingDirectory module-root `
  -Agent codex `
  -Profile <profile-id>
```

真实项目验证中，Agent 应优先使用本工具运行 main class 或 E2E program。若工具能力不足，应先把需求沉淀为 stable tool 修复或扩展候选，再记录 workflow evidence。

`-JavaWorkingDirectory` 可选值：

| 值 | 含义 |
|---|---|
| 省略或 `module-root` | 从模块根目录运行 Java main；这是兼容旧行为的默认值。 |
| `project-root` | 从项目根目录运行 Java main；适合需要复现 IDE 项目根工作目录语义的 E2E program。 |
| 相对路径 | 相对 `ProjectRoot` 解析。 |
| 绝对路径 | 仅作为本次命令参数使用，不写入 tracked docs。 |

## 6. Local Repository Override

当 private Maven profile 指向当前 sandbox runtime 不可写的 local repository 时，稳定调用应显式覆盖到 Harness runtime 路径：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -ProjectRoot <HARNESS_ROOT>\projects\<project-id> `
  -Agent codex `
  -Profile <profile-id> `
  -Goals test `
  -LocalRepo <HARNESS_ROOT>\var\m2\<run-id>
```

记录规则：

- profile ID 可以进入 workflow evidence；
- `var/m2/<run-id>` 可以作为 runtime configuration 记录；
- 私有 settings 路径、私有仓库路径、credential、raw log 和 status JSON 正文不得进入 tracked docs；
- 不可写 local repository 导致的首次失败应归因到 `tool/execution`。

## 7. Workflow Evidence

Java/Maven 任务的 workflow evidence 应记录：

| 字段 | 来源 |
|---|---|
| command surface | 本文命令门面 |
| project root | Task Brief / Project Profile |
| profile | Project Profile 或用户输入 |
| goals / mainClass | Task Brief / execution plan |
| status JSON path | 稳定脚本输出 |
| log path | 稳定脚本输出 |
| state / exitCode | status summary |
| failure mode | 稳定脚本输出或 Agent 归因 |
| repair suggestion | rerun 或修复计划 |

tracked docs 只记录安全摘要和路径，不粘贴 status JSON 正文或 raw log。

## 8. 禁止事项

1. 不要手动读取或打印 Maven settings XML。
2. 不要把 private settings path、repository path、credential 或 raw log 写入 tracked docs。
3. 不要默认使用 historical smoke script。
4. 不要把 status JSON 或 redacted log path 藏在自然语言描述里。
5. 不要在默认 workflow 中手工拼接复杂 Maven classpath。

## 9. 未来 CLI

未来可以实现统一 `harness` CLI，中文解释是命令行入口：

```text
harness validate java-maven --project <project-id> --profile <profile-id>
harness run java-main --project <project-id> --main-class <package.MainClass>
```

当前这些命令只是目标形态，不代表 CLI 已经实现。
