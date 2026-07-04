---
documentName: user/knowledge/README.md
version: v1.6.0-candidate-cleanup-llm-wiki-mechanisms
updatedAt: 2026-07-03 22:30:00.000 +08:00
status: active
purpose: 定义真实用户知识、候选知识和 reviewed knowledge 的本地边界。
scope:
  - user-knowledge-boundary
  - local-only-boundary
  - candidate-knowledge
prerequisites:
  - AGENTS.md
  - INDEX.md
relatedDocuments:
  - INDEX.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/architecture/PLANS.md
outputTo:
  - user/knowledge/README.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-03
  decision: candidate-cleanup-and-llm-wiki-mechanism-boundary-added
---
# 用户知识边界

`user/knowledge/` 是真实用户知识和 candidate knowledge 的本地边界。除本 README 外，目录内容默认 local-only，不进入通用 Harness Git。

## Obsidian 入口

人类用户在 Obsidian 中打开本目录时，日常入口是：

```text
Home.md
```

审核候选知识时仍从同一个入口进入，在 `Home.md` 中查看 Candidate Review Queue：

```text
Home.md
```

本 README 是文件系统边界说明，不作为日常 Obsidian 阅读入口。

可放入本目录的内容包括：

- 用户提供的 raw source；
- candidate wiki；
- reviewed user knowledge；
- project-specific knowledge；
- 不适合进入通用 Harness Git 的私有知识库工作副本。

默认子路径建议：

| 子路径 | 用途 | Git 边界 |
|---|---|---|
| `raw/<domain>/` | 用户提供或工具复制的 raw source，按知识主题领域归档。 | local-only |
| `candidate/<run-id>/wiki` | raw-to-candidate workflow 生成的候选知识。 | local-only |
| `candidate/_archive/by-source/<source-id>/<bucket>/` | 已晋升证据、历史候选或测试候选的 source-centered 非破坏性归档。 | local-only |
| `reviewed/<domain>/` | 经 human review 或用户批准后的用户知识，按知识主题领域组织。 | local-only 或外部 private repo |
| `reviewed/<domain>/schema.md` | 领域命名、frontmatter、目录和验证规则。 | local-only 或外部 private repo |
| `reviewed/_archive/` | reviewed validation evidence、superseded page 或 archived page。 | local-only 或外部 private repo |
| `project-id/<project-id>/` | 项目相关知识。 | local-only 或外部 private repo |

当前维护口径：

- `Home.md` 是唯一 Obsidian 日常入口和审核入口。
- `candidate/` 根目录只保留当前 active-review candidate；历史候选移动到 `candidate/_archive/`。
- Candidate 晋升、拒绝或归档后，full corpus 默认应移出 Obsidian 默认图谱或删除，只保留轻量审计记录；清理前运行 `candidate-cleanup-plan` dry-run。
- 一份 raw source 应收敛到一个 canonical candidate evidence、一个 authoritative reviewed page，以及可选多个 reviewed concept pages。
- 正式 reviewed page 使用语义命名，不使用 `smoke`、`pipeline`、阶段编号或工具 run id。
- 已晋升 reviewed Knowledge 如果引用了候选证据，归档时应同步 source trace 到新的 archive path。
- 一键验证使用 `harness/tools/scripts/stable/invoke-rag-knowledge.ps1 -Command validate-knowledge-vault`；通过标准是 registry、Home、domain schema、reviewed frontmatter、source trace、graph、duplicate、archive、Git ignore 和 Obsidian plugin boundary 均无 blocking issue。
- Obsidian LLM Wiki 类插件只作为阅读、candidate generation 和本地治理辅助；插件输出不能绕过 review 写入 `reviewed/`，插件配置、API key、workspace state 和 query history 必须留在 local-only。
- LLM Wiki 类工具的 schema、受控 tag vocabulary、source gate、source fingerprint、alias-aware dedup、repair order 和 graph retrieval 可以作为 Harness 机制参考，但写入 reviewed 仍必须走 review gates。
- `reviewed/_archive/` 是 reviewed validation evidence、superseded page 或 archived page 的审计归档，不是垃圾桶；被 source trace、duplicate governance 或 validation report 引用时不得直接删除。
- 根目录不长期保留 `CandidateReviewQueue.md`、`CandidateReviewPackage.md`、`CandidateEvidenceIndex.md`、`KnowledgeIndex.md`、`ReviewedKnowledgeIndex.md`、`ReviewedOverview.md`、`RawSourceIndex.md` 或 `KnowledgeGovernance.md` 等二级视图文件；这些内容应折叠进 `Home.md` 或由 runtime report 重建。

`harness/rag/` 只保存可复用摄取机制；`var/rag/` 保存 extracted artifacts、eval reports、graph、embedding、index 和 cache。

禁止把 credential、auth 文件、private settings、raw logs、未脱敏 trace 或私有仓库细节写入 tracked docs。
