---
documentName: harness/skills/candidate/rag-structured-ingestion/references/obsidian-review.md
version: v1.2.1-candidate-path-normalized
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 说明如何使用 Obsidian 审查 local-only candidate knowledge。
scope:
  - obsidian-review
  - candidate-knowledge
prerequisites:
  - harness/skills/candidate/rag-structured-ingestion/SKILL.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
outputTo:
  - harness/skills/candidate/rag-structured-ingestion/references/obsidian-review.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/skills/candidate/rag-structured-ingestion/SKILL.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-05
  decision: moved-to-candidate-skill-boundary
---
# Obsidian 候选知识审查

当人类希望在 Obsidian 中检查 candidate knowledge 后再决定 promotion 时，使用本文。

## 1. 推荐打开范围

可以打开 Harness Root，也可以只打开：

```text
user/knowledge/candidate/<run-id>/wiki
```

不要把 Obsidian workspace files 当作事实源。`.obsidian/workspace*.json`、graph settings、plugin runtime files 和 cache 都是 editor state。

## 2. Review Workflow

1. 从 `index.md` 开始，再读 `overview.md`。
2. 打开 `sources/` 下的每个页面，并与 `var/rag/<run-id>/extracted/` 中的 extracted Markdown 对照。
3. 使用 backlinks 和 graph view 检查 isolated pages、missing concepts 和 weak connections。
4. 检查每个 source page 的 summary、key claims、contradictions、applicability、sensitive content 和 usage-rights risk。
5. 在 candidate pages 中加入 review notes，或要求 agent 更新。
6. 只批准 source-grounded、scoped、non-sensitive 且长期有用的 statement。

## 3. Promotion Boundary

raw-to-candidate Skill 在 promotion 前停止。Human review 可以产生 feedback、requested edits 或单独的 promotion request。

promotion approval 应在后续 workflow 中明确表达，例如：

```text
Promote candidate <path> to reviewed knowledge under scope global/domain/project-reviewed.
```

审批后，agent 应优先使用稳定命令：

```text
harness/tools/scripts/stable/invoke-rag-candidate.ps1 -Command promote-reviewed
```

创建 reviewed knowledge，并保留 reviewer、approval note、reviewAfter、source trace 和 promotion result。`harness/templates/knowledge/ReviewedKnowledgeTemplate.md` 是输出结构参考，不再要求 agent 每次手工套模板。
