---
documentName: harness/tools/docs/command-surfaces/RagDocumentPipeline.md
version: v1.3.0-evaluation-boundary
updatedAt: 2026-10-29
status: active
purpose: 定义现有 RAG 命令下的逐页 PDF、来源绑定摄取、精确内容批量晋升和只读语料核验契约。
scope:
  - rag-tools
  - reviewed-promotion
  - corpus-audit
prerequisites:
  - harness/tools/ToolsIndex.md
relatedDocuments:
  - harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
  - harness/rag/pipelines/PdfNormalizationContract.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/governance/KnowledgePromotionPolicy.md
outputTo:
  - harness/tools/docs/command-surfaces/RagDocumentPipeline.md
owner: mixed
reviewAfter: '2026-11-29'
supersededBy: null
dependsOn:
  - harness/tools/scripts/stable/invoke-rag-candidate.ps1
  - harness/tools/scripts/stable/invoke-rag-knowledge.ps1
review:
  reviewedBy: user
  reviewedAt: '2026-10-29'
  decision: user-approved-rag-assets-and-evaluation-boundary-with-implementation-regression
---

# RAG 文档工具契约

## 统一入口

现有 `invoke-rag-candidate.ps1` 与 `invoke-rag-knowledge.ps1` 继续作为默认入口。通用转换、核验和晋升放入其模块，避免每批重写转换脚本、拆分来源清单、循环启动晋升后再覆盖正文。

两个 Python CLI 对成功和运行失败都输出一个 JSON 对象。失败仍返回非零退出码；已产生的 `blockingIssues` 保留在同一对象中，调用方不再需要截取“第一个 JSON”。参数解析错误仍由命令行解析器报告。

## PDF 与摄取

```powershell
& harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command normalize-pdf `
  -InputPath 'user/knowledge/raw/<domain>/<source>.pdf' `
  -NormalizedDir 'user/knowledge/raw/<domain>/normalized' -RunId '<run-id>' `
  -OcrMode auto -OcrLanguage auto

& harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command ingest `
  -NormalizationManifest 'var/rag/<run-id>/normalization-manifest.json' -RunId '<candidate-run-id>'
```

清单传递原 PDF、哈希、normalized 路由和质量标记。工具验证清单与实际文件，不把转换稿重新当作没有原始来源的独立材料，也不需要手工改 manifest。`CopyRaw` 不与该清单方式混用。

普通 `ingest -InputPath` 仍可使用。目录扫描跳过下级生成的 `normalized`、`assets` 和归档目录；显式指定 normalized 目录仍可读取其中 Markdown。分部分编号和来源指纹不再被点号截断。同名原件冲突时使用路径指纹隔离，避免相互覆盖。

## 审核与精确内容晋升

候选补全仍由 agent 按原件完成。工具不从文件名猜测知识结论，也不把固定论文摘要填入其他资料。

单来源可采用通用候选模板，或提供位于 candidate 边界内的完整 `ReviewedDraft`。多来源使用 `PromotionMap`；不再隐式晋升清单第一项。

```json
{
  "items": [
    {
      "sourceId": "<manifest-source-id>",
      "draft": "user/knowledge/candidate/<run-id>/drafts/<semantic-name>.md",
      "target": "user/knowledge/reviewed/<domain>/<semantic-name>.md"
    }
  ]
}
```

```powershell
& harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command review-package `
  -Manifest 'var/rag/<run-id>/extracted/metadata-manifest.json' `
  -Wiki 'user/knowledge/candidate/<run-id>/wiki' -PromotionMap '<local-map.json>'

& harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command promote-reviewed `
  -Manifest 'var/rag/<run-id>/extracted/metadata-manifest.json' `
  -Wiki 'user/knowledge/candidate/<run-id>/wiki' -PromotionMap '<local-map.json>' `
  -Reviewer '<reviewer>' -ApprovalNote '<explicit-authorization>' -ReviewAfter '<staleness-rule>'
