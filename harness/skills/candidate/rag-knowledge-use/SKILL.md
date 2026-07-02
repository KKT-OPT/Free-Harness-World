---
name: rag-knowledge-use
description: Use reviewed Harness knowledge through stable RAG knowledge commands. Use when Codex needs to initialize or check the local Obsidian knowledge vault, sync the single Home entry, query reviewed Knowledge, read matched reviewed pages before answering, build reviewed graphs, generate candidate-only gap plans, enrich unresolved reviewed wikilinks, produce human review packages, promote user-approved gap concepts into reviewed concept pages, govern the knowledge vault, or run a full raw-to-reviewed query pipeline smoke.
documentName: harness/skills/candidate/rag-knowledge-use/SKILL.md
version: v0.7.0-pipeline-smoke
updatedAt: 2026-07-02 00:00:00.000 +08:00
status: review
purpose: 定义 reviewed Knowledge 使用、Obsidian 阅读入口和 reviewed gap candidate plan 的 candidate Skill。
scope:
  - rag-skill
  - reviewed-knowledge
  - knowledge-query
  - obsidian-vault
  - candidate-gap-plan
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
  - harness/tools/docs/script-index/ScriptIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/tools/scripts/stable/invoke-rag-knowledge.ps1
  - harness/skills/rag-structured-ingestion/SKILL.md
outputTo:
  - harness/skills/candidate/rag-knowledge-use/SKILL.md
owner: mixed
reviewAfter: 2026-07-15
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-02
  decision: pipeline-smoke-command-added
---
# RAG Reviewed Knowledge Use Skill

## 1. 边界

本 Skill 只使用已经通过审核的 reviewed Knowledge。事实回答必须来自 `user/knowledge/reviewed/` 或用户指定的 private reviewed knowledge repo。

不要把 raw source、candidate wiki、chunks、graph JSON、eval reports 或 Obsidian generated index 当作 authoritative knowledge。`reviewed-gap-plan` 只能生成 candidate-only 补强任务，不执行 promotion。

## 2. 稳定命令

统一使用 stable wrapper：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root <HARNESS_ROOT> -Command <command>
```

常用 commands：

| Command | 用途 |
|---|---|
| `init-obsidian-vault` | 初始化 `user/knowledge/` Obsidian vault view。 |
| `sync-reviewed-index` | 扫描 reviewed Knowledge 并同步单入口 `Home.md`。 |
| `health-reviewed` | 检查 reviewed docs、index files、frontmatter 和敏感模式。 |
| `build-reviewed-graph` | 重建 reviewed graph runtime。 |
| `query-reviewed` | 对 reviewed Knowledge 做 deterministic lookup。 |
| `reviewed-gap-plan` | 把 reviewed 文档里的 unresolved wikilinks 转为 candidate enrichment plan。 |
| `enrich-gap-candidates` | 用 reviewed Knowledge evidence 补强 gap candidate pages。 |
| `gap-review-package` | 生成 human review package，列出 ready / dedup / revise 决策输入。 |
| `promote-gap-candidates` | 在用户明确批准后，将 approved gap candidates 晋升为 reviewed concept pages。 |
| `govern-vault` | 审核前治理 Obsidian vault 单入口、candidate review queue 和 archive summary。 |
| `govern-vault -ArchiveInactiveCandidates` | 将 inactive candidates 非破坏性移动到 `candidate/_archive/`，并同步 reviewed source trace。 |
| `pipeline-smoke` | 用一个稳定命令验证 raw -> candidate -> approved promotion -> reviewed vault -> query 的完整链路。 |

## 3. 回答问题流程

1. 运行 `query-reviewed -Question <question>`。
2. 读取 query JSON 中命中的 reviewed page；只用 reviewed page 的正文、frontmatter、Source Trace 和 Governance Notes 作为事实依据。
3. 如命中不足，说明 reviewed Knowledge 暂无足够证据，不要回退到 raw/candidate/runtime artifacts 当事实源。
4. 回答中说明依据来自 reviewed Knowledge，并保留必要的 scope、reviewedAt、source trace 或 staleness caveat。

## 4. Obsidian 阅读流程

1. 运行 `init-obsidian-vault` 或 `sync-reviewed-index`。
2. 人类用户在 Obsidian 中打开 `user/knowledge/` vault。
3. 从 `Home.md` 进入 reviewed docs；不要依赖旧的 `KnowledgeIndex.md`、`ReviewedKnowledgeIndex.md` 或 `ReviewedOverview.md`。
4. Obsidian view 是阅读界面，不是事实源；事实源仍是 reviewed docs。

## 5. Gap 处理流程

1. 运行 `build-reviewed-graph` 或直接运行 `reviewed-gap-plan`。
2. 默认只生成 gap report；需要创建候选概念页时加 `-WriteCandidates`。
3. `-WriteCandidates` 写入 `user/knowledge/candidate/reviewed-gap-concepts/wiki`，该目录仍是 local-only candidate knowledge。
4. 运行 `enrich-gap-candidates`，从 reviewed docs 的 Key Concepts 和引用段落补充候选定义、evidence、适用范围和 promotion hint。
5. 对候选 gap wiki 运行 candidate `health`、`lint` 和 `build-graph`。
6. 运行 `gap-review-package`，生成 reviewer decision template。
7. 只有用户明确批准后，运行 `promote-gap-candidates -Reviewer <reviewer> -ApprovalNote <note>`，把 approved concepts 写入 `user/knowledge/reviewed/concepts/`。
8. 运行 `build-reviewed-graph`、`health-reviewed` 和 `query-reviewed` 验证 reviewed concept pages 可用。
9. 运行 `govern-vault`，刷新单入口 `Home.md`。
10. 如果用户要求审核前治理混乱候选，运行 `govern-vault -ArchiveInactiveCandidates`；该命令只归档 inactive candidates，不晋升 reviewed Knowledge。

## 6. 完成标准

- 使用 `invoke-rag-knowledge.ps1`，不手动调用 Python internals。
- reviewed query 返回命中页，agent 已阅读命中页再回答。
- Obsidian vault view 可从 `user/knowledge/` 打开，并以 `Home.md` 作为单一入口。
- gap plan 明确列出 unresolved wikilinks、引用来源、candidate target 和 `candidate-only-no-promotion` boundary。
- 如写入 candidate gap wiki，已运行 `enrich-gap-candidates`、`gap-review-package` 和 `govern-vault`，并且 candidate `health`、`lint` 和 `build-graph` 均通过或给出明确 repair action。
- 如用户批准晋升，`promote-gap-candidates` 已生成 reviewed concept pages，并且 reviewed `health`、`build-reviewed-graph`、`query-reviewed` 均通过。
- 如用户要求 full pipeline smoke，使用 `pipeline-smoke -InputPath <raw> -Reviewer <reviewer> -ApprovalNote <note> -Question <query>`；通过标准是 candidate gates、promotion、vault governance、reviewed health、reviewed graph 和 reviewed query 全部通过，且 query 命中新晋升 reviewed target。
- 未经用户明确批准，不写入 reviewed Knowledge、Memory、Project Fact 或 Harness architecture authority。
