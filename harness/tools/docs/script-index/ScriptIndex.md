---
documentName: harness/tools/docs/script-index/ScriptIndex.md
version: v1.0.0-h7-verification-observability
updatedAt: 2026-06-23 06:51:14.830 +08:00
status: active
purpose: 按 stable、candidate、runtime、historical 和 external 分类索引 Harness 脚本，并记录稳定工具契约。
scope:
  - script-index
  - stable-tool-contract
  - tool-classification
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
  - harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
outputTo:
  - harness/tools/docs/script-index/ScriptIndex.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/tools/ToolsIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: h7-verification-observability-aligned
---
# 脚本索引

本文按稳定性和默认暴露范围索引 Harness 脚本。stable scripts 是 Tool Assets，中文解释是工具资产；candidate、runtime、historical 和 external 资产不是默认命令门面。

## 1. 稳定脚本总览

| 稳定脚本 | 主要用途 | 默认暴露 |
|---|---|---|
| `harness/tools/scripts/stable/show-java-maven-config.ps1` | 输出 Java/Maven profile 安全摘要。 | yes |
| `harness/tools/scripts/stable/invoke-maven-project.ps1` | 运行 Maven goals 并输出验证证据。 | yes |
| `harness/tools/scripts/stable/invoke-java-main.ps1` | 编译、构建 classpath、运行 Java main。 | yes |
| `harness/tools/scripts/stable/clean-sandbox.ps1` | 清理运行态日志和临时文件，默认 dry-run。 | yes，`-Apply` 需审批 |
| `harness/tools/scripts/stable/test-project-registry.ps1` | 只读校验本地项目 registry。 | yes |
| `harness/tools/scripts/stable/test-harness-governance.ps1` | 运行 Harness Root 治理自检。 | yes |
| `harness/tools/scripts/stable/bootstrap-harness-workspace.ps1` | 初始化或检查 Harness Workspace bootstrap 基础设施。 | yes |
| `harness/tools/scripts/stable/invoke-rag-candidate.ps1` | 通过稳定门面运行 RAG candidate 流程。 | yes |
| `harness/tools/scripts/stable/publish-harness-agent-branch.ps1` | 管理 agent-owned Git branch、提交和推送。 | yes，写操作需审批 |

## 2. 稳定工具契约

### `show-java-maven-config.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Agent`、`-Profile`、`-Config`、`-InspectSettingsMetadata`、`-CheckVersion`。 |
| Outputs | JSON 安全摘要；可选 Maven version 检查结果。 |
| Status Summary | profile、Java/Maven 路径是否存在、settings/local repo 是否存在。 |
| Redacted Log Path | 默认不写日志；调用方如需审计，应把 stdout 摘要写入 workflow evidence。 |
| Sensitive Handling | 默认不解析 settings XML，不输出 credential；`-InspectSettingsMetadata` 也只能输出安全 metadata。 |
| Failure Mode | `tool/config`、`tool/execution` 或 `environment/missing-dependency`。 |
| Repair Suggestion | 检查 profile ID、Java/Maven 路径或本地配置文件边界。 |
| Validation Instruction | 使用占位 profile 运行 dry summary；不得粘贴 settings 正文。 |

### `invoke-maven-project.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-ProjectRoot`、`-Agent`、`-Goals`、`-Module`、`-Profile`、`-Offline`、`-SkipTests`、`-Settings`、`-LocalRepo`、`-Maven`、`-Java`。 |
| Outputs | status summary、status JSON path、redacted log path。 |
| Status Summary | state、exitCode、profile、goals、module、projectRoot 摘要。 |
| Redacted Log Path | `var/logs/` 下的 Maven 执行日志路径；tracked docs 只记录路径。 |
| Sensitive Handling | settings path 只传给 Maven，不解析 XML，不打印 credential。 |
| Failure Mode | `tool/execution`、`environment/maven`、`input/project-root`、`project/build`、`project/test`。 |
| Repair Suggestion | 修正 ProjectRoot、profile、goals、LocalRepo，或按测试失败修复项目。 |
| Validation Instruction | 对 sandbox 项目运行 `test` 或 `test-compile`，检查 status JSON 与 log path 是否生成。 |

