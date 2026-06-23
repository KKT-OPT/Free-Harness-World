---
documentName: harness/tools/manifests/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 定义工具 manifest 目录边界，用于保存工具输入输出契约和非私有示例。
scope:
  - tool-manifest
  - input-output-contract
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
outputTo:
  - harness/tools/manifests/README.md
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
# 工具 Manifest

本目录用于保存 Tool Manifest，中文解释是工具清单或工具契约。Manifest 可描述工具的输入、输出、状态摘要、脱敏日志路径、失败模式和修复建议。

Manifest 不得包含：

- 真实本机绝对路径；
- 私有 settings/auth 正文；
- token、password、credential；
- 未脱敏日志；
- 真实私有仓库 URL。

当前稳定工具契约集中维护在：

```text
harness/tools/docs/script-index/ScriptIndex.md
```
