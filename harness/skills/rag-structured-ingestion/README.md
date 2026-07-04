---
documentName: harness/skills/rag-structured-ingestion/README.md
version: v1.4.0-source-centered-raw-boundary
updatedAt: 2026-07-03 16:45:00.000 +08:00
status: active
purpose: 说明 RAG structured ingestion Skill 的定位、使用方式和 H6 后输出边界。
scope:
  - rag-skill
  - human-guide
  - candidate-knowledge
  - reviewed-knowledge-promotion
prerequisites:
  - AGENTS.md
  - harness/skills/rag-structured-ingestion/SKILL.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
  - harness/governance/KnowledgePromotionPolicy.md
outputTo:
  - harness/skills/rag-structured-ingestion/README.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-03
  decision: source-centered-raw-boundary-added
---
# RAG 结构化摄取使用手册

本文是 `rag-structured-ingestion` Skill 的人类使用手册。它负责 raw-to-candidate knowledge workflow，中文可理解为“原始资料到候选知识的结构化转换流程”；在用户明确批准后，也提供受控的 reviewed Knowledge promotion command。

## 1. 定位

流程如下：

```text
raw source
-> extracted artifacts
-> candidate wiki
-> health / lint / graph evidence
```

本 Skill 不负责把内容自动晋升为 reviewed knowledge。Promotion，中文解释是晋升，必须由单独的 human review / governance workflow 处理。

用户明确表示审核通过后，可以使用本 Skill 的 `promote-reviewed` 命令完成受控写入。该命令不是默认自动晋升路径。

## 2. 使用场景

适合：

- 用户提供 raw path，希望转换成可审查的 candidate knowledge；
- 处理 PDF、DOCX、PPTX、TXT、Markdown、HTML 等材料；
- 生成 Obsidian-friendly candidate wiki；
- 运行 `health`、`lint`、`build-graph`、`query`、`enrichment-plan`、`review-package`、`promotion-plan` 或 `stale-plan`。
- 用户明确批准后，把已通过 gates 的 candidate wiki 晋升为 reviewed Knowledge。

不适合：

- 未经 explicit approval 写入 reviewed Knowledge；
- 创建 reviewed Memory、Project Fact、reviewed Skill 或正式治理规则；
- 把 RAG Index、graph JSON、chunks JSONL 当成事实源；
- 摄入 credentials、auth files、private settings、raw logs 或未脱敏运行记录。

## 3. 常用命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command ingest `
  -InputPath <raw-path> `
  -RunId <run-id>
```

示例：补全候选 wiki 后重新验证。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command enrichment-plan `
  -Manifest var\rag\<run-id>\extracted\metadata-manifest.json `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Report var\rag\<run-id>\evals\enrichment-plan.md `
  -RunId <run-id>
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command health `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Report var\rag\<run-id>\evals\health-report.md `
  -RunId <run-id>
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command lint `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Report var\rag\<run-id>\evals\lint-report.md `
  -RunId <run-id>
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command build-graph `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Graph var\rag\<run-id>\graph `
  -Report var\rag\<run-id>\evals\graph-report.md `
  -RunId <run-id>
```

示例：生成 human review package。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command review-package `
  -Manifest var\rag\<run-id>\extracted\metadata-manifest.json `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Report var\rag\<run-id>\evals\review-package.md `
  -RunId <run-id>
```

示例：生成 promotion plan，但不写入 reviewed knowledge。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command promotion-plan `
  -Manifest var\rag\<run-id>\extracted\metadata-manifest.json `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Scope user-private `
  -Target user\knowledge\reviewed\<domain>\<semantic-page>.md `
  -Report var\rag\<run-id>\evals\promotion-plan.md `
  -RunId <run-id>
