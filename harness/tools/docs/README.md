---
documentName: harness/tools/docs/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 路由工具说明、命令门面和脚本索引文档。
scope:
  - tool-docs
  - command-surface
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
outputTo:
  - harness/tools/docs/README.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/tools/ToolsIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: h5-complete
---
# 工具文档

本目录保存稳定工具说明、Command Surface，中文解释是命令门面，以及脚本索引。

## 当前文档

| 文档 | 作用 |
|---|---|
| `script-index/ScriptIndex.md` | 按 stable、candidate、runtime、historical 分类索引脚本，并记录稳定工具契约。 |
| `command-surfaces/StableToolSurfaceModel.md` | 说明稳定工具表面、调用规则、证据输出和敏感边界。 |
| `command-surfaces/JavaMavenCommandSurface.md` | 说明 Java/Maven 工具命令门面。 |
| `command-surfaces/JavaMavenCommandCookbook.md` | 提供可复用命令示例，使用占位符，不写真实项目事实。 |

工具文档应以中文说明为主，允许保留命令、参数、路径和专业词英文。
