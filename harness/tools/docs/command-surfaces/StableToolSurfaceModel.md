---
documentName: harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
version: v1.8.0-code-review-evidence-gate
updatedAt: 2026-07-02 00:00:00.000 +08:00
status: active
purpose: 定义 Harness 稳定工具门面的长期模型、调用规则、证据输出、安全边界和真实项目 code review workflow evidence 门禁入口。
scope:
  - stable-tool-surface
  - command-surface
  - tool-evidence
  - sensitive-boundary
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
  - harness/governance/security/CredentialBoundaryPolicy.md
outputTo:
  - harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/tools/ToolsIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-02
  decision: code-review-evidence-gate-added
---
# 稳定工具门面模型

本文定义 Agent 如何调用 Harness Stable Tool，中文解释是稳定工具。稳定工具是可复用、可验证、可记录证据的工具资产，不等同于一次性命令、临时脚本、runtime helper 或外部下载依赖。

## 1. 术语

| 术语 | 中文说明 |
|---|---|
| Tool Asset | 工具资产，包括稳定脚本、命令门面文档、manifest 和经审查的辅助资产。 |
| Command Surface | 命令门面，Agent 面向任务调用的稳定工具接口。 |
| Status Summary | 状态摘要，工具在 stdout 或结构化结果中给出的安全摘要。 |
| Status JSON | 状态 JSON，工具执行后写出的机器可读结果文件。 |
| Redacted Log Path | 脱敏日志路径，指向可审计日志位置，但不在 tracked docs 中粘贴日志正文。 |
| Failure Mode | 失败模式，用于区分工具执行、环境、输入、项目源码、测试和审批阻塞。 |
| Repair Suggestion | 修复建议，用于说明下一次 rerun 或人工处理动作。 |

## 2. 工具分类

| 分类 | 路径 | 默认暴露 | 说明 |
|---|---|---|---|
| stable | `harness/tools/scripts/stable/` | yes | 默认可被 Agent 调用的稳定工具。 |
| candidate | `harness/tools/scripts/candidate/` | no | 候选工具，必须 review 后才能晋升。 |
| runtime | `harness/tools/scripts/runtime/` | no | 本机 runtime helper，默认 local-only。 |
| historical | `harness/tools/scripts/historical/` | no | 历史脚本，只作为背景或回溯证据。 |
| external | `harness/tools/external/` | no | 外部工具、下载依赖或第三方仓库，本机 local-only。 |

## 3. 稳定工具契约

每个 stable tool 必须在 `harness/tools/docs/script-index/ScriptIndex.md` 或专门 command surface 中记录：

- inputs；
- outputs；
- status summary；
- status JSON path；
- redacted log path；
- sensitive handling；
- failure mode；
- repair suggestion；
- validation instruction。

缺少上述契约的脚本不得作为默认 stable tool 使用。

## 4. 默认调用规则

Agent 应优先使用稳定命令门面：

```text
show-java-maven-config
invoke-maven-project
invoke-java-main
invoke-rag-candidate
invoke-rag-knowledge
clean-sandbox
test-project-registry
test-project-lifecycle-evidence
test-code-review-workflow-evidence
test-harness-governance
publish-harness-agent-branch
```

Agent 不应：

- 手动拼接复杂 Maven classpath；
- 手动拼接 RAG ingestion 的 Python venv、PYTHONPATH 或 Unicode 环境变量；
- 手工串联 raw -> candidate -> reviewed vault -> query 的 RAG smoke；应使用 `invoke-rag-knowledge pipeline-smoke`，并显式传入 reviewer、approval note、raw input 和 query；
- 手工判断真实项目 code review workflow evidence 是否闭环；应使用 `test-code-review-workflow-evidence` 按阶段检查结构、用户审核、修复交接、复查和最终审核状态；
- 手动扫描 reviewed wikilinks 后直接创建 reviewed Knowledge；应使用 `invoke-rag-knowledge reviewed-gap-plan`、`enrich-gap-candidates` 和 `gap-review-package` 形成 candidate-only gap workflow，并在用户明确批准后用 `promote-gap-candidates` 晋升 approved concepts；
- 手动整理 `user/knowledge/candidate/` 后要求用户逐个审核；应先使用 `invoke-rag-knowledge govern-vault -ArchiveInactiveCandidates` 生成 `Home.md` 单入口、active review queue 和 archive summary；
- 直接读取 settings/auth 正文；
- 把 historical script 当作默认稳定工具；
- 把临时命令或一次性脚本加入稳定索引；
- 隐藏 status JSON、redacted log path、failure mode 或 repair suggestion。

## 5. 标准证据输出

稳定工具输出应让 Agent 能记录以下字段：

| 字段 | 中文说明 |
|---|---|
| `state` | `passed`、`failed`、`partial` 或 `blocked`。 |
| `exitCode` | 命令退出码。 |
| `agent` | 调用方，例如 `codex`、`hermes` 或 `shared`。 |
| `profile` | 可公开记录的 profile ID 或运行配置标识。 |
| `projectRoot` | 项目根路径；tracked docs 中应使用占位符或安全摘要。 |
| `statusJson` | status JSON path。 |
| `log` | redacted log path。 |
| `failureMode` | 工具、环境、输入、项目源码、测试或审批阻塞。 |
| `repairSuggestion` | 下一步修复或 rerun 建议。 |

tracked docs 可以记录路径和安全摘要，不粘贴 status JSON 正文或 raw log。

## 6. 敏感信息规则

稳定工具不得打印 settings/auth 正文、server 用户名、password、token、credential helper 状态或完整 XML。

允许记录：

- profile ID；
- 是否存在某个 settings path 的布尔摘要；
- Harness runtime 路径，例如 `var/logs/<run-id>.log`、`var/m2/<run-id>`；
- 不含私有值的 failure mode 和 repair suggestion。

不得记录：

- 私有 settings 绝对路径；
- 私有 Maven repository 路径；
- 私有仓库 URL；
- raw log；
- status JSON 正文；
- credential、token、password 或 auth 文件内容。

## 7. 晋升规则

候选脚本晋升为 stable tool 前必须满足：

1. 有明确 command surface 或 ScriptIndex 条目；
2. 有输入、输出、证据、失败模式和修复建议；
3. 不读取或输出敏感正文；
4. 能在 Harness Root 中以相对路径或占位符方式调用；
5. 经过 review 或用户明确批准。
