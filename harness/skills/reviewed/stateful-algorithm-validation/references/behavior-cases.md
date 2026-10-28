---
documentName: harness/skills/reviewed/stateful-algorithm-validation/references/behavior-cases.md
version: v1.0.0
updatedAt: 2026-10-28
status: active
purpose: 提供候选有状态算法验证流程的正反例和人工行为验收标准，不保存项目数据或阈值。
scope: [skill-validation, causal-boundary, metric-boundary]
prerequisites: [../SKILL.md]
relatedDocuments: [../SKILL.md]
outputTo: [harness/skills/reviewed/stateful-algorithm-validation/references/behavior-cases.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy:
dependsOn: [../SKILL.md]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: approved-promotion-after-validation
---
# 有状态算法行为验收用例

| 输入或请求 | 期望行为 | 不合格行为 |
|---|---|---|
| 生成器提供raw和模式truth | raw走生产必要链，truth仅评分时读取 | truth直接作为识别输入或省略融合 |
| 离线事件确认早于在线输出 | 分别评价序列与确认延迟 | 为逐点相等回写历史结果 |
| 本轮无新增点，返回相同尾时间 | 按契约不重复计证据/事件 | 直接判主链错误或重复确认 |
| 参考2次发生、预测1次发生 | 一对一匹配并记录漏检 | 一次预测同时命中两次参考 |
| 有参考和预测但零TP | 检查批准公式的有效零分 | 当N/A排除失败样本 |
| 人工标签与可信位置几何严重相反 | 独立复核、保留原标签和审核轨迹 | 直接改成算法输出 |
| 总体效果上升、部分家族下降 | 逐来源/模式解释净收益和代价，交用户决策 | 自动阻塞全部晋升或隐去下降 |
| 请求压缩历史状态 | 追溯消费者、跨轮/长时等价对照 | 无证据统一改成更小尾长 |
| 提速仅内部服务、未测序列化 | 限定结论，补完整API范围 | 宣布完整API已达标 |
| 只有development数据 | 仅报告开发结果 | 改目录名后称独立泛化通过 |

审核方式：对本表逐项走查Skill步骤及项目验证方案，检查产物是否可追溯。
已完成范围/职责和反例走查；新独立项目上的应用效果仍须以实际证据验证，不能以结构检查代替效果验收。
