---
documentName: harness/rag/policies/SourceVersionAndRelocationPolicy.md
version: v1.0.0
updatedAt: '2026-11-02'
status: active
purpose: 定义来源版本冲突审读、正式原件路径迁移、不可变历史证据及工具沉淀边界。
scope: [rag-source-version, conflict-review, source-relocation]
prerequisites: [AGENTS.md, harness/governance/KnowledgePromotionPolicy.md]
relatedDocuments:
  - harness/tools/docs/command-surfaces/RagDocumentPipeline.md
  - harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
  - harness/rag/pipelines/PdfNormalizationContract.md
outputTo: [harness/rag/policies/SourceVersionAndRelocationPolicy.md]
owner: mixed
reviewAfter: '2027-05-02'
supersededBy: null
dependsOn: [harness/tools/scripts/stable/invoke-rag-candidate.ps1]
review:
  reviewedBy: agent
  reviewedAt: '2026-11-02'
  decision: user-authorized-knowledge-tool-consolidation
---
# 来源版本审读与原件迁移

## 版本与冲突

查询先匹配事项、分类轴、对象和场景，再按领域schema中用户确认的取证规则选择来源。检索分数不是效力或版本优先级。通用Harness不硬编码某一文种总是优先于法规，也不凭发布时间自动认定废止、替代或适用义务消失。

`sourceVersion`分别保存成文日、正式发布日期、实施日、核验日、稿件状态和适用事项。未知日期显式保留null，不使用文件名年份、目标年份或知识维护日期补造。草稿、占位编号和译本须标明；稿件日期不是正式发布日期，中文概述不自动成为认证译文。已到实施日不证明当前有效，未来实施版本不得作为当前已实施依据。

`audit-versions`只读检查日期格式、必要字段和核验日期，统计未知、草稿及译本，按同系列编号提示多版本复核组。不确定的日期先后关系、同系列多页或元数据齐全，都不等于已发现或解决语义冲突。跨来源审读记录应包含问题事项、完整条件及单位、各来源正文行号与版本事实、用户规则、处置和未核实事项。可区分范围独立、同事项较新已实施、明确替代、草稿参考和仍未解决；推理不能补齐缺失证据。

来源页中的综合说明采用具体事项标题，把条件、结论、端点、例外和日期放在可连贯检索的段落中。大量相同的通用冲突提示可能挤掉实际条款，必须用原题及完整断言复验。标题中的来源标识用于区分对象，不得把题目关键词堆砌当作内容补强。

## 原件路径迁移

原件位置改变是一项有明确范围的存储治理，不是新版本标准。迁移前盘点原件、normalized、侧车、reviewed和当前封印，以SHA-256绑定完整清单。复审仍按用户已授权的范围执行，不要求重复批准已明确授权的必要引用修复。

稳定`prepare-source-relocation`默认仅生成计划；显式`-Apply`并提供reviewer和approval note后，只复制原件到新raw路径、生成新normalized及侧车和candidate草稿。旧原件、旧派生稿和reviewed保留不变，工具不删除、不自动晋升。新派生稿引用原图时保留正确的跨目录链接，不重新OCR或扩大校核声明。工具要求迁移前后原件哈希一致，并验证渲染到reviewed的完整来源正文及sourceVersion不变；内容变化必须改走内容修复。

候选仍须补全、审核并通过`review-package`、`promote-reviewed`实际晋升。PromotionMap中的`expectedTargetHashSha256`绑定准备时目标字节，目标变化后即使指定Overwrite也停止。晋升后复验来源、完整正文、真实封印、查询及vault门禁，才进入已获授权的旧文件清理。若采用保留原normalized路径的专项迁移，必须另存修改前字节、修复侧车和哈希并重新审核晋升，不能直接替换已封印页面。

删除只针对用户明确指定的文件集合；先确认解析后的绝对路径仍在目标目录内，排除链接绕行并检查新路径、引用、原件哈希及保护文件。使用原生同一shell执行受限文件操作，可用现有[清理核验工具](../../tools/docs/command-surfaces/ArtifactCleanupTool.md)保存前后回执。RAG迁移工具不提供自动递归删除，未知或新增文件应重新纳入审核范围。

## 历史证据与全库口径

历史审核包、失败用例、晋升快照和原路径记录保留原字节，通过迁移对照连接当前位置，不回填历史批准、不把当时失败改为通过。缺少封印只能报告缺失并重新审核晋升。`audit-corpus`可显式接收多个既有晋升记录，选择与当前原件和页面字节匹配的条目，并记录输入路径与哈希；它不认证批准来源真实性，也不扫描日志补造记录。

全库检查分别报告主来源数、物理页覆盖、同版副本、版本元数据、重点语义主题、查询用例和全局门禁。结构、哈希、OCR覆盖及已知用例通过均不证明全文逐字准确或库外无新版本。副本不重复计为独立主来源；领域通过与全局失败不能互换。得到清理授权并完成治理后，用新记录证明遗留项清零，保留旧记录。

## 通用资产与私有资料

反复使用的解析、校验、路径重绑定、候选准备与证据归档进入稳定工具；真实日期判定、具体条款、文种取证偏好、原件清单和审计记录留在本地知识领域。批次脚本作为历史证据保留，不把其中的领域知识、绝对路径和私有输入原样复制进通用代码。合成夹具验证工具行为，真实语料只用于本地验收。发布按既有Harness分支工具和Git边界执行。
