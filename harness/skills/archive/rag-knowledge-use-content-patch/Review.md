---
documentName: harness/skills/archive/rag-knowledge-use-content-patch/Review.md
version: v1.0.0
updatedAt: 2026-10-29
status: archived
purpose: 审核用户纠正触发的 reviewed 正文查询流程补丁。
scope:
  - skill-patch-review
prerequisites:
  - harness/skills/SkillPolicy.md
relatedDocuments:
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/tools/docs/command-surfaces/RagDocumentPipeline.md
outputTo:
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
owner: mixed
reviewAfter: source-updated
supersededBy: harness/skills/reviewed/rag-knowledge-use/SKILL.md
dependsOn:
  - harness/tools/scripts/stable/test-rag-tools.ps1
review:
  reviewedBy: agent
  reviewedAt: 2026-10-29
  decision: approved-and-merged-after-47-regressions-and-reviewed-only-query-validation
---

# 查询流程补丁审核

触发：用户指出只找到目录、依靠原PDF得到答案不符合RAG目标，并明确要求修复。采用现有Skill补丁，不新建同类Skill。

拟修订：查询返回实质条款及reviewed行号；内容不足判为知识缺口，原件核验放在摄取补强流程；晋升验证增加正文覆盖与仅开放reviewed的问答回归；版本判断区分发布日期、实施日期与知识维护日期。

授权：已有本轮修复指令；例行治理审核与回归通过后合入。此记录不宣称用户完成最终验收或授权无关知识晋升。

验证：稳定工具正反例、实际reviewed-only查询、符号边界及版本日期测试。实际来源与正文留在用户和运行态边界。


审核结果：测试与读取隔离通过，补丁已合入现有 reviewed Skill；本记录归档，不作为新Skill或真实知识事实源。
