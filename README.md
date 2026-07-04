---
documentName: README.md
version: v1.4.1-h9-4-closeout
updatedAt: 2026-07-05 00:00:00.000 +08:00
status: active
purpose: 作为 Harness Distribution Repo 的用户安装和使用手册，说明项目定位、安装、验证、卸载、快速开始、Knowledge/RAG 使用、Memory 使用、常用命令、边界、贡献和 License。
scope:
  - user-manual
  - installation-guide
  - quick-start
  - knowledge-rag-user-guide
  - memory-user-guide
  - command-reference
  - contribution-guide
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
  - harness/bootstrap/BootstrapIndex.md
  - harness/tools/ToolsIndex.md
  - harness/rag/RAGIndex.md
  - harness/memory/MemoryIndex.md
  - harness/governance/MemoryGovernance.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/tools/docs/script-index/ScriptIndex.md
  - harness/skills/reviewed/rag-knowledge-use/SKILL.md
  - harness/skills/reviewed/memory-governance-use/SKILL.md
  - harness/skills/rag-structured-ingestion/SKILL.md
  - user/knowledge/README.md
outputTo:
  - README.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
  - harness/bootstrap/BootstrapIndex.md
  - harness/rag/RAGIndex.md
  - harness/memory/MemoryIndex.md
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/governance/MemoryGovernance.md
review:
  reviewedBy: user
  reviewedAt: 2026-07-05
  decision: h9-4-closeout-confirmed
---
# Free Harness World

Free Harness World 是一个面向 Agent Runtime 的通用 Harness 工作区。它提供统一的入口规则、项目路由、工具资产、验证、自检、治理、知识库与 RAG 机制、Memory/Skill 机制和项目模板，用于把 Codex、Hermes 等执行主体接入到可审查、可迁移、可持续演进的本地工作区。

当前仓库还不是正式产品化 release。H8 已完成 bootstrap、install、uninstall 和 `agent-git` 分支验证；H9 正在用真实项目验证 Skill、Governance、Knowledge/RAG 和 Memory 闭环。正式发布需要等待 H9 完整验收和后续 release gate。`main` 分支由用户维护，agent 只在 `agent-git` 分支提交和推送。

## 1. 适用对象

| 对象 | 用途 |
|---|---|
| 普通用户 | 下载、安装、初始化 Harness Workspace，并按 README 执行自检。 |
| 项目维护者 | 在 `projects/<project-id>/` 下挂载项目实例，维护项目事实和工作流证据。 |
| Agent / Runtime 集成者 | 使用 `AGENTS.md`、`INDEX.md`、`harness/HarnessIndex.md` 和工具脚本接入自动化任务。 |
| Harness 贡献者 | 在 `agent-git` 分支修改文档、工具、模板或治理机制，并通过自检后提交。 |

## 2. 当前状态

```text
stage = H9 real project validation
currentLoop = H9-5 summary and H10 gate assessment
defaultAgentBranch = agent-git
humanReleaseBranch = main
license = MIT
```

当前已验证：

- 从 GitHub clone `agent-git`；
- 运行 `bootstrap-harness-workspace.ps1 -Mode status`；
- 运行 `bootstrap-harness-workspace.ps1 -Mode install`；
- 运行 governance self-check；
- 运行 `bootstrap-harness-workspace.ps1 -Mode uninstall`；
- 确认卸载不删除 Git clone、tracked 文档或项目挂载点；
- 用真实项目验证项目 workflow evidence、Skill、Governance 和 Knowledge/RAG 机制；
- Knowledge/RAG 已具备 raw -> candidate -> reviewed -> cleanup -> validation -> query 的稳定命令面和一键门禁；
- Memory 已具备 candidate -> review -> reviewed/delete 的受控生命周期命令、reviewed Skill、store gate、self-test 和 governance self-check 集成；
- H9-4 Knowledge/RAG 和 Memory 收口已由用户确认，当前进入 H9-5 汇总和 H10 门禁判定。

## 3. 系统要求

最低要求：

- Git；
- Windows PowerShell 5.1 或 PowerShell 7；
- 能访问 GitHub 仓库 `KKT-OPT/Free-Harness-World`。

按任务可选：

- Java 和 Maven：用于 Java/Maven 项目验证；
- Python：用于 RAG candidate 或文档处理工具；
- Codex、Hermes 或其他 Agent Runtime：用于执行受管任务。

## 4. 安装

选择一个本机目录作为 `<HARNESS_ROOT>`，然后 clone `agent-git`：

```powershell
git clone --branch agent-git --single-branch git@github.com:KKT-OPT/Free-Harness-World.git <HARNESS_ROOT>
cd <HARNESS_ROOT>
```

检查工作区状态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode status
```

安装本机 workspace 状态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode install
```

