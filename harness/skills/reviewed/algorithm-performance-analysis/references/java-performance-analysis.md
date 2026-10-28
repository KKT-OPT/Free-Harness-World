---
documentName: harness/skills/reviewed/algorithm-performance-analysis/references/java-performance-analysis.md
version: v1.0.0-reviewed
updatedAt: 2026-07-11 13:55:45.000 +08:00
status: active
purpose: 提供 algorithm-performance-analysis Skill 在 Java/JVM 场景下的计时、冷启动、JIT、GC、JFR、JMH 和热路径分析参考。
scope:
  - algorithm-performance-analysis
  - java-performance
  - jvm-runtime
  - cold-start
  - profiling
prerequisites:
  - AGENTS.md
  - harness/skills/reviewed/algorithm-performance-analysis/SKILL.md
relatedDocuments:
  - harness/skills/SkillIndex.md
  - harness/skills/SkillPolicy.md
  - harness/skills/reviewed/code-review/SKILL.md
  - harness/skills/reviewed/code-implementation/SKILL.md
outputTo:
  - harness/skills/reviewed/algorithm-performance-analysis/references/java-performance-analysis.md
owner: mixed
reviewAfter: 2026-07-25
supersededBy:
dependsOn:
  - harness/skills/reviewed/algorithm-performance-analysis/SKILL.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-11
  decision: approved-and-promoted-to-reviewed
---
# Java/JVM 性能分析参考

仅在目标运行时为 Java/JVM 时读取本文件。主流程和审核边界以 `../SKILL.md` 为准。

## 1. 计时口径

1. 使用 `System.nanoTime()` 计算进程内持续时间；不要用系统墙钟计算短耗时。
2. 同时保留外层 API、核心服务、流水线阶段和目标热路径计时，避免把边界初始化全部归到算法。
3. 计时器本身应轻量，并可在诊断结束后关闭；不要在每个循环元素输出日志。
4. 首轮、预热区间和稳态分别统计。首轮单独记录，不从原始数据中删除。
5. 报告 JVM 版本、关键 JVM 参数、heap 设置和是否启用 profiler。

## 2. 冷启动和 forked JVM

每个冷启动样本必须来自独立 JVM。一个 JVM 内重复调用只能描述预热和稳态，不能生成多个冷启动样本。

建议把启动诊断程序拆成可选择的阶段：

- 仅加载目标类；
- 仅初始化配置或管理注册；
- 仅初始化算法注册；
- 初始化全部共享服务；
- 完全冷首 API；
- 已初始化共享服务后的首 API；
- 同进程后续 API。

通过外层和内层计时差、独立阶段计时和源码生命周期三类证据交叉验证。静态 holder 或 singleton 只能证明设计意图，仍需运行证据证明没有在请求路径重复构建。

预热、readiness、并发首请求和进程池属于宿主生命周期策略。若目标交付物只是算法库，且用户确认这些职责在上游，则诊断到所有权边界后停止，不在算法内部增加线程或预热入口。

## 3. JIT、类加载和 GC

- JIT 会使前若干调用逐步变快；固定丢弃一个样本可能不足，应观察时间序列何时进入稳定区间。
- 类加载、反射、Jackson/JSON、日志框架、配置读取和静态初始化常集中在首轮，需与核心算法计时拆开。
- GC 或 allocation 问题应同时观察吞吐、暂停、分配热点和 heap；不能只根据一次长尾推断 GC。
- 需要诊断时可使用 JVM 原生日志或 JFR；原始输出进入运行态目录，不进入长期 Skill 或项目正式文档。

常用诊断参数示例：

```text
-XX:StartFlightRecording=filename=<runtime-path>/recording.jfr,settings=profile,dumponexit=true
-Xlog:gc*
-Xlog:class+load=info
```

这些参数可能产生大量输出，只在受控诊断运行中启用。

## 4. JFR 归因顺序

按问题选择事件，不要求每次全部开启：

1. CPU hotspot 和 method samples；
2. allocation in new TLAB / outside TLAB；
3. GC pause、heap summary 和 object count；
4. monitor enter、park 和 thread state；
5. file/socket I/O；
6. class loading、compilation 和 deoptimization。

先定位占比，再回到源码检查调用次数、生命周期和复杂度。Profiler 排名只能说明成本集中位置，不能单独证明某次代码变更造成回归。

## 5. 微基准边界

对独立原子函数、数据结构或数学内核使用 JMH，避免手写循环被 dead-code elimination、constant folding 或 JIT 优化误导。JMH 结果仍需满足：

- 输入规模和业务分布可解释；
- 包含 warmup、measurement 和 fork；
- 使用返回值或 `Blackhole`；
- 报告单位和误差；
- 最终用端到端真实数据或代表性仿真复核。

不要仅为一次排障把 JMH 依赖强行加入生产项目；可在独立测试模块或经用户批准的性能测试边界使用。

## 6. Java 热路径检查

重点检查：

- 循环、递归、stream、sort comparator 中重复解析、坐标转换、正则、反射或对象创建；
- 每请求重复构建本可按进程或配置版本缓存的不可变对象；
- 序列化大对象、深拷贝和中间集合；
- 装箱、临时数组、字符串拼接和高频日志；
- 锁范围过大、共享可变状态和并发首轮初始化；
- 算法复杂度是否随输入规模出现预期外放大。

优化不变量时必须确认缓存生命周期、失效条件、线程安全、内存上限和序列化边界。减少 CPU 不能以引入陈旧状态或跨请求污染为代价。

## 7. Java 验收建议

正式对比至少包含：

| 维度 | 建议证据 |
|---|---|
| 编译与功能 | `test-compile`、单元测试、端到端或仿真 oracle。 |
| 冷启动 | 5 个及以上独立 JVM 样本，报告中位数和范围。 |
| 预热 | 同进程时间序列，说明稳定区间判断方法。 |
| 稳态 | 固定调用数，报告 avg/P50/P95/P99、吞吐和成功率。 |
| 资源 | 视问题报告 CPU、allocation、GC、heap、I/O 或 lock 证据。 |
| 回归 | 同数据、同配置、同环境的优化前后对比。 |
