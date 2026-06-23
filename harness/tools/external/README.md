---
documentName: harness/tools/external/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 定义外部工具、运行时、二进制和大依赖的 local-only 边界。
scope:
  - external-tool-assets
  - local-only
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/manifests/README.md
outputTo:
  - harness/tools/external/README.md
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
# 外部工具

本目录保存 external tools，中文解释是外部工具、本地运行时、下载依赖、二进制或大文件。

除本 README 外，本目录默认 local-only，并由 `.gitignore` 忽略。

规则：

1. 不把下载工具、第三方仓库、二进制依赖或外部 runtime 提交通用 Harness Git。
2. 可在 `harness/tools/manifests/` 或 `harness/tools/docs/` 中记录非私有的安装说明和版本约束。
3. 不记录真实私有仓库 URL、auth 文件、token、settings 正文或本机私有路径。
