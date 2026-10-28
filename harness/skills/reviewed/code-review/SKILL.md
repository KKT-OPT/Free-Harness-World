---
name: code-review
description: 审查真实项目或通用仓库中的代码变更、源码片段、PR diff、补丁、测试代码和重构方案，优先发现正确性、回归风险、并发、异常、数据一致性、安全、可维护性、测试缺口和规范偏差。适用于用户要求 code review、代码规范检查、Java 企业级代码审查、修改前审查、修改后验收审查、建立可追踪项目 workflow evidence、完成审查-用户审核-代码修改-复查-再审核闭环，或从真实项目反向沉淀代码规范的场景；审查 Java 代码时读取 references/java-code-standards.md。
metadata:
  short-description: 代码审查与 Java 规范检查
  asset-state: reviewed
  review-state: approved
---
# Code Review Skill（代码审查技能）

## 1. 笔记属性

| 属性 | 内容 |
|---|---|
| 文档 | `harness/skills/reviewed/code-review/SKILL.md` |
| 资产状态 | reviewed |
| 审核状态 | approved，已由用户通过真实项目 forward-test、revise 和最终条件批准 |
| 主题语言 | 中文；专业词、命令、路径、类名和代码标识保留英文 |
| 适用对象 | 真实项目源码、补丁、PR diff、测试代码、重构方案和代码规范沉淀 |
| 输出结果 | 项目 workflow evidence、目录/文件覆盖矩阵、注释审查矩阵、按严重程度排序的代码审查发现、证据、影响、建议、测试缺口、用户审核状态和可选规范沉淀候选 |
| 事实边界 | 项目事实留在项目文档或 workflow evidence；本 Skill 只保留可复用审查流程 |

## 2. 关联文档和读取路径

执行代码审查前，先读取 Harness 入口和目标项目入口，再按语言读取 reference。

| 文档 | 读取目的 |
|---|---|
| `AGENTS.md` | 获取 Harness Root 入口、读取顺序、敏感边界和文档语言规则。 |
| `INDEX.md` | 路由到 Harness、项目实例、本地用户边界和运行态边界。 |
| `harness/HarnessIndex.md` | 确认 Skill、Tool、Governance、Project Template 和 Verification 入口。 |
| `harness/skills/SkillIndex.md` | 确认现有 Skill 状态，避免重复创建或绕过 candidate。 |
| `harness/skills/SkillPolicy.md` | 确认 Skill 创建、candidate、review 和晋升边界。 |
| `harness/governance/ProjectHarnessFeedbackPolicy.md` | 当审查结果需要反向优化 Harness 时，判断目标资产类型。 |
| `projects/<project-id>/AGENTS.md` | 获取项目级代码风格、技术栈、敏感边界和验证入口。 |
| `projects/<project-id>/docs/project/ProjectIndex.md` | 路由到项目架构、源码布局、测试策略、验证命令和项目事实。 |
| `projects/<project-id>/docs/project/workflow/` | 真实项目代码审查必须在这里创建或更新 workflow evidence，用于保存 Task Brief、trace、findings、用户审核、修复和复查记录。 |
| `harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1` | 代码审查 workflow evidence 的稳定门禁；按阶段检查结构、用户审核、修复交接、复查和最终审核状态。 |
| `harness/tools/scripts/stable/test-java-javadoc-coverage.ps1` | Java 包级/目录级注释覆盖稳定门禁；当注释完整性是审查或验收目标时，用脚本强制检查类级标签、必需类级章节、最少说明长度、public/protected 或全部显式声明方法 Javadoc、参数、返回值和空白星号行。 |
| `harness/tools/scripts/stable/test-java-magic-values.ps1` | Java 数值字面量只读候选扫描器；用于生成完整候选清单，人工区分配置、版本化业务阈值、单位/数学常量、协议常量、测试夹具和可解释内联值。 |
| `harness/skills/reviewed/code-implementation/SKILL.md` | 用户批准修复或实现后，代码修改阶段的 Skill；修改完成后必须交回本 Skill 复查。 |
| `references/java-code-standards.md` | 审查 Java 代码时读取，作为企业级 Java 规范和项目风格适配参考。 |

## 3. 边界规则

