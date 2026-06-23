---
documentName: harness/tools/scripts/stable/README.md
version: v1.0.0-h5-tool-layer
updatedAt: 2026-06-18 14:30:00.000 +08:00
status: active
purpose: 定义稳定脚本目录边界和默认调用规则。
scope:
  - stable-tool-scripts
  - default-command-surface
prerequisites:
  - AGENTS.md
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/tools/docs/command-surfaces/StableToolSurfaceModel.md
outputTo:
  - harness/tools/scripts/stable/README.md
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
# 稳定脚本

本目录保存已评审的 stable tool scripts，中文解释是稳定工具脚本。Agent 在有稳定脚本可用时应优先调用本目录脚本，而不是临时拼接命令。

稳定脚本必须满足：

1. 文档化 inputs 和 outputs；
2. 输出 status summary 或等价状态摘要；
3. 输出 redacted log path 或说明无需日志；
4. 明确 sensitive handling；
5. 明确 failure mode；
6. 提供 repair suggestion；
7. 提供 validation instruction。

具体契约见：

```text
harness/tools/docs/script-index/ScriptIndex.md
```

H8 bootstrap 初始化命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode status
powershell -NoProfile -ExecutionPolicy Bypass -File harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode install
powershell -NoProfile -ExecutionPolicy Bypass -File harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode uninstall
```

`-Mode install` 只创建缺失的本地 registry 和运行态目录，不覆盖已有本地文件，不写入凭据。`-Mode uninstall` 只删除 install 生成的本地 registry 文件和空的运行态目录。
