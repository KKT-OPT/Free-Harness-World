# Harness Asset Ontology And Local RAG Strategy

Status: archived
Version: v0.1.1-archived-post-p11-cleanup
Date: 2026-06-08

## 1. Purpose

This archived design note refined the asset model before the final `HarnessEngineering.md` rewrite. Its durable conclusions have been absorbed into `docs/architecture/HarnessEngineering.md`.

It records the current agreed position:

- the knowledge base is split into `global`, `domain`, and `project-reviewed` scopes;
- Harness is not copied wholesale into each project;
- the landing model is central Harness Root plus project Profile and project entry;
- RAG should prefer free, open-source, local, private, secure, and mature components.

This document does not perform migration and does not choose a final vector database implementation.

## 2. Core Corrections

The design must keep these concepts separate:

```text
Skill != Knowledge
Memory != Knowledge
Project Facts != Root Knowledge
RAG Index != Knowledge Source
Workflow Evidence != Stable Fact
```

### Skill

A Skill is a reusable task workflow.

It tells an agent how to perform a class of work, such as architecture design, code review, failure attribution, Java feature implementation, or knowledge promotion.

A Skill should define:

- trigger conditions;
- required inputs;
- execution steps;
- allowed and preferred tools;
- expected outputs;
- evidence requirements;
- acceptance checks;
- risk and clarification rules.

### Knowledge

Knowledge is reviewed and citable information.

It may come from Markdown, PDF, image, source code, external documentation, reports, or project evidence, but it becomes stable knowledge only after extraction, structuring, and review.

### Memory

Memory is experience.

It records practical lessons such as how a previous issue was fixed, how a project is usually tested, which command is unreliable, or which user preference has been repeatedly confirmed.

Memory is useful but may be situational. It should have scope, source, confidence, and expiration or review guidance.

### Project Facts

Project Facts are authoritative facts inside one managed project working copy.

They live under the project root, normally in:

```text
projects/<project-id>/docs/project/
```

Project Facts are higher priority than reusable root knowledge for that project.

### RAG Index

A RAG index is a derived access mechanism.

It is not the source of truth. It can be rebuilt from reviewed knowledge, project facts, and approved source metadata.

## 3. Asset Ontology

| Asset Class | Role | Typical Location | Git Policy |
|---|---|---|---|
| Policy Assets | Hard constraints, safety, approval, git boundary, governance | `docs/governance/` | tracked |
| Template Assets | Task Brief, report, workflow, project templates | `templates/` | tracked |
| Skill Assets | Reusable task workflows | `skills/` or `docs/skills/` | tracked after review |
| Knowledge Assets | Raw, extracted, candidate, reviewed, archived knowledge | `knowledge/` or `docs/knowledge/` | reviewed tracked; raw selective |
| Memory Assets | Experience, preferences, repair patterns, testing lessons | `memory/` or `docs/memory/` | tracked after review |
| Project Fact Assets | Project-specific authoritative facts | `projects/<project-id>/docs/project/` | tracked inside project repo |
| Tool Assets | Stable command surfaces and helper scripts | `scripts/`, `tools/`, skill helper scripts | tracked |
| Evidence Assets | Task Brief, workflow summary, validation report, failure attribution | project workflow docs, `docs/reports/` | redacted tracked |
| RAG Index Assets | Chunks, embeddings, keyword index, vector collections | `var/rag/` or `knowledge/indexes/` | rebuildable; ignored by default |

The root design may later choose either top-level asset directories or `docs/*` subdirectories. The important boundary is asset ownership, not the first directory name.

## 4. Knowledge Scope Model

Reviewed knowledge is split by scope:

| Scope | Meaning | Example | Promotion Rule |
|---|---|---|---|
| `global` | Reusable across domains and projects | general code review policy, generic Maven validation rules | requires high confidence and broad reuse |
| `domain` | Reusable inside one domain | aircraft model parameters, finance reporting terminology | requires domain owner or explicit review |
| `project-reviewed` | Stable for one managed project | this project's module boundaries, accepted test commands | stays inside project unless reuse is proven |

Not every stable project fact should be promoted to global knowledge.

Promotion should move information upward only when it is reusable, reviewed, and not sensitive.

## 5. Knowledge Lifecycle

Knowledge moves through these states:

```text
raw source
-> extracted content
-> structured content
-> candidate knowledge
-> reviewed knowledge
-> indexed retrieval artifact
-> deprecated or archived
```

State meanings:

| State | Meaning | Notes |
|---|---|---|
| raw source | Original input such as PDF, image, DOCX, Markdown, web export, source snippet | may be private, large, or untracked |
| extracted content | Machine-extracted Markdown, text, tables, OCR, metadata | must keep provenance |
| structured content | Parsed blocks, sections, tables, images, coordinates, entities, and source metadata prepared for chunking | still not authoritative |
| candidate knowledge | Agent-summarized or human-drafted candidate | not authoritative |
| reviewed knowledge | Accepted stable knowledge with scope and source | authoritative for its scope |
| indexed retrieval artifact | Chunked, embedded, keyword-indexed copy | rebuildable |
| deprecated/archive | No longer active but retained for traceability | should not be routed by default |

