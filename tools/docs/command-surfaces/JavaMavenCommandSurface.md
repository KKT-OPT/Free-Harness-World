# Java/Maven Command Surface

Status: draft
Version: v0.3.0-p11.4
Date: 2026-06-10

## 1. Purpose

本文定义 Java/Maven 项目的稳定命令表面。

Command Surface，中文解释是命令门面，表示 agent 应调用的稳定工具接口。

## 2. Current Stable Commands

### 2.1 Show Profile

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile isolated-sandbox-maven
```

用途：

- 查看 profile 是否可用；
- 默认不解析 Maven settings XML；
- 默认不输出 credentials。

### 2.2 Validate Maven Project

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Agent codex `
  -Profile isolated-sandbox-maven `
  -Goals test
```

用途：

- 运行 Maven 验证；
- 输出 status JSON；
- 输出 log path；
- 作为 Java 项目默认 validation surface。

### 2.2.1 Private Profile Local Repository Override

When a private Maven profile points to a local repository that is not writable by the current sandbox runtime, the stable invocation should override the local repository to a Harness-managed runtime path:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-maven-project.ps1 `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -Agent codex `
  -Profile real-local-maven `
  -Goals test `
  -LocalRepo <HARNESS_ROOT>\var\m2\<run-id>
```

Rules:

- the profile ID may be recorded;
- the Harness-managed local repository path under `var/m2` may be recorded as runtime configuration;
- private settings paths, private repository paths, credentials, raw log contents and status JSON contents must not be recorded in tracked docs;
- a failed first run caused by an unwritable local repository should be attributed as `tool/execution`, not as Java source failure.

### 2.3 Run Java Main

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\invoke-java-main.ps1 `
  -ProjectRoot <HARNESS_ROOT>\projects\java-demo `
  -MainClass com.example.Main `
  -Agent codex `
  -Profile isolated-sandbox-maven
```

用途：

- 编译；
- 构建 classpath；
- 执行 main class；
- 输出 status JSON 和 log path。

### 2.4 Cleanup Runtime Evidence

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\clean-sandbox.ps1
```

默认 dry-run。

真正删除必须显式使用：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\clean-sandbox.ps1 -Apply
```

`-Apply` 需要用户授权。

## 3. Required Workflow Evidence

Java/Maven 任务 workflow 必须记录：

| Evidence | 来源 |
|---|---|
| command surface | 本文命令 |
| project root | Task Brief / Project Profile |
| profile | Project Profile |
| goals/mainClass | Task Brief / execution plan |
| status JSON path | 脚本输出 |
| log path | 脚本输出 |
| pass/fail | status JSON |
| repair action | workflow evidence, when a rerun is needed |

P9 private Maven validation may record the private profile ID, but must not copy private settings paths, repository paths, credentials, raw log contents, or status JSON contents into tracked docs.

P11.4 confirmed that status JSON may contain local execution paths. Tracked evidence should therefore record only the status JSON path and safe summary fields such as `state`, `exitCode`, `profile` and `goals`.

## 4. Do Not

agent 不应：

- 手动组装 Maven classpath；
- 手动读取 Maven settings XML；
- 打印 settings 正文；
- 默认使用 `run-real-java-smoke.ps1`；
- 把 historical smoke scripts 当作稳定工具；
- 隐藏 status JSON 或 log path。

## 5. Future Facade

未来可以包装为：

```text
harness validate java-maven --project java-demo --profile isolated-sandbox-maven
harness run java-main --project java-demo --main-class com.example.Main
```

当前未实现该 CLI。
