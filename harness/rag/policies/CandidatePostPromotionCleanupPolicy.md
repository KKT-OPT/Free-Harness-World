---
documentName: harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
version: v1.1.1-reviewed-skill-link
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: active
purpose: 定义 Knowledge candidate 完成生命周期后的 full corpus 清理规则、审计保留方式和稳定命令边界。
scope:
  - rag-policy
  - candidate-knowledge
  - post-promotion-cleanup
  - obsidian-graph-boundary
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
relatedDocuments:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/README.md
  - harness/rag/policies/ObsidianLlmWikiPluginBoundary.md
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - user/knowledge/README.md
outputTo:
  - harness/rag/policies/CandidatePostPromotionCleanupPolicy.md
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
# Candidate 晋升后清理策略

本文定义 candidate knowledge 在晋升、拒绝、合并、归档或判定为 evidence-only 后的清理规则。目标是让 `user/knowledge/` 的 Obsidian 图谱默认只暴露 active review、reviewed Knowledge 和轻量审计记录，不长期保留已经完成生命周期的 full candidate corpus。

## 1. 规则

1. Active review candidate 可以暂时保留在 `user/knowledge/candidate/<run-id>/wiki`。
2. Candidate 完成生命周期后，full corpus 默认移出 Obsidian vault 或删除。
3. 晋升后的保留物应是轻量审计记录，不是完整 candidate wiki 正文。
4. 轻量审计记录至少保留 corpus id、source fingerprint、content hash、review decision、reviewer、reviewedAt、原路径、备份路径和必要 provenance。
5. 如果 reviewed source trace、registry、Home 或 report 仍引用 full corpus 路径，必须先改写到轻量审计记录，再执行移动或删除。
6. `candidate/_archive/` 不是长期垃圾站；它只允许保留 archive index、轻量审计例外、过渡期 full corpus 和用户明确要求保留的例外。
7. 实际删除或移出 vault 必须先有 dry-run report、用户明确批准和清理后的 validation 回归。

## 2. 稳定命令

Dry-run 命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root <HARNESS_ROOT> -Command candidate-cleanup-plan
```

Apply 命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root <HARNESS_ROOT> -Command candidate-cleanup-apply -Reviewer <reviewer> -ApprovalNote <approval-note>
```

默认报告：

```text
var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-plan.md
var/rag/reviewed-knowledge/evals/candidate-post-promotion-cleanup-apply.md
```

`candidate-cleanup-plan` 只读：不删除、不移动、不改写 reviewed Knowledge、不执行 promotion。它盘点 active candidate、archived full corpus、轻量审计记录、wikilink 数量、reviewed/Home/registry 引用，并给出 recommended action。

`candidate-cleanup-apply` 需要 reviewer 和 approval note。它将 post-promotion full candidate corpus 移出 `user/knowledge` vault，写入 `var/rag/candidate-full-corpus-archive/` 运行态备份，在 `user/knowledge/candidate/_audit/post-promotion/` 保留轻量审计记录，改写 reviewed/Home/registry 中指向 full corpus 的路径，并更新 Obsidian graph filter。它不执行 reviewed promotion。

## 3. 推荐动作

| 动作 | 含义 |
|---|---|
| `keep-active-review-in-candidate-boundary` | 当前仍是 active review candidate，保留在 candidate boundary。 |
| `keep-lightweight-audit-record` | 当前对象已经是轻量审计记录，可以保留。 |
| `rewrite-source-trace-to-audit-record-before-removal` | reviewed 或 registry 仍引用 full corpus；先把 source trace 改写到轻量审计记录。 |
| `compact-to-audit-record-and-remove-full-corpus-from-vault` | full corpus 生命周期已经完成，保留审计摘要后移出 Obsidian vault 或删除。 |

## 4. 验收

完成清理时应满足：

1. `candidate-cleanup-plan` 执行通过并生成 report。
2. `candidate-cleanup-apply` 只在用户批准后执行。
3. 清理后 `candidate-cleanup-plan` 中 `fullCorpusCandidateCount` 为 0，`recommendedCleanupActionCount` 为 0。
4. `user/knowledge/candidate/_audit/post-promotion/` 保存轻量审计记录。
5. `validate-knowledge-vault` 回归通过，blocking issues 为 0。
6. Obsidian `graph.json` 默认排除 `candidate/`、`raw/` 和 `.obsidian/`。
