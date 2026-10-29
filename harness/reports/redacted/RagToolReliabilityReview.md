---
documentName: harness/reports/redacted/RagToolReliabilityReview.md
version: v1.3.0-query-evaluation-boundary
updatedAt: 2026-10-29
status: active
purpose: 记录临时文档转换脚本与稳定 RAG 工具的审查、通用能力沉淀和既有知识库的合规边界。
scope:
  - rag-tools
  - source-bound-pdf-normalization
  - reviewed-promotion-integrity
  - legacy-corpus-audit
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
  - harness/rag/RAGIndex.md
  - harness/rag/pipelines/PdfNormalizationContract.md
  - harness/tools/docs/command-surfaces/RagDocumentPipeline.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
outputTo:
  - harness/reports/redacted/RagToolReliabilityReview.md
owner: mixed
reviewAfter: '2026-11-29'
supersededBy: null
dependsOn:
  - harness/governance/KnowledgePromotionPolicy.md
review:
  reviewedBy: user
  reviewedAt: '2026-10-29'
  decision: user-approved-rag-assets-and-evaluation-boundary-with-implementation-regression
---

# RAG 工具可靠性复查

## 任务简报

目标是复查上一批文档转换脚本，将必要的通用能力纳入既有稳定工具，并核验旧知识库。projectId 为 null，执行对象是 Harness 自身，不涉及业务项目。用户明确要求优化工具和沉淀必要脚本；本次工具及 Skill 修改已进行 agent review，用户最终验收仍待完成。

范围为 RAG 机制、稳定 candidate/knowledge 门面、相关 Skill、工具契约与测试。验收要求：统一入口能够处理 PDF 页级来源与 OCR；审核对象和最终正文可核对；多源不会隐式选择第一项；失败不静默留下半批 reviewed 更新；旧语料检查能报告实际问题。验证使用合成 fixture、实际本机 OCR、既有机制门禁和真实语料只读审计。不存在阻断工具实现的缺失字段；具体领域事实及原文校正不纳入通用代码。

风险为中等：错误的文本转换或晋升证据会污染知识回答。本次不重写旧知识正文，不回填历史批准，也不调整无关目录。原有架构计划和另一 Skill 的用户修改保留。

## 审查发现与修复

| 发现 | 后果 | 本次处置 |
|---|---|---|
| 稳定晋升曾隐式使用 `sources[0]`，且内置特定主题正文 | 多源错配或把模板推断写成知识 | 显式 sourceId 或完整映射；通用格式仅使用选定 candidate 的实质内容，排除 candidate 机制概念占位 |
| 临时流程在稳定晋升之后覆盖 reviewed 文件 | 工具记录没有对应最终正文 | 提交 reviewed 草稿，审核快照绑定原件、规范化稿、wiki、草稿与目标映射；写入原始草稿字节并记录正文哈希 |
| 多源逐项执行，缺少完整预检和失败恢复 | 后续冲突留下半批结果 | 整批预检、同目录临时文件替换、提交前目标重检、原件备份和尽力回滚；保存 transaction plan 与恢复记录，保护并发第三方改动 |
| 正则解析 YAML 未覆盖折行、BOM 和多种列表格式 | sourceRefs、审核元数据或路径误读 | 使用 PyYAML 结构化解析，拒绝重复键；显式 UTF-8；两个 PowerShell 门面恢复调用前编码设置 |
| 对无扩展名语义 slug 使用 `Path.stem` | 点号后的标准分册及指纹被截断 | slug 不再把名称当文件扩展名处理 |
| CLI 先打印报告再抛异常 | 自动化收到多个 JSON 对象 | 成功或失败均只输出一个 JSON 对象，保留 blockingIssues |
| 旧 PDF 辅助脚本依赖特定字体和全局 NFKC | 漏掉 Latin 字形替换，或改写上标与单位 | 按页字体/字符异常检查、保守字符规范化、原页图像回退和离线 OCR；公式私用字形与整页乱码分开处理 |
| 宽泛水印或数值替换缺少来源边界 | 正文误删或错误修数 | 配置要求源哈希、页/字体条件、审核人与证据；精确替换次数不符即停止；未识别低透明文字保留 |
| OCR 输出复用及空输出边界不充分 | 显式语言可能读到旧英文结果，空页误算完成 | 只使用本轮生成的英文重试结果；无可读 OCR 文本不准进入 candidate |
| Home 列出 normalized 图像；归档后 manifest 指针失效 | 阅读入口噪声和审计失联 | 排除生成资产；按 source-centered 目录归档并更新可变 manifest 指针，保留不可变晋升记录 |
| 旧全库门禁只证明结构关系 | 字体乱码仍可显示通过 | 新增 `normalized-source-quality`；另外提供显式语料 `audit-corpus` 和可选严格正文封印检查 |

