---
documentName: harness/tools/scripts/candidate/README.md
version: v1.2.0-cleanup-candidate-promoted
updatedAt: 2026-10-28
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
reviewAfter: 2026-11-11
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/tools/ToolsIndex.md
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: cleanup-candidate-validated-and-promoted
---
# 候选脚本

`verify-artifact-cleanup.py`及测试已按用户授权晋升到stable，不在本目录保留活跃副本。
调用、限制和测试见[稳定工具契约](../../docs/command-surfaces/ArtifactCleanupTool.md)。

本目录保存 candidate tool scripts，中文解释是候选工具脚本。

候选脚本不是默认稳定工具。晋升为 stable tool 前必须补齐稳定工具契约，并通过 Governance Review 或用户明确批准。

候选脚本不得读取或输出 settings/auth 正文，不得把运行日志、私有路径或 token 写入 tracked docs。
