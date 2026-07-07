---
documentName: harness/skills/reviewed/code-review/references/java-code-standards.md
version: v1.8.0-semantic-comment-preservation
updatedAt: 2026-07-07 10:30:00.000 +08:00
status: active
purpose: 作为 code-review reviewed Skill 的 Java 代码审查规范参考，吸收阿里巴巴 P3C Java 开发手册、真实项目风格和用户定制规则，覆盖命名、Javadoc 格式、语义保留式注释修复、可执行 Javadoc 覆盖门禁、版本标签、字段常量注释、编程、工程结构、异常日志、安全、测试和项目风格适配。
scope:
  - skill-reference
  - java-code-review
  - java-code-standards
  - p3c-java-guidelines
  - enterprise-java
  - project-style-adaptation
  - logging-and-exception-policy
  - javadoc-style-policy
  - javadoc-version-policy
  - field-constant-comment-policy
  - batch-comment-coverage-policy
  - semantic-comment-preservation-policy
  - executable-javadoc-gate
prerequisites:
  - harness/skills/reviewed/code-review/SKILL.md
relatedDocuments:
  - harness/skills/SkillIndex.md
  - harness/skills/SkillPolicy.md
  - harness/governance/ProjectHarnessFeedbackPolicy.md
  - harness/tools/scripts/stable/test-java-javadoc-coverage.ps1
outputTo:
  - harness/skills/reviewed/code-review/references/java-code-standards.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/skills/reviewed/code-review/SKILL.md
review:
  reviewedBy: agent
  reviewedAt: 2026-07-07
  decision: semantic-comment-preservation-rule-added
---
# Java Code Standards（Java 代码审查规范）

本文件是 `code-review` reviewed Skill 的 Java reference。它不是某个项目的强制格式化配置，也不是阿里巴巴 P3C 手册的全文副本；它用于指导智能体在 Java 代码审查时形成稳定、可复用、可解释的判断。

适用优先级：

```text
用户当前指令
-> 项目 AGENTS.md / ProjectIndex.md / 项目规范
-> 目标代码库已经形成的一致风格
-> 本 Java reference
-> 通用 Java 判断
```

如果项目风格与本文件冲突，先记录冲突、影响和建议，不直接强制重写。

## 目录

1. 外部基线和吸收原则
2. 项目风格参考方法
3. 命名规范
4. 注释规范
5. 文件长度、职责和拆分
6. 编程规范
7. Spring 和企业级 Java
8. 异常、日志和可观测性
9. 安全和隐私
10. 测试规范
11. Code Review Checklist
12. 风格适配规则

## 1. 外部基线和吸收原则

参考材料：

- 阿里巴巴 P3C Java 开发手册入口：`https://alibaba.github.io/p3c/`
- P3C 命名风格：`https://alibaba.github.io/p3c/编程规约/命名风格.html`
- P3C 代码格式：`https://alibaba.github.io/p3c/编程规约/代码格式.html`
- P3C 注释规约：`https://alibaba.github.io/p3c/编程规约/注释规约.html`
- P3C 异常日志、单元测试、安全规约和工程结构章节。

P3C 的价值在于：

1. 以 Java 开发者为中心，把规范分为编程规约、异常日志、单元测试、安全规约、MySQL 数据库和工程结构。
2. 按约束强度区分强制、推荐、参考，便于 code review 判断严重程度。
3. 对命名、格式、注释、异常、日志、测试、安全和分层给出了企业级基线。

在 Harness 中的吸收方式：

1. 不复制 P3C 全文，只沉淀适合作为智能体审查规则的摘要。
2. P3C 强制项默认至少按 P2 处理；如果影响正确性、安全、数据一致性或生产稳定性，升级为 P0/P1。
3. P3C 推荐项默认按 P3 或 open question 处理；只有造成真实维护风险时才作为 finding。
4. 用户定制规则高于通用规则，例如本文件中的 500 行长度、类级注释模板、Javadoc 格式、版本标签来源、方法注释、字段常量注释、行内注释、通用原子函数拆分、main/test 日志和异常优先级。
5. 项目局部约定必须被尊重；若项目约定本身引入明确风险，再作为风险提出。

