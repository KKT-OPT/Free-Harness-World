---
documentName: IsolationDecisionMatrix.md
version: v1.0.0-pre-h8-frontmatter
updatedAt: 2026-06-23 08:18:39.000 +08:00
status: active
purpose: '定义本地沙盒、低权限用户、容器、虚拟机和远程 worker 的隔离选择规则。'
scope:
  - runtime-isolation
  - sandbox-boundary
  - worker-selection
prerequisites:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/governance/GovernanceIndex.md
  - harness/governance/security/SandboxRuntimeSecurityModel.md
outputTo:
  - harness/governance/security/IsolationDecisionMatrix.md
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
# Isolation Decision Matrix（隔离决策矩阵）

## 1. 文档定位

本文定义 Harness 后续选择本地沙盒、低权限账号、Docker、虚拟机或远程 worker 的决策矩阵。

Isolation，中文解释是隔离，用于限制 agent 命令对宿主机、凭据、网络和真实项目的影响范围。

本文不实施任何隔离方案。

## 2. 当前判断

当前 `<HARNESS_ROOT>` 是本地沙盒。

它适合：
- 框架设计；
- 文档落地；
- demo 项目；
- 用户在环的本地验证；
- 可重复、低风险的 Java/Maven 验证。

它不等于硬隔离。

当前本地沙盒仍然共享当前 Windows 用户的主机权限，因此不能作为生产网关无人值守执行的最终安全边界。

## 3. 决策矩阵

| 方案 | 中文解释 | 适用场景 | 优点 | 风险/成本 | 当前建议 |
|---|---|---|---|---|---|
| Local Host Sandbox | 当前本地主机沙盒 | 设计、demo、用户在环开发 | 成本最低，路径兼容好 | 不是硬隔离，共享用户权限 | 当前继续使用 |
| Dedicated Low-Privilege User | 专用低权限用户 | 本地真实项目验证、减少误操作范围 | Windows 兼容好，隔离强于当前用户 | 配置成本，工具链重复 | P8 后可评估 |
| Docker/Podman | 容器隔离 | demo、CI-like 验证、生产 gateway worker 候选 | 可重复，环境干净，适合自动化 | Windows 路径和 Maven 缓存挂载复杂 | P9/P10 后 PoC |
| Virtual Machine | 虚拟机 | 高风险真实项目、强隔离、生产前验证 | 隔离强，快照可回滚 | 启动慢，资源成本高 | 高风险场景优先 |
| Remote Worker | 远程工作机 | 与主机隔离的专用执行节点 | 可控网络和权限 | 运维和凭据治理复杂 | 生产化候选 |
| Managed Isolated Worker | 托管隔离 worker，例如 Modal、Daytona | 云端或托管执行 | 隔离和弹性较好 | 成本、数据出境、私有代码合规 | 需单独安全评估 |

## 4. 风险到隔离级别映射

| 任务风险 | 最低建议隔离 |
|---|---|
| 只读文档设计 | Local Host Sandbox |
| demo 项目代码修改 | Local Host Sandbox 或 Docker |
| 真实业务项目本地修改，用户在环 | Local Host Sandbox 加审批，或 Dedicated Low-Privilege User |
| 真实业务项目无人值守修改 | Docker/VM/Remote Worker |
| 需要真实凭据访问私有仓库 | Dedicated Low-Privilege User 或 VM，凭据 allowlist |
| 发布、部署、远端写入 | VM/Remote Worker，加人工审批 |
| 不可信外部代码执行 | Docker/VM，默认无凭据、限制网络 |
| 强安全或合规场景 | VM 或专用 Remote Worker |

## 5. Docker 升级路径

未来 Docker PoC 应按以下顺序推进：

1. 选择 demo 项目，不使用真实业务源码。
2. 使用无凭据 Maven settings 或公开依赖源。
3. 只挂载必要项目目录和只读 Harness 入口文档。
4. Maven local repo 使用容器内缓存或显式挂载的 runtime cache。
5. 默认无 auth 文件、无全量环境变量。
6. 输出 status JSON 和 log path 到受控 evidence 目录。
7. 验证 Windows 路径、文件编码、Maven 缓存和性能。

## 6. 虚拟机升级路径

未来 VM PoC 应按以下顺序推进：

1. 创建可回滚快照。
2. 使用低权限用户。
3. 只同步受管项目工作副本。
4. 凭据按 allowlist 注入。
5. 网络出口限制到必要仓库。
6. 执行后输出脱敏报告。
7. 快照回滚或清理 runtime state。

## 7. 默认禁止

以下场景不能只依赖当前本地沙盒：
- 无人值守处理真实业务项目；
- 自动发布或部署；
- 执行不可信外部代码；
- 关闭危险命令审批；
- 默认转发宿主机环境变量；
- 使用真实凭据但没有 allowlist；
- 允许消息网关用户任意触发命令。

## 8. 当前决策

P8 当前决策：

```text
继续使用 Local Host Sandbox 进行文档设计和后续 Java demo。
生产 gateway 或高风险真实项目任务必须先完成 Docker/VM/Remote Worker PoC 和安全评估。
```
