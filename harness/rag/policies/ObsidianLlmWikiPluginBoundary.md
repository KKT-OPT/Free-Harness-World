---
documentName: harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
version: v1.2.1-reviewed-skill-link
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: active
purpose: 定义 Obsidian LLM Wiki 类插件在 Harness Knowledge vault 中的使用边界、禁止路径和验证要求。
scope:
  - rag-policy
  - obsidian-vault
  - llm-wiki-plugin-boundary
  - reviewed-knowledge-boundary
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PHASE5_RAG_KNOWLEDGE_ACCESS_PLANS.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/README.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - user/knowledge/README.md
outputTo:
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
owner: mixed
reviewAfter: 2026-07-24
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-04
  decision: rag-knowledge-use-reviewed-skill-link-updated
---
# Obsidian LLM Wiki 插件边界策略

本文定义 Obsidian、Karpathy LLM Wiki 类插件和类似知识库插件在 Harness Knowledge vault 中的边界。插件可以提升人类阅读、候选生成、链接导航和本地 lint 体验，但不能成为 reviewed Knowledge 的写入权威或事实源。

## 1. 允许用途

插件可用于：

1. 在 `user/knowledge/` 作为 Obsidian vault 中的人类阅读界面；
2. 从用户提供的 raw source 生成 candidate wiki、entity page、concept page、source page、schema 草案或 index 草案；
3. 辅助发现 broken link、orphan page、tag sprawl、source drift、stale page 或概念重复；
4. 为 human review 准备候选材料、交叉链接建议和查询线索；
5. 辅助用户浏览 reviewed Knowledge，但回答事实问题时仍必须读取 reviewed page 正文、frontmatter、Source Trace 和 Governance Notes。

## 2. 禁止路径

插件不得执行或诱导以下路径：

1. plugin output -> `user/knowledge/reviewed/`；
2. plugin query result -> authoritative fact；
3. plugin auto ingest / auto smart fix / periodic lint -> reviewed page direct edit；
4. plugin config / API key / token / auth / workspace state -> tracked Harness doc；
5. plugin generated `schema` / `index` / `concepts` -> reviewed Knowledge without review；
6. plugin runtime state -> RAG index source of truth；
7. duplicate reviewed page -> multiple active authoritative pages。

插件生成的内容默认属于 candidate boundary。只有通过 Knowledge Promotion Policy、review gates 和用户明确批准后，才能进入 reviewed boundary。

## 3. 配置和本地边界

插件配置、API key、model selection、workspace state、query history、watched folders、auto watch 状态和插件 runtime cache 必须留在 local-only boundary。

当前推荐 Git 边界：

```text
user/knowledge/**
user/registry/*.local.json
var/rag/**
```

通用 Harness Git 只保存插件使用规则、模板、门禁和验证命令，不保存真实用户知识、插件配置或插件运行态。

## 4. Reviewed 写入门禁

插件辅助产物如果要进入 reviewed Knowledge，必须满足：

1. 有 raw source provenance；
2. 先进入 candidate knowledge 或 review package；
3. 通过 candidate health、lint、graph 或等价 review gate；
4. 通过 duplicate source/topic governance；
5. 由用户明确批准或 human review 记录批准；
6. 使用 Harness stable command 或已记录的 governance workflow 写入 reviewed；
7. 写入后运行 reviewed health、reviewed graph、query 和一键 Knowledge validation gate。

未满足这些条件时，插件输出只能作为 candidate evidence 或 local reading aid。

## 5. `reviewed/_archive` 规则

`reviewed/_archive/` 不是垃圾桶。它用于保存已经进入 reviewed boundary、但不应作为 active authoritative page 的 validation evidence、superseded page 或 archived page。

保留条件：

1. archived page 被 authoritative reviewed page 的 Source Trace、Governance Notes、domain index、Home 或 validation report 引用；
2. archived page 用于证明 duplicate reviewed governance 的处置结果；
3. archived page 记录 pipeline smoke、promotion evidence 或历史审核结论；
4. 删除会降低 reviewed Knowledge 的可审计性。

删除条件：

1. 无 reviewed source trace、domain index、Home、registry 或 report 引用；
2. 已有更合适的 candidate archive 或 project report 承接审计证据；
3. dry-run report 证明删除不会破坏 reviewed graph、duplicate governance 或 source trace；
4. 用户明确批准删除。

`reviewed/_achieve/` 不是 Harness canonical path。如果本地出现该目录，应先按拼写错误处理，确认是否应迁移到 `reviewed/_archive/`，再按上述删除条件处置。

## 6. 验证命令

插件边界变更后至少运行：

```text
harness/tools/scripts/stable/invoke-rag-knowledge.ps1 -Command validate-knowledge-vault
git check-ignore -v -- user/knowledge/.obsidian/plugins/karpathywiki/data.json
```

通过标准：

1. `validate-knowledge-vault` 的 Obsidian plugin boundary 检查通过；
2. 插件配置中没有 API key、token、password、secret 或 auth 泄露；
3. reviewed source trace 不引用 `.obsidian/`、plugin runtime 或 plugin config；
4. Git ignore 覆盖 `user/knowledge/.obsidian/` 和 `user/registry/*.local.json`；
5. reviewed graph、duplicate governance 和 archive references 无 blocking issue。
