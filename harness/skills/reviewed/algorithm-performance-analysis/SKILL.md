---
name: algorithm-performance-analysis
description: 对算法、计算流水线或高频服务建立可复现性能基线，拆分冷启动、预热和稳态，使用分段计时、调用生命周期、profiler 与对照实验定位延迟、吞吐、CPU、内存、分配、GC、I/O 或锁竞争根因，并形成优化前后验证和用户审核闭环。适用于仿真或真实负载变慢、功能开关导致性能退化、首轮与后续耗时差异、热路径或算法复杂度异常、注册与初始化成本归因、性能优化方案评审及优化后验收；若问题仅是普通代码风险则由 code-review 处理，获批后的代码修改由 code-implementation 执行。
---
# Algorithm Performance Analysis（算法性能分析）

## 1. 笔记属性

| 属性 | 内容 |
|---|---|
| 文档 | `harness/skills/reviewed/algorithm-performance-analysis/SKILL.md` |
| 资产状态 | reviewed |
| 触发模式 | user-directed；用户明确要求从真实项目性能归因经验拆分候选 Skill |
| 审核状态 | approved；用户于 2026-07-11 审核通过并批准晋升 |
| 主题语言 | 中文；专业词、命令、指标和代码标识保留英文 |
| 输出结果 | 项目 workflow evidence、可复现实验矩阵、性能基线、阶段归因、处置结论、验证结果和用户审核状态 |
| 事实边界 | 项目数据、类名、日志和数值留在项目证据；本 Skill 只保存跨项目流程 |

## 2. 关联文档和读取路径

按以下顺序读取；仅在 Java/JVM 场景加载 Java reference：

| 文档 | 读取目的 |
|---|---|
| `AGENTS.md` | 获取 Harness 入口、硬约束和读取顺序。 |
| `INDEX.md` | 路由到 Harness、项目实例和运行态边界。 |
| `harness/HarnessIndex.md` | 定位 Skill、Tool、Governance 和项目模板。 |
| `harness/skills/SkillPolicy.md` | 遵守 Skill candidate、review 和晋升规则。 |
| `harness/skills/SkillIndex.md` | 检查已有 Skill，避免职责重复。 |
| `harness/skills/reviewed/code-review/SKILL.md` | 获取性能风险发现、代码审查和复查入口。 |
| `harness/skills/reviewed/code-implementation/SKILL.md` | 将用户批准的优化方案交给实现流程。 |
| `projects/<project-id>/AGENTS.md` | 获取目标项目的本地约束。 |
| `projects/<project-id>/docs/project/ProjectIndex.md` | 定位架构、测试手册、workflow evidence 和项目稳定命令。 |
| `scripts/summarize_latency.py` | 对结构化调用记录确定性拆分 cold/warmup/steady 并计算统计摘要。 |
| `references/java-performance-analysis.md` | Java/JVM 冷启动、JIT、GC、JFR、JMH 和分段计时方法。 |

## 3. 职责边界

按以下边界协同，不把完整性能流程继续堆入通用代码 Skill：

| 资产 | 职责 |
|---|---|
| `code-review` | 发现性能风险，要求基线和功能 oracle，并路由到本 Skill。 |
| 本 Skill | 设计实验、拆分阶段、定位根因、判断是否需要优化并完成性能验收。 |
| `code-implementation` | 在用户批准方案后修改代码，保留正确性并运行回归。 |
| 项目测试或仿真资产 | 提供代表性输入、可执行程序、业务正确性 oracle 和性能原始记录。 |
| 上游宿主或后端 | 负责进程生命周期、并发模型、readiness 和是否预热；目标算法无权自行改变这些策略。 |

冷启动必须测量和归因，但不自动等于算法缺陷。若确认成本只在新进程首轮发生，稳态无回归，且预热或并发属于上游宿主职责，则记录 `no-algorithm-fix` 和交接边界；不得让算法自行启动线程、隐藏首轮请求或实现未获授权的预热。

## 4. 必需输入

