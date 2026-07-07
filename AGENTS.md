---
documentName: AGENTS.md
version: v1.1.0-powershell-encoding-rule
updatedAt: 2026-07-06 09:30:00.000 +08:00
status: active
purpose: 定义 Harness Root 的 Agent 入口契约、最高优先级硬约束、读取顺序、PowerShell 编码规则和长期文档格式、语言规范治理规则。
scope:
  - harness-root-entry
  - agent-loading-order
  - hard-constraints
  - powershell-encoding-standard
  - important-document-frontmatter
  - document-language-standard
prerequisites:
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
outputTo:
  - AGENTS.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: mixed
  reviewedAt: 2026-07-06
  decision: user-requested-powershell-encoding-rule
---
# Harness Root 智能体入口

## 1. 根目录定义

当前工作目录是 Harness Root，也是本地执行沙盒。

```text
<HARNESS_ROOT>
```

推荐发现规则：

```text
cwd = <HARNESS_ROOT>
HARNESS_ROOT = <HARNESS_ROOT>
```


## 2. 必须读取顺序

处理任何非简单任务时，按以下顺序读取：

```text
1. AGENTS.md
2. INDEX.md
3. harness/HarnessIndex.md
4. harness/architecture/PLANS.md
5. 由 INDEX.md 和 harness/HarnessIndex.md 路由到当前任务相关的 Harness 文档、计划、模板、Skill、Tool 或 Policy
6. user/registry/projects.local.json 或 Project Profile，如果已经存在
7. projects/<project-id>/AGENTS.md
8. projects/<project-id>/docs/project/ProjectIndex.md
```

如果后续文档与本文件的硬约束冲突，以本文件为准，除非用户明确要求修改 Harness 设计。

## 3. 最高优先级硬约束

1. 不要把运行态日志、缓存、临时文件、原始会话记录、私有设置或密钥当作稳定事实。
2. 不要把密钥、凭据、私有 Maven settings、auth 文件或未脱敏日志写入可跟踪文档。
3. 除非当前任务明确要求对应阶段，否则不要迁移目录、移动脚本或重构根目录。
4. 不要直接修改外部真实业务源码。受管项目应使用 `projects/<project-id>` 下的沙盒工作副本。
5. 不要把真实业务项目的 git 历史混入 Harness 根仓库。
6. 不要把 RAG Index 当作权威知识源。RAG Index，中文解释是检索索引，是可重建的检索产物。
7. 不要把 Skill、Knowledge、Memory、Project Facts、Workflow Evidence 和 RAG Index 混为同一类资产。
8. 高风险任务在目标、范围、目标项目、验收标准或风险边界缺失或冲突时，必须先向用户澄清。
9. 有稳定 Tool Assets，中文解释是工具资产，时应优先使用稳定工具。临时命令和一次性脚本不会自动成为 Harness 资产。
10. Governance，中文解释是治理，相关变更、Skill 更新、Memory 更新、Knowledge 晋升和 Project Fact 变更，在成为长期资产前需要 review 或用户明确批准。
11. 受 Git 管控的重要 Harness Markdown 文档必须维护基础 YAML frontmatter；文档状态必须使用 `draft`、`review`、`active`、`stale`、`deprecated`、`archived`、`superseded` 之一。
12. 受 Git 管控的重要 Harness Markdown 文档应以中文作为文档主题说明语言；允许保留专业词、命令、路径、代码标识和通用技术名词的英文写法。
13. 读取或写入包含中文的 Markdown、JSON、YAML、PowerShell 输出或项目文档时，在 PowerShell 中必须优先使用显式 UTF-8，例如 `Get-Content -Encoding UTF8`、`Set-Content -Encoding UTF8` 或对应工具参数；不要根据默认终端乱码判断原文损坏，也不要把乱码回写到受 Git 管控的文档或源码。
14. 稳定 PowerShell 脚本应尽量保持源码 ASCII 化。确需中文文本、中文正则或中文字符串时，必须确认目标 Windows PowerShell 运行环境能按 UTF-8 正确解析；旧版 Windows PowerShell 对无 BOM UTF-8 `.ps1` 可能按本机代码页解析，导致中文字符串被破坏。脚本中的长期规则应优先使用机器字段、ASCII key、结构化配置或外部 UTF-8 文档数据，减少中文源码文本依赖。

