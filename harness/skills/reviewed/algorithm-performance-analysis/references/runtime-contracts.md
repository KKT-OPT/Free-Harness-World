---
documentName: harness/skills/reviewed/algorithm-performance-analysis/references/runtime-contracts.md
version: v1.0.0
updatedAt: 2026-10-28
status: active
purpose: 统一完整API计时、输出选型和历史状态减容的可比实验边界。
scope: [api-latency-envelope, observability-profile, state-capacity]
prerequisites: [../SKILL.md]
relatedDocuments: [../../stateful-algorithm-validation/SKILL.md]
outputTo: [harness/skills/reviewed/algorithm-performance-analysis/references/runtime-contracts.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy:
dependsOn: [../SKILL.md]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: approved-patch-merged-after-validation
---
# 运行与状态实验边界

## 1. 计时包络

明确入口解析、配置/状态读取、算法、投影、响应组装和序列化哪些实际计入。
内部函数耗时不代表完整API；测试编译、启动、磁盘落盘和绘图成本不能冒充API耗时。
端到端与子阶段分别报告，冷启动、预热、稳态和独立进程重复分列，失败和partial样本不静默排除。

固定正式配置、数据身份和可观测输出组合；主画像由用户选定，不能把某项目关闭摘要的设置当作通用默认。
可选输出开/关可作对照，但不要在不同画像间直接比较P99或以剔除异常样本换达标。

## 2. 状态与容量

分别报告整体状态、目标服务状态、summary及response字节，说明编码/计量对象，不能混用字符数和字节数。
用自然长时输入与跨轮输出等价证明减容不影响效果，不能只测最短包或截断全部历史以追逐容量目标。
持久化保留依据是后续决策消费，展示摘要或无消费者旧版本不自动成为必要状态；活跃候选/重叠窗口/组合引用不能盲删。

## 3. 效果保持

基线与实验冻结数据、参考、评价器和参数身份；历史高分不是当前实现未退化的证据。
功能oracle须来自被测实现。在线参考/生命周期按[有状态验证](../../stateful-algorithm-validation/SKILL.md)执行。
如果只完成静态或容量核验，限定结论，不新增准确率或完整API性能事实。
