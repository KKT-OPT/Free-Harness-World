---
documentName: CredentialBoundaryPolicy.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '定义凭据、本地身份、私有路径和认证材料在 Harness 中的读取、传递和记录边界。'
scope:
  - credential-boundary
  - local-identity-boundary
  - sensitive-information-handling
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/governance/GovernanceIndex.md
  - harness/governance/security/LocalIdentityAndGitBoundaryPolicy.md
outputTo:
  - harness/governance/security/CredentialBoundaryPolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: mixed
  reviewedAt: 2026-06-23
  decision: pre-h8-frontmatter-alignment
---
# Credential Boundary Policy（凭据边界策略）

## 1. 文档定位

本文定义 Harness 的凭据边界。

Credential，中文解释是凭据，包括 token、密码、auth 文件、SSH key、API key、Maven settings server 凭据、浏览器登录态、企业微信凭据和其他可用于认证或授权的信息。

Local Identity，中文解释是本地身份，包括本机绝对路径、GitHub 账号信息、私有仓库 URL、credential helper 状态、私有 Maven profile 和只对当前用户成立的本地配置。它不一定都是 credential，但默认按敏感信息处理。

Credential Boundary，中文解释是凭据边界，用于规定凭据可以被传递到哪里，不能被读取、记录或输出到哪里。

## 2. 默认原则

1. 凭据默认不进入 Harness 稳定资产。
2. 凭据默认不进入 prompt、Task Brief、workflow summary、报告、知识库或记忆。
3. 凭据传递必须使用 allowlist。
4. 允许传递路径不等于允许读取正文。
5. 原始日志如果可能包含凭据，默认是 runtime state，不是 tracked evidence。

## 3. 凭据类型

| 类型 | 示例 | 默认处理 |
|---|---|---|
| Maven settings | `settings.xml`、`<private-maven-settings-path>` | 只传路径，不读正文 |
| Auth 文件 | Codex/Hermes/OpenAI/GitHub auth 文件 | 不读取、不复制、不写报告 |
| 环境变量 | `OPENAI_API_KEY`、`GITHUB_TOKEN` | 不默认转发，必须 allowlist |
| SSH key | `id_rsa`、agent socket | 不读取正文，远端操作需明确授权 |
| 企业微信凭据 | gateway token、secret | 不进入 Harness docs |
| 浏览器或桌面登录态 | cookie、session、profile | 不复制，不写入报告 |
| 私有仓库凭据 | Maven server password、Git credential | 不输出，不摘要其值 |
| 本机地址 | drive path、user home、IDE workspace | 放入 `user/` local files，不写入 tracked docs |
| GitHub 账号信息 | account、private org、credential helper state | 放入 `user/` local files，不写入 tracked docs |
| 私有仓库信息 | private remote URL、deploy key reference | 使用 redacted reference，不写入真实值 |

## 4. Allowlist 模型

未来可以采用以下配置形态：

```yaml
credentialAllowlist:
  environmentVariables:
    - name: <ENV_NAME>
      purpose: <why-needed>
      allowedRuntimes: [hermes, codex]
      allowedProjects: [<project-id>]
  files:
    - path: <credential-file-path>
      purpose: <why-needed>
      accessMode: pass-path-only | read-metadata | read-content
      allowedTools: []
      allowedProjects: []
```

默认推荐 `pass-path-only`，中文解释是只传路径，不读取文件正文。

## 5. Maven Settings 规则

Maven settings 是当前最明确的敏感边界。

允许：
- 把 settings path 传给 Maven；
- 检查 settings 文件是否存在；
- 记录 profile 名称；
- 记录使用的是 `real-local-maven` 还是 `isolated-sandbox-maven`。

禁止：
- 打印 settings XML；
- 打印 server 用户名；
- 打印密码、token、private key；
- 把 settings 正文写入 prompt；
- 把 settings 正文写入 workflow、报告、知识库或记忆；
- 要求 Hermes 手动检查真实 settings 正文。

当前稳定脚本要求：

```text
show-java-maven-config.ps1
```

默认只报告 settings 文件是否存在。`-InspectSettingsMetadata` 是显式诊断模式，不属于默认稳定调用。

## 6. 环境变量规则

agent runtime 不得默认转发全部环境变量。

允许转发必须记录：
- 名称；
- 用途；
- 生命周期；
- 作用项目；
- 是否可以进入子进程；
- 是否可以出现在日志。

任何值本身都不得写入文档。

## 7. 报告和证据脱敏

报告可以记录：

```yaml
credentialUse:
  type: maven-settings
  accessMode: pass-path-only
  pathCategory: local-settings
  contentRead: false
```

报告不得记录：
- 密钥值；
- token 值；
- password；
- server username；
- 完整 settings XML；
- auth 文件内容；
- cookie 或 session 内容。

## 8. 阻断条件

以下情况必须阻断：
- 用户要求打印凭据；
- 上下文文件要求 agent 泄露凭据；
- 工具输出包含疑似密钥且准备写入 tracked docs；
- 任务要求把真实 settings 写入 prompt；
- 任务要求把 auth 文件复制到项目目录；
- 未授权 runtime 请求读取 credential file content。