`install` 会创建：

- `user/registry/projects.local.json`；
- `user/registry/knowledge.local.json`；
- `var/`、`var/logs/`、`var/tmp/`、`var/rag/`。

安装不会：

- 覆盖已有本地 registry；
- 写入凭据；
- 导入真实项目；
- 修改 `main` 分支；
- 把 `var/`、`projects/*/`、用户本地配置或私有知识加入 Git。

## 5. 验证安装

运行 bootstrap status：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode status -RunSelfCheck
```

运行治理自检：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-harness-governance.ps1
```

运行 registry self-test：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-project-registry.ps1 -SelfTest
```

通过标准：

- bootstrap status 为 `passed`；
- governance self-check 为 `passed`；
- registry self-test 为 `passed`；
- `git status --short --ignored` 中本地 registry 和运行态目录只显示为 ignored 或不显示。

## 6. 卸载

卸载本机 workspace 安装态：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode uninstall
```

`uninstall` 会删除：

- install 生成的 `user/registry/projects.local.json`；
- install 生成的 `user/registry/knowledge.local.json`；
- 空的 `var/` 运行态目录。

`uninstall` 不会删除：

- Git clone 本身；
- tracked 文档；
- `AGENTS.md`、`INDEX.md`、`README.md`；
- `harness/`；
- `projects/README.md`；
- 真实项目目录。

## 7. 快速开始

1. 安装 Harness：

```powershell
git clone --branch agent-git --single-branch git@github.com:KKT-OPT/Free-Harness-World.git <HARNESS_ROOT>
cd <HARNESS_ROOT>
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\bootstrap-harness-workspace.ps1 -Mode install
```

2. 阅读入口：

```text
AGENTS.md
INDEX.md
harness/HarnessIndex.md
harness/architecture/PLANS.md
```

3. 挂载项目实例：

```text
projects/<project-id>/
```

真实项目应作为独立 Git 仓库或本地工作区存在，不能把项目 Git 历史混入 Harness 根仓库。

4. 初始化项目文档：

```text
harness/templates/project-template/
-> projects/<project-id>/
```

项目事实入口：

```text
projects/<project-id>/AGENTS.md
projects/<project-id>/docs/project/ProjectIndex.md
```

5. 修改本地项目 registry：

```text
user/registry/projects.local.json
```

6. 执行自检：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-harness-governance.ps1
```

## 8. Knowledge / RAG 快速使用

Harness 的知识库目标是：用户提供原始材料并审核候选结果，Agent 负责把原始材料转换为结构化候选知识、维护双向链接、执行验证和清理。真实知识默认存放在 `user/knowledge/` 或用户指定的 private knowledge repo，不进入通用 Harness Git。

### 8.1 知识库目录

| 路径 | 用途 | 说明 |
|---|---|---|
| `user/knowledge/raw/<domain>/` | 原始材料 | 用户提供 PDF、Markdown 或其他来源材料；按领域分组。 |
| `user/knowledge/raw/<domain>/normalized/` | 原始材料转换后的 Markdown | 长期可读派生版本，供人类和 Agent 理解原材料结构；不是 reviewed 结论。 |
| `user/knowledge/candidate/` | 候选知识 | raw-to-candidate 或 gap plan 生成的候选材料，默认不进入 Obsidian 正式图谱。 |
| `user/knowledge/reviewed/<domain>/` | 已审核知识 | 用户审核通过后的 authoritative reviewed Knowledge。 |
| `user/knowledge/Home.md` | Obsidian 单入口 | 人类阅读和审核入口。 |
| `var/rag/` | 运行态 | extracted artifacts、graph、query report、cache 和验证报告，可清理、可重建。 |

### 8.2 Agent 应读取的 Skill

当任务是“使用、查询、治理或验证已审核知识库”时，让 Agent 读取：

```text
harness/skills/reviewed/rag-knowledge-use/SKILL.md
```

当任务是“从 raw source 生成 candidate，并准备晋升为 reviewed Knowledge”时，让 Agent 同时读取：

```text
harness/skills/rag-structured-ingestion/SKILL.md
harness/skills/reviewed/rag-knowledge-use/SKILL.md
```

详细规则不要复制到 README；按需继续阅读：

```text
harness/rag/RAGIndex.md
harness/governance/KnowledgePromotionPolicy.md
harness/rag/policies/
harness/tools/docs/script-index/ScriptIndex.md
user/knowledge/README.md
```

### 8.3 从 raw 快速生成 reviewed Knowledge

完整验证链路可使用 `pipeline-smoke`，它会按稳定命令完成 raw -> candidate -> approved promotion -> reviewed vault -> query 的端到端检查。写入 reviewed Knowledge 需要 reviewer 和 approval note；没有用户批准时，只能生成 candidate、review package 或 promotion plan。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 `
  -Root . `
  -Command pipeline-smoke `
  -InputPath .\user\knowledge\raw\<domain>\<source-file> `
  -Domain <domain> `
  -Reviewer <reviewer> `
  -ApprovalNote "<approval-note>" `
  -Question "<acceptance-query>" `
  -CopyRaw
```

