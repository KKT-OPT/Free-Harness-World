---
documentName: harness/skills/archive/engineering-reliability-patches/PATCH.md
version: v1.0.0
updatedAt: 2026-10-28
status: archived
purpose: 留存已批准并合入三个reviewed Skill的补丁来源；不作为活跃规则或待执行任务。
scope: [skill-patch-candidate, implementation, review, performance]
prerequisites: [../../SkillPolicy.md]
relatedDocuments:
  - ../../reviewed/code-implementation/SKILL.md
  - ../../reviewed/code-review/SKILL.md
  - ../../reviewed/algorithm-performance-analysis/SKILL.md
  - ../../reviewed/stateful-algorithm-validation/SKILL.md
outputTo: [harness/skills/archive/engineering-reliability-patches/PATCH.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy: harness/reports/redacted/H9-5EngineeringReliabilityFeedback.md
dependsOn: [../../SkillPolicy.md]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: approved-patches-merged-after-validation
---
# 已合入Skill补丁来源归档

本次由用户明确要求沉淀；不是自动触发。既有Skill足以承担常规实现/审查/性能职责，不再新建同类大Skill。
此目录没有SKILL.md，不可当成可执行Skill，也不覆盖工作区中已存在的reviewed改动。
以下保留原候选内容供追踪。用户2026-10-28明确授权测试通过后晋升，现已合入三个reviewed Skill的专题reference与入口。
当前规则以reviewed目标为准；本归档不再作为待审核候选或执行入口。

## 1. code-implementation

目标：`harness/skills/reviewed/code-implementation/SKILL.md` 4.2设计修改、4.4验证及6验收。

- 配置/阈值：先建立“语义、单位、所有者、默认值、可调范围、消费者、版本”清单。
  名称相近但目的不同的死区、迟滞、冲突门槛、时间窗口不共用参数；禁止只为消除字面量机械提取常量。
  修改可选字段默认值同时验证构造器/builder、显式null、反序列化和模拟调用；不以示例JSON代替真实默认行为。
- 实现辅助服务时列出不可变主链/输出边界。只有触及共享上游或公共契约时才加对应主链等价回归，
  不要求每次局部文档或私有实现修改都重跑整个系统。
- 接口/历史状态/摘要各司其职；状态字段以“下一轮决策是否消费”为保留依据。
  删除前追踪所有消费者及窗口依赖，保留必要统计/活跃状态，不复制显示摘要或无消费的旧版本。
  可选可观测开关关闭时，应避免无意义的构造/序列化，但不得跳过识别所需计算。
- 参数试验先隔离冻结，明确是否晋升。被拒试验只删除其专属配置/测试/无调用分支，保护正式行为与仍被复用的逻辑。
- 测试/标注脚本需要迁移环境或IDE运行时，将Java启动适配留在项目可移植工具包，显式支持运行时选型，
  不依赖Harness路径或项目文档才能执行；测试编译与已有产物运行分开，禁止悄悄选旧产物。
  Maven缺失、离线依赖未缓存、算法失败分别报告；复制宿主私有settings不是修复方案。
- 有状态算法的独立参考、因果回放及评价范围，路由到本批次候选Skill；未晋升前仅按用户授权试用，不自动激活。

## 2. code-review

目标：`harness/skills/reviewed/code-review/SKILL.md` 4审查流程、6验收；数值细节仍留Java reference，不复制一份规范。

- 分别审查领域语义、运行实现、测试适配器、评价器和参考资产，避免“测试PASS”等同于正确识别。
  对机器/人工参考冲突检查独立证据，不以当前预测反向污染参考。
- 审查指标边界：零命中是否被误当N/A、重复匹配、partial混入整航、切片/家族重复计分、生命周期与逐点标签混用。
  主指标阈值和阶段批准范围以用户批准契约为准，不把某个项目目标推广到所有算法。
- 清理文档/JSON/CSV前检索代码默认路径及传递引用、冻结身份和未结风险；扩展名与文件年龄不能证明它是临时文件。
  使用精确清单和保护哈希，保留必要短历史路由；只读核验工具不能证明动态依赖不存在。
- Findings必须区分当前可复现缺陷、历史症状、参考问题、未测项和已接受风险；不能让过期结论重新变成门禁。

## 3. algorithm-performance-analysis

目标：`harness/skills/reviewed/algorithm-performance-analysis/SKILL.md` 5.2至5.4及6验证；保留现有独立性能职责。

- 首先定义计时包络：入口解析、配置/状态读取、算法、投影、响应装配及序列化哪些实际计入。
  内部函数耗时不替代完整API；测试磁盘落盘、绘图或启动编译耗时不能冒充API耗时。
- 固定可观测输出组合与正式配置，分列开/关对照；主画像由用户选定，不擅自规定所有项目默认关闭摘要。
  冷启动、预热、稳态、独立进程重复分别呈现；失败调用与partial样本不静默丢弃。
- 减容同时报告整体状态、目标服务state、summary和response字节，明确编码/计量对象。
  用自然长时输入和跨轮输出等价验证，而非只报最短包或用截断历史换容量。
- 效果保持需冻结数据/参考/评价器/参数并核查当前实现；历史高分不是优化后不退化的证据。
  仅测容量或静态核验时，不新增准确率/性能结论。

## 4. 合入门禁

1. 用户已明确授权测试通过后晋升；本批测试与补丁范围走查通过，合入结果由审核包记录。
2. 合入前重读当前目标（可能有用户未提交改动），不覆盖、不复制整包，不同时保留同名候选活跃Skill。
3. 结构验证、行为反例走查、相关稳定脚本自测及Git差异通过；项目数值、路径、数据和私有设置不进入通用规则。
4. 更新SkillIndex/usage的真实本次修订记录，不反推数月使用次数或虚构successRate，再按治理要求限定Git纳管。
