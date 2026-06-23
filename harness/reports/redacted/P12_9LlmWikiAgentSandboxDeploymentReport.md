---
documentName: P12_9LlmWikiAgentSandboxDeploymentReport.md
version: v1.0.0-pre-h8-report-archive
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: archived
purpose: 记录 LLM Wiki Agent 沙盒 PoC 的历史分析和可吸收方法；当前知识晋升规则以 Governance 和 RAG 机制文档为准。
scope:
  - redacted-historical-report
  - non-authoritative-evidence
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/governance/ReportArchivePolicy.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/reports/redacted/P12_9LlmWikiAgentSandboxDeploymentReport.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/governance/ReportArchivePolicy.md
review:
  reviewedBy: mixed
  reviewedAt: 2026-06-23
  decision: pre-h8-report-archive-frontmatter-alignment
---
# P12.9 LLM Wiki Agent 沙盒部署分析报告

# P12.9 LLM Wiki Agent 沙盒部署分析报告

## 1. 结论

`KKT-OPT/llm-wiki-agent` 更适合作为“知识库建立方法”和 agent 维护协议，而不是作为 Harness 的新知识库本体。它的核心价值不在向量库或服务端，而在一套稳定的 Markdown wiki 编译规则：raw source、source page、entity page、concept page、overview、log、wikilink graph 和 lint/health。

Harness 应吸收其方法，而不是照搬任一具体 agent 的部署方式。建议定位为：

```text
external method/tooling -> Harness structured ingestion -> extracted artifacts -> candidate wiki knowledge -> review -> reviewed knowledge -> rebuildable index
```

本次 PoC 已在沙盒内跑通：依赖安装、TXT/Markdown/PDF 转换、候选 wiki 生成、结构健康检查、断链校验和图谱构建均通过。

## 2. 官方方法分析

官方 README 的使用模型是：把原始资料放进 `raw/`，让 coding agent 根据 `AGENTS.md`、`CLAUDE.md` 或 `GEMINI.md` 维护 `wiki/`。不同 runtime 的入口文件不同，但 wiki 规则一致。

官方值得借鉴的部分：

- `raw/` 不直接变成事实，而是经 agent 整理为 `wiki/sources/`。
- 每个来源生成 source page，反复出现的对象生成 entity page，关键思想生成 concept page。
- `wiki/overview.md` 是随语料增长更新的综合页。
- `wiki/log.md` 是 append-only 操作记录。
- `[[wikilink]]` 让人类可读知识自然形成 graph。
- `health.py` 提供零 LLM 调用的结构健康检查。
- `build_graph.py --no-infer` 可以只从显式 wikilink 生成可重建图谱。
- MarkItDown、tqdm、PyMuPDF4LLM 可作为离线提取层工具。

不应照搬的部分：

- 不应把官方 `AGENTS.md` 作为 Harness 根入口；Harness 已有统一入口和治理边界。
- 不应把 `wiki/` 直接当成 reviewed Knowledge；它只能先进入 `rag/knowledge/candidate`。
- 不应默认使用官方 `ingest.py`、`query.py`、`lint.py` 的 LLM API 路径；这些脚本通过 `litellm` 调模型，和当前 Harness P12.9 离线 PoC 边界不一致。
- 不应把 graph/cache 当作事实源；它们属于 `var/rag` 可重建运行态。
- 不应把具体 Codex、Claude Code、Gemini CLI 的安装建议写成 Harness 通用部署要求。

## 3. Harness 部署方案

本次采用以下落点：

