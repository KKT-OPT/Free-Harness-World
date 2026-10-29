---
documentName: harness/skills/archive/rag-knowledge-use-evaluation-patch/Review.md
version: v1.0.0
updatedAt: 2026-10-29
status: archived
purpose: 审核用户批准的纯库测试与正式混合查询边界补丁。
scope:
  - skill-patch-review
prerequisites:
  - harness/skills/SkillPolicy.md
relatedDocuments:
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/rag/policies/KnowledgeQueryEvaluationPolicy.md
outputTo:
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
owner: mixed
reviewAfter: source-updated
supersededBy: harness/skills/reviewed/rag-knowledge-use/SKILL.md
dependsOn:
  - harness/tools/scripts/stable/test-rag-tools.ps1
review:
  reviewedBy: user
  reviewedAt: 2026-10-29
  decision: user-approved-rules-merged-after-67-regressions-and-skill-validation
---

# 评测来源边界补丁审核

用户审核通过并授权沉淀工具、脚本和文档，完成后提交仓库。对已有Skill修订，不新建同类Skill。

补丁明确纯库测试与正式混合查询；纯库测试不允许网页元数据核验例外，库内缺证据时报告缺口；正式混合使用分别标明来源。查询传递来源前缀和模式，验收覆盖完整工具活动，区分局部文件守卫与整轮来源审计。

验证覆盖正文摄取与封印、查询来源筛选和跨页连续性、外部事件反例、混合模式归属、局部日志不足、证据哈希/行号变化、Skill元数据与治理。真实知识、清单、工具日志与校录配置保留在本地边界。

审核收口：双PowerShell各67项回归及Skill校验通过，补丁合入已有reviewed Skill，本记录归档。
