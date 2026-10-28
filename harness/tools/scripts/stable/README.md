---
documentName: harness/tools/scripts/stable/README.md
version: v1.4.0-artifact-cleanup-stable
updatedAt: 2026-10-28
status: active
purpose: 定义稳定脚本目录边界、默认调用规则和 Java 源码只读发现/分类门禁边界。
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
reviewAfter: 2026-11-11
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/tools/ToolsIndex.md
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: evidence-gate-fixes-validated-cleanup-tool-promoted
---
# 稳定脚本

两份workflow/lifecycle证据门禁已补充中文章节和显式UTF-8读取，保留英文契约和机器状态。
结构门禁通过不等于人审或内容正确。新增verify-artifact-cleanup.py已获条件批准并通过测试后晋升，
无自动删除功能；所有新测试统一由`python -B -m unittest discover -s harness/tools/scripts/stable/tests -v`运行。

本目录保存已评审的 stable tool scripts，中文解释是稳定工具脚本。Agent 在有稳定脚本可用时应优先调用本目录脚本，而不是临时拼接命令。

稳定脚本必须满足：

1. 文档化 inputs 和 outputs；
2. 输出 status summary 或等价状态摘要；
3. 输出 redacted log path 或说明无需日志；
4. 明确 sensitive handling；
5. 明确 failure mode；
6. 提供 repair suggestion；
7. 提供 validation instruction。

Java 源码门禁规则：

1. `test-java-javadoc-coverage.ps1` 检查注释结构覆盖，不生成或覆盖业务注释；
2. `test-java-magic-values.ps1` 只生成数值字面量候选，默认 report-only；
3. 数值候选必须由智能体结合项目配置、量纲、公式和测试意图人工分类；稳定分类可写入 `java-magic-value-classification-v1` JSON，并通过 `-ClassificationFile` 加载；
4. 需要关闭未分类缺口时使用 `-FailOnUnclassified`，不得用 `-FailOnFindings` 把已解释候选误判为缺陷；
5. 稳定脚本不得机械提取常量、替换源码或把候选数直接解释为缺陷数。

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
