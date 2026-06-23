---
name: rag-structured-ingestion
description: Convert user-provided raw or unstructured material into Harness RAG runtime artifacts and local-only candidate knowledge. Use when the user asks to ingest raw files, convert PDFs/Office/TXT/Markdown into candidate wiki pages, run raw-to-candidate health/lint/graph/query/stale-plan checks, or prepare Obsidian-reviewable candidate notes before reviewed-knowledge approval.
documentName: harness/skills/rag-structured-ingestion/SKILL.md
version: v1.0.0-h6-rag-boundary
updatedAt: 2026-06-22 23:41:15.773 +08:00
status: active
purpose: 定义 raw-to-candidate RAG Skill 的执行边界、稳定命令和输出路径。
scope:
  - rag-skill
  - raw-to-candidate
  - candidate-knowledge
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/RAGIndex.md
  - user/knowledge/README.md
  - harness/governance/KnowledgePromotionPolicy.md
outputTo:
  - harness/skills/rag-structured-ingestion/SKILL.md
owner: mixed
reviewAfter: 2026-07-22
supersededBy:
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-22
  decision: h6-complete
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

不要写入 reviewed Knowledge、active Memory、Project Facts 或 reviewed Skill。用户要求 promotion 时，本 Skill 应停在 candidate evidence，并要求单独的 explicit approval workflow。

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
| `lint` | 检查 broken links、orphans 和 sparse pages。 |
| `build-graph` | 从 wikilinks 重建 graph JSON / HTML。 |
| `query` | 对 candidate pages 做 keyword lookup。 |
| `stale-plan` | 比较 manifest source hash，只输出 changed / missing 计划。 |

## 4. 流程

1. 读取 Harness entry、RAG policy 和本 Skill，把 raw files 视为 unreviewed source material。
2. 使用 `invoke-rag-candidate.ps1 -Command ingest` 运行摄取。
3. 读取 status JSON path 和 candidate wiki path。
4. 需要可审查候选语料时，再按 `references/candidate-enrichment.md` 补全 candidate pages。
5. agent 编辑 candidate pages 后，重新运行 `health`、`lint` 和 `build-graph`。
6. 用户提问时，`query` 只用于找页面；最终回答必须阅读页面并引用来源。
7. 更新检查使用 `stale-plan`，先报告 changed / missing sources，再做 refresh 或 archive。
8. 收尾时说明 candidate paths、validation state、known gaps，并明确没有写入 reviewed knowledge。

## 5. 输出

- `user/knowledge/raw/<run-id>/`，仅在显式 `-CopyRaw` 时写入；
- `var/rag/<run-id>/extracted/metadata-manifest.json`；
- `var/rag/<run-id>/extracted/chunks.jsonl`；
- `var/rag/<run-id>/extracted/extraction-report.md`；
- `user/knowledge/candidate/<run-id>/wiki`；
- `var/rag/<run-id>/evals/health-report.md`；
- `var/rag/<run-id>/evals/lint-report.md`；
- `var/rag/<run-id>/evals/graph-report.md`；
- `var/rag/<run-id>/graph`；
- `var/logs/<run-id>.json`。

## 6. 完成标准

- 使用 stable wrapper，而不是 ad hoc Python command。
- runtime extracted artifacts、candidate wiki、eval reports、graph output 和 status JSON 均存在。
- candidate pages 有 source provenance 和可供 human / agent review 的 wikilinks。
- agent 编辑后已重新运行 `health`、`lint` 和 `build-graph`。
- partial state 有具体 report path 和 repair action。
- 没有写入 reviewed Knowledge、Memory、Project Fact 或 promotion artifact。

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
