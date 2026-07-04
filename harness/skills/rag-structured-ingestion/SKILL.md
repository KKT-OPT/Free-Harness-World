---
name: rag-structured-ingestion
description: Convert user-provided raw or unstructured material into Harness RAG runtime artifacts and local-only candidate knowledge, and after explicit approval promote candidate evidence into reviewed Knowledge. Use when the user asks to ingest raw files, convert PDFs/Office/TXT/Markdown into candidate wiki pages, run raw-to-candidate health/lint/graph/query/enrichment-plan/review-package/promotion-plan/promote-reviewed/stale-plan checks, or prepare Obsidian-reviewable candidate notes before reviewed-knowledge approval.
documentName: harness/skills/rag-structured-ingestion/SKILL.md
version: v1.6.1-reviewed-knowledge-use-handoff
updatedAt: 2026-07-04 00:00:00.000 +08:00
status: active
purpose: 定义 raw-to-candidate RAG Skill 的执行边界、稳定命令和输出路径。
scope:
  - rag-skill
  - raw-to-candidate
  - candidate-knowledge
  - reviewed-knowledge-promotion
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/rag/policies/LlmWikiMechanismAbsorptionPolicy.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
outputTo:
  - harness/skills/rag-structured-ingestion/SKILL.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-04
  decision: rag-knowledge-use-reviewed-handoff-updated
---
# RAG 结构化摄取 Skill

## 1. 边界

本 Skill 只执行 raw-to-candidate workflow：

```text
raw source
-> runtime extracted artifacts
-> local-only candidate wiki
-> health / lint / graph evidence
```

默认不要写入 reviewed Knowledge、active Memory、Project Facts 或 reviewed Skill。用户明确批准 promotion 后，本 Skill 只允许通过稳定命令 `promote-reviewed` 从已通过 review gates 的 candidate evidence 写入 reviewed Knowledge。

## 2. 输入

| 输入 | 是否必需 | 说明 |
|---|---|---|
| raw path(s) | yes | 文件、文件夹或 glob。支持 Markdown、PDF、Office、HTML、TXT、CSV、JSON、XML、RST、EPUB、notebook、YAML、TSV、WAV、MP3。 |
| run id | no | 用户给出 named corpus 或测试用例时使用稳定 kebab-case run id。 |
| candidate wiki path | checks 需要 | 默认 `user/knowledge/candidate/<run-id>/wiki`。 |
| question | query 需要 | 仅做 keyword lookup；agent 必须阅读命中的页面后再综合。 |

## 3. 稳定命令门面

使用 stable wrapper；它设置 `PYTHONUTF8=1`，查找本地 RAG venv，并调用 Python subcommands。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root <HARNESS_ROOT> `
  -Command ingest `
  -InputPath <raw-path> `
  -RunId <run-id>
```

常用 subcommands：

| Command | 用途 |
|---|---|
| `ingest` | 转换 raw files，生成 runtime extracted artifacts、candidate wiki、eval reports 和 graph runtime。 |
| `health` | 检查空页、index/log 同步和敏感模式。 |
| `lint` | 检查 broken links、orphans、sparse pages、phantom hubs 和 duplicate titles。 |
| `build-graph` | 从 wikilinks 重建 graph JSON / HTML，并输出 graph health。 |
| `query` | 对 candidate pages 做 graph-aware keyword lookup。 |
| `enrichment-plan` | 根据 manifest 和 candidate wiki 输出 agent enrichment checklist。 |
| `review-package` | 生成 human review package，汇总 provenance、validation、page inventory 和 review gates。 |
| `promotion-plan` | 生成 reviewed Knowledge 晋升计划和阻塞原因；不写入 reviewed Knowledge。 |
| `promote-reviewed` | 用户明确批准后写入 reviewed Knowledge，并生成 promotion result。 |
| `stale-plan` | 比较 manifest source hash，只输出 changed / missing 计划。 |

## 4. 流程

