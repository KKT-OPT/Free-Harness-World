---
documentName: user/knowledge/README.md
version: v1.2.0-single-entry-archive
updatedAt: 2026-07-01 23:45:00.000 +08:00
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
  reviewedAt: 2026-07-01
  decision: single-entry-and-non-destructive-candidate-archive-aligned
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
| `raw/<run-id>/` | 用户提供或工具复制的 raw source。 | local-only |
| `candidate/<run-id>/wiki` | raw-to-candidate workflow 生成的候选知识。 | local-only |
| `candidate/_archive/<state>/<run-id>/` | 已晋升证据、历史候选或测试候选的非破坏性归档。 | local-only |
| `reviewed/` | 经 human review 或用户批准后的用户知识。 | local-only 或外部 private repo |
| `project-id/<project-id>/` | 项目相关知识。 | local-only 或外部 private repo |

当前维护口径：

- `Home.md` 是唯一 Obsidian 日常入口和审核入口。
- `candidate/` 根目录只保留当前 active-review candidate；历史候选移动到 `candidate/_archive/`。
- 已晋升 reviewed Knowledge 如果引用了候选证据，归档时应同步 source trace 到新的 archive path。
- 根目录不长期保留 `CandidateReviewQueue.md`、`CandidateReviewPackage.md`、`CandidateEvidenceIndex.md`、`KnowledgeIndex.md`、`ReviewedKnowledgeIndex.md`、`ReviewedOverview.md`、`RawSourceIndex.md` 或 `KnowledgeGovernance.md` 等二级视图文件；这些内容应折叠进 `Home.md` 或由 runtime report 重建。

`harness/rag/` 只保存可复用摄取机制；`var/rag/` 保存 extracted artifacts、eval reports、graph、embedding、index 和 cache。

禁止把 credential、auth 文件、private settings、raw logs、未脱敏 trace 或私有仓库细节写入 tracked docs。
