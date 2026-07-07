---
name: code-implementation
description: 基于用户批准的 code review findings、明确修复请求、功能实现请求、回归缺陷、Java 企业级代码修改、测试修复或重构任务执行代码修改。适用于真实项目或通用仓库中需要从 review 切换到 implementation workflow 的场景，必须读取项目入口、相关 workflow evidence、code-review Skill 输出和语言规范，先确认用户授权、范围、风险和验证计划，再修改代码、运行验证、更新项目 workflow evidence，并将结果交回 code-review Skill 复查和用户再次审核。
metadata:
  short-description: 代码修改与实现闭环
  asset-state: reviewed
  review-state: approved
---
# Code Implementation Skill（代码实现技能）

## 1. 笔记属性

| 属性 | 内容 |
|---|---|
| 文档 | `harness/skills/reviewed/code-implementation/SKILL.md` |
| 资产状态 | reviewed |
| 审核状态 | approved，已由用户与 code-review Skill 一起通过真实项目闭环验证 |
| 主题语言 | 中文；专业词、命令、路径、类名、函数名和代码标识保留英文 |
| 适用对象 | 用户批准后的代码修复、功能实现、测试修复、重构、review finding 修复和实现后验证 |
| 输出结果 | 代码变更、验证结果、workflow evidence 更新、残余风险、交回 code-review 复查的明确 handoff |
| 事实边界 | 项目事实留在项目文档或 workflow evidence；本 Skill 只保存可复用实现流程 |

## 2. 关联文档和读取路径

执行代码修改前，先读取 Harness 和项目入口，再读取审查证据与语言规范。

| 文档 | 读取目的 |
|---|---|
| `AGENTS.md` | 获取 Harness Root 入口、硬约束、敏感边界和文档语言规则。 |
| `INDEX.md` | 路由到 Harness、项目实例、本地用户边界和运行态边界。 |
| `harness/HarnessIndex.md` | 确认 Tool、Skill、Governance、Project Template 和 Verification 入口。 |
| `harness/skills/SkillIndex.md` | 确认当前 Skill 状态，避免绕过 candidate/review。 |
| `harness/skills/reviewed/code-review/SKILL.md` | 读取审查 findings、复查和用户再次审核流程。 |
| `harness/skills/reviewed/code-review/references/java-code-standards.md` | 修改 Java 代码时读取，作为 Java 规范和项目风格适配参考。 |
| `harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1` | 修改前后校验 code review workflow evidence 是否完整。 |
| `harness/tools/scripts/stable/test-java-javadoc-coverage.ps1` | Java 注释或 Javadoc 修复后的覆盖门禁；当修复目标包含完整 Javadoc 时必须运行。 |
| `projects/<project-id>/AGENTS.md` | 获取项目级代码边界、技术栈、Git 边界和验证入口。 |
| `projects/<project-id>/docs/project/ProjectIndex.md` | 路由到项目架构、源码布局、测试策略、验证命令和 workflow evidence。 |
| `projects/<project-id>/docs/project/workflow/<task-id>.md` | 真实项目实现任务必须更新的审查、修复、验证、复查和审核证据。 |

## 3. 边界规则

1. 没有用户明确要求修改代码，或没有用户批准的 finding / 功能目标时，不进入实现阶段。
2. 不把 code review findings 自动等同于修复授权；findings 需要用户 approve、revise 或明确要求修复。
3. 修改范围必须限定在用户目标和 workflow evidence 记录的 scope 内；超出范围先停下并请求确认。
4. 不直接修改外部真实业务源码；受管项目只修改 `projects/<project-id>` 下的沙盒工作副本。
5. 不读取或写入 settings/auth、密钥、私有 Maven settings、未脱敏日志或完整生产数据。
6. 不把项目事实、实现细节或一次性日志写入通用 Skill；项目证据写入项目 workflow evidence。
7. 实现完成不等于闭环完成；必须交回 code-review 复查，并等待用户再次审核。
8. 遇到高风险重构、接口兼容、安全、数据迁移、并发模型或验收标准不清时，先补设计和确认，不直接改代码。
9. Java 注释或 Javadoc 修复不得用批量脚本机械覆盖原有业务注释。脚本只能用于只读门禁、覆盖检查或报告生成；注释内容修改必须基于源码行为、现有注释和必要历史版本进行语义保留式编辑。

## 4. 实现流程

### 4.1 接收 handoff

进入实现前确认：

| 字段 | 要求 |
|---|---|
| 目标 | 明确修复哪些 findings、实现什么功能或修改什么测试。 |
| 用户授权 | 明确用户已要求修复或实现；如果只是 review 输出，不能默认修改。 |
| Workflow Evidence | 真实项目必须有 `docs/project/workflow/<task-id>.md`，并记录当前状态。 |
| 范围 | 明确允许修改的文件、模块、测试和禁止路径。 |
| 验证计划 | 明确编译、单测、main program、仿真、回归或手工验证命令。 |
| 风险 | 标记是否涉及真实业务源码、接口兼容、状态迁移、并发、安全或数据治理。 |

如果来自 code-review Skill，先运行：

```text
harness/tools/scripts/stable/test-code-review-workflow-evidence.ps1
  -Root <HARNESS_ROOT>
  -ProjectId <project-id>
  -WorkflowEvidence <docs/project/workflow/<task-id>.md>
```

若命令失败，先补证据或请用户确认是否允许继续。

