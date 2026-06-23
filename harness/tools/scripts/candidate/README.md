---
documentName: harness/tools/scripts/candidate/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 定义候选脚本目录边界和晋升规则。
scope:
  - candidate-tool-scripts
  - tool-promotion
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/scripts/stable/README.md
  - harness/governance/GovernanceIndex.md
outputTo:
  - harness/tools/scripts/candidate/README.md
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
# 候选脚本

本目录保存 candidate tool scripts，中文解释是候选工具脚本。

候选脚本不是默认稳定工具。晋升为 stable tool 前必须补齐稳定工具契约，并通过 Governance Review 或用户明确批准。

候选脚本不得读取或输出 settings/auth 正文，不得把运行日志、私有路径或 token 写入 tracked docs。