## 2. 项目风格参考方法

当用户提供真实项目中的参考类或项目已有统一风格时，先把它当作“项目局部风格样本”，不要把具体项目名、包名、类名或业务术语沉淀为通用 Skill 规则。通用 Skill 只沉淀可复用判断方法。

可借鉴点：

1. 类级 Javadoc 放在 `import` 之后、注解和 `class` 声明之前，提前说明文件的功能、定位、边界、主链路、运行约束、作者、日期、版本和相关文件。这个位置适合让读者在进入代码前先理解影响面和职责范围。
2. 顶层入口类清楚表达 orchestration 与 algorithm/business logic 的边界：网关负责调度和响应封装，不实现算法、策略或插件选择逻辑。
3. 长流程方法使用编号分段注释，有助于审查主链路、定位故障和确认阶段顺序。
4. 业务异常和系统异常分开处理，外部响应只返回公开摘要，内部日志保留 root cause 或原始异常。
5. 日志通过管理服务组装结构化请求，而不是散落直接字符串日志，有利于 trace、errorCode 和 event 统一治理。

需要改进或不建议机械照搬的点：

1. 所有 Java 文件都应有类级 Javadoc，但注释密度要随文件类型变化。网关、编排器、状态机、核心服务可以使用较高密度注释；普通 DTO、简单 mapper、短工具方法不应堆叠重复注释。
2. 类 Javadoc 中不应出现嵌套 `/** ...` 这类注释起始标记；结构化小标题应写为普通文本，例如 `【职责】`、`【边界】`、`【影响面】`。
3. 字段、常量和短方法的注释应解释业务语义、线程安全、边界或不变量，不应重复变量名字面含义。
4. 长分段横幅适合主流程编排，不适合短方法；短方法优先通过命名、抽取方法和测试表达意图。
5. static wildcard import 只在项目局部 helper 函数高度集中且已有明确惯例时接受；通用 Java 规范中优先显式导入。

参考结论：

架构关键类可以作为“如何表达职责、边界和影响面”的样本，但不应作为所有 Java 文件的统一格式模板。更合理的沉淀是：保留类级功能说明、职责边界、结构化日志、异常隔离和长流程分段说明；减少普通代码中的注释噪声和视觉横幅。

## 3. 命名规范

### 3.1 总原则

1. 命名必须自解释，优先使用完整英文单词或清晰技术缩写，不为了短而牺牲语义。
2. 禁止拼音与英文混用，禁止中文命名；行业通用地名、品牌名或项目已有专有名词除外。
3. 不使用下划线或美元符号作为变量、方法、类名的开头或结尾。
4. 避免不规范缩写，例如 `condi`、`bizProc`、`tmpObj`。缩写只允许使用行业、协议、项目已稳定接受的词，例如 `DTO`、`HTTP`、`ID`。
5. 同一概念在同一模块内只能有一套命名，不要在 `state`、`status`、`phase` 之间随意切换。

### 3.2 包和模块

- package 使用全小写，按组织、产品、领域、模块分层。
- 点分隔符之间只放一个自然语义单词，包名优先使用单数形式。
- 不把实现细节、临时阶段名、个人名或日期放入正式包名。
- 通用工具包可使用 `util` 或 `utils`，但必须遵从项目既有惯例；新建包前先检查项目已有命名。

### 3.3 类型命名

| 类型 | 规则 | 示例 |
|---|---|---|
| class | `UpperCamelCase`，名词或名词短语 | `OrderService`, `RequestAssembler` |
| interface | `UpperCamelCase`，表达能力、契约或服务名 | `SolverService`, `StateProjectionService` |
| implementation | 对接口实现类可使用 `Impl` 后缀，遵从项目分层 | `CacheServiceImpl` |
| abstract/base class | 使用 `Abstract` 或 `Base` 前缀 | `AbstractSolverPlugin` |
| enum | 类名可带 `Enum` 后缀，枚举成员使用 `UPPER_SNAKE_CASE` | `LogEventEnum.GATEWAY_FAILURE` |
| exception | 以 `Exception` 结尾，表达失败语义 | `BusinessRuleException` |
| DTO/VO/BO/DO/PO | 保持项目语义，不混用 | `GatewayRequest`, `GatewayResponse` |
| test | 与被测对象对应，以 `Test` 或项目约定后缀结尾 | `GatewayServiceTest` |

