# Harness Root 智能体入口

Status: active
Version: v0.9.0-index-led-entry
Date: 2026-06-12

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

Harness 是面向智能体运行时，英文 Agent Runtime，的通用文档系统知识库、项目自动化控制层、工具资产层和治理层。Codex、Hermes 等 Agent Runtime 负责推理、用户交互、工具调用、文件修改、命令执行和会话管理；Harness 负责入口、约束、项目路由、知识/记忆/技能、稳定工具、验证报告、安全治理和资产沉淀。

## 2. 必须读取顺序

处理任何非简单任务时，按以下顺序读取：

```text
1. AGENTS.md
2. harness/INDEX.md
3. 由 harness/INDEX.md 路由到当前任务相关的 Harness 文档、计划、模板、Skill 或 Policy
4. user/registry/projects.local.json 或 Project Profile，如果已经存在
5. projects/<project-id>/AGENTS.md
6. projects/<project-id>/docs/project/ProjectIndex.md
```

`docs/` 当前只保留短期兼容入口。不要把 `docs/` 里的 stub 当成架构、计划或治理正文来源。

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

## 4. 关键稳定记忆

- `<HARNESS_ROOT>` 是 Harness Root，也是当前本地沙盒。
- 当前项目落地模型是中央 Harness Root + Project Profile + 项目入口，不是把整套 Harness 复制进每个项目。
- 真实项目实例只放在 `projects/<project-id>`。
- `harness/architecture/HarnessEngineering.md` 是唯一最终架构权威。
- `harness/INDEX.md` 是长期总索引，负责把 agent 快速路由到架构、计划、治理、模板、工具、RAG、项目模型和报告。
- 阶段状态、验收状态和下一步由 `harness/INDEX.md` 路由到 `harness/PLANS.md`；`AGENTS.md` 不记录每轮阶段更新。
- `adapter/` 是用户、gateway 和 Agent Runtime 的交互适配层。
- `tools/scripts/` 是稳定脚本、runtime helper、历史脚本和候选脚本的统一工具层。
- `user/` 是本地用户和私有配置边界；其中的本机路径、settings、auth、GitHub 账号信息、私有仓库信息和私有 Maven 信息不得进入 prompt、Task Brief、workflow summary 或 tracked docs。
- `rag/knowledge/` 是用户知识库的人类可读分层；`var/rag/` 是可重建索引、embedding 和运行态产物。
- Hermes、Codex 等 Agent Runtime 仍然是外部执行主体。
- P11 及后续阶段证据应优先收敛到阶段级合并报告和项目 workflow evidence，避免每轮任务新增零散临时文档。

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

## 6. 继续读取

继续读取：

```text
harness/INDEX.md
```