批量写入具有预检和恢复能力，并非数据库事务；断电或恢复时 IO 继续失败仍需根据运行态备份处置。OCR 依赖 Windows 语言包，表格、公式、数值和法规状态需要结合原件审核。

## 临时脚本取舍

| 上一轮脚本 | 可复用机制 | 最终去向 |
|---|---|---|
| `prepare.py` | 原件清单、哈希、页级质量检查与 OCR 队列 | `rag_candidate/pdf_normalize.py`，通过 `normalize-pdf` 调用 |
| `ocr-pages.ps1` | WinRT 离线 OCR、语言选择、资源释放 | 内部 helper `rag_candidate/pdf_ocr_windows.ps1`；不增加第二个用户入口 |
| `english-queue.py` | 混合语料的英文重试 | 归入规范化模块；按本轮识别内容选择重试，不按文件名猜测 |
| `normalize.py` | 逐页 Markdown、表格/原图、原件链接 | 归入规范化模块；来源特定水印与校正改用 local-only profile |
| `pipeline.py` | 摄取与晋升编排 | 复用 `ingest`、`review-package`、`promote-reviewed`，完整映射代替逐项绕行 |
| `audit.py` | 页数、哈希、图片和链接检查 | `audit-corpus` 与全库质量检查 |
| `finalize.py` | 入口同步、归档、收口验证 | 复用 knowledge 稳定命令，取消晋升后正文覆盖方式 |
| `enrich.py`、`enrich-core.py` | 来源特定摘要、分组和引文抽取 | 保留本地历史证据；未晋升为通用工具。领域内容应人工形成 reviewed 草稿，不能用文件名推断或固定词表生成 |

原运行态脚本保留以便审计，未移动到 stable 后继续默认执行。通用实现位于现有工具模块中；实际知识、原始文档、标准号清单、水印实例和数值修正不进入本报告或 tracked Harness 资产。

## 验证与复查

隔离回归覆盖结构化元数据、完整批次映射、审核快照失效、来源错配、目标冲突、写入异常回滚、幂等、正文封印、归档指针、完整显式草稿 pipeline smoke、逐页转换、水印保护、扫描件阻断、单位保留、两种实际语言 OCR，以及两个 PowerShell 门面的中文 JSON。入口为 `test-rag-tools.ps1`，日志保存在本次 `var/rag/` 运行目录。

最终 32 项回归在 Windows PowerShell 5.1 和 PowerShell 7 均通过，无平台跳过项。Skill 校验通过；Harness 治理检查为 passed，error/warning 均为 0；`git diff --check` 无空白错误。两个真实异常字体页面在隔离夹具中通过转换结构审计，分别触发中文 OCR 与英文重试；混合语言页仍出现词内多余空格，保留需要人工核验的边界。

本机 `validate-llm-wiki-mechanisms` 为 9/9。真实全库 `validate-knowledge-vault` 为 11/13：既有未注册 raw 目录检查失败；新增转换质量检查正确阻断有问题的旧转换稿。检查失败是待处理的语料状态，不用移动无关目录或放宽门禁消除。