### 3.4 方法、字段和变量

- 方法、参数、成员变量、局部变量统一使用 `lowerCamelCase`，必须遵从驼峰形式。
- 方法名使用动词或动宾短语开头，表达动作和返回语义。
- 获取单个对象可用 `get` 前缀，获取多个对象可用 `list` 前缀，统计可用 `count` 前缀，插入可用 `save` 或 `insert` 前缀，删除可用 `remove` 或 `delete` 前缀，修改可用 `update` 前缀。
- boolean 方法使用 `is`、`has`、`can`、`should`、`requires` 等前缀；POJO 布尔字段不要加 `is` 前缀，避免序列化或框架解析歧义。
- 集合变量名体现元素含义，不用 `list`、`map` 单独命名。
- 临时变量必须服务于可读性；禁止用 `a`、`b`、`data`、`info`、`obj`、`temp` 表达核心领域对象。
- 常量使用 `UPPER_SNAKE_CASE`，语义完整清楚，不要嫌名字长。
- long/Long 字面量使用大写 `L`，不用小写 `l`。

## 4. 注释规范

### 4.1 类级 Javadoc

每个 Java 程序文件原则上都应有类级 Javadoc。业务入口、核心服务、状态机、编排器、SPI、插件、工具类、领域模型和测试基类必须具备清晰类注释。

类级 Javadoc 推荐放置位置：

```text
package

import

/**
 * 类级 Javadoc
 */
@Annotation
public class Xxx {
}
```

如果存在版权、许可证或生成声明，放在 `package` 之前；业务功能说明不放在版权块里。

类级 Javadoc 建议字段：

```java
/**
 * <一句话说明本文件/类的核心功能>
 * 【定位】
 * 说明该类在系统分层中的位置，例如 gateway、service、domain、util、plugin、test。
 * 【职责】
 * 说明本类负责什么。
 * 【边界】
 * 说明本类不负责什么，不能越过哪些服务或状态区域。
 * 【影响面】
 * 说明修改本类可能影响的调用链、状态、日志、错误码、数据一致性或性能。
 * 【主链路】
 * 对核心编排类列出主要执行阶段；普通类可省略。
 * 【相关文件】
 * 使用 @see 指向接口、入口、模型、测试或关键协作者。
 * @author <作者或团队>
 * @since <用户确认的引入日期或本次补充注释/契约确认日期>
 * @version <项目既有版本号；来源于项目版本常量、构建元数据、package-info、项目文档或用户确认>
 */
```

审查标准：

1. 注释应在读代码前解释功能、定位、边界和影响面。
2. 架构关键类应说明主链路和运行约束。
3. 普通 DTO、枚举、简单工具类可以使用轻量模板，但仍要说明用途。
4. 如果项目 IDE、Javadoc 或 Checkstyle 对注释内部 `*` 空白行提示“空白行将被忽略”，类级和方法级 Javadoc 使用连续结构化小标题，不在注释内部插入空白 `*` 行。
5. `@since` 表示类、方法或契约被引入或被用户确认的时间；对既有代码补充 Javadoc 且没有可靠历史来源时，不杜撰旧日期，按用户确认或本次修订日期填写，或先请求用户确认。
6. 对有版本维护口径的项目，架构关键类 Javadoc 应包含 `@version`；版本值必须来自项目已有版本来源，例如集中版本常量、构建元数据、package-info、项目文档或用户明确确认。
7. `@version` 不是变更触发器。agent 不得因为一次普通代码改动、注释补齐或局部修复擅自升级版本号；只能引用已有版本口径。
8. 如果当前上下文无法确认版本号，必须向用户询问，或在 code review 中记录 open question；不要删除版本标签来规避未知，也不要猜测版本号。
9. 注释中的作者、日期和版本策略需要遵从项目约定；如果项目明确不维护 `@version`，记录该项目约定，不强行引入。
10. 不在 Javadoc 中写变更历史，Git 记录负责历史。