```

- `review-package` 重新执行候选 health/lint/graph，检查实际章节、来源一致性与哈希，并绑定原件、转换稿、清单、候选及完整草稿的快照。
- `promote-reviewed` 在写入前核对同一快照、明确授权、目标边界、全部来源对应关系和草稿 sourceRefs。多源 map 必须完整覆盖所选清单；需要子集时先明确形成独立作用域的清单。
- 同批所有目标先预检。已有不同内容须显式 `Overwrite`；相同内容可重复执行且记为未更新。
- 草稿通过后按原字节写入，记录最终内容 SHA-256、源文件 SHA-256、审核人、授权说明、时间与事务结果。不得在命令成功后直接覆盖正文而沿用旧晋升记录。
- 原件、候选或草稿变化后必须重新生成审核包。无需重新批准已授权范围内的例行修订，但证据必须对应本次实际内容。
- 单文件替换使用临时文件和 `os.replace`；批量是全量预检与失败回滚，不等同于数据库事务。备份和恢复记录位于 `var/rag/<run-id>/promotions/<transaction-id>/`；恢复时保留第三方并发修改并明确记录未恢复项。

## 可独立查询的知识正文

来源页的章节表仅供导航，不能作为正文覆盖的验收依据。PDF 来源晋升要求 `contentCoverage` 与来源对齐的逐页文本；检查规范化稿哈希、页数、正文封印及提取方法。`ingest` 保留页级契约，不能在摄取后丢弃 `pageCount` 和 `pages`。

对于已有来源页，使用以下候选准备命令。它保留来源页的综合说明并补充可检索正文，输出完整 PromotionMap，仍需内容审核、review-package 与明确授权后的 promote-reviewed。

```powershell
& harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command prepare-reviewed-content `
  -Manifest 'var/rag/<run-id>/extracted/metadata-manifest.json' `
  -Reviewed 'user/knowledge/reviewed/<domain>' -RunId '<new-run-id>' -Reviewer '<reviewer>' `
  -ContentProfile '<local-source-bound-profile.json>'
```

`ContentProfile` 可省略。需要单独校录条款或维护版本事实时，配置 `sources` 列表，每项绑定 `sourceHashSha256` 和 `normalizedHashSha256`；`sections` 每项包含 `heading`、`text`、`physicalPages`、`reviewedBy` 和 `evidence`。`verification` 可区分原页校录与官方状态核验。`sourceVersion` 可记录标准标识、发布日期、实施日期、核验状态、核验日期、官方证据与适用事项。真实条款、来源清单及配置只留在用户边界。

完整文本覆盖属于转换与来源一致性检查，不能证明全部数值、公式和图示已经语义审核；各页保留校核级别。已核验的条款应在 reviewed 内表达完整条件与结论，不要求日常问答再次回查原件。尚未可靠转写的内容作为知识缺口进入候选补强。

`query-reviewed -Question '<question>' -AsOf 'YYYY-MM-DD'` 按实际命中的条款排序并返回 reviewed 内的正文、行号及版本上下文；不再按整页词频优先返回前几个章节。`AsOf` 默认当前日期，不使用 `reviewedAt` 代替标准实施日。尚未实施或尚未发布分别标记；已到实施日但缺最新官方核验时，不自动宣称现行。先确认同一事项、适用范围和替代关系，再比较时间；不同分类轴不自动覆盖。

查询验收同时检查正确来源、完整答案、边界符号和仅依赖 reviewed 的读取边界；命令成功与命中文档不能单独证明答案可用。

## 完整流程验证

`pipeline-smoke` 继续串联摄取、候选检查、晋升、领域入口、图谱和查询，但必须提供显式 `ReviewedDraft`。草稿来源需与本次输入对应；本命令不再按关键词自动补写论文知识或自动晋升一组预设概念。概念页按独立的 gap review 流程处理。

`Overwrite` 只授权受控替换 reviewed 目标，不删除旧候选和运行证据；重新运行选择新的 `RunId`。已存在的领域 index 保留原有内容，只补缺失来源链接。

## 本批与全库核验

```powershell
& harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command audit-corpus `
  -Manifest '<normalization-or-corpus-manifest.json>' `
  -Reviewed 'user/knowledge/reviewed/<domain>' `
  -PromotionRecord 'var/rag/<run-id>/promotions/<transaction-id>/result.json' `
  -RequireSealed -Report 'var/rag/<audit-run-id>/corpus-audit.json'
```

不传 `PromotionRecord` 时，旧知识页可检查来源、页数和链接，但会报告 `reviewed-content-unsealed`；不能因此声称历史晋升已验证最终正文。`RequireSealed` 将此问题设为阻断项。

