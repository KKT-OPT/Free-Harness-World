---
documentName: harness/tools/scripts/runtime/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 定义运行态脚本和本地 helper 的 local-only 边界。
scope:
  - runtime-tool-scripts
  - local-only
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/scripts/stable/README.md
outputTo:
  - harness/tools/scripts/runtime/README.md
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
# 运行态脚本

本目录保存 runtime helper，中文解释是运行态辅助脚本，和临时生成脚本。

除本 README 外，本目录默认 local-only，并由 `.gitignore` 忽略。

规则：

1. 不把 runtime helper 当作默认 stable tool。
2. 不提交运行态脚本、私有路径、auth 文件、settings 正文或原始日志。
3. 需要晋升的脚本先进入 `harness/tools/scripts/candidate/`，补齐契约并审查。
