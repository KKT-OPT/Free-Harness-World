---
documentName: GatewayAuthorizationPolicy.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '定义 Hermes WeCom、CLI gateway 和未来消息入口在任务进入 Agent Runtime 前的授权检查规则。'
scope:
  - gateway-authorization
  - user-allowlist
  - project-allowlist
  - risk-gating
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/governance/GovernanceIndex.md
  - adapter/gateways/wecom/HermesWeComTaskFlow.md
outputTo:
  - harness/governance/security/GatewayAuthorizationPolicy.md
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
# Gateway Authorization Policy（网关授权策略）

## 1. 文档定位

本文定义 Hermes WeCom、Hermes CLI gateway 或未来消息入口的用户授权策略。

Gateway Authorization，中文解释是网关授权，指消息入口在把任务交给 agent runtime 前，必须确认用户、项目、任务类型和风险边界是否被允许。

本文不实现 Hermes gateway，不配置企业微信，不创建真实 allowlist 文件。

## 2. 核心原则

1. 消息来源不等于授权。
2. 用户必须在 allowlist 中。
3. 项目必须在 allowlist 中。
4. 高风险任务必须能回到用户澄清或人工审批。
5. 网关不能绕过 Harness Root 的 `AGENTS.md` 和安全策略。
6. 网关不得把群聊中的任意消息自动视为执行命令。

## 3. 建议授权模型

未来 gateway 配置应至少支持：

```yaml
gatewayAuthorization:
  users:
    - userId: <stable-user-id>
      displayName: <name>
      channels: [wecom, cli]
      roles: [requester, reviewer]
  projects:
    - projectId: <project-id>
      allowedUsers: []
      allowedTaskTypes: [read, validate, edit, report]
      defaultRiskLimit: medium
  channels:
    - channel: wecom
      requirePairing: true
      requireExplicitProject: true
```

中文解释：
- requirePairing：需要用户和 gateway 完成绑定或配对。
- defaultRiskLimit：默认风险上限，超过时必须人工确认。

## 4. 任务入口规则

Gateway 收到任务后应按顺序检查：

1. 用户身份是否可识别；
2. 用户是否在 allowlist；
3. 项目是否明确或可高置信推断；
4. 用户是否有权访问该 projectId；
5. 任务类型是否在允许范围；
6. Task Brief 是否标记高风险；
7. 高风险任务是否已有明确授权；
8. 是否触碰凭据、外部路径、git push、发布或部署。

如果不能通过检查，应返回澄清或拒绝执行，而不是继续运行。

## 5. 风险分级

| 场景 | 默认处理 |
|---|---|
| 只读查询 Harness 文档 | 可自动执行 |
| 查询项目事实或源码 | 需要项目授权 |
| 运行稳定验证命令 | 需要项目授权和稳定工具表面 |
| 修改源码或测试 | 高风险，必须记录 Task Brief 和执行计划 |
| 访问凭据或敏感路径 | 默认阻断，除非显式授权且符合凭据策略 |
| 发布、部署、推送、合并 | 默认需要人工审批 |
| 请求关闭审批 | 默认阻断，除非隔离环境明确允许 |

## 6. 证据记录

Gateway 任务的 workflow evidence 应记录：

```yaml
gateway:
  channel: wecom | cli | other
  userId: <redacted-or-stable-id>
  authorizationResult: allowed | denied | clarification-required
  projectAllowed: true | false
  riskLimit: low | medium | high
```

不得记录：
- 用户私密 token；
- 企业微信认证凭据；
- 原始消息中的敏感内容全文；
- auth 文件正文。

## 7. 阻断条件

以下情况必须阻断或先澄清：
- 用户身份不可识别；
- 用户不在 allowlist；
- projectId 无法确定且任务需要项目上下文；
- 用户没有该项目权限；
- 请求访问敏感路径；
- 请求把凭据发给 agent；
- 请求绕过审批；
- 请求对真实业务项目执行高风险操作但没有验收标准或回滚边界。

## 8. 与 P10 的关系

P8 只定义网关授权策略。

P10 Runtime Adapter 阶段再定义 Hermes WeCom、Hermes CLI 和 Codex 如何实际消费这些策略。