### `invoke-java-main.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-ProjectRoot`、`-MainClass`、`-Agent`、`-MavenGoals`、`-Module`、`-Profile`、`-ProgramArgs`、`-JvmArgs`、`-PassMarker`、`-ReactorClasspathModules`。 |
| Outputs | status summary、status JSON path、redacted log path、classpath runtime evidence。 |
| Status Summary | state、exitCode、mainClass、profile、module、passMarker 结果。 |
| Redacted Log Path | `var/logs/` 下的 Java/Maven 执行日志路径；tracked docs 只记录路径。 |
| Sensitive Handling | 不解析 settings XML；程序参数如含私有值不得写入 tracked docs。 |
| Failure Mode | `tool/execution`、`environment/java`、`input/main-class`、`project/build`、`project/runtime`。 |
| Repair Suggestion | 修正 MainClass、module、classpath modules、profile 或项目运行参数。 |
| Validation Instruction | 对 sandbox main class 运行并检查 pass marker、status JSON 与 log path。 |

### `clean-sandbox.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Root`、`-Apply`、`-KeepLatestPerLogFamily`、`-KeepTmp`。 |
| Outputs | cleanup candidate summary。 |
| Status Summary | 待清理文件数量、保留数量、dry-run 或 apply 模式。 |
| Redacted Log Path | 默认不写日志；清理结果可记录为摘要。 |
| Sensitive Handling | 不读取日志正文，只处理运行态文件路径。 |
| Failure Mode | `tool/execution`、`approval/missing`、`runtime/path-boundary`。 |
| Repair Suggestion | 默认先 dry-run；执行 `-Apply` 前必须有用户明确授权。 |
| Validation Instruction | 先运行 dry-run，确认候选路径都在 `var/` 边界内。 |

### `test-project-registry.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Root`、`-Registry`、`-SelfTest`。 |
| Outputs | JSON status summary、project count、error list、routed project summary。 |
| Status Summary | registry status、entry count、error count。 |
| Redacted Log Path | 默认不写日志；stdout JSON 可作为安全摘要。 |
| Sensitive Handling | 只读校验 registry shape 和项目根存在性，不读取 settings/auth 正文。 |
| Failure Mode | `registry/missing`、`registry/schema`、`project/root-missing`、`project/out-of-bound`。 |
| Repair Suggestion | 修正 registry JSON、projectId 重复项或项目路径边界。 |
| Validation Instruction | 运行 `-SelfTest`，再对本地 registry 执行只读检查。 |

### `test-harness-governance.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Root`、`-Registry`。 |
| Outputs | JSON status summary、severity counts、check list、findings 和 repair suggestions。 |
| Status Summary | status、findingCount、error/warning/info counts。 |
| Redacted Log Path | 默认不写日志；stdout JSON 可作为安全摘要。 |
| Sensitive Handling | 默认排除 `var/`、user-local、runtime、external、projects 等边界；不读取 credential 正文。 |
| Failure Mode | `governance/route`、`governance/boundary`、`governance/gitignore`、`registry/*`。 |
| Repair Suggestion | 根据 finding 的 `repairSuggestion` 更新索引、边界或 registry。 |
| Validation Instruction | 在 Harness Root 运行 dry-run 自检，确认 required routes、Verification/Observability 目标路由与 Git 边界。 |

### `bootstrap-harness-workspace.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Mode status|init`、`-Root`、`-RunSelfCheck`。 |
| Outputs | JSON status summary、required file check、ignored boundary check、可选 governance self-check。 |
| Status Summary | mode、missingRequiredFiles、actions、ignoredChecks、nextActions。 |
| Redacted Log Path | 默认不写日志；stdout JSON 可作为安全摘要。 |
| Sensitive Handling | 不读取 settings/auth 正文；`init` 只复制 example registry 到 ignored local registry，不覆盖已有文件。 |
| Failure Mode | `bootstrap/missing-route`、`bootstrap/gitignore-boundary`、`governance/self-check`。 |
| Repair Suggestion | 补齐缺失入口、修复 `.gitignore` 或运行治理自检定位 route/boundary 问题。 |
| Validation Instruction | 先运行 `-Mode status`，首次本机初始化再运行 `-Mode init`。 |

