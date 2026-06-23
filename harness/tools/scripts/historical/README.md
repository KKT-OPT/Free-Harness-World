---
documentName: harness/tools/scripts/historical/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 定义历史脚本目录边界，说明历史脚本不作为默认稳定工具。
scope:
  - historical-tool-scripts
  - archive-boundary
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
outputTo:
  - harness/tools/scripts/historical/README.md
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
# 历史脚本

本目录保存 historical scripts，中文解释是历史脚本或保留脚本。

历史脚本可以作为迁移背景或故障复盘参考，但默认不进入 Agent stable command surface。使用历史脚本需要明确任务授权，并记录风险边界。