Each reviewed knowledge item should contain:

```yaml
id: <stable-id>
scope: global | domain | project-reviewed
domain: <optional-domain>
projectId: <optional-project-id>
sourceRefs: []
status: candidate | reviewed | deprecated | archived
owner: <optional-reviewer-or-role>
reviewedAt: <date-or-null>
expiresAt: <date-or-null>
tags: []
summary: <short-summary>
```

## 6. Project Profile And Entry Model

Harness is not copied wholesale into every project.

The target model is:

```text
Central Harness Root
-> project registry
-> project Profile
-> project root AGENTS.md
-> project docs/project/ProjectIndex.md
-> project facts, source, validation, workflow
```

The project Profile records routing and defaults:

```yaml
projectId: <project-id>
root: projects/<project-id>
entry: AGENTS.md
projectIndex: docs/project/ProjectIndex.md
defaultValidationProfile: <profile-id>
knowledgeScopes:
  - project-reviewed:<project-id>
  - domain:<domain-id>
  - global
sensitiveBoundaries: []
defaultCommands: []
```

Project-level constraints may narrow root Harness constraints, but they must not weaken security, privacy, approval, git, or governance hard stops.

## 7. Local-First RAG Requirements

The first RAG implementation should prefer:

- free or open-source components;
- local execution by default;
- private data control;
- mature ecosystem and documentation;
- reproducible indexing;
- metadata filtering by scope, project, domain, source, status, and review state;
- hybrid retrieval when possible;
- citation and provenance in every answer;
- evaluation before promotion.

Hosted retrieval services may remain optional future adapters, but they should not be the default for private project automation.

## 8. Recommended RAG Landing Path

### v0 - No Vector Database

Use:

- Markdown with front matter;
- structured indexes;
- `rg` and deterministic file routing;
- explicit source links.

Purpose:

- prove the asset ontology;
- avoid premature infrastructure;
- keep knowledge review and promotion visible.

### v1 - Structured Local Corpus

Add:

- raw source inventory;
- extraction outputs;
- structured extraction outputs;
- `chunks.jsonl`;
- source metadata;
- chunk IDs;
- review status.

Purpose:

- make future indexing reproducible;
- separate source truth from retrieval artifacts.

### v2 - Local Vector Store

Candidate options:

| Option | Strength | Fit |
|---|---|---|
| Chroma | simple local vector store, easy developer start | good first prototype |
| Qdrant | mature filtering and hybrid search support | strong default candidate |
| pgvector | simple if PostgreSQL is already accepted | good for relational metadata |
| Weaviate | strong hybrid search and schema model | good when a service is acceptable |
| Milvus | strong scale-out vector database | later-stage option |

Default recommendation for Harness:

```text
Start with v0/v1, then prototype Qdrant and Chroma locally before choosing one default.
```

### v3 - Hybrid Retrieval And Reranking

Add:

- dense vector retrieval;
- keyword or BM25 retrieval;
- metadata filters;
- reranking;
- citation enforcement;
- answer grounding checks.

### v4 - Evaluation And Governance

Add:

- retrieval test sets;
- context precision and recall checks;
- groundedness or faithfulness checks;
- failed retrieval attribution;
- promotion rules for new knowledge candidates.

## 9. Candidate Open-Source Stack

Initial local-first stack:

```text
Document parsing: MarkItDown, Docling, or Unstructured
OCR: RapidOCR for offline image and scanned-PDF text extraction
Audio/video transcription: Whisper for offline speech-to-text before Markdown conversion
Corpus format: Markdown + YAML front matter + JSONL chunks
RAG orchestration: LlamaIndex, LangChain, or Haystack
Vector store: Qdrant or Chroma first; pgvector if PostgreSQL is introduced
Evaluation: Ragas or TruLens
Runtime evidence: Harness workflow and verification reports
```

Selection should be made by a local proof-of-concept, not only by feature lists.

## 10. Structured Ingestion Tool Layer

Structured ingestion，中文解释是结构化摄取，是 RAG 知识库建设中把原始非结构化资料转换为可治理语料的工具层。它位于：

```text
raw source
-> extracted content
-> structured content
-> candidate knowledge
```

它不等于 RAG index，也不等于 reviewed Knowledge。即使工具能自动生成 Markdown、JSON、表格、章节树或实体字段，输出也只能先进入 `extracted` 或 `candidate` 状态，必须经过 review 才能成为稳定知识。

### 10.1 Tool Role

这类工具适合承担：

- PDF、图片、DOCX、HTML、网页导出、扫描件等原始资料解析；
- OCR，中文解释是光学字符识别；
- layout parsing，中文解释是版面解析；
- table extraction，中文解释是表格抽取；
- formula、image、caption 和 footnote 保留；
- section tree，中文解释是章节树；
- metadata 和 source coordinates，中文解释是来源坐标；
- Markdown、JSON、JSONL 或 HTML 输出；
- 为后续 chunk、embedding、metadata filter 和 citation 做准备。

它不应该承担：