## 4. 关键稳定记忆

- `<HARNESS_ROOT>` 是 Harness Root，也是当前本地沙盒。
- 当前目标落地模型是 Harness Distribution Repo + Harness Workspace + Project Instance，不是把整套 Harness 复制进每个项目。
- 真实项目实例只放在 `projects/<project-id>`。
- `harness/architecture/HarnessEngineering.md` 是唯一最终架构权威。
- `INDEX.md` 是全局总索引，负责把 agent 路由到 General Harness、项目实例、本地用户边界和运行态边界。
- `harness/HarnessIndex.md` 是 General Harness 资产分层索引。
- 阶段状态、验收状态和下一步由 `INDEX.md` 路由到 `harness/architecture/PLANS.md`；`AGENTS.md` 不记录每轮阶段更新。
- `adapter/` 是用户、gateway 和 Agent Runtime 的交互适配层。
- `harness/tools/` 是工具资产层；稳定脚本、工具文档、manifest、候选脚本、历史脚本、runtime helper 和 external tool 边界由 `harness/tools/ToolsIndex.md` 路由。
- `user/` 是本地用户和私有配置边界；其中的本机路径、settings、auth、GitHub 账号信息、私有仓库信息和私有 Maven 信息不得进入 prompt、Task Brief、workflow summary 或 tracked docs。
- `harness/rag/` 是目标 RAG 摄取机制层；真实用户知识进入 `user/knowledge/` 或外部 private knowledge repo；`var/rag/` 是可重建索引、embedding 和运行态产物。
- Hermes、Codex 等 Agent Runtime 仍然是外部执行主体。
- Harness 任务证据应优先收敛到架构计划、治理报告或项目 workflow evidence，避免每轮任务新增零散临时文档。

## 5. 任务接入规则

用户提示词是自然语言，不要求用户填写固定模板。

agent 应把提示词整理为 Task Brief，中文解释是任务简报，至少记录：

- 目标；
- projectId；
- 范围；
- 验收标准；
- 验证计划；
- 缺失关键字段；
- 推断字段和来源；
- 风险等级；
- 是否需要审批。

涉及项目执行的任务必须把 Task Brief 保存进 workflow evidence，中文解释是工作流证据。

## 6. 文档格式治理规则

所有受 Git 管控的重要 Harness Markdown 文档，在创建或更新时应包含基础 YAML frontmatter，并至少维护以下字段：

```yaml
documentName:
version:
updatedAt:
status:
purpose:
scope:
prerequisites:
relatedDocuments:
outputTo:
owner:
reviewAfter:
supersededBy:
dependsOn:
review:
  reviewedBy:
  reviewedAt:
  decision:
```

规则：

1. `status` 只表示文档状态，不表示迁移阶段、实现状态或验收结果。
2. 阶段状态、验收结果和下一步只写入 `harness/architecture/PLANS.md`。
3. 兼容跳转、历史文档或被替代文档应使用 `deprecated`、`archived` 或 `superseded`，并填写 `supersededBy`。
4. 非 Markdown 文件、许可证正文、JSON example、脚本和运行态产物不套用 Markdown frontmatter。
5. 补齐 frontmatter 不得引入密钥、私有 settings、本机绝对路径、私有仓库 URL 或未脱敏日志。

## 7. 文档语言规范

受 Git 管控的重要 Harness Markdown 文档应以中文作为文档主题说明语言。

允许保留英文的内容包括：

- 专业词和通用技术名词，例如 Agent Runtime、Tool Asset、Command Surface、Status JSON、Workflow Evidence；
- 命令、参数、路径、文件名、类名、函数名、配置键和代码标识；
- 必须与外部工具、协议或标准保持一致的原文名称。

规则：

1. 文档标题、目的、范围、规则、边界、验收和维护说明应优先使用中文表达。
2. 英文专业词首次出现时，必要时补充中文解释。
3. 不把整篇 Harness 正式文档写成英文说明，除非该文件是外部规范、第三方原文或代码内注释。

## 8. 继续读取

继续读取：

```text
INDEX.md
```