语义保留式注释修复规则：

1. 修复既有 Java 注释时，先读取当前文件、相关上下文和必要的历史版本，识别原注释中的业务规则、算法约束、边界条件、降级原因、错误归因、运行假设和测试口径。
2. 新 Javadoc 可以调整结构、补齐标签和消除告警，但必须吸收原注释中有价值的信息；不得用“执行 xxx 相关处理”“当前方法所需参数”这类模板句覆盖原业务语义。
3. 如果原注释与当前源码不一致，不能直接保留旧说法；应以源码事实为准修正，并在 workflow evidence 中记录该处为语义校正。
4. 对大量文件进行注释修复时，必须按模块分批处理，并在 workflow evidence 中区分 `structural-javadoc-passed`、`semantic-reviewed`、`semantic-refined` 和 `deferred` 状态。
5. 只运行 Javadoc gate 不能证明注释语义质量。脚本通过只能说明结构门禁通过，不能作为“业务注释精修完成”的唯一证据。
6. 稳定脚本不得作为批量注释内容生成器纳入 Skill 流程；它只用于只读检查、覆盖统计、报告输出和回归门禁。

Java 包级/目录级审查如果用户要求“完整 Javadoc”“注释完整性”或“批量注释修复”，必须使用稳定脚本做只读门禁：

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

门禁输出必须写入项目 workflow evidence。`ExpectedAuthor` 和 `ExpectedVersion` 不能硬编码到通用 Skill；必须来自用户确认、项目版本常量、构建元数据、package-info 或项目文档。无法确认时，先把作者或版本作为 open question，不要猜测。

该门禁只检查结构覆盖、标签、章节和格式，不判断注释是否准确表达业务和算法语义。语义质量必须通过人工源码审查、历史注释对比和项目架构文档交叉验证完成。

### 4.2 方法级 Javadoc

以下方法原则上应写方法级 Javadoc：

- public API、SPI、扩展点、抽象方法；
- 架构关键类中的 public、protected 或包可见协作方法；
- 具有统一错误包装、状态写入、上下文读写、并发、资源释放或安全边界的方法；
- 虽然是 private，但承载非平凡契约、降级规则或复用门禁的 helper 方法；
- 测试工具、诊断 main program 和 fixture 中会被其他测试复用的方法。

方法级 Javadoc 建议字段：

```java
/**
 * <一句话说明方法功能>
 * 【架构约束】说明本方法所在层、禁止越界的职责或调用契约。
 * 【返回】void 方法写“无返回值；失败时抛出...”；非 void 方法使用 @return。
 * @param request 参数业务语义、是否允许为空、状态读写边界
 * @return 返回对象的业务含义、空值策略或封装规则
 */
```

审查标准：

1. public 方法的 Javadoc 必须说明功能、关键架构约束、参数语义和返回结果。
2. void 方法不使用 `@return` 标签，避免 Javadoc 告警；用 `【返回】` 说明“无返回值”和失败语义。
3. 参数说明不只重复变量名，应说明业务语义、是否允许为空、是否只读或会被写入。
4. 方法可能抛出项目标准异常、业务异常或明确非法状态异常时，应在说明中写清楚失败语义；是否使用 `@throws` 遵从项目风格。
5. getter、setter、简单构造器和显然的 DTO 方法可以不写方法 Javadoc，除非项目要求或存在特殊语义。

### 4.3 字段和内部注释

字段和常量注释应覆盖：

- 服务标识、trace key、errorCode、event、registry、shared holder、全局单例、状态字段；
- 业务阈值、时间窗口、重试次数、精度、默认值、配置 key、枚举值和跨模块常量；
- 线程安全、可变性、不变量、生命周期或敏感边界不明显的字段；
- 影响日志、异常、链路追踪、响应封装或状态投影的字段。

应写内部注释：

- 架构关键类、状态机、编排器、复杂策略；
- 业务不变量、边界条件、失败语义、兼容逻辑；
- 安全、并发、数据一致性相关的关键约束；
- 枚举字段和错误码，说明每个值的用途。

不应写注释：

