---
documentName: harness/rag/evals/README.md
version: v1.1.0-query-evaluation-boundary
updatedAt: 2026-10-29
status: active
purpose: 说明 RAG evaluation 模板和运行态 eval report 的分离边界。
scope:
  - rag-evaluation
  - runtime-evidence-boundary
prerequisites:
  - AGENTS.md
  - harness/rag/RAGIndex.md
relatedDocuments:
  - harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
  - harness/rag/RAGIndex.md
  - harness/rag/policies/README.md
outputTo:
  - harness/rag/evals/README.md
owner: mixed
reviewAfter: '2026-11-29'
supersededBy: null
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: user
  reviewedAt: '2026-10-29'
  decision: user-approved-rag-assets-and-evaluation-boundary-with-implementation-regression
---

# RAG Eval

本目录保存 RAG evaluation 模板、检查维度和非私有示例。

运行时生成的 health report、lint report、graph report、graph JSON、graph HTML、embedding、index 和 cache 应写入：

```text
var/rag/<run-id>/
```

这些运行态产物可重建，不是事实源，不进入通用 Harness Git。

## 查询评测来源边界

被测试的知识版本与来源范围先固定。默认纯库模式只从 reviewed 获取事实和版本证据，允许库内推理；网页、原件及图像不能补答。正式混合使用允许分别归属外部来源，但不能计作纯库通过。详见 [评测策略](../policies/KnowledgeQueryEvaluationPolicy.md)。

模板 [QueryEvaluationRecord.example.json](QueryEvaluationRecord.example.json) 故意保持不完整状态；复制后必须按真实事件和知识文件补齐，不能只修改complete字段取得通过。记录保存在var边界，使用 `audit-query-evaluation -EvaluationRecord <record.json>`。输入记录校验不等于运行时完整采集或真实性证明。

检查来源召回、逻辑条款完整性、数值/单位/边界、版本适用性、原问题与补充查询耗时、整轮工具来源和证据完整性。局部函数I/O结果不能代替整轮审计。未知、失败、无效和混合使用分别记录；来源越界的旧测试保留原证据，不通过修改报告变成新复测。