1. 默认只做代码审查，不直接修改代码；用户明确要求修复时，先说明将从 review 切换到 implementation workflow。
2. Findings 必须基于代码事实、diff、测试结果、项目文档或明确推断；不要凭风格偏好制造问题。
3. 正确性、安全、数据一致性、并发、异常处理和回归风险优先于格式和命名偏好。
4. 不粘贴未脱敏日志、凭据、私有 settings、本机绝对路径、完整生产数据或私有仓库细节。
5. 项目已有明确风格优先于通用规范；通用规范与项目风格冲突时，记录冲突并请求用户决策。
6. 代码规范沉淀必须先作为 candidate 或 project fact，不直接晋升 reviewed Skill、Memory、Knowledge 或 Governance。
7. 真实项目代码审查必须落到项目文档系统：创建或更新 `projects/<project-id>/docs/project/workflow/<task-id>.md`，否则不得宣称审查闭环完成。
8. Findings 输出只是审查阶段结果；闭环完成必须记录用户审核、修复决策、代码修改或不修改原因、复查结果和再次审核状态。
9. Java 注释审查中，Javadoc 覆盖脚本只能作为只读门禁和覆盖证据，不得被解释为可机械覆盖业务注释的生成器。发现注释缺口时，必须先读取现有注释、源码行为和必要历史版本，再判断如何保留或吸收原有业务语义。
10. 魔法值扫描器只能发现数值字面量候选，不能独立判断业务语义，也不得自动提取或替换常量。每个候选必须结合配置来源、量纲、算法公式和测试意图完成分类与处置。

## 4. 审查流程

### 4.1 确认范围

审查前确认：

| 字段 | 要求 |
|---|---|
| 目标 | 明确是 review、pre-review、post-fix review、规范检查还是候选规范沉淀。 |
| 范围 | 明确文件、diff、commit、PR、模块或测试范围。 |
| 项目 | 明确 projectId 和项目入口路径；没有项目时按仓库根入口处理。 |
| 风险 | 判断是否涉及真实业务源码、安全、数据治理、并发、接口兼容或高影响重构。 |
| 验证 | 明确已有测试结果、可运行命令和无法运行的原因。 |
| 证据 | 真实项目审查必须确定 workflow evidence 文件路径；没有路径时先创建。 |

目录、包或 glob 级审查必须先进入 batch review mode：

1. 使用 `rg --files` 或等价稳定命令生成完整目标文件清单。
2. 在 workflow evidence 中记录文件总数、每个文件的项目相对路径和审查状态。
3. 对每个文件至少记录一行覆盖结论：`reviewed`、`reviewed-with-findings`、`deferred`、`excluded-with-reason` 之一。
4. Java 目录级审查必须同时记录注释覆盖结论：类级 Javadoc、方法级 Javadoc、字段/常量注释、关键行内注释四层是否检查，发现项是否修复或 defer。
5. Java 目录级审查如果把 Javadoc 完整性作为验收目标，必须运行 `test-java-javadoc-coverage.ps1`；仅靠人工阅读或正则抽查不能宣称 Javadoc 完整。
6. 如果文件数量过大导致本轮不能完整读取和审查，必须把任务状态标为 `partial`，说明未覆盖文件和原因，并请求用户拆分或确认抽样；不得把抽样结果写成全包审核完成。
7. 用户明确要求“全部文件/整个包/批量修改”时，不允许自动降级为抽样审查。
8. 批量注释审查必须区分“结构覆盖”和“语义质量”。脚本通过只能证明结构覆盖通过；若未逐文件吸收原业务注释和算法语义，只能记录为结构化修复，不能宣称语义精修完成。
9. Java 目录级审查必须扫描数值字面量候选，并在 workflow evidence 中记录分类结果；不能把“提取为 `private static final`”本身当作消除魔法值的充分条件。

### 4.2 建立项目 workflow evidence

真实项目代码审查先创建或更新项目 workflow evidence，至少记录：

- Task Brief：目标、projectId、范围、验收标准、风险等级、是否需要审批。
- Scope：审查文件、调用方、被调用方、测试范围和禁止访问的敏感边界。
- Coverage Matrix：目录级审查必须列出全量文件清单、逐文件审查状态、注释审查状态和是否存在 finding。
- Trace：读取的项目入口、命令、搜索结果摘要、关键代码定位。
- Findings：每条发现的文件、行号、证据、影响、建议、严重程度。
- User Review：用户对 findings 的 approve/reject/revise/defer 决策。
- Fix Handoff：如需修改代码，记录切换到 `harness/skills/reviewed/code-implementation/SKILL.md` 的边界。
- Recheck：修改后的复查结果、验证命令和残余风险。
- Final Review：用户再次审核和闭环状态。

