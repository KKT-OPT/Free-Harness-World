---
documentName: harness/tools/ToolsIndex.md
version: v1.18.0-java-javadoc-coverage-gate
updatedAt: 2026-07-06 22:15:00.000 +08:00
status: active
purpose: 路由 Harness 工具资产层，定义 stable、candidate、runtime、historical、external 的分类边界、稳定工具契约入口、项目生命周期证据门禁、code review workflow evidence 门禁、Java Javadoc 覆盖门禁、Memory 流程状态、只读验证门禁、受控候选删除命令和治理自检集成。
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
  - harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1
  - harness/tools/scripts/stable/test-java-javadoc-coverage.ps1
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
  reviewedAt: 2026-07-06
  decision: java-javadoc-coverage-gate-added
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

Workspace bootstrap 稳定脚本：

```text
harness/tools/scripts/stable/bootstrap-harness-workspace.ps1
```

真实项目生命周期证据门禁脚本：

```text
harness/tools/scripts/stable/test-project-lifecycle-evidence.ps1
```

该脚本用于在真实项目任务收口前，只读检查项目 workflow evidence 和项目 report 是否覆盖 Task Brief、项目入口、设计或执行计划、开发变更、验证、用户验收、治理候选、项目 report 落点和 non-promotion 边界。它是通用 Harness 机制，不保存任何具体项目资产。

Code Review workflow evidence 门禁脚本：

```text
harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1
```

该脚本用于只读检查真实项目代码审查 workflow evidence 是否覆盖 Task Brief、审查范围、trace、findings、用户审核、修复交接、复查、最终审核和闭环状态字段。默认模式检查结构完整性；`-RequireUserReview`、`-RequireFixDisposition`、`-RequireRecheck`、`-RequireFinalReview` 和 `-RequireClosedLoop` 用于按阶段强制提高门禁要求。通用治理自检脚本 `test-harness-governance.ps1` 必须调用该脚本的 `-SelfTest`，确保 code review workflow 不是只靠文档约束。

Java Javadoc 覆盖门禁脚本：

```text
harness/tools/scripts/stable/test-java-javadoc-coverage.ps1
```

该脚本用于只读检查 Java 文件、目录或包的类级 Javadoc、作者、since、version、必需类级章节、最少类级说明长度、public/protected 或全部显式声明方法 Javadoc、`@param`、`@return` 和 Javadoc 空白星号行。真实项目的 Java 包级代码审查如果把注释完整性作为验收标准，必须在 workflow evidence 中记录该脚本的命令和 JSON 摘要。通用治理自检脚本 `test-harness-governance.ps1` 必须调用该脚本的 `-SelfTest`，确保 Java 注释覆盖不是只靠自然语言约束。

Reviewed Knowledge access 稳定脚本：

```text
harness/tools/scripts/stable/invoke-rag-knowledge.ps1
```

该脚本用于初始化 `user/knowledge/` Obsidian vault 入口、同步 reviewed Knowledge 索引、构建 reviewed graph、执行 reviewed-only query、health check，把 unresolved reviewed wikilinks 转为 candidate-only gap plan，处置 residual workflow gap，执行 source-centered canonical vault layout，运行 one-click validation gate，生成 task-scoped schema context，验证 LLM Wiki 已吸收机制，生成 post-promotion candidate cleanup dry-run plan，执行显式批准后的 candidate cleanup apply，用 reviewed evidence 补强 gap candidate pages，生成供人类审核的 gap review package，并在审核前治理 vault 入口、候选审核队列和历史证据索引。它不得把 raw、candidate、chunks 或 runtime graph 当作 authoritative knowledge；`reviewed-gap-plan -WriteCandidates`、`dispose-residual-gaps`、`canonicalize-vault-layout`、`validate-knowledge-vault`、`schema-context`、`validate-llm-wiki-mechanisms`、`candidate-cleanup-plan`、`enrich-gap-candidates`、`gap-review-package` 和 `govern-vault` 只能写入 candidate wiki、vault navigation、机制引用处置、local-only 目录治理、schema context 摘要或 runtime review/governance package，不能绕过 review 写入 reviewed Knowledge；`schema-context` 不写 knowledge page，`validate-llm-wiki-mechanisms` 不执行后台自动修复或 reviewed promotion；`candidate-cleanup-plan` 不删除、不移动、不改写 reviewed source trace；`candidate-cleanup-apply` 只有在 reviewer 和 approval note 齐备时才移动 post-promotion full candidate corpus、写入轻量审计记录并改写 source trace，且不执行 reviewed promotion。

Memory validation gate 稳定脚本：

```text
harness/tools/scripts/stable/invoke-memory.ps1
```

该脚本当前提供 Memory 流程状态、只读 Memory 门禁、候选审核包和受控生命周期命令：`memory-flow-status` 对照架构权威 Memory Update Flow 输出节点覆盖、已有命令和停止规则；`verify-source-evidence`、`detect-from-workflow`、`classify-candidate-suitability`、`record-no-memory-disposition`、`create-candidate`、`classify-memory-type`、`detect-memory-duplicate-conflict`、`reject-or-merge-candidate`、`conflict-review-package`、`candidate-review-package`、`apply-review-decision`、`promote-reviewed`、`archive-candidate`、`delete-candidate`、`revise-candidate`、`sync-memory-index` 和 `validate-memory-store` 覆盖 Memory Update Flow 的 A-Q 节点。默认命令为 dry-run 或 report-only；写入 candidate、reviewed、archive、删除 candidate 或 candidate 修订必须显式传入 `-Apply`，并提供 reviewer、approval note 和 reason。普通 reject 默认走 `archive-candidate`；只有用户明确要求删除时才走 `delete-candidate`。所有运行态输出进入 `var/memory/` report / status JSON。通用治理自检脚本 `test-harness-governance.ps1` 必须调用 `validate-memory-store` 和 `validate-memory-store -SelfTest`；任一失败应作为 governance finding 输出并使自检失败。

## 4. 禁止事项

1. 不要把 runtime helper 或一次性脚本作为默认 stable tool。
2. 不要把 external tool、二进制、下载依赖或第三方仓库提交进通用 Harness Git。
3. 不要读取、打印或写入 settings/auth 正文。
4. 不要在工具文档中写入真实私有路径、真实仓库 URL、token、password 或未脱敏日志。
5. 不要在旧顶层 `tools/` 下新增工具资产。
