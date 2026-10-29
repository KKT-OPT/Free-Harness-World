---
documentName: harness/rag/evals/README.md
version: v1.2.0-frozen-batch-regression
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
reviewAfter: 2026-11-29
supersededBy: null
dependsOn:
  - harness/rag/RAGIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: user-requested-batch-tool-consolidation-reviewed
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


## 建设后已知用例回归

[QueryRegressionCases.example.json](QueryRegressionCases.example.json)用于`query-regression -Cases <private-cases.json> -RunId <new-run>`。复制后按实际reviewed内容填写问题、目标、完整条件、表格单元格和版本断言；模板不是可直接验收的真实用例。断言留在数据配置中，工具不内置领域答案。

该命令冻结reviewed与用例文件，独立Python工作进程执行相同检索实现，并保存引用和guard记录。任何reviewed新增、删除或改动均使基线失效；失败、断言修正和知识补强以新RunId分别留存。机器检查只证明规定断言、引用和局部读取边界，不证明全答案语义正确，也不能替代整轮`audit-query-evaluation`。