- 自动把抽取结果晋升为 reviewed Knowledge；
- 自动覆盖 Project Facts；
- 自动生成不可追溯的总结；
- 自动写入长期 memory；
- 自动选择 vector store；
- 自动忽略授权、隐私和敏感边界。

### 10.2 Evaluation Criteria

候选工具进入 Harness 前，应按以下维度评估：

| Dimension | Question |
|---|---|
| Input coverage | 是否支持 PDF、图片、DOCX、HTML、Markdown、网页导出和扫描件 |
| Layout fidelity | 是否保留标题层级、段落顺序、表格结构、图片、公式和页码 |
| Structured output | 是否能输出 Markdown、JSON、JSONL，且字段稳定 |
| Provenance | 是否保留 source file、page、block id、coordinate、hash |
| Privacy | 是否可本地运行，是否默认上传资料到外部服务 |
| Reproducibility | 同一输入是否能稳定生成同一结构，是否记录工具版本和参数 |
| Error reporting | 是否报告 OCR 置信度、失败页、坏表格和无法解析内容 |
| Incremental build | 是否支持增量解析、缓存和变更检测 |
| License and deployment | 许可证、商用限制、Windows 本地部署成本是否可接受 |
| RAG fit | 是否方便生成 chunk、metadata filter、citation 和 eval samples |

### 10.3 Current External Tool Candidate

用户最初提供了一个微信文章链接：

```text
https://mp.weixin.qq.com/s/q3JDrXeDUUrtzlknw_Ol8g
```

后续用户明确补充该工具链可直接参考官方仓库：

```text
https://github.com/microsoft/markitdown
https://github.com/RapidAI/RapidOCR
https://github.com/openai/whisper
```

因此当前候选从未确认微信文章工具更新为：

```yaml
candidateId: markitdown-rapidocr-whisper-offline-ingestion
status: candidate-for-poc
role: structured-ingestion
sourceRefs:
  - https://github.com/microsoft/markitdown
  - https://github.com/RapidAI/RapidOCR
  - https://github.com/openai/whisper
reviewNeeded: true
```

建议定位：

```text
MarkItDown: 多格式文档到 Markdown 的主转换入口。
RapidOCR: 图片、扫描件和 PDF 内嵌图片的本地 OCR 补充模块。
Whisper: 音频和视频的本地 speech-to-text 预处理模块。
```

该组合应优先作为 `v1 - Structured Local Corpus` 的候选解析器，而不是作为向量库或最终知识库本身。

### 10.4 Offline Ingestion Profile

离线内网环境下建议定义一个独立 profile：

```yaml
profileId: offline-markitdown-rapidocr-whisper
network: disabled
llmApiRequired: false
documentConverter: markitdown
ocrEngine: rapidocr
speechToTextEngine: whisper
allowedInputs:
  - pdf
  - docx
  - pptx
  - xlsx
  - html
  - csv
  - json
  - xml
  - image
  - audio
  - video
outputs:
  - markdown
  - metadata-manifest
  - extraction-report
  - chunks-jsonl
```

该 profile 的关键规则：

- 默认禁用需要 OpenAI-compatible API、Azure API 或其他云端服务的功能；
- 图片和扫描 PDF 优先走 RapidOCR；
- 音频和视频先用 Whisper 离线转文字，再进入 MarkItDown/Markdown 语料流程；
- 每次转换必须记录工具版本、模型版本、输入 hash、输出 hash、失败页、OCR 置信度和转写模型；
- 输出仍然只能进入 `knowledge/extracted` 或 `knowledge/candidate`，不能自动进入 `knowledge/reviewed`；
- 若后续启用云端 LLM/Azure 模式，必须使用另一个显式 profile，并经过凭据和数据出境审批。

### 10.5 PoC Acceptance

后续 RAG PoC 可以用一组小样本评估该组合：

```text
1. 输入：1 个文本 PDF、1 个扫描 PDF、1 个图片样本、1 个 Office 文档、1 个 HTML/网页导出、1 个音频或视频样本。
2. 输出：Markdown + metadata manifest + extraction report + chunks.jsonl。
3. 检查：页码、章节、表格、图片引用、OCR 置信度、音视频时间戳、sourceRef、hash、解析错误。
4. 治理：输出进入 knowledge/extracted 或 knowledge/candidate，不进入 reviewed。
5. 离线性：在禁用网络和无 OpenAI/Azure API key 的环境中完成转换。
6. 检索：通过 rg/BM25/向量检索验证 citation 是否可追溯。
```

## 11. Source References

Reference URLs used for later evaluation:

```text
https://developers.llamaindex.ai/python/framework/understanding/rag/
https://docs.langchain.com/oss/python/langchain/retrieval
https://docs.haystack.deepset.ai/docs/pipelines
https://qdrant.tech/documentation/tutorials/hybrid-search-fastembed/
https://docs.trychroma.com/
https://github.com/pgvector/pgvector
https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/
https://www.trulens.org/getting_started/core_concepts/rag_triad/
https://docling-project.github.io/docling/reference/document_converter/
https://docs.unstructured.io/open-source/core-functionality/partitioning
https://github.com/microsoft/markitdown
https://github.com/RapidAI/RapidOCR
https://github.com/openai/whisper
```