- 重复代码字面含义；
- 给每个 getter、setter 或简单字段写空泛说明；
- 用注释掩盖本可通过命名、抽取方法或测试表达的逻辑；
- 保留注释掉的大段旧代码；
- 没有 owner、原因和触发条件的 TODO。

内部单行注释放在被注释语句上方，`//` 后保留一个空格。方法内部多行注释使用 `/* */`，与代码缩进对齐。

行内注释审查标准：

1. 关键编排步骤应有简短行内注释说明阶段、原因或边界，例如“服务返回失败时保留原始结果，由错误管理服务映射阶段错误”。
2. 统一错误包装、状态投影、上下文分区读写、降级和兼容逻辑应说明“为什么这样做”，不要只重复“调用某方法”。
3. 短工具方法可以少写行内注释，但如果方法内部包含多段校验或降级路径，应在段落前说明意图。
4. 不用大段注释替代清晰命名；注释应服务于审查者理解边界和不变量。

## 5. 文件长度、职责和拆分

1. 每个 Java 文件理论上不应超过 500 行，除非程序功能确实不可拆分，且拆分会破坏一致性、性能或可理解性。
2. 超过 500 行时，code review 必须追问是否可以按职责拆分为 service、strategy、assembler、validator、helper、plugin、domain object 或 test fixture。
3. 单个类只承担清晰职责，不同时做校验、编排、计算、持久化、响应组装、日志治理和外部调用。
4. 通用原子函数应拆分到工具包，例如 `util/` 或项目既有工具包；但工具函数必须是无状态、无隐藏外部依赖、可测试、可复用的。
5. 不要把业务规则塞进 `util/`。如果函数依赖业务上下文、状态迁移、错误码、权限或外部服务，它更可能属于 domain/service/strategy，而不是通用工具。
6. `util/` 中的类应避免大而全，例如 `CommonUtils`、`DateUtils` 无限膨胀；按能力拆分为清晰命名的工具类。
7. 重复三次以上、且语义完全一致的原子逻辑应考虑抽取；只是代码形状相似但业务语义不同的逻辑不要强行合并。

## 6. 编程规范

### 6.1 代码格式

- 使用 4 个空格缩进，禁止 tab 字符。
- 左大括号不换行；非空代码块中左大括号后换行、右大括号前换行。
- `if`、`for`、`while`、`switch`、`do` 等关键字与左括号之间保留一个空格。
- 二目、三目运算符左右各保留一个空格。
- 单行字符数原则上不超过 120 个；超出时按调用链、参数、运算符自然换行。
- `if/else/for/while/do` 即使只有一行也必须使用大括号。
- `switch` 的每个 `case` 必须通过 `break`、`return`、`throw` 等终止，或明确注释 fall-through；必须包含 `default`。

### 6.2 常量和枚举

- 不允许魔法值直接散落在代码中；业务含义稳定的值应定义为常量、枚举或配置。
- 不要用一个全局常量类维护所有常量；按功能和复用层次归类。
- 仅在固定范围内变化的值优先用 enum 表达。
- 常量不要过度提升复用层级。只在类内使用的常量定义在类内；跨模块共享的常量才进入公共 constant 包。

### 6.3 OOP 和方法设计

- 所有覆写方法必须加 `@Override`。
- 可变参数只用于相同参数类型、相同业务含义的场景，并放在参数列表最后。
- 方法应短而明确；长方法只在主流程编排场景可接受，并应有清晰阶段和测试覆盖。
- 条件分支过深时优先使用 guard clause、策略对象、枚举分发或小方法抽取。
- 避免 boolean 参数控制复杂流程；使用枚举、配置对象或策略。
- public 方法明确 null 契约；不允许 null 时尽早校验。
- 不返回含义不明的 null；优先返回空集合、Optional 或明确异常。
- Optional 不作为 DTO 字段或序列化字段，除非项目约定允许。
- 不通过对象引用访问静态变量或静态方法，直接使用类名访问。

### 6.4 集合、泛型和 Stream