### `invoke-rag-candidate.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Command`、`-Root`、`-InputPath`、`-RunId`、`-Wiki`、`-Report`、`-Graph`、`-Question`、`-Manifest`。 |
| Outputs | stdout JSON、`var/rag/<run-id>/extracted/`、`user/knowledge/candidate/<run-id>/wiki`、`var/rag/<run-id>/evals/`、runtime graph、status JSON。 |
| Status Summary | command、runId、artifact paths、state。 |
| Redacted Log Path | `var/logs/<run-id>.json` 或对应 runtime path；tracked docs 只记录路径。 |
| Sensitive Handling | 只写 user-local candidate 和 runtime artifacts，不写 reviewed knowledge、Memory 或 Project Facts。 |
| Failure Mode | `rag/input`、`rag/pipeline`、`rag/lint`、`rag/query`、`tool/execution`。 |
| Repair Suggestion | 修正 input path、manifest、candidate wiki、graph 或 pipeline 配置。 |
| Validation Instruction | 使用非敏感样例运行 `health` 或 candidate ingest，确认只生成候选和运行态产物。 |

### `publish-harness-agent-branch.ps1`

| 契约项 | 内容 |
|---|---|
| Inputs | `-Mode`、`-Root`、`-RemoteUrl`、`-BaseBranch`、`-AgentBranch`、`-GitSshCommand`、`-CommitMessage`、`-SkipGovernanceCheck`、`-AllowNoChanges`。 |
| Outputs | JSON status summary、branch、head、staged file count、push heads。 |
| Status Summary | mode、branch、head、governance status、Git status lines。 |
| Redacted Log Path | 默认不写日志；Git 输出只作为摘要，不记录 credential。 |
| Sensitive Handling | 不保存 GitHub account、SSH config path 或 credential；写操作前扫描 staged sensitive content。 |
| Failure Mode | `git/base-branch-refused`、`git/governance-failed`、`git/no-changes`、`git/push`、`sensitive/staged-content`。 |
| Repair Suggestion | 切换 agent branch、修复治理 finding、移除敏感内容或补充 remote 参数。 |
| Validation Instruction | 先运行 `-Mode status`；提交前确认 governance self-check 通过。 |

## 3. 候选、历史、运行态和外部边界

| 资产 | 分类 | 默认暴露 | 说明 |
|---|---|---|---|
| `harness/tools/scripts/candidate/rag_candidate_ingest.py` | candidate | no | RAG candidate ingest 的候选实现；由 stable wrapper 调用或经 review 后晋升。 |
| `harness/tools/scripts/historical/run-java-smoke.ps1` | historical | no | 历史 smoke proof，不作为默认命令门面。 |
| `harness/tools/scripts/historical/run-real-java-smoke.ps1` | historical-restricted | no | 涉及真实本地参数的历史验证脚本，不默认暴露给 Agent。 |
| `harness/tools/scripts/runtime/audio_core.ps1` | runtime local-only | no | 本机 runtime helper，除 README 外不进入通用 Git。 |
| `harness/tools/scripts/runtime/hermes-update-codex.ps1` | runtime local-only | no | Hermes/Codex 辅助脚本，除 README 外不进入通用 Git。 |
| `harness/tools/scripts/runtime/Start-Hermes-Desktop.ps1` | runtime local-only | no | 桌面启动 helper，除 README 外不进入通用 Git。 |
| `harness/tools/scripts/runtime/hermes-wecom-generic-java-prompt.md` | runtime local-only | no | 运行态 prompt helper，默认不作为 Harness 文档入口。 |
| `harness/tools/external/` | external local-only | no | 外部工具和下载依赖，除 README 外不进入通用 Git。 |

## 4. 维护规则

1. 新 stable script 必须先补齐稳定工具契约。
2. candidate script 不能直接进入默认上下文。
3. runtime 和 external 资产默认 local-only，不提交正文。
4. historical script 只能作为背景或归档证据，不作为默认工具。
5. 工具文档以中文说明为主题，专业词、命令、路径和代码标识可以保留英文。
