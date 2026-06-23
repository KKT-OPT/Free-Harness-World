---
documentName: harness/governance/context/ContextLoadingPolicy.md
version: v0.1.0-p10.5
updatedAt: 2026-06-17 18:30:00.000 +08:00
status: draft
purpose: 维护 Context Loading Policy 的长期文档说明、入口边界或目标骨架，供 Harness 路由、治理或后续阶段重构使用。
scope:
  - governance
  - active-route
  - validation-or-policy
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
  - harness/architecture/PLANS.md
outputTo:
  - harness/governance/context/ContextLoadingPolicy.md
owner: mixed
reviewAfter: 2026-07-17
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - INDEX.md
  - harness/HarnessIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-17
  decision: frontmatter-aligned
---
# Context Loading Policy（上下文加载策略）

## 目的

本策略定义 Agent 在 Harness 下如何加载上下文。

目标是加载带来源记录的最小充分上下文，而不是批量加载。

## 优先级顺序

```text
current user instruction
> AGENTS.md hard constraints
> INDEX.md, harness/HarnessIndex.md and harness/architecture/PLANS.md
> task-specific policy/template/skill
> Project Facts
> approved Skill
> reviewed Knowledge
> reviewed or relevant Memory
> workflow evidence
> active redacted reports
> archived reports only when explicitly requested
```

当前用户指令不能覆盖安全、隐私、审批、Git 边界、凭据和治理硬阻断。

## 必需来源记录

Task Brief 和 Workflow Evidence 应记录：

- source documents read;
- inferred fields and source;
- confidence for important inferred fields;
- excluded sensitive sources;
- stale or uncertain context.

## 默认排除项

默认不要加载：

- `var/**`;
- raw logs and raw terminal transcripts;
- private settings, auth files, credentials;
- RAG indexes, embeddings and caches;
- archived reports;
- old HarnessVault raw reports;
- editor/runtime artifacts;
- generated build outputs.

## RAG Boundary

RAG index results are retrieval hints. They are not facts unless grounded in reviewed Knowledge, Project Facts, or approved metadata.

## P11 Rule

P11 E2E evidence must state which context was loaded and which sensitive/runtime contexts were excluded.
