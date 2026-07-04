---
documentName: harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
version: v1.3.0-normalized-source-depth-validated
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: active
purpose: 定义从 obsidian-llm-wiki 吸收到 Harness RAG/Knowledge 机制中的可复用设计、执行门禁和边界。
scope:
  - rag-policy
  - llm-wiki-pattern
  - knowledge-governance
  - reviewed-graph-query
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
relatedDocuments:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/README.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/templates/knowledge/StructuredIngestionManifestTemplate.md
  - harness/templates/knowledge/CandidateKnowledgeTemplate.md
  - harness/templates/knowledge/ReviewedKnowledgeTemplate.md
  - user/knowledge/README.md
outputTo:
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
owner: mixed
reviewAfter: 2026-07-24
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-03
  decision: normalized-source-depth-mechanisms-validated
---
# LLM Wiki 机制吸收策略

本文记录从 `green-dalii/obsidian-llm-wiki` 吸收到 Harness RAG/Knowledge 机制中的设计。吸收对象是机制，不是插件运行态。插件仍受 `ObsidianLlmWikiPluginBoundary.md` 约束：可辅助 candidate generation、human reading、lint 和 query，但不得绕过 review 写入 reviewed Knowledge。

参考 upstream 版本：

```text
repository: green-dalii/obsidian-llm-wiki
commit: 906fa4c996437ae9e0fbe38ee43be4126e37c3f5
date: 2026-07-03 08:13:52 +0800
subject: Merge pull request #236 from green-dalii/chore/license-apache-2.0
```

## 1. 可吸收机制

| 机制 | Harness 吸收方式 | 当前执行承接 |
|---|---|---|
| Schema 配置 | 将 `schema/config.md` 风格吸收为 domain schema、schema parser 和 validation gate；任务执行时只注入相关 schema section。 | `schema-context` 按任务裁剪 schema section；`validate-knowledge-vault` 和 `validate-llm-wiki-mechanisms` 检查 registry domain schema、受控标签、alias rules、source gate rules 和任务 section 覆盖。 |
| 提取颗粒度 | 在 raw-to-candidate manifest 中记录并执行 `extractionGranularity`、entity cap、concept cap 和 batch strategy。 | `rag_candidate ingest` 根据 `fine/standard/coarse/minimal/custom` 调整 effective chunk size、preview limits、batch id、entity cap、concept cap 和 batch strategy 记录；`validate-llm-wiki-mechanisms` 用 fixture 验证 fine 与 minimal 的分块差异。 |
| Tag vocabulary | 每个 reviewed domain 定义受控 tag vocabulary；agent 只能使用 vocabulary 内标签。 | `validate-knowledge-vault` 对 reviewed pages 的 tags 做越界检查；`validate-llm-wiki-mechanisms` 要求 authoritative content pages 声明 tags 并落在 controlled vocabulary 内。 |
| Source gate | candidate ingest 前拦截空文件、frontmatter-only 文件、不兼容类型和重复 body hash。 | `rag_candidate ingest` 在写 candidate 前执行 source gate，并把 accepted/blocked 结果写入 manifest。 |
| Source fingerprint | source slug 结合 path fingerprint 和 content hash，避免同名 source 覆盖或跨目录混淆。 | `rag_candidate ingest` 使用路径指纹生成 source slug，并记录 body hash/source fingerprint；开启 raw copy 时同时把 normalized Markdown 写入 `raw/<domain>/normalized/`，`var/rag` 只保留运行态副本。 |
| Alias-aware dedup | `aliases`、同义词和跨语言别名是重复治理输入，不只是展示字段。 | `govern-reviewed-duplicates` 将 title、frontmatter aliases、Key Concepts aliases 和 body similarity candidates 纳入重复治理报告。 |
| Causality-aware lint fix | 修复顺序为 structure pollution -> aliases -> duplicate merge -> dead links -> orphans -> empty pages -> retag。 | `validate-knowledge-vault` 在机制吸收 gate 中输出 repair plan order。 |
| Graph retrieval | 使用 wikilink graph、lexical match 和 PPR cascade 做 reviewed-only query 增强。 | `query-reviewed` 只扫描 authoritative reviewed graph，并用 lexical score seed 执行 PPR 扩展；`validate-llm-wiki-mechanisms` 验证 graph PPR match。 |
| Auto maintenance | watcher、debounce、recentWrites、防自触发和 startup quick fixes 只吸收为工程经验。 | Harness 不允许后台自动写 reviewed；只能落为 dry-run、candidate-only 或显式批准后的稳定命令；`validate-llm-wiki-mechanisms` 检查插件配置中不启用危险 auto write。 |