```

示例：用户明确审核通过后，写入 reviewed Knowledge 并生成 promotion result。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command promote-reviewed `
  -Manifest var\rag\<run-id>\extracted\metadata-manifest.json `
  -Wiki user\knowledge\candidate\<run-id>\wiki `
  -Scope user-private `
  -Target user\knowledge\reviewed\<domain>\<semantic-page>.md `
  -Reviewer <reviewer> `
  -ApprovalNote "<approval-note>" `
  -ReviewAfter source-updated-or-2026-12-31 `
  -Report var\rag\<run-id>\evals\promotion-result.md `
  -RunId <run-id>
```

## 4. 输出目录

| 输出 | 说明 |
|---|---|
| `user/knowledge/raw/<domain>/` | `-CopyRaw -RawDomain <domain>` 时保存 raw source，local-only；未确定 domain 的临时 run-id copy 不作为最终 raw 布局。 |
| `var/rag/<run-id>/extracted/metadata-manifest.json` | Metadata Manifest。 |
| `var/rag/<run-id>/extracted/chunks.jsonl` | Rebuildable chunks。 |
| `var/rag/<run-id>/extracted/extraction-report.md` | Extraction Report。 |
| `user/knowledge/candidate/<run-id>/wiki` | Candidate Wiki，local-only。 |
| `var/rag/<run-id>/evals/health-report.md` | Health Report。 |
| `var/rag/<run-id>/evals/lint-report.md` | Lint Report。 |
| `var/rag/<run-id>/evals/graph-report.md` | Graph Report。 |
| `var/rag/<run-id>/evals/enrichment-plan.md` | Candidate Enrichment Plan，显式运行 `enrichment-plan` 时生成。 |
| `var/rag/<run-id>/evals/review-package.md` | Human Review Package，显式运行 `review-package` 时生成。 |
| `var/rag/<run-id>/evals/promotion-plan.md` | Promotion Plan，显式运行 `promotion-plan` 时生成，不代表已批准。 |
| `user/knowledge/reviewed/<domain>/<semantic-page>.md` | Reviewed Knowledge，只有用户明确批准后运行 `promote-reviewed` 才生成；正式 reviewed page 不使用 smoke、pipeline 或 run id 命名。 |
| `var/rag/<run-id>/evals/promotion-result.md` | Promotion Result，记录 reviewer、approval note、target 和 gates。 |
| `var/logs/<run-id>.json` | Status JSON。 |
| `var/rag/<run-id>/graph` | Runtime graph。 |

## 5. 候选知识补全

`ingest` 生成的 candidate wiki 可能只是 scaffold。若用户需要“待评估的结构化候选知识”，agent 应继续执行 candidate enrichment：

- 先运行 `enrichment-plan`，生成 source-grounded checklist；
- 阅读 extracted Markdown 和 manifest；
- 更新 source page 的 summary、key claims、concepts、entities、contradictions、applicability；
- 只在有复用价值时创建 `concepts/` 和 `entities/`；
- 更新 `overview.md`、`index.md` 和 `log.md`；
- 重新运行 `health`、`lint` 和 `build-graph`。
- 运行 `review-package`，供 human review 使用；
- 只有用户明确批准 promotion 时，才运行 `promote-reviewed` 进入 reviewed Knowledge 写入 workflow。

详细规则见：

```text
harness/skills/rag-structured-ingestion/references/candidate-enrichment.md
```

## 6. 关键边界

- Candidate Knowledge 不是 authoritative knowledge。
- RAG Index / graph / chunks 是 rebuildable runtime artifacts，不是 source of truth。
- Source-grounded enrichment 可以由 agent 完成，但 Promotion 必须由 human review 或 explicit approval 驱动，并通过稳定命令记录审批证据。
- 不要把本机绝对路径、credentials、private settings 或 raw logs 写入 tracked docs。

## 7. 报告语言

面向人类审核的 reports 应使用中文作为主说明语言，包括：

- `enrichment-plan.md`
- `review-package.md`
- `promotion-plan.md`
- `promotion-result.md`

允许保留 English keywords / terms，例如 `Candidate Wiki`、`Manifest`、`reviewed Knowledge`、status code、命令、路径和 YAML key。
