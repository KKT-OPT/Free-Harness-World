---
documentName: harness/memory/candidate/java-maven-real-project-validation.md
version: v0.1.0-candidate
updatedAt: 2026-06-23 18:54:52.291 +08:00
status: review
purpose: 记录真实 Java/Maven 项目命令行自测链路的候选通用记忆，等待 Memory review。
scope:
  - memory-candidate
  - java-maven-validation
  - agent-operation
prerequisites:
  - harness/memory/MemoryPolicy.md
relatedDocuments:
  - harness/tools/docs/command-surfaces/JavaMavenCommandSurface.md
  - projects/lfms-decision/docs/project/workflow/20260623-h9-0-s7-commandline-validation.md
outputTo:
  - harness/memory/candidate/java-maven-real-project-validation.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/memory/MemoryPolicy.md
review:
  reviewedBy:
  reviewedAt:
  decision: pending
---
# Java/Maven 真实项目验证候选记忆

## 元数据

```yaml
memoryId: java-maven-real-project-validation
assetState: candidate
scope: agent-operation
projectId: null
sourceEvidence: projects/lfms-decision/docs/project/workflow/20260623-h9-0-s7-commandline-validation.md
confidence: medium
reviewedBy:
reviewedAt:
stalenessRule: review-after-H9-real-project-validation
```

## Memory Statement

真实 Java/Maven 项目自测应先从项目验证契约发现 profile、module、main class 和命令面，再调用稳定 Harness 工具；不要在任务中手工查找 Maven 安装、读取 settings XML 或拼接复杂 classpath。

## Source And Evidence

| Source | Evidence Summary | Notes |
|---|---|---|
| `projects/lfms-decision/docs/project/workflow/20260623-h9-0-s7-commandline-validation.md` | 稳定工具可发现本机 Java/Maven profile，并自动编译、构建 classpath、运行 E2E main program。 | 证据来自单个真实项目，仍需 H9 后续任务复核。 |

## Applicability

适用于真实 Java/Maven 项目的 agent 自测、E2E main program 运行、命令行验证和本机 profile 检查。

## Non-Applicability

不适用于保存项目业务事实、场景固定输出、用户私有 Maven settings、本机真实路径、私有仓库 URL 或原始日志。项目文档或用户当前指令与本候选记忆冲突时，以项目文档和用户当前指令为准。

## Review Notes

| Check | Result |
|---|---|
| Stable beyond one task | unknown |
| Future reuse value | yes |
| Sensitive content excluded | yes |
| Conflict check completed | partial |
| Approval recorded | no |

## Promotion Decision

```yaml
decision: defer
targetState: candidate
reviewer:
decisionDate:
reason: 等待 H9 后续真实任务验证后再决定是否晋升 reviewed memory。
```
