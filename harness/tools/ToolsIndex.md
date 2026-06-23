---
documentName: harness/tools/ToolsIndex.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 路由 Harness 工具资产层，定义 stable、candidate、runtime、historical、external 的分类边界和稳定工具契约入口。
scope:
  - tool-assets
  - stable-tool-contract
  - command-surface
  - tool-boundary
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/HarnessIndex.md
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/tools/ToolsIndex.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: h5-complete
---
# 工具资产索引

`harness/tools/` 是 Harness 的 Tool Asset，中文解释是工具资产，目标层。

工具资产包括稳定脚本、命令门面文档、manifest、候选脚本、历史脚本、runtime helper 和本地 external tool 边界。顶层 `tools/` 不再作为工具资产入口。

## 1. 分区

| 分区 | 路径 | Git 边界 | 默认上下文 |
|---|---|---|---|
| 工具文档 | `harness/tools/docs/` | tracked | yes |
| 工具 manifest | `harness/tools/manifests/` | tracked | yes |
| 稳定脚本 | `harness/tools/scripts/stable/` | tracked | yes |
| 候选脚本 | `harness/tools/scripts/candidate/` | tracked after review | no |
| 运行态脚本 | `harness/tools/scripts/runtime/` | local-only，除 README 外忽略 | no |
| 历史脚本 | `harness/tools/scripts/historical/` | tracked | no |
| 外部工具 | `harness/tools/external/` | local-only，除 README 外忽略 | no |

## 2. 稳定工具契约

稳定工具必须在 `harness/tools/docs/script-index/ScriptIndex.md` 或对应 command surface 中记录：

- inputs，中文解释是输入；
- outputs，中文解释是输出；
- status summary，中文解释是状态摘要；
- redacted log path，中文解释是脱敏日志路径；
- sensitive handling，中文解释是敏感信息处理；
- failure mode，中文解释是失败模式；
- repair suggestion，中文解释是修复建议；
- validation instruction，中文解释是验证方式。

## 3. 默认稳定工具

默认可被 Agent 优先调用的稳定工具位于：

```text
harness/tools/scripts/stable/
```

当前稳定命令门面由以下文档维护：

```text
harness/tools/docs/script-index/ScriptIndex.md
harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
harness/tools/docs/command-surfaces/JavaMavenCommandCookbook.md
```

H8 新增 bootstrap 稳定脚本：

```text
harness/tools/scripts/stable/bootstrap-harness-workspace.ps1
```

## 4. 禁止事项

1. 不要把 runtime helper 或一次性脚本作为默认 stable tool。
2. 不要把 external tool、二进制、下载依赖或第三方仓库提交进通用 Harness Git。
3. 不要读取、打印或写入 settings/auth 正文。
4. 不要在工具文档中写入真实私有路径、真实仓库 URL、token、password 或未脱敏日志。
5. 不要在旧顶层 `tools/` 下新增工具资产。