| 输入 | 要求 |
|---|---|
| 目标与范围 | 明确被测算法、API、流水线、功能开关和允许修改的边界。 |
| 指标 | 至少明确 latency 或 throughput；按问题补充 CPU、allocation、GC、memory、I/O、lock。 |
| 负载 | 使用真实数据或可说明代表性的固定数据；记录调用数、输入规模和配置。 |
| 环境 | 记录代码版本、运行时版本、启动方式、进程模型和关键硬件条件。 |
| 正确性 oracle | 明确成功率、数值误差、输出结构或业务断言；性能提升不能替代正确性。 |
| 对照条件 | 保证基线与实验组使用相同数据、配置、环境和代码路径，只改变待验证变量。 |
| SLO 与所有权 | 有 SLO 时按阈值验收；没有 SLO 时只能完成归因和相对比较，不擅自做结构性优化。 |

缺少关键输入时，先从项目文档、配置和现有测试中恢复；无法恢复且会改变结论时再向用户澄清。

## 5. 执行流程

### 5.1 建立项目证据

真实项目必须创建或更新 `projects/<project-id>/docs/project/workflow/` 下的 workflow evidence，并记录：

- Task Brief、范围、指标、SLO、所有权和风险；
- 数据、配置、环境、命令、代码版本和正确性 oracle；
- 假设清单、实验矩阵、原始结果引用和统计摘要；
- 根因、处置决策、优化计划、验证和用户审核状态。

若性能任务来自代码审查，沿用同一 workflow evidence，不另建割裂的性能报告。若当前证据采用 code-review 闭环格式，运行：

```powershell
& harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1 `
  -ProjectId <project-id> `
  -WorkflowEvidence <project-relative-workflow-path>
```

### 5.2 定义实验矩阵

涉及完整API、可观测输出组合或历史状态减容时，先读取
[运行与状态实验边界](references/runtime-contracts.md)，定义计时包络和同口径的效果保持证据。

至少拆分以下维度中与问题相关的组合：

1. **阶段**：新进程冷启动、预热区间、稳态区间。
2. **功能**：功能关闭控制组、功能开启实验组、优化前、优化后。
3. **入口**：外层 API 总耗时、内部阶段耗时、目标热路径耗时。
4. **规模**：输入条数、点数、批量大小、历史长度或其他复杂度变量。
5. **进程**：同进程重复调用与独立 forked process 分开采样。

探索性归因至少保留 3 个独立样本；用于正式性能验收时优先保留 5 个及以上独立样本。样本不足时明确标记，不把单次日志当成稳定结论。

### 5.3 建立可复现基线

1. 先运行编译和功能 oracle，确认基线正确。
2. 用项目稳定命令运行固定数据，不手工挑选最快或最慢样本。
3. 至少记录 `count`、`successRate`、`avg`、`P50`、`P95`、`P99`、`max` 和总耗时；小样本无法支持高分位数时明确说明。
4. 将冷启动样本与稳态样本分别汇总；`max` 只能作为异常线索，不能单独作为回归结论。
5. 保存原始记录到运行态目录，workflow evidence 只保存可复现命令、摘要和证据引用。

项目性能程序应优先输出 JSON array、JSONL 或 CSV 结构化记录，默认字段为 `elapsedMillis` 和 `success`。使用本 Skill 内的确定性统计脚本生成分段摘要：

```powershell
python -X utf8 harness/skills/reviewed/algorithm-performance-analysis/scripts/summarize_latency.py `
  --input <runtime-performance-records> `
  --cold-count 1 `
  --warmup-count <warmup-call-count> `
  --output <runtime-performance-summary-json>
```

Java 项目优先通过稳定入口执行：

```powershell
& harness/tools/scripts/stable/invoke-maven-project.ps1 `
  -ProjectRoot <project-root> `
  -Agent <agent-id> `
  -Goals test-compile `
  -RunName <run-name>

& harness/tools/scripts/stable/invoke-java-main.ps1 `
  -ProjectRoot <project-root> `
  -MainClass <performance-main-class> `
  -Agent <agent-id> `
  -RunName <run-name>
```

### 5.4 分段定位与因果验证