| 层 | 路径 | 说明 |
|---|---|---|
| 外部方法仓库 | `tools/external/llm-wiki-agent` | ignored，本地外部工具副本，不进入 Harness git 历史 |
| PoC 工作区 | `var/rag/llm-wiki-agent-poc/work` | ignored，可重建运行态 |
| Python venv | `var/rag/venvs/llm-wiki-agent` | ignored，安装转换依赖 |
| raw 样例 | `rag/knowledge/raw/llm-wiki-agent-poc` | 合成、非敏感输入 |
| extracted | `rag/knowledge/extracted/llm-wiki-agent-poc` | Markdown、manifest、chunks、extraction report |
| candidate wiki | `rag/knowledge/candidate/llm-wiki-agent-poc/wiki` | agent 生成的候选 wiki，不是 reviewed knowledge |
| eval | `rag/evals/llm-wiki-agent-poc` | 图谱健康报告等评估输出 |
| graph runtime | `var/rag/llm-wiki-agent-poc/work/graph` | 可重建图谱 JSON/HTML/cache |

安装的关键依赖：

| Package | Version | 用途 |
|---|---:|---|
| markitdown | 0.1.6 | 多格式转 Markdown |
| tqdm | 4.68.2 | 批量转换进度 |
| pymupdf4llm | 1.27.2.3 | PDF 转 Markdown |
| PyMuPDF | 1.27.2.3 | PDF 运行依赖 |
| networkx | 3.6.1 | graph report 社群和连通性分析 |

## 4. 跑通案例

案例输入是三份合成资料：

- Markdown：Harness 知识方法说明。
- TXT：部署 checklist，经 MarkItDown + tqdm 转成 Markdown。
- PDF：本地生成的 PoC PDF，经 PyMuPDF4LLM 转成 Markdown。

关键命令：

```powershell
$env:PYTHONUTF8='1'
$py = '<HARNESS_ROOT>\var\rag\venvs\llm-wiki-agent\Scripts\python.exe'
& $py tools/file_to_md.py --input_dir raw/imports
& $py tools/pdf2md.py raw/papers/harness-wiki-poc.pdf --backend pymupdf4llm --output raw/papers/harness-wiki-poc.md
& $py tools/health.py --json
& $py tools/ingest.py --validate-only
& $py tools/build_graph.py --no-infer --report --save
```

验证结果：

| 检查 | 结果 |
|---|---|
| dependency import | passed |
| MarkItDown + tqdm TXT conversion | passed |
| PyMuPDF4LLM PDF conversion | passed |
| official health check | passed，9 pages，0 empty，index sync clean，log coverage clean |
| official validate-only | passed，无 broken wikilinks，全部 pages indexed |
| official graph build | passed，9 nodes，26 deduplicated edges，0 orphan nodes |

## 5. Windows 注意事项

官方脚本会打印 `✓`、箭头和 emoji。在 Windows 默认 GBK 控制台下，`pdf2md.py` 成功写出文件后可能因打印 Unicode 符号触发 `UnicodeEncodeError`。设置：

```powershell
$env:PYTHONUTF8='1'
```

即可让同一步成功结束。这应作为未来工具包装的兼容性要求。

## 6. 治理判断

本次不做以下事情：

- 不把候选 wiki 晋升到 `rag/knowledge/reviewed`。
- 不更新 Harness 最终架构。
- 不新增 reviewed Memory 或 Skill。
- 不选择 vector store。
- 不把官方仓库复制进可跟踪源码历史。

建议进入 review 的候选：

| 类型 | 候选 | 建议 |
|---|---|---|
| Tool Asset | `invoke-rag-structured-ingestion.ps1` 或等价 wrapper | review 后再进入 stable |
| Knowledge | `rag/knowledge/candidate/llm-wiki-agent-poc/wiki` | 人工 review 后按需晋升 |
| Governance | Windows `PYTHONUTF8=1` 运行约束 | 可进入 RAG 工具说明 |
| RAG | LLM Wiki Agent 方法作为 P12.9 structured ingestion 候选方法 | defer/review |

## 7. Sources

- [KKT-OPT/llm-wiki-agent](https://github.com/KKT-OPT/llm-wiki-agent)
- [microsoft/markitdown](https://github.com/microsoft/markitdown)
- [tqdm/tqdm](https://github.com/tqdm/tqdm)
- [PyMuPDF4LLM / pymupdf RAG link used by upstream README](https://github.com/pymupdf/RAG)