## 2. 执行边界

1. 通用 Harness 保存 schema 模板、manifest 字段、validation gate、policy 和稳定命令。
2. 具体 domain schema、tag vocabulary、raw source 和 reviewed pages 落在 `user/knowledge/` 或外部 private knowledge repo。
3. Candidate ingest 可以自动生成 candidate wiki，但不能自动晋升 reviewed Knowledge。
4. Reviewed query 和 graph retrieval 只能读取 authoritative reviewed pages、领域 index/schema 和必要的 reviewed validation evidence metadata。
5. Auto maintenance 默认只能 dry-run；需要写文件时，优先写 candidate 或 runtime report；写 reviewed 必须有 review gates 和用户批准。

## 3. Manifest 字段

raw-to-candidate manifest 应包含以下机制字段：

```yaml
sourceGate:
  acceptedSourceCount: <number>
  blockedSourceCount: <number>
sources:
  - sourceFingerprint: <path-fingerprint>
    sourceGate:
      state: accepted | blocked
      bodyHashSha256: <hash>
      duplicateBodyHashOf: null
    extraction:
      extractionGranularity: fine | standard | coarse | minimal | custom
      entityCap: <number>
      conceptCap: <number>
      batchStrategy: <strategy>
    normalizedMarkdown: user/knowledge/raw/<domain>/normalized/<source>.md
    runtimeExtractedMarkdown: var/rag/<run-id>/extracted/<source>.md
    tagVocabulary:
      mode: default | custom
      allowedTags: []
```

## 4. 验收

机制吸收完成时应满足：

1. `validate-knowledge-vault` 包含 `llm-wiki-mechanism-absorption` 检查项。
2. `validate-llm-wiki-mechanisms` 一键通过 schema context、source gate fixture、extraction granularity fixture、tag vocabulary、alias/body similarity duplicate governance、repair order、reviewed graph PPR 和 auto maintenance boundary。
3. domain schema 存在受控标签、alias rules、source gate rules 和 validation rules，且 `schema-context` 能按任务裁剪 section。
4. raw-to-candidate ingest 能在 LLM 或候选生成前拦截无效 source，并根据 extraction granularity 改变实际分块和记录。
5. duplicate governance 能使用 aliases 和 body similarity candidates 作为重复治理输入。
6. reviewed-only query 不读取 raw、candidate、plugin runtime，并能通过 graph PPR 扩展相关 reviewed pages。
7. auto maintenance 不以后台 watcher 方式自动写 reviewed Knowledge。
8. reviewed authoritative page 的长期 `sourceRefs` 不依赖 `var/rag/<run-id>/extracted/*.md`；normalized source Markdown 应保存在 `raw/<domain>/normalized/` 或外部 private raw source boundary。
9. source-level reviewed page 应有足够的中文主体综合内容，不能只保存一两句摘要或关键词表。

## 5. 可执行验收命令

```powershell
powershell -ExecutionPolicy Bypass -File harness/tools/scripts/stable/invoke-rag-knowledge.ps1 `
  -Command schema-context `
  -Root . `
  -Domain <domain> `
  -Task promotion

powershell -ExecutionPolicy Bypass -File harness/tools/scripts/stable/invoke-rag-knowledge.ps1 `
  -Command validate-llm-wiki-mechanisms `
  -Root .

powershell -ExecutionPolicy Bypass -File harness/tools/scripts/stable/invoke-rag-knowledge.ps1 `
  -Command validate-knowledge-vault `
  -Root .
```

真实 raw source 的端到端验收还必须补充 `pipeline-smoke`、post-promotion `candidate-cleanup-plan` 或 approved `candidate-cleanup-apply`、以及 focused reviewed-only query。
