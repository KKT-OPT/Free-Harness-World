# Harness 稳定工具表面模型

Status: draft
Version: v0.5.0-p12.3
Date: 2026-06-11

## 1. 文档定位

本文是 P7 阶段交付物，用于定义 agent 如何调用稳定工具，而不是临时拼接命令。

专业术语说明：

- Tool Assets：工具资产。稳定脚本、命令门面和 helper scripts。
- Command Surface：命令表面或命令门面。agent 面向任务调用的稳定命令接口。
- Status JSON：状态 JSON。工具执行后写出的机器可读结果。
- Log Path：日志路径。工具执行后写出的可审计日志位置。

本文记录稳定工具表面。P9-preflight 7.2 已将脚本按稳定、历史和运行态候选分区。

## 2. P7 交付物

| 交付物 | 路径 |
|---|---|
| 稳定工具表面模型 | `tools/docs/command-surfaces/StableToolSurfaceModel.md` |
| 脚本索引 | `tools/docs/script-index/ScriptIndex.md` |
| Java/Maven 命令表面 | `tools/docs/command-surfaces/JavaMavenCommandSurface.md` |

## 3. 当前脚本分类

| Script | Classification | Default Exposure | Reason |
|---|---|---|---|
| `tools/scripts/stable/show-java-maven-config.ps1` | stable | yes | 安全展示 Java/Maven profile 摘要，默认不检查 settings metadata |
| `tools/scripts/stable/invoke-maven-project.ps1` | stable | yes | 通用 Maven 项目验证工具 |
| `tools/scripts/stable/invoke-java-main.ps1` | stable | yes | 通用 Java main 验证工具 |
| `tools/scripts/stable/clean-sandbox.ps1` | stable-with-approval | yes, dry-run first | 清理运行态，`-Apply` 需要明确授权 |
| `tools/scripts/stable/test-project-registry.ps1` | stable | yes | P12.2 本地项目 registry 只读校验工具 |
| `tools/scripts/stable/test-harness-governance.ps1` | stable | yes | P12.3 Harness Root 治理自检工具，默认 dry-run |
| `tools/scripts/historical/run-java-smoke.ps1` | historical | no | 历史 smoke 脚本，不作为稳定门面 |
| `tools/scripts/historical/run-real-java-smoke.ps1` | historical-restricted | no | 真实项目历史验证脚本，涉及真实 settings 和外部项目 |
| `tools/scripts/runtime/hermes-wecom-generic-java-prompt.md` | prompt-candidate | no | 后续 P6/P10 可重写为 adapter 示例 |
| `tools/scripts/runtime/audio_core.ps1` | candidate-helper | no | 与 Harness 主流程关系待 P7/P10 评审 |
| `tools/scripts/runtime/hermes-update-codex.ps1` | candidate-helper | no | Hermes/Codex 支撑脚本，需安全评审 |
| `tools/scripts/runtime/Start-Hermes-Desktop.ps1` | candidate-runtime-helper | no | 桌面启动 helper，需 P10 判断 |

## 4. 稳定工具调用规则

agent 应优先使用稳定命令表面：

```text
show-java-maven-config
invoke-maven-project
invoke-java-main
clean-sandbox
test-project-registry
test-harness-governance
```

agent 不应：

- 手动拼接复杂 Maven classpath；
- 直接读取 settings XML 正文；
- 把历史 smoke 脚本当作默认工具；
- 把临时命令或一次性脚本加入稳定索引；
- 隐藏 status JSON 或 log path。

治理自检命令示例：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\tools\scripts\stable\test-harness-governance.ps1 `
  -Root <HARNESS_ROOT> `
  -Registry user/registry/projects.local.json
```

## 5. 标准输出证据

稳定工具输出必须让 agent 能记录：

| 字段 | 中文解释 |
|---|---|
| `state` | passed、failed、partial、blocked |
| `exitCode` | 命令退出码 |
| `agent` | codex、hermes、shared |
| `profile` | Java/Maven profile |
| `projectRoot` | 项目根 |
| `log` | log path |
| `details` | 工具特定详情 |

当前 `invoke-maven-project.ps1` 和 `invoke-java-main.ps1` 已写出 status JSON 和 log path。

P9 修正：两个脚本通过直接进程调用写日志，不再依赖 `Start-Process`，以避免 Windows 环境变量 `Path`/`PATH` 重复键导致的启动失败。

P11.4 修正：当 private Maven profile 的默认 localRepository 对当前 sandbox runtime 不可写时，agent 应继续使用稳定脚本，并通过 `-LocalRepo` 指向 Harness 管理的 `var/m2/<run-id>`。这属于工具/执行环境 repair，不应误判为项目源码或测试失败。

## 6. 敏感 settings 规则

稳定工具不得打印 Maven settings 正文、server 用户名、密码、token 或完整 XML。

当前规则：

- `invoke-maven-project.ps1` 只把 settings path 传给 Maven，不解析 XML；
- `invoke-java-main.ps1` 只把 settings path 传给 Maven，不解析 XML；
- `show-java-maven-config.ps1` 默认只报告 settings 文件是否存在；
- `show-java-maven-config.ps1 -InspectSettingsMetadata` 是显式诊断模式，不属于默认稳定调用；
- `run-real-java-smoke.ps1` 会读取 settings metadata，因此被排除出默认稳定脚本索引。
- status JSON 可能包含本地执行路径；tracked docs 只记录 status JSON 路径和安全摘要字段，不粘贴 JSON 正文。

## 7. 未来命令门面

未来可实现统一 `harness` CLI，中文解释是命令行入口：

```text
harness tools show-java-maven-config --profile isolated-sandbox-maven
harness validate java-maven --project java-demo --profile isolated-sandbox-maven
harness run java-main --project java-demo --main-class com.example.Main
harness cleanup sandbox --dry-run
```

当前这些只是目标形态，不代表已实现 CLI。

## 8. P7 完成标准自检

P7 原完成标准：

```text
1. Every stable script has documented inputs, outputs, and safety notes.
2. Temporary scripts are excluded from the script index.
3. Java/Maven validation can be called through a stable documented surface.
4. Status JSON and log path are standard evidence outputs.
5. Scripts do not inspect or print sensitive Maven settings.
```

自检结果：

| 检查项 | 结果 | 证据 |
|---|---|---|
| 每个稳定脚本有输入、输出和安全说明 | pass | `tools/docs/script-index/ScriptIndex.md` |
| 临时/历史脚本排除出默认稳定索引 | pass | 第 3 节、`tools/docs/script-index/ScriptIndex.md` |
| Java/Maven 验证有稳定文档化表面 | pass | `tools/docs/command-surfaces/JavaMavenCommandSurface.md` |
| Status JSON 和 log path 是标准证据输出 | pass | 第 5 节、Java/Maven command surface |
| 稳定脚本默认不检查或打印敏感 Maven settings | pass | 第 6 节，`show-java-maven-config.ps1` 默认行为已调整 |

P7 当前结论：

```text
P7 draft deliverable is complete for review.
Stable scripts have been moved to tools/scripts/stable/ during P9-preflight 7.2 landing.
No historical smoke script is exposed as a default stable tool.
```
