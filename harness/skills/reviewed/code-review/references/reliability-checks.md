---
documentName: harness/skills/reviewed/code-review/references/reliability-checks.md
version: v1.0.0
updatedAt: 2026-10-28
status: active
purpose: 定义参考资产、指标、清理依赖和结论有效性的专项审查，不复制语言规范或项目事实。
scope: [review-reliability, reference-independence, metrics, cleanup-safety]
prerequisites: [../SKILL.md]
relatedDocuments: [../../stateful-algorithm-validation/SKILL.md]
outputTo: [harness/skills/reviewed/code-review/references/reliability-checks.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy:
dependsOn: [../SKILL.md]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: approved-patch-merged-after-validation
---
# 审查可靠性专题检查

## 1. 算法与评价边界

分别审查领域语义、运行实现、测试适配器、评价器和参考资产；“程序PASS”不等于识别正确。
检查参考独立性：机器/人工参考严重冲突必须用独立证据复核，不能用待测预测反向改参考。
有状态在线/离线评价读取[有状态算法验证](../../stateful-algorithm-validation/SKILL.md)。

指标重点检查零命中误当N/A、重复匹配、partial混入整航、切片/家族重复计分、生命周期与逐点标签混用。
主指标、阈值和阶段批准范围来自用户批准契约，不把单项目目标推广到所有算法。
总体改善与局部退化分列，验收代价由用户判断，不能临时更换统计口径制造提升。

## 2. 文件清理

清理文档/JSON/CSV前检查源码默认路径、传递引用、冻结身份和未结风险。
扩展名、文件年龄或所在文档目录不能证明文件可删。需要明确删除清单、保护哈希和恢复依据，保留必要短历史路由。
可使用`harness/tools/scripts/stable/verify-artifact-cleanup.py`核验精确文件集合；工具不推断动态依赖，不替代源码审查。
检查风险是否迁入持续维护入口，而不只是随旧工作流消失；不得通过修改冻结校验清单迎合删除结果。

## 3. 发现与结论

明确区分当前可复现缺陷、历史症状、参考问题、未测项和用户已接受风险。
过期结论不能重新变成门禁，已接收的有限范围也不能冒充全项目/生产验收。
结构门禁只检查结构/状态，不能确认文字真实性；失败复查、partial修复和标题存在不构成闭环批准。
