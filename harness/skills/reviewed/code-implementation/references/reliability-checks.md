---
documentName: harness/skills/reviewed/code-implementation/references/reliability-checks.md
version: v1.0.0
updatedAt: 2026-10-28
status: active
purpose: 为配置默认值、辅助服务、历史状态、隔离试验和可移植测试工具提供按风险加载的实现检查。
scope: [implementation-reliability, configuration, state, portable-tools]
prerequisites: [../SKILL.md]
relatedDocuments: [../../stateful-algorithm-validation/SKILL.md]
outputTo: [harness/skills/reviewed/code-implementation/references/reliability-checks.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy:
dependsOn: [../SKILL.md]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: approved-patch-merged-after-validation
---
# 实现可靠性专题检查

只在变更触及相应风险时使用，不要求每个小改动运行全项目回归。

## 1. 配置与数值

先列出值的语义、单位、所有者、默认值、可调范围、消费者和版本来源。
名称相近但目的不同的死区、迟滞、冲突门槛或时间窗口不因此共用参数。
配置值必须流入实际消费者，不能只新增声明/校验而运行时仍用旧字面量。
不要为消除数字机械提取常量，数值审查仍使用Java reference和只读门禁。

可选字段默认值要分别验证构造器/builder、显式null、反序列化和真实模拟调用；
示例JSON与展示输出不能证明请求缺省行为。未授权时不改变默认值或配置版本。

## 2. 主链隔离与状态

辅助服务先列出不可变主链与输出边界。触及共享上游或公共契约时增加相应等价回归，
局部文档或私有实现修改不机械重跑全系统。
接口结果、下一轮历史状态和展示摘要分开设计；持久字段应说明下一轮消费者。
减容前追踪消费者、重叠窗口、候选状态和组合引用，不复制无消费的摘要/旧版本，
也不能通过盲目截尾删除识别所需证据。可观测开关关闭应避免无意义组装/序列化，但不跳过必要识别计算。
验证时记录逐轮输出/状态演进是否等价，而不只比较最终分数或字节数。

## 3. 隔离试验与清理

参数试验和正式默认分别冻结；用户批准后才能晋升参数/版本。
被拒试验只清除其专属配置、测试和无调用分支，保留复用逻辑与正式行为。
有状态算法的独立参考、因果回放和评价范围由
[有状态算法验证](../../stateful-algorithm-validation/SKILL.md)补充，不复制其完整流程。

## 4. 可移植工具

项目测试/标注脚本需要IDE或迁移环境执行时，把Java启动适配保留在项目可移植工具包，显式支持运行时选型。
运行时不应依赖Harness路径或项目文档才能启动。编译与使用已有产物分别记录，不能静默选用旧产物。
区分Maven缺失、离线依赖未缓存、启动失败和算法失败；复制私有settings不是修复方案。

完成时提供与风险匹配的正反例、命令、结果和未覆盖项；不能把脚本退出0等同于业务功能正确。