- 只要重写 `equals`，必须重写 `hashCode`；自定义对象作为 Set 元素或 Map key 时尤其要检查。
- 不把 `subList` 结果强转为 `ArrayList`。
- 集合入参说明是否可变、是否允许空、是否保持顺序。
- Stream 用于清晰的数据转换；复杂控制流优先普通循环。
- 不在 Stream 中隐藏副作用，尤其是写状态、打日志、调用外部服务。
- 使用泛型消除裸类型和不安全强转。
- 大集合处理注意复制、排序、去重和内存占用。

### 6.5 数值、时间和精度

- 金额、评分、概率、权重和精度敏感计算使用 `BigDecimal` 或项目指定数值模型，明确 scale 和 rounding。
- 时间使用 `java.time`，明确时区、业务时间、采集时间、处理时间和系统时间含义。
- 不在业务代码中散落 `System.currentTimeMillis()`；关键路径应封装为 clock/time policy，便于测试。
- 禁止魔法数字；阈值、窗口、超时、重试次数应有业务语义。

### 6.6 并发和共享状态

- 单例对象必须保证线程安全；单例方法如果访问共享状态，也必须说明线程安全边界。
- 创建线程或线程池时指定有意义的线程名称。
- 共享 mutable state 必须有同步、不可变封装或线程安全容器。
- 不在请求上下文之间共享可变业务状态。
- 异步任务必须定义失败处理、取消、超时和上下文传播。
- 高并发场景避免用等值判断作为退出条件，优先使用区间或原子状态转换。

### 6.7 资源管理

- IO、连接、流、锁使用 try-with-resources 或明确释放策略。
- 外部调用设置超时、重试、熔断或失败边界。
- 不在 finally 中覆盖原始异常。

## 7. Spring 和企业级 Java

- Constructor injection 优先于 field injection。
- Transaction 边界放在 service 层，避免 controller/gateway 隐式持有事务。
- 配置使用 typed properties，避免散落字符串常量。
- Bean 初始化逻辑应可测试、可失败、可观测。
- Controller/Gateway 只做入口、校验、编排和响应，不实现核心业务算法。
- Controller/Gateway 不直接访问 repository，除非项目架构明确允许。
- DTO 入参使用校验注解或显式 validator。
- API 兼容变更必须记录版本、默认值、迁移策略和回滚风险。
- 分层依赖应从入口层向服务层、领域层、基础设施层有序流动，避免循环依赖和跨层读写状态。

## 8. 异常、日志和可观测性

### 8.1 异常处理

- 区分业务异常、系统异常和外部依赖异常。
- 可以通过预检查规避的运行时异常，不应用 catch 作为常规控制流。
- 不吞异常；如果降级、跳过或兜底，必须有可审计原因和日志。
- 不用通用 `RuntimeException` 表示可预期业务失败。
- 项目源码 `main/` 中如果存在定制化异常机制，优先使用项目定制异常、错误码、异常工厂或错误管理服务；只有没有项目定制机制且确实是非法状态时，才考虑 `throw new IllegalStateException(...)`。
- 项目测试包 `test/` 可以优先使用 `throw new IllegalStateException(...)` 表示测试夹具、测试前置条件或不可恢复的测试构造失败，但测试断言仍应优先使用测试框架断言。
- 外部响应不泄露 internalMessage、堆栈、SQL、路径、凭据或敏感上下文。
- 内部日志保留足够 root cause、traceKey、event、errorCode 和安全 message。

### 8.2 日志规范

- 项目源码 `main/` 中如果存在定制化日志机制，优先使用项目定制日志、结构化日志或日志治理服务；没有定制机制时，使用 Lombok `@Slf4j` 提供的 `log`。
- 项目测试包 `test/` 中优先使用 Lombok `@Slf4j` 提供的 `log`；一般情况下严格禁止使用 `System.out.println` 做日志打印。
- `log` 应按语义选择 `debug`、`info`、`warn`、`error` 级别，不要把可恢复业务异常全部打成 ERROR，也不要把失败路径静默处理。
- 通用 Java 项目至少应依赖 SLF4J 门面，不直接绑定 Log4j/Logback API。
- 日志包含 service、method、trace key、event、errorCode 和安全 message。
- 不记录 token、password、auth、settings、完整请求响应或未脱敏生产数据。
- 高频路径避免无意义 info 日志。
- WARN 表示业务可继续但存在异常语义；ERROR 表示失败或不可完成。
- 同一事件不要在多层重复打相同错误日志，除非有不同上下文价值。

