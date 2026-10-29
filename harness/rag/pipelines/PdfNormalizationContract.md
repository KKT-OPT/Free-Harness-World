---
documentName: harness/rag/pipelines/PdfNormalizationContract.md
version: v1.1.0-reviewed-page-overrides
updatedAt: 2026-10-29
status: active
purpose: 定义逐页 PDF 转换、离线 OCR、来源绑定的水印与校正配置，以及转换质量证据边界。
scope:
  - pdf-normalization
  - source-quality
prerequisites:
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/tools/docs/command-surfaces/RagDocumentPipeline.md
  - harness/governance/KnowledgePromotionPolicy.md
outputTo:
  - harness/rag/pipelines/PdfNormalizationContract.md
owner: mixed
reviewAfter: 2026-11-12
supersededBy:
dependsOn:
  - harness/tools/scripts/stable/rag_candidate/pdf_normalize.py
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: user-requested-tool-integration-with-regression-review
---
# PDF 逐页转换契约

默认入口仍是 `invoke-rag-candidate.ps1`。普通文档可直接 `ingest`；遇到扫描件、损坏字体映射、水印、表格或公式，需要可追踪逐页转换时，先执行 `normalize-pdf`，再把其 `NormalizationManifest` 交给 `ingest`。

## 输入与输出

- 输入 PDF 位于本地 `user/knowledge/raw/<domain>/`；原件不被修改。
- 完整转换稿位于 `raw/<domain>/normalized/`，每页保留 `## PDF 第 n 页`、原件页链接、提取方法及必要原图。
- 原图与转换 sidecar 位于 `normalized/assets/<source-id>/`；来源清单、OCR JSON 和运行报告位于 `var/rag/<run-id>/`。
- 清单记录原件 SHA-256、转换稿 SHA-256、物理页数、逐页方法、质量标记、校正依据和配置哈希。清单是过程证据，原件与 reviewed 知识仍分别承担来源和结论职责。
- 相同来源、配置和完整输出可以重复使用；输出被编辑、配置变化或图片缺失时，不静默覆盖，要求复核后显式 `-Overwrite`。

## 字体与 OCR

- 识别扫描页、明显损坏编码、已知字体映射异常，以及将英文字母替换为罕用汉字的字体。
- Windows OCR 使用本机已安装的语言包，不调用云模型。`OcrLanguage auto` 先用中文识别，对明显英文页尝试 en-US；也可明确指定语言。
- 缺少可用 OCR 时可用 `OcrMode none` 生成待处理转换稿和原图，但未解决的页面标为 `needs-ocr`，不允许通过清单进入 candidate。
- 数学 Symbol 字体和私用字符不能等同于整页乱码。保留原文与原图并标注视觉复核需求；工具不猜测公式、上下标或数值。
- 全角 ASCII 可规范化；不对整篇执行会折叠平方、立方及单位字符的 NFKC。

## 本地配置

领域规则不写进通用代码。水印及校正配置保存于本地用户或运行态边界，示例结构如下，哈希由实际原件计算后填写。

```json
{
  "watermarks": [
    {
      "sourceHashes": ["<source-sha256>"],
      "text": "<exact-watermark-text>",
      "font": "<exact-font-name>",
      "minSize": 200,
      "maxOpacity": 0.4,
      "reviewedBy": "<reviewer>",
      "evidence": "<local-visual-review-evidence>"
    }
  ],
  "corrections": [
    {
      "sourceHashSha256": "<source-sha256>",
      "page": 4,
      "old": "<exact-observed-text>",
      "new": "<verified-correct-text>",
      "expectedCount": 1,
      "reviewedBy": "<reviewer>",
      "evidence": "<local-visual-review-evidence>"
    }
  ],
  "sourceIds": {},
  "languages": {}
}
```

- 只排除同时匹配原件哈希、文字、字体、字号和透明度的文本水印；未配置的低透明度文字保留并提示复核。
- 原图保留水印。OCR 光栅图中的水印不作推断性像素删除。
- 发生水印过滤时，不再从原 PDF 自动重建可能重新引入水印的表格；使用原页图保留表格版式。
- 数字校正必须绑定原件哈希及物理页，精确旧文字数量不符即停止，不能从相似上下文推断替换。
- `sourceIds` 和 `languages` 按原件哈希配置稳定语义名或语言，不根据某个业务文件名硬编码。

## 核验含义

对于表格、公式或漏掉关键符号的 OCR 页，可在 local-only profile 中增加 `pageOverrides`：每项必须包含 `sourceHashSha256`、物理 `page`、`expectedTextHashSha256`、完整校录 `text`、`reviewedBy` 和原图核对 `evidence`。预期哈希取本轮同配置转换记录中的该页机器文本哈希；已有逐项 correction 时取 correction 之后的文本。配置缺少证据、重复页面或前提哈希变化即停止。

校录只替换该页文本与自动表格，继续保留原 PDF 链接和原图；逐页方法及 sidecar 记录校录证据和替换哈希。未解决的 OCR 缺失不能被此配置绕过。它用于有来源的人工校录，不根据邻近值猜补数值；具体内容不进入 tracked profile 示例或通用代码。

`audit-corpus` 核验原件哈希、PDF 物理页、转换方法、原图、Markdown 文件链接、来源对应及可选晋升内容哈希。正文存在但不可读、缺页或 OCR 页面没有原图会产生具体 finding。

通过结果只证明该项机器核验通过。`semanticState` 明确为结构检查不能证明的状态；关键词命中、无替换字符或页数相等，不能证明术语、数值、公式和引用页码全部正确。

`validate-knowledge-vault` 对声明此逐页契约的派生稿增加 `normalized-source-quality` 检查。旧版未声明逐页契约的 normalized 文档单独列为 legacy，不伪造物理页证据，也不把它们自动改写为新格式。