code-review 复查重点为来源选择、审核到写入之间的数据绑定、回滚、归档后路径、UTF-8 与 PDF 特殊字形。回归中补充了旧英文 OCR 结果串用、空 OCR 和 candidate 基础概念泄漏的反例。机制通过不等同于整个知识库已完成内容审核。

## 既有知识库结论

本节保留工具优化阶段的修复前结论。用户随后明确要求执行本批修复；最新语料状态与验收结果以本地修复审核记录为准，不把本报告当作当前知识内容的事实源。

原件哈希与物理页覆盖匹配，但不能判为完全符合当前 Harness 要求：部分转换稿仍有异常字体映射或缺少特殊字形原图；上一轮最终正文缺少可与稳定晋升记录核对的哈希封印。旧脚本的晋升后覆盖方式不能作为正文已经被工具审核的证据。

语料细节、文件名、物理页码、warnings、完整审计 JSON 与整改顺序只保存在 local-only 报告中。本次未补造历史封印、未把结构通过当成摘要/数值/引文正确性，也未替用户完成最终验收。

## 修复执行中的通用补充

后续实际使用发现：仅逐项字符串替换不足以恢复失真的二维表格和公式，因此稳定规范化 profile 增加源哈希、物理页、机器文本哈希与审核证据绑定的 `pageOverrides`；原图与逐页方法继续保留，前提变化或缺失 OCR 不得静默放行。

真实 CRLF 草稿还暴露出 fenced YAML 的闭合行未兼容 `\r\n`：读取模式的审核包能通过，而按原字节预检的晋升会漏读来源字段。解析器已修复，新增保留 CRLF 原始字节晋升和严格哈希核验的回归。批量预检失败先阻断写入；错误消息补充 source ID 以便定位。

新增整页校录、错误前提、缺少审核证据和 CRLF 契约后，回归规模为35项。前文32项结果是首次工具优化时的验证记录；本次平台验证和语料验收结果保存在 local-only 修复运行目录。

## 正文覆盖与查询可靠性复查

用户纠正表明：章节表与少量摘记不能满足知识问答，命中文档也不能证明答案来自 reviewed。稳定工具补齐逐页正文覆盖门禁、哈希绑定的条款校录配置、摄取时页级契约保留、按条款排序与准确行号，以及独立版本日期上下文。

47项回归在 PowerShell 7 和 Windows PowerShell 5.1 均通过。实际查询覆盖完整分类、边界值、相邻条款、实施日期和空命中；对本地查询函数的读取隔离只允许 reviewed 文件，阻止该调用读取 raw、PDF、图像及运行态索引；这不能证明Agent整轮未联网。测试输入、来源正文与逐项证据仅存于本地用户和运行态边界。

Skill 采用已有条目补丁，删除把原件回查视为正常问答成功的路径，内容不足转为知识缺口和候选补强。逐页文本覆盖并不证明全部OCR、公式或图表已经逐字语义审核。

## 评测边界审查与通用沉淀

用户审核通过知识库构建与查询测试边界，并授权将通用工具、脚本和文档提交仓库。纯库测试不得搜索网页，即使目的只是核验现行状态或实施日期；局部读文件守卫不能证明整轮无外部访问。此前涉及外部核验的真实查询记录已在本地更正为不可计入纯库验收，原诊断保留，不通过修改报告冒充复测。

稳定知识门面增加显式模式、来源前缀与评测记录审计；查询区分逻辑条款和物理分页，并避免文档标题重复主导条款相关性。审计检查实际提交的事件与证据，输出明确限定为记录校验，不宣称运行时隔离、日志真实性或语义正确性。

长期规则进入评测策略、既有Knowledge Promotion Policy、RAG索引、命令契约及reviewed Skill。真实资料、校录表、清单、原始工具日志和本地设置继续留在user/var边界；仓库只保留通用机制和合成回归。双PowerShell环境各67项工具回归通过，Skill元数据校验通过。回归包含元数据网页核验越界、局部日志不足、模式归属、证据变化、跨页混合校核标记和图谱不得越过来源范围等反例。阶段与最终治理收口由PLANS维护。