按由外到内的顺序缩小范围：

1. 对比外层调用耗时与服务内部耗时，识别初始化、序列化或调用边界成本。
2. 检查对象和注册中心生命周期，证明目标成本是每进程一次、每请求一次还是每数据点一次。
3. 对循环、递归、排序 comparator、空间索引和批处理检查复杂度及不变量重复计算。
4. 按证据选择 profiler，区分 CPU、allocation/GC、I/O、锁竞争、类加载和 JIT。
5. 每个候选根因只改变一个关键变量，重复同口径实验；相关性不足以证明因果。
6. 同时运行正确性 oracle，防止通过跳过计算、降低精度或吞掉失败获得虚假提速。

### 5.5 决定处置

| 结论 | 处置 |
|---|---|
| 算法可控热路径存在可复现瓶颈 | 形成优化方案、风险和预期收益，等待用户批准后交给 `code-implementation`。 |
| 仅有新进程首轮成本，稳态正常，生命周期由上游负责 | 记录 `no-algorithm-fix`；向宿主/后端交接预热、readiness 或并发决策，不修改算法。 |
| 注册或配置只初始化一次 | 不把它误判为每请求回归；只有存在首请求 SLO 且职责在当前范围内时才提出优化。 |
| 没有回归或结果在 SLO 内 | 记录 `no-fix-required`，保留基线和残余风险。 |
| 数据噪声、样本不足或环境不一致 | 记录 `evidence-insufficient`，修正实验后再判断。 |

### 5.6 实现、复查和验收

1. 用户批准优化方案后，调用 `code-implementation` 完成最小必要修改。
2. 用同一实验矩阵重跑优化后样本，并报告绝对值、相对变化、波动范围和正确性结果。
3. 调用 `code-review` 复查算法正确性、并发、资源、回归和测试证据。
4. 更新 workflow evidence 的处置、文件摘要、验证和残余风险。
5. 等待用户最终审核；未获批准不得标记 accepted 或沉淀项目结论为通用事实。

## 6. 验证门禁

完成性能分析至少满足：

- 基线和实验组可由记录命令复现；
- 冷启动、预热和稳态没有混为一个平均值或 `max`；
- 真实负载或代表性负载、输入规模和配置已记录；
- 功能 oracle 与性能数据来自同一实现；
- 根因有生命周期、分段计时、profiler 或单变量实验支持；
- 已区分算法可控范围与宿主/上游职责；
- 代码修改经过 `code-implementation` 和 `code-review` 闭环；
- workflow evidence 保存用户审核状态和残余风险；
- `scripts/summarize_latency.py --self-test` 通过，或项目已使用等价的稳定统计程序；
- `git diff --check` 通过，运行态日志未写入长期 Skill。

## 7. 失败处理

| 情况 | 处理 |
|---|---|
| 项目无法编译或功能 oracle 失败 | 先停止性能结论；记录基线无效并处理正确性问题。 |
| profiler 不可用 | 使用分段计时、调用计数和单变量实验；明确证据强度，不伪造 profiler 结论。 |
| 环境噪声过大 | 增加样本、固定负载、关闭无关进程或改用隔离环境，保留异常样本说明。 |
| 无法区分冷启动与稳态 | 使用独立进程测首轮、同进程测后续，不用一次完整运行的 `max` 代替。 |
| 优化跨越用户授权范围 | 停止实现，只提交归因、影响和下一步方案。 |
| 根因属于宿主或上游 | 记录交接边界和所需证据；算法侧不自行预热或改变并发模型。 |

## 8. 禁止事项

- 不用单次耗时、`max` 或肉眼观察直接宣布性能回归。
- 不把新 JVM 的类加载、配置和 JIT 成本误写成每轮算法耗时。
- 不在没有 SLO、所有权和用户批准时引入 lazy initialization、线程池或预热。
- 不通过降低精度、改变业务语义、跳过算法阶段或吞掉异常换取性能数字。
- 不把项目类名、私有数据、绝对路径、原始日志或一次性数值写入本 Skill。
- 不把微基准结果替代端到端真实数据验证。