创建或更新后运行：

```text
harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1
  -Root <HARNESS_ROOT>
  -ProjectId <project-id>
  -WorkflowEvidence <docs/project/workflow/<task-id>.md>
```

当用户审核、修复、复查或最终审核完成后，按阶段增加 `-RequireUserReview`、`-RequireFixDisposition`、`-RequireRecheck`、`-RequireFinalReview` 或 `-RequireClosedLoop`。

如果只是通用仓库或一次性片段审查，没有项目文档系统，也要在最终答复中说明无项目 workflow evidence 的原因。

Java 包级 Javadoc 完整性验收时运行：

```text
harness/tools/scripts/stable/test-java-javadoc-coverage.ps1
  -Root <PROJECT_ROOT>
  -Target <java-file-or-package>
  -ExpectedAuthor <user-confirmed-author>
  -ExpectedVersion <project-version>
  -RequiredClassSection <project-required-section>
  -MinClassJavadocLines <minimum-lines>
  -RequireClassAuthor
  -RequireClassSince
  -RequireClassVersion
  -RequirePublicMethodJavadocs
  -RequireAllMethodJavadocs
  -RequireParamTags
  -RequireReturnTags
  -ForbidBlankJavadocLines
```

其中 `ExpectedAuthor` 和 `ExpectedVersion` 必须来自用户确认、项目版本来源或项目文档；无法确认时先记录 open question，不能猜测。

Java 数值字面量候选扫描时运行：

```text
harness/tools/scripts/stable/test-java-magic-values.ps1
  -Root <PROJECT_ROOT>
  -Target <java-file-or-package>
  -ClassificationFile <reviewed-classification-json>
  -FailOnUnclassified
```

首次扫描默认使用 report-only。先对每条候选记录 `configuration`、`domain-policy`、`unit-or-math`、`protocol-contract`、`test-fixture`、`justified-inline` 或 `unresolved`，再把可重复的审核结论保存为 `java-magic-value-classification-v1` JSON，并用 `-FailOnUnclassified` 关闭未处置缺口。只有目标范围禁止任何数值候选时才使用 `-FailOnFindings`。允许值列表只能豁免明确的数学或控制流恒等值，不能用大范围 `-AllowLiteral` 掩盖业务阈值。

### 4.3 读取上下文

1. 读取目标项目 `AGENTS.md` 和 `ProjectIndex.md`。
2. 读取相关架构、源码布局、测试策略、验证命令和敏感边界文档。
3. 使用 `rg`、`git diff`、`git show`、`git status` 和项目构建文件定位变更上下文。
4. Java 代码审查时读取 `references/java-code-standards.md`。
5. 如果是局部文件审查，至少查看调用方、被调用方、模型对象、异常和测试覆盖。
6. 如果审查涉及 Java 注释或规范，按 Java reference 同时检查类级 Javadoc、方法级 Javadoc、字段/常量注释、行内注释和版本标签来源，不只检查用户显式指出的一类注释。
7. 如果审查范围是目录、包或 glob，必须逐文件读取或通过结构化扫描加人工复核覆盖每个文件；仅凭编译告警、正则命中或少数代表文件不得宣称完成目录级审查。

### 4.4 审查维度

按以下顺序检查：

1. 行为正确性：业务条件、边界输入、状态迁移、返回值和错误路径。
2. 回归风险：兼容性、持久化状态、历史数据、接口契约、日志和错误码。
3. 异常和错误处理：异常类型、包装、外部消息、内部诊断信息和失败状态。
4. 数据一致性：时间、金额、精度、幂等、重复、排序、去重和并发写入。
5. 并发和资源：共享状态、线程安全、锁、异步、连接、流和资源释放。
6. 安全和隐私：输入校验、越权、注入、敏感信息、日志脱敏和依赖风险。
7. 可维护性：职责边界、模块耦合、命名、注释、复杂度、重复和测试性。
8. 测试覆盖：单元、集成、回归、真实数据复跑、负向用例和断言质量。
9. 语言规范：按对应 reference 检查命名、注释、编程规范和企业级约束。
10. 配置与数值来源：检查数值字面量是否来自用户配置、版本化 policy、单位/数学定义、协议契约或测试夹具；检查默认值和阈值是否具有名称、来源、量纲、可配置性和边界验证。

当功能同时包含总开关、更新标记、可选本轮输入和历史状态时，必须额外执行状态决策表审查：

