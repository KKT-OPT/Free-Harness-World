---
documentName: harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
version: v1.0.0
updatedAt: 2026-10-29
status: active
purpose: 定义知识库测试、正式混合查询与知识补强的来源边界和验收证据。
scope: [rag-query, knowledge-evaluation, source-boundary]
prerequisites: [AGENTS.md, harness/governance/KnowledgePromotionPolicy.md]
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/rag/evals/README.md
  - harness/tools/docs/command-surfaces/RagDocumentPipeline.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
outputTo: [harness/rag/policies/KnowledgeQueryEvaluationPolicy.md]
owner: mixed
reviewAfter: 2026-11-29
supersededBy: null
dependsOn: [harness/tools/scripts/stable/rag_knowledge/evaluation.py]
review:
  reviewedBy: user
  reviewedAt: 2026-10-29
  decision: user-approved-source-boundary-and-rag-asset-consolidation
---
# 知识查询与评测来源边界

## 模式与范围

| 模式 | 可使用的答题证据 | 输出与验收 |
|---|---|---|
| 纯知识库测试 `knowledge-only` | 已审核 reviewed 正文及其库内元数据；允许基于这些证据比较、归纳和推理 | 缺少内容或证据时报告知识缺口，不能外查补齐；只有符合整轮来源边界的结果才能计入纯库验收 |
| 正式混合使用 `mixed` | reviewed 知识及任务允许的网页等外部资料 | 分别归属来源，保留核验时间与不确定性；不能记为纯知识库测试通过 |
| 摄取与补强 | 原件、规范化稿、图像或外部记录 | 进入 candidate、审核与晋升；不是同一轮冻结基线上的查询成功 |

用户要求“测试、验证知识库查询”时默认使用纯库模式。正式使用可以按任务需要结合网页；两种模式不应相互套用。`query-reviewed` 默认 `knowledge-only`，`mixed` 只声明正式使用的来源契约，该命令本身仍只检索 reviewed，不执行网页访问。

工具文档、任务入口和可重建索引可以辅助执行；它们不能作为答题事实。Source Trace 中的网页链接可以按库内记录列出，测试时不能打开该链接补证。已在测试前审核晋升的网页来源记录可作为 reviewed 证据，但只能陈述其记录范围与核验时间。

## 时间、效力与推理

“最新优先”在纯库测试中只使用库内证据，不构成实时联网核验的授权。发布日期、实施日期、核验时间、知识维护时间和文档状态分开；`status: active` 不代表标准现行。缺少可靠的现行状态、替代关系或时间条件时，保留未知或冲突，不凭模型记忆补齐。

先确认同一事项、分类轴、适用对象及替代关系，再比较有效时间。国家标准、行业标准、推荐性与强制性条款分别保留来源；不能只按年份、风级、数值大小或单一重量合并。来源标识可通过 `-SourcePrefix` 限定，例如 `GB` 同时包括其斜线子系列；Agent应把用户指定的来源范围映射为参数，而不是在检索后把其他类型资料当成同类依据。

推理可以整理库内条件、比较范围和解释差异，必须能追溯到前提；不能推断没有依据的废止、替代、实时状态或数值。原件或规范化来源变化时，已校录结论必须复审，不能自动继承。

## 正文与查询验收

reviewed 必须具有实际条款、完整条件、单位、数值边界及必要例外，不能只有目录和原件链接。物理分页不应终止同一逻辑条款；跨页结果保留准确的 reviewed 行号、来源物理页及各页校核级别，不因一页已校录就将相邻页标为已校录。

来源对齐全文覆盖、结构门禁和正文哈希不能证明所有OCR、公式与图表都已逐字语义审核。已验证条款可以直接回答；未可靠转写的内容必须暴露为缺口，回到补强流程。测试过程中不改知识正文来消除失败，再把结果称为原基线通过。

验收分别记录：正确来源召回、条款完整性、语义与边界、适用时间、检索耗时及整轮来源合规。命令成功、文档命中、首位排名或局部读文件守卫通过，都不能单独证明完整回答通过。已有网页信息参与答案后，删除引用或更正报告不构成一次新的独立纯库复测。

## 整轮工具来源审计

必须覆盖从问题开始至答案形成的整轮工具活动，包括Agent在RAG函数之外追加的调用。网页即使用于标准状态、日期或其他元数据核验，也属于纯库测试越界；原件和图像不能作为查询答题的回退来源。通过shell或适配器访问网络同样属于外部访问，不能因工具名是本地执行而忽略。

评测记录区分实际工具事件、答题证据和基于证据的推理。只读文件守卫只证明其覆盖的函数调用，不证明整轮未联网。事件不完整、事件未分类或仅有Agent自行声明“未联网”时，不能判为纯库通过。

`audit-query-evaluation` 校验提供的记录、事件分类、证据路径、哈希与行号，并绑定输入记录哈希。它不会联网、不会补全答案，也不能证明未提供的事件不存在；其输出明确为“输入记录校验”，不等同于运行时隔离或真实性证明。有效的全量事件采集由运行时提供，或由审核人对完整工具记录确认。语义结论仍需审核，引用存在不代表推理正确。

发现外部来源越界时，将该次纯库评测标为无效，保留原始记录和诊断，不据此宣布知识本身错误或所有局部测试失败。正式混合使用可以保留合法外部证据，但不能改变纯库测试的验收口径。