如果只想生成候选材料，不晋升 reviewed Knowledge，使用 candidate workflow：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-candidate.ps1 `
  -Root . `
  -Command ingest `
  -InputPath .\user\knowledge\raw\<domain>\<source-file> `
  -RawDomain <domain> `
  -CopyRaw
```

### 8.4 查询、验证和清理

常用 reviewed Knowledge 命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root . -Command query-reviewed -Question "<question>"
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root . -Command validate-knowledge-vault
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root . -Command validate-llm-wiki-mechanisms
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 -Root . -Command candidate-cleanup-plan
```

如 dry-run 显示晋升后的 candidate full corpus 需要移出 Obsidian 图谱，在用户批准后执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-rag-knowledge.ps1 `
  -Root . `
  -Command candidate-cleanup-apply `
  -Reviewer <reviewer> `
  -ApprovalNote "<approval-note>"
```

## 9. Memory 快速使用

Harness Memory 保存通用化、非私有、未来可复用的短经验。它不是项目事实源、不是 Knowledge、不是 Skill，也不保存 raw logs、settings、auth、本机路径、私有业务数据或用户私有偏好。

### 9.1 Agent 应读取的 Skill

当任务涉及记忆候选、Memory store 验证、审核包、用户 approve/reject/delete/defer/revise 决策或 Memory 生命周期收口时，让 Agent 读取：

```text
harness/skills/reviewed/memory-governance-use/SKILL.md
```

详细规则继续阅读：

```text
harness/memory/MemoryIndex.md
harness/memory/MemoryPolicy.md
harness/governance/MemoryGovernance.md
harness/tools/docs/script-index/ScriptIndex.md
```

### 9.2 常用 Memory 命令

Memory 命令默认只读或 dry-run。写入 candidate、reviewed、archive、删除 candidate 或修订 candidate 时，必须有用户明确决策，并提供 reviewer、approval note、reason 和 `-Apply`。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-memory.ps1 -Root . -Command memory-flow-status
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-memory.ps1 -Root . -Command validate-memory-store
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-memory.ps1 -Root . -Command validate-memory-store -SelfTest
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-memory.ps1 -Root . -Command candidate-review-package -CandidateId <memory-id>
```

Memory 生命周期写入统一通过 `apply-review-decision` 或对应受控命令完成，不能手工移动文件替代。

## 10. 常用命令

| 命令 | 用途 |
|---|---|
| `bootstrap-harness-workspace.ps1 -Mode status` | 检查 Harness Workspace 必需入口和 Git ignore 边界。 |
| `bootstrap-harness-workspace.ps1 -Mode install` | 安装本机 workspace 状态。 |
| `bootstrap-harness-workspace.ps1 -Mode uninstall` | 卸载本机 workspace 安装态。 |
| `test-harness-governance.ps1` | 运行 Harness Root 治理自检。 |
| `test-project-registry.ps1 -SelfTest` | 校验项目 registry 验证器行为。 |
| `test-project-registry.ps1` | 校验本机项目 registry。 |
| `show-java-maven-config.ps1` | 输出 Java/Maven profile 的安全摘要。 |
| `invoke-maven-project.ps1` | 运行 Maven goals 并输出状态摘要和脱敏日志路径。 |
| `invoke-java-main.ps1` | 编译并运行 Java main class。 |
| `invoke-rag-candidate.ps1` | 运行 RAG candidate 流程，不直接晋升 reviewed knowledge。 |
| `invoke-rag-knowledge.ps1 -Command query-reviewed` | 查询已审核 reviewed Knowledge，供 Agent 读取命中页后回答。 |
| `invoke-rag-knowledge.ps1 -Command validate-knowledge-vault` | 一键验证本地知识库 registry、Home、domain schema、source trace、graph、duplicate、archive 和 Git 边界。 |
| `invoke-rag-knowledge.ps1 -Command validate-llm-wiki-mechanisms` | 验证已吸收的 LLM Wiki 机制，包括 schema context、source gate、granularity、tag、dedup、repair order 和 graph retrieval。 |
| `invoke-rag-knowledge.ps1 -Command candidate-cleanup-plan` | dry-run 盘点晋升后 candidate full corpus 和轻量审计记录。 |
| `invoke-rag-knowledge.ps1 -Command pipeline-smoke` | 验证 raw 到 reviewed Knowledge 的端到端链路；需要 reviewer 和 approval note。 |
| `invoke-memory.ps1 -Command memory-flow-status` | 对照架构 Memory Update Flow 输出节点覆盖、稳定命令和停止规则。 |
| `invoke-memory.ps1 -Command validate-memory-store` | 验证 Memory candidate、reviewed、archive、frontmatter、review、source evidence、重复和敏感边界。 |
| `invoke-memory.ps1 -Command validate-memory-store -SelfTest` | 用负向 fixture 验证 Memory store gate 能检出典型坏样本。 |
| `invoke-memory.ps1 -Command candidate-review-package` | 为候选 Memory 生成用户审核包。 |
| `clean-sandbox.ps1` | 清理运行态文件；默认 dry-run，`-Apply` 需要明确审批。 |
| `publish-harness-agent-branch.ps1` | 在 `agent-git` 分支执行受控提交和推送。 |

示例：治理自检

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-harness-governance.ps1
```