1. 明确列出每个独立输入维度，禁止把“输入是否存在”和“更新标记”隐式绑定为同一条件。
2. 明确总开关优先级、请求输入与历史状态优先级、无输入降级行为、缓存更新条件和日志级别。
3. 检查 warning/error 是否由掌握完整决策事实的层输出，避免入口层在历史状态尚未解析前误报。
4. 要求自动回归覆盖有业务差异的组合；只有单个 happy path 不能证明状态优先级正确。
5. workflow evidence 应保存决策表、覆盖场景和各场景断言，不只记录“测试通过”。

当用户报告性能退化，或变更涉及排序、递归、批处理、空间索引和高频循环时，必须额外执行热路径审查：

1. 建立同数据、同配置、同运行环境的控制组和实验组，至少记录总调用数、成功率、平均值、P50、P95 和总耗时；不能只比较单次日志或 max。
2. 检查循环体、递归函数、排序 comparator、Stream pipeline 和查询路径中是否重复计算与本轮输入无关的不变量；可预计算派生值应在明确生命周期内只计算一次。
3. 同时保留功能 oracle 和端到端性能证据。性能变快不能替代数值正确性，微基准通过也不能替代真实数据或代表性负载复跑。
4. workflow evidence 应记录基线、根因、复杂度或调用次数放大方式、优化方案和前后对比结果。

目录级审查必须把覆盖本身作为审查维度。若 workflow evidence 中没有文件覆盖矩阵和注释覆盖矩阵，本轮只能称为“局部审查”或“扫描”，不能称为“批量审核完成”。

当审查涉及独立参考、指标计算、阶段资产清理或历史结论收口时，读取
[审查可靠性专题检查](references/reliability-checks.md)。只读核验不能替代依赖审查，结构门禁也不能替代用户批准。
在线跨轮与离线标签的评价边界由 `harness/skills/reviewed/stateful-algorithm-validation/SKILL.md`补充。

### 4.5 输出格式

有问题时，先输出 Findings，再输出开放问题和测试缺口。每条 Finding 使用：

```text
[P0|P1|P2|P3] 标题
文件:行号
证据:
影响:
建议:
```

严重程度：

| 等级 | 含义 |
|---|---|
| P0 | 会导致严重数据损坏、安全事故、生产不可用或无法发布。 |
| P1 | 高概率功能错误、兼容性破坏、关键回归或严重测试缺口。 |
| P2 | 中等风险缺陷、边界遗漏、可维护性明显下降或局部规范问题。 |
| P3 | 低风险风格、命名、注释或局部改善建议。 |

没有发现问题时，明确说明未发现阻塞问题，并列出仍未验证的风险或测试缺口。

### 4.6 用户审核和修复闭环

代码审查的闭环状态分为：

| 状态 | 含义 |
|---|---|
| review-draft | 已完成初审，等待用户审核 findings。 |
| user-reviewed | 用户已对 findings 做 approve/reject/revise/defer 决策。 |
| fix-requested | 用户要求修改代码，必须切换到代码修改 workflow；本 Skill 只负责交接和后续复查。 |
| fixed-pending-recheck | 代码已修改，等待按原 findings 和测试计划复查。 |
| rechecked | 已复查代码和验证结果，等待用户再次审核。 |
| accepted | 用户完成最终审核，workflow evidence 可标记为闭环。 |
| rejected-or-deferred | 用户拒绝或暂缓，本轮审查不得宣称完成修复闭环。 |

当用户要求修改代码时：

1. 不在 code-review Skill 内直接实现修复。
2. 记录修复范围、目标 findings 和验证计划。
3. 切换到 `harness/skills/reviewed/code-implementation/SKILL.md`；后续应由独立 implementation Skill 承担实现。
4. 修改完成后重新使用本 Skill 复查原 findings、相关 diff 和验证结果。
5. 将用户再次审核写回项目 workflow evidence。

当用户在最终审核或中间审核中返回 `revise` 时：

1. 不把本轮标记为 `accepted`，继续保持同一项目 workflow evidence 作为权威证据。
2. 将用户审核意见拆分为新的 Review Findings，记录文件、行号、证据、影响和建议。
3. 判断用户意见是否暴露可复用规则缺口；如果是 Java 代码规范缺口，优先 patch `references/java-code-standards.md`，如果是流程缺口，patch 本 Skill。
4. 使用更新后的 Skill/reference 重新复查目标代码和 diff；需要改代码时再次切换到 `code-implementation`。
5. 修改后重新运行 evidence gate、必要的项目验证和复查，再交给用户最终审核。