1. 读取 Harness entry、RAG policy 和本 Skill，把 raw files 视为 unreviewed source material。
2. 使用 `invoke-rag-candidate.ps1 -Command ingest` 运行摄取。
3. 读取 status JSON path、metadata manifest 和 candidate wiki path；manifest 应记录 source gate、source fingerprint、domain schema、extraction granularity、entity/concept cap、batch strategy 和 tag vocabulary。
4. 需要可审查候选语料时，先运行 `enrichment-plan`，再按 `references/candidate-enrichment.md` 补全 candidate pages。
5. agent 编辑 candidate pages 后，重新运行 `health`、`lint` 和 `build-graph`。
6. 用户提问时，`query` 只用于找页面；最终回答必须阅读页面并引用来源。
7. 候选页面通过验证后，运行 `review-package` 生成审核包。
8. 需要进入晋升讨论时，运行 `promotion-plan` 生成计划；没有用户明确批准时不得写入 reviewed Knowledge。
9. 用户明确表示审核通过后，运行 `promote-reviewed` 写入 reviewed Knowledge，并记录 reviewer、approval note、reviewAfter 和 promotion result。
10. 用户需要查询、阅读或用 Obsidian 查看 reviewed Knowledge 时，转入 `harness/skills/reviewed/rag-knowledge-use/SKILL.md` 的 reviewed Knowledge use workflow。
11. 更新检查使用 `stale-plan`，先报告 changed / missing sources，再做 refresh 或 archive。
12. 收尾时说明 candidate paths、reviewed target、validation state、known gaps 和是否写入 reviewed knowledge。

执行 raw-to-candidate 前应先判断 source gate：空文件、frontmatter-only、不兼容类型和重复 body hash 不应继续进入 LLM 提取；同名 source 应使用 path fingerprint 和 content hash 防止覆盖或混淆。Candidate tags 必须来自目标 domain schema 或 review package 中的受控 tag vocabulary。

Human-facing reports，中文解释是面向人类审核的报告，例如 `enrichment-plan.md`、`review-package.md` 和 `promotion-plan.md`，必须使用中文作为主说明语言；允许保留 command、path、status code、frontmatter key 和专业术语英文。

## 5. 输出

- `user/knowledge/raw/<domain>/`，仅在显式 `-CopyRaw -RawDomain <domain>` 时写入；未确定 domain 的临时 run-id copy 不得作为最终 raw 布局；
- `var/rag/<run-id>/extracted/metadata-manifest.json`；
- `var/rag/<run-id>/extracted/chunks.jsonl`；
- `var/rag/<run-id>/extracted/extraction-report.md`；
- `user/knowledge/candidate/<run-id>/wiki`；
- `var/rag/<run-id>/evals/health-report.md`；
- `var/rag/<run-id>/evals/lint-report.md`；
- `var/rag/<run-id>/evals/graph-report.md`；
- `var/rag/<run-id>/evals/enrichment-plan.md`，仅在显式运行 `enrichment-plan` 时写入；
- `var/rag/<run-id>/evals/review-package.md`，仅在显式运行 `review-package` 时写入；
- `var/rag/<run-id>/evals/promotion-plan.md`，仅在显式运行 `promotion-plan` 时写入；
- `user/knowledge/reviewed/<domain>/<semantic-page>.md`，仅在用户明确批准后运行 `promote-reviewed` 时写入；正式 reviewed page 不使用 smoke、pipeline 或 run id 命名；
- `var/rag/<run-id>/evals/promotion-result.md`，仅在显式运行 `promote-reviewed` 时写入；
- `var/rag/<run-id>/graph`；
- `var/logs/<run-id>.json`。

## 6. 完成标准

- 使用 stable wrapper，而不是 ad hoc Python command。
- runtime extracted artifacts、candidate wiki、eval reports、graph output 和 status JSON 均存在。
- candidate pages 有 source provenance 和可供 human / agent review 的 wikilinks。
- 需要 agent enrichment 时，先生成 `enrichment-plan`，再编辑 candidate pages。
- agent 编辑后已重新运行 `health`、`lint` 和 `build-graph`。
- 用户审核前已生成 `review-package`。
- promotion 前只能生成 `promotion-plan`；没有 explicit approval 不得写入 reviewed Knowledge。
- explicit approval 后，`promote-reviewed` 必须成功生成 reviewed Knowledge、promotion result，并更新 status JSON。
- 面向人类审核的报告为中文主文档，英文只作为关键词、状态码或路径保留。
- partial state 有具体 report path 和 repair action。
- 未获批准时没有写入 reviewed Knowledge、Memory、Project Fact 或 promotion artifact；获批晋升时只写入 reviewed Knowledge 和 promotion result。

## 7. 常见风险

- 不要把 chunks、graph JSON 或 generated candidate pages 当作 authoritative knowledge。
- 不要 ingest credentials、auth files、private settings 或 unredacted logs。
- 不要自动晋升 private、copyrighted、contradictory 或 low-confidence material。
- 不要把 external agent-specific setup 写入 Harness entry files。
- 不要只根据 `query` 输出回答，必须阅读命中页面。

## 8. 参考文件

- `harness/skills/rag-structured-ingestion/references/candidate-enrichment.md`
- `harness/skills/rag-structured-ingestion/references/obsidian-review.md`
- `harness/tools/scripts/stable/invoke-rag-candidate.ps1`
- `harness/tools/scripts/stable/rag_candidate/`