### 4.2 设计修改

修改前记录：

- 问题和目标 finding；
- 受影响文件、调用方、被调用方和测试；
- 修改方案；
- 回滚或不修改方案；
- 验证命令；
- 预计残余风险。

设计原则：

1. 优先保持项目已有架构和局部风格。
2. 小范围修复优先于跨层重构。
3. 不把业务规则伪装成 util；不把通用原子逻辑重复散落。
4. Java main 源码优先使用项目定制日志和异常机制；测试代码优先使用 `@Slf4j log`，避免 `System.out.println`。
5. 修改错误码、日志、状态、响应或持久化语义时，同步考虑回归测试和项目文档证据。
6. 修改 Java 注释或规范类 finding 时，按 code-review Java reference 复查类级 Javadoc、方法级 Javadoc、字段/常量注释、行内注释和版本标签来源，避免只修用户点名的一行。
7. 修改既有注释时，先识别原注释是否包含业务规则、算法约束、边界条件、降级原因、错误归因或运行假设；有价值的信息必须吸收到新注释中，不能被模板化句子替换。

### 4.3 执行修改

执行时：

1. 先读取目标文件和相关上下文。
2. 用 `apply_patch` 进行手工代码编辑。
3. 保留用户已有改动，不做无关格式化、重排或大范围重构。
4. 对共享行为、错误码、日志、状态投影、持久化和 API 输出保持最小必要变更。
5. 若发现新问题超出原 scope，记录为新增 finding 或 open question，不顺手扩展修改范围。
6. 对目录级注释修复，按模块分批执行并记录 partial/full 状态；不能用一次性机械替换把整个包声明为语义精修完成。

### 4.4 验证

按风险选择验证：

| 风险 | 验证要求 |
|---|---|
| 文档或注释改动 | `git diff --check`，必要时跑文档/治理脚本。 |
| Java Javadoc 完整性修复 | 运行 `test-java-javadoc-coverage.ps1`，检查类级标签、方法 Javadoc、`@param`、`@return` 和空白星号行；用户要求每个子函数都有 Javadoc 时启用 all-method 模式。 |
| Java 编译相关 | 使用 `invoke-maven-project.ps1` 或 `invoke-java-main.ps1`，至少覆盖 `test-compile` 或相关 main program。 |
| 单元逻辑 | 运行目标测试或最小 main regression。 |
| 真实数据或仿真 | 使用项目测试手册和稳定命令运行对应仿真/回放/业务指标链路。 |
| 高风险共享行为 | 增加或更新回归测试，并说明未覆盖风险。 |

验证失败时，不掩盖失败；记录失败、原因、已尝试动作和下一步修复建议。

### 4.5 更新 workflow evidence

真实项目必须更新 `docs/project/workflow/<task-id>.md`：

- Fix Plan：修改方案和范围。
- File Change Summary：修改文件、目的、行为影响。
- Validation Report：命令、结果、失败或通过摘要、未跑原因。
- Fix State：`fixed-pending-recheck`、`blocked`、`not-fixed` 或 `partial`。
- Recheck Handoff：交回 code-review Skill 复查的范围和验证证据。
- Residual Risk：残余风险和用户需要决策的问题。

修改后再次运行 code review evidence gate；若修复阶段尚未完成最终复查，可不启用 `-RequireClosedLoop`，但必须保证结构完整。

### 4.6 交回复查

实现阶段结束后：

1. 汇总代码变更和验证结果。
2. 明确是否需要 code-review Skill 复查原 findings、diff 和验证证据。
3. 不宣称 accepted，除非用户完成最终审核。
4. 若用户要求继续修复复查发现，重复本流程。

## 5. 输出格式

最终答复包含：

```text
变更摘要:
验证:
Workflow Evidence:
交回复查:
残余风险:
```

如果未能修改或验证，明确说明阻塞原因和下一步。

## 6. 验收清单

- 已确认用户授权修复或实现。
- 已读取项目入口、code-review evidence 和相关源码上下文。
- 已用稳定命令检查 workflow evidence 结构。
- 已按范围完成最小必要代码修改，未混入无关重构。
- 已运行与风险匹配的验证，或清楚记录未运行原因。
- Java 注释或规范修复已按 code-review reference 复查同类规则的其它层级，例如类、方法、字段/常量、行内注释和版本标签来源。
- Java 注释内容修改已保留或吸收原有业务语义；若只完成结构门禁，应在 workflow evidence 中明确标记，不宣称语义精修完成。
- Java Javadoc 完整性修复已运行 `test-java-javadoc-coverage.ps1`，并把结果写回 workflow evidence。
- 已更新项目 workflow evidence 的 Fix Plan、File Change Summary、Validation Report、Fix State 和 Recheck Handoff。
- 已交回 code-review Skill 复查；最终 accepted 状态等待用户再次审核。

## 7. 当前限制

本 Skill 已完成真实项目 forward-test、用户 revise 和最终条件批准，当前 reviewed 版本仍有以下维护边界：

1. 当前只定义实现 workflow；语言细节主要依赖 code-review Java reference。
2. 不提供自动批量覆盖注释内容的修改策略脚本；实现仍由 agent 按项目上下文和 `apply_patch` 执行，稳定脚本只承担检查和报告职责。
3. 后续如拆分 `java-feature-implementation` 或 `test-development`，需要通过新的真实任务验证。