### 4.7 反向优化候选

如果审查暴露出可复用规范或流程缺口，按 `ProjectHarnessFeedbackPolicy.md` 分类：

| 信号 | 候选 |
|---|---|
| 通用审查流程缺口 | patch 本 Skill 或新增 reference |
| 项目专属代码风格 | 项目文档或 Project Fact |
| 可执行检查缺口 | Tool 或 Verification gate candidate |
| 代码修改流程缺口 | `harness/skills/reviewed/code-implementation/SKILL.md` patch candidate |
| 企业级 Java 通用规范 | `references/java-code-standards.md` patch candidate |
| 跨语言通用规范 | 单独的 shared code review reference 或 Governance policy |

## 5. Java 代码审查

审查 Java 代码时，读取：

```text
harness/skills/reviewed/code-review/references/java-code-standards.md
```

Java 注释和 Javadoc 审查必须同时覆盖类、方法、字段/常量和关键行内注释四个层级；`@version` 只能引用项目已有版本来源，无法确认时询问用户或记录 open question。

Java 魔法值审查必须同时覆盖生产代码和本轮测试代码。重点不是“所有数字都变成常量”，而是防止用户可配置参数、算法阈值、时间窗口、单位换算和协议值以无来源字面量进入实现；明显的 `0/1` 恒等值、局部循环边界或夹具输入可保留，但应能从上下文解释。

当审查目标是补齐或修复既有 Java 注释时，必须检查新注释是否保留了原注释中有价值的业务语义、算法约束、边界条件、降级规则、错误处理原因和运行假设。不得用通用模板句替换原有有信息量的注释。

不要把 Java 规范硬套到其他语言。后续 Python、Cpp 等规范应分别新增 reference，并在本 Skill 中增加语言选择路由。

## 6. 验收清单

- 已读取项目入口和相关项目事实，或说明没有项目上下文。
- 真实项目审查已创建或更新项目 workflow evidence，并记录 Task Brief、trace、findings 和当前闭环状态。
- 目录、包或 glob 级审查已记录全量文件覆盖矩阵；每个目标文件都有明确审查状态和结论。
- Java 目录级审查已记录注释覆盖矩阵；类级 Javadoc、方法级 Javadoc、字段/常量注释、关键行内注释均已检查或明确 defer 原因。
- Java 包级 Javadoc 完整性作为验收目标时，已运行 `test-java-javadoc-coverage.ps1`，并在 workflow evidence 中记录 JSON 摘要。
- Java 注释修复已明确区分结构覆盖和语义质量；若使用脚本检查 Javadoc，已说明该脚本是只读门禁，不是注释内容生成依据。
- Java 目标范围已运行 `test-java-magic-values.ps1`；候选已分类并记录来源/量纲/处置，`unresolved` 候选未被误报为完成。
- 多开关、可选本轮输入和历史状态共同决定行为时，已记录状态决策表并用自动回归覆盖关键组合。
- 已使用 `test-code-review-workflow-evidence.ps1` 检查 workflow evidence；阶段尚未闭环时不启用 `-RequireClosedLoop`。
- 已检查代码行为、异常、数据、并发、安全、可维护性和测试。
- Java 代码已读取 Java reference。
- Findings 有文件和行号或明确定位方式。
- 未运行测试时，说明原因和残余风险。
- 用户审核、修复交接、复查和再次审核状态已记录；如果尚未发生，明确标记为 pending。
- 用户返回 revise 时，已作为新一轮 Review Findings 记录，并按可复用程度 patch Skill/reference 或项目文档。
- 没有把项目私有事实或敏感内容写入 Skill、Memory、Knowledge 或通用 Harness 文档。
- 产生规范沉淀需求时，已标记为 candidate 或 needs-user-review。

## 7. 当前限制

本 Skill 已完成真实项目 forward-test、用户 revise 和最终条件批准，当前 reviewed 版本仍有以下维护边界：

1. 当前只提供 Java reference；Python、Cpp 等语言需后续补齐。
2. 已新增独立 `code-implementation` reviewed Skill；代码审查发现进入修复阶段时必须切换到该 Skill，并在修改后交回本 Skill 复查。
3. 是否拆分出 `java-feature-implementation` 和 `test-development` reviewed Skill，需由后续真实任务验证。