示例：Java/Maven profile 安全摘要

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\show-java-maven-config.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -CheckVersion
```

示例：Maven 验证

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\invoke-maven-project.ps1 `
  -Agent codex `
  -Profile <profile-id> `
  -ProjectRoot .\projects\<project-id> `
  -Goals test
```

## 11. 目录结构

| 路径 | 说明 | Git 边界 |
|---|---|---|
| `AGENTS.md` | Agent 入口契约、硬约束和读取顺序。 | tracked |
| `INDEX.md` | 全局导航入口。 | tracked |
| `harness/architecture/` | 架构权威、计划和变更记录。 | tracked |
| `harness/bootstrap/` | 安装、卸载、初始化和 bootstrap 验收入口。 | tracked |
| `harness/governance/` | 治理、晋升、清理、文档和索引维护策略。 | tracked |
| `harness/tools/` | 稳定工具、工具文档、manifest、候选、历史、runtime 和 external 边界。 | tracked with local-only exclusions |
| `harness/templates/project-template/` | 项目模板唯一目标路径。 | tracked |
| `harness/verification/` | readiness、validation、regression 和验证用例。 | tracked |
| `harness/observability/` | trace、failure attribution 和观测结构。 | tracked |
| `harness/rag/` | RAG 机制层；真实知识不放这里。 | tracked |
| `harness/memory/` | Memory policy、candidate、reviewed 和 archive 边界。 | tracked |
| `harness/skills/` | Skill policy、candidate、reviewed、archive 和 usage sidecar。 | tracked |
| `projects/` | 项目实例挂载点。 | only `projects/README.md` tracked |
| `user/` | 本地 registry、settings、auth、identity、knowledge 边界；除 README/example 外默认不进入通用 Git。 | local/private files ignored |
| `var/` | 运行态日志、缓存、临时文件和 RAG index。 | ignored |

## 12. 数据和安全边界

不得提交或写入 tracked docs：

- token、password、secret、auth 文件；
- Maven settings 正文；
- 未脱敏日志；
- 本机私有路径；
- 私有仓库 URL；
- 真实项目源码；
- `var/**` 运行态；
- `user/settings/**`、`user/auth/**`、`user/identity/**`；
- `user/registry/*.local.json`；
- `user/knowledge/**` 中的真实或候选私有知识。

RAG Index 是可重建检索产物，不是事实源。Workflow Evidence 只产生候选事实，不能直接晋升为 Knowledge、Memory、Skill 或 Project Fact。

## 13. 架构文档

长期架构权威：

```text
harness/architecture/HarnessEngineering.md
```

阶段计划和验收状态：

```text
harness/architecture/PLANS.md
```

General Harness 索引：

```text
harness/HarnessIndex.md
```

## 14. 贡献

当前贡献目标分支：

```text
agent-git
```

贡献要求：

1. 不直接修改或推送 `main`。
2. 不提交真实项目源码、私有设置、auth、token、未脱敏日志或运行态产物。
3. 重要 Markdown 文档必须保留 YAML frontmatter。
4. 正式 Harness 文档以中文作为主题说明语言，允许保留专业词、命令、路径和代码标识的英文写法。
5. 新增稳定工具必须补齐工具契约，并更新 `harness/tools/docs/script-index/ScriptIndex.md`。
6. 涉及 Knowledge、Memory、Skill、Project Fact 或 Governance 晋升的变更必须 candidate-first、review-first，并保留用户审批边界。

提交前运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-harness-governance.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\test-project-registry.ps1 -SelfTest
git diff --check
```

受控提交和推送：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\harness\tools\scripts\stable\publish-harness-agent-branch.ps1 `
  -Mode commit-and-push `
  -CommitMessage "<commit-message>"
```

## 15. License

本项目使用 MIT License。详见 [LICENSE](LICENSE)。