## 9. 安全和隐私

- 所有外部输入必须校验格式、范围、长度和权限。
- 用户敏感数据禁止直接展示，日志、异常和响应必须脱敏。
- SQL 参数使用参数绑定或白名单限定，禁止字符串拼接 SQL。
- 文件路径、URL、命令参数、反序列化输入必须有边界检查。
- 不把认证细节、密钥、私有 settings 写入代码、文档或日志。
- 测试数据不能包含未脱敏生产敏感数据。

## 10. 测试规范

- 单元测试遵守 AIR：Automatic、Independent、Repeatable。
- 测试必须自动断言，不使用 `System.out` 或人工观察作为验证。
- 测试之间不能相互依赖执行顺序。
- 单元测试覆盖分支、边界、异常和状态变化。
- 集成测试覆盖真实配置装配、序列化、事务和外部接口模拟。
- 回归测试围绕 bug 的业务契约，不只断言偶然日志文本。
- 时间、随机、并发和外部依赖必须可控。
- 测试命名表达 given/when/then 或业务场景。
- 测试失败信息应能定位业务条件和实际值。

## 11. Code Review Checklist

审查 Java 代码时至少检查：

| 维度 | 问题 |
|---|---|
| 命名 | 是否遵守 UpperCamelCase、lowerCamelCase、UPPER_SNAKE_CASE、自解释、无拼音混用、无随意缩写？ |
| 类注释 | 是否在类声明前说明功能、定位、职责、边界、影响面、相关文件、作者、日期和版本策略？是否避免 Javadoc 空白行告警？是否没有擅自引入或升级 `@version`？ |
| 方法注释 | public 或关键 helper 方法是否说明功能、架构约束、参数语义和返回/失败语义？void 方法是否没有误用 `@return`？ |
| 字段常量注释 | 服务标识、错误码、trace key、registry、共享单例、阈值、配置 key、状态字段等是否说明用途、边界或不变量？ |
| 文件长度 | 是否超过 500 行？超过时是否有不可拆分理由和测试覆盖？ |
| 职责拆分 | 是否混入不属于本类的校验、编排、计算、持久化、响应组装或工具逻辑？ |
| 工具抽取 | 通用原子函数是否进入合适的 `util/` 或 helper？是否误把业务规则塞入工具类？ |
| 行为 | 是否满足业务契约、边界输入和失败路径？ |
| 分层 | 是否越层访问、循环依赖或写入不属于本层的状态？ |
| 异常 | 是否区分业务失败和系统失败？外部响应是否安全？ |
| 异常机制 | `main/` 是否优先使用项目定制异常机制？`test/` 是否只在测试前置失败等场景使用 `IllegalStateException`？ |
| 日志 | `main/` 是否优先使用项目定制日志机制？`test/` 是否使用 `@Slf4j log` 而不是 `System.out.println`？日志是否结构化、可追踪、无敏感泄露、无重复噪声？ |
| 状态 | 是否存在重复处理、状态回退、共享状态污染？ |
| 并发 | 单例、缓存、上下文和异步是否线程安全？ |
| 数据 | 时间、精度、排序、去重、幂等是否明确？ |
| 安全 | 输入、路径、反序列化、权限和依赖是否有边界？ |
| 测试 | 是否有单元、集成或真实场景回归？测试是否自动、独立、可重复？ |
| 注释 | 注释是否解释不变量、复杂意图和边界，而不是重复代码？关键流程是否有必要的行内注释？ |
| 注释语义保留 | 修复既有注释时，是否保留或吸收了原注释中的业务规则、算法约束、边界条件、降级原因和运行假设？是否避免用模板句覆盖有价值注释？ |

目录、包或 glob 级 Java 审查额外要求：