对于已有转换稿，`ExportManifest` 可以在实际核验后导出运行态来源清单，记录为 `adopted-existing-normalized-no-regeneration`。失败来源仍标为不可摄取，不通过“导出”掩盖原问题。

全库仍运行 `validate-knowledge-vault`；本批核验不能替代全库检查，也不能通过临时过滤目录来制造全库通过。全库新增 normalized 质量项，保留未注册目录、来源问题和转换问题的真实失败。

## 归档与入口

`govern-vault -ArchiveInactiveCandidates` 直接按 source-centered 结构归档，更新活跃 manifest 的路径，保留不可变晋升记录，并使已归档审核快照失效。候选完整语料的删除或移出 vault 仍走 cleanup-plan 与既有批准边界。

Home 中不逐张列出 `normalized/assets/` 的生成图片；原始图片资料及 normalized 文档仍保留入口。

## 验证与失败修复

- 回归入口：`test-rag-tools.ps1 -Root <HARNESS_ROOT>`。依赖 PyMuPDF、PyYAML；优先使用已有 RAG venv。Windows OCR 还需要系统语言包。
- OCR 缺失：先保留原图与待处理清单，安装所需语言包或选择兼容转换环境，再重新转换。
- 校正前提不符：回到原页检查配置，不扩大正则或猜测数值。
- OCR 丢失表格关系或关键符号：按原图校录完整页面，使用 profile 的 `pageOverrides` 绑定原件、物理页、机器文本哈希和审核证据；通过同一 normalize-pdf 入口重建，原图继续保留。
- 快照变化：更新候选与草稿后重新执行 review-package。
- 内容哈希不符：定位未记录的覆盖，恢复已审核版本或以新审核包和明确授权重新晋升。
- 结构通过而语义未核对：保留 `semanticState` 与待核页码，不声明逐字正确。

## 查询模式与评测记录

```powershell
& harness/tools/scripts/stable/invoke-rag-knowledge.ps1 -Command query-reviewed `
  -Question '<question>' -Mode knowledge-only -SourcePrefix '<identifier-family>' -AsOf 'YYYY-MM-DD'

& harness/tools/scripts/stable/invoke-rag-knowledge.ps1 -Command audit-query-evaluation `
  -EvaluationRecord 'var/rag/<run-id>/evaluation-record.json' -RunId '<run-id>'
```

`Mode` 为 `knowledge-only`（默认）或 `mixed`。命令本身始终只读取 reviewed；模式明确Agent后续工具来源约束，不会自动禁用其他工具。纯库测试不允许额外网页元数据核验；正式混合使用分别标明来源。`sourceBoundary.coverage` 明确只有命令范围，不是整轮无外部访问证明。

`SourcePrefix` 限定库内来源标识的ASCII系列前缀及斜线子系列。先采用sourceVersion.standardId或sourceIdentifier，再读取来源页标题标识；不会用正文引用误判该页类型，也不按年份推断效力。Agent负责从用户意图设置范围。逻辑条款跨物理页保持连续，返回sourcePages和准确行号，混合校核级别不会自动升级成全已校录。

审计输入包含mode、question、reviewer、assessment（passed/failed/incomplete）、trace和evidence。trace包括scope=whole-turn、complete、capturedBy（runtime-export或reviewer-audited）及events。事件kind可为knowledge-query、reviewed-read、guidance-read、evidence-write、local-check，或外部的web-search、web-open、external-status-check、raw-read、image-read；未分类事件使记录不完整。本地执行中发生的网络访问仍按外部事件记录。

evidence以id引用；reviewed证据包含path、sha256、startLine、endLine，并要求authoritative来源页。正式mixed的网页证据包含kind=web与url；工具不会打开URL。inferences可记录statement与premiseEvidenceIds，不据此证明推理正确。示例及模板见 [评测入口](../../../rag/evals/README.md)。

输出JSON保留mode、knowledgeOnlyAcceptance、externalEvents、blockingIssues、incompleteEvidence、coverageAssurance、semanticAssurance及输入记录哈希。来源越界为invalid，日志或来源证据不足为inconclusive；混合使用为mixed-usage-recorded，不计入纯库验收。失败返回非零退出码，详细原状态保留在运行态report中。此命令仅验证提交的记录，不能证明遗漏事件不存在，也不替代运行时禁网或审核人核对完整工具活动。