1. 先列出全部 Java 文件，并为每个文件记录一行注释覆盖结论。
2. 类级 Javadoc：判断是否说明功能、定位、职责、边界、影响面；简单 DTO 可以轻量，但不能没有用途说明。
3. 方法级 Javadoc：public API、关键协作方法、状态写入、错误包装、降级规则和复杂 private helper 必须检查；简单 getter/setter 可豁免，但应在覆盖矩阵中说明属于 trivial accessor。
4. 字段/常量注释：服务标识、状态字段、默认值、协议字段、不可变字段、trace/error/log 相关字段必须检查；简单 DTO 字段如果已有 `@Schema` 且语义清楚，可以视为字段注释满足。
5. 行内注释：状态迁移、上下文分区写入、降级、兼容、异常包装、特殊默认值和业务不变量必须检查；普通字段赋值和 Lombok DTO 不强制增加噪声注释。
6. 如果本轮因为业务口径不明不修改注释，必须记录为 deferred finding 或 open question，不能从审查矩阵中省略。
7. 当用户要求完整 Javadoc 时，必须运行 `test-java-javadoc-coverage.ps1` strict switches，并把 fileCount、findingCount 和最终 status 记录到 workflow evidence；脚本未通过时不能宣称批量注释修复完成。
8. 当用户要求注释质量或语义精修时，必须记录每个文件是否完成原注释对比和语义吸收；仅 `findingCount=0` 不足以证明语义精修完成。

## 12. 风格适配规则

审查时按以下方式处理项目风格：

1. 如果项目已有统一风格，优先保持一致。
2. 如果项目风格存在明显 bug 风险、安全风险或维护风险，可以作为 finding 提出。
3. 如果只是审美差异，最多作为 P3 或 open question。
4. 如果用户提供定制规范，记录为本次审查的最高优先级规则。
5. 如果需要沉淀为长期规范，按 `ProjectHarnessFeedbackPolicy.md` 进入 candidate，不直接改 reviewed Skill。

当目标项目存在以下定制倾向时，按项目文档、用户口径或 workflow evidence 记录为“项目级规则”，不要把具体项目名称、包路径或类名写入通用 Skill：

- 架构关键类必须使用中文 Javadoc 说明功能、定位、边界、影响面和主链路；专业词、类名、命令和路径保留英文。
- Javadoc 不应为了视觉分段插入会触发 IDE/Javadoc 告警的空白 `*` 行；优先使用连续的 `【定位】`、`【职责】`、`【边界】`、`【影响面】` 小标题。
- 既有代码补 Javadoc 时，`@since` 不自动沿用邻近类的历史日期；没有可靠来源时按用户确认或本次修订日期。`@version` 读取项目已有版本口径；无法确认时询问用户，不得写死某个项目的版本常量路径。
- 架构关键类的 public 方法和承载降级/错误包装契约的 private helper 方法应有方法级 Javadoc；void 方法用 `【返回】` 说明结果，不写 `@return` 标签。
- 网关、编排器和 helper 中的关键失败路径、上下文写入检查和降级路径应有简短行内注释，说明阶段和原因。
- 网关、编排器和 helper 中的 `SERVICE_NAME`、registry、共享实例、错误码和 trace 相关字段应有字段注释，说明其日志、异常或链路追踪定位用途。
- 长编排流程可以使用编号分段注释，但短方法不应使用大横幅注释。
- 日志和错误处理应优先使用项目管理服务，避免绕过统一日志和错误码机制。
- `main/` 源码应优先使用项目的日志治理服务和异常/错误码管理服务；无定制机制时才退回 `@Slf4j log` 或 `IllegalStateException`。
- `test/` 测试代码一般使用 `@Slf4j log` 输出诊断，严格避免 `System.out.println`；测试构造失败可使用 `IllegalStateException`，业务断言仍用测试框架断言。
- Gateway / service orchestration 层不应混入下游核心算法、策略或插件选择实现，除非项目架构明确要求。
- 状态投影、数据治理、时间轴、求解、响应组装等子服务应保持职责边界清晰。
- 单个 Java 文件原则上控制在 500 行以内；超过时必须说明不可拆分理由。
- 通用原子函数应下沉到合适的 util/helper 包，但业务规则和状态迁移不得伪装成工具函数。
- 大范围注释修复必须保留项目已有业务语义；脚本只作为只读门禁，不作为内容生成器。
