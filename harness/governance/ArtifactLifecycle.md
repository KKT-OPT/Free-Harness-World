---
documentName: harness/governance/ArtifactLifecycle.md
version: v1.0.0-pre-h8-governance-mechanism
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Harness 资产从 workflow evidence 到 candidate、review、promotion、archive 和 closeout 的通用生命周期。
scope:
  - governance
  - artifact-lifecycle
  - candidate-first
  - review-first
  - human-approval
prerequisites:
  - AGENTS.md
  - harness/governance/GovernanceIndex.md
relatedDocuments:
  - harness/governance/KnowledgePromotionPolicy.md
  - harness/governance/MemoryGovernance.md
  - harness/governance/SkillGovernance.md
  - harness/templates/governance/GovernanceCloseoutTemplate.md
outputTo:
  - harness/governance/ArtifactLifecycle.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/governance/GovernanceIndex.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-governance-mechanism-aligned
---
# Artifact Lifecycle

本文定义 Harness 资产生命周期。Workflow Evidence、Report、RAG chunks、Trace Summary 和运行态输出只产生候选，不自动成为长期事实或长期能力。

## 1. 通用生命周期

```mermaid
flowchart TD
    A["Workflow Evidence / Report / User Feedback"] --> B["Detect Promotion Candidate"]
    B --> C{"Candidate Type?"}
    C --> D["Project Fact"]
    C --> E["Knowledge"]
    C --> F["Memory"]
    C --> G["Skill"]
    C --> H["Tool / Template / Governance / Architecture"]
    D --> I["Route to Target Asset"]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J["Sensitivity Check"]
    J --> K["Conflict Check"]
    K --> L["Governance Review"]
    L --> M{"Human Approval / Explicit Approval?"}
    M -->|approved| N["Update Target Asset"]
    M -->|rejected| O["Archive / Reject Candidate"]
    M -->|needs repair| P["Revise Candidate"]
    P --> L
    N --> Q["Update Index / ReviewAfter"]
    Q --> R["Closeout"]
    O --> R
```

## 2. Candidate 类型

| 类型 | 默认目标 |
|---|---|
| `ProjectFact` | `projects/<project-id>/docs/project/` |
| `Knowledge` | `user/knowledge/candidate/`，review 后进入 `user/knowledge/reviewed/` 或外部 private repo。 |
| `Memory` | `harness/memory/candidate/`，review 后进入 `harness/memory/reviewed/`。 |
| `Skill` | `harness/skills/candidate/`，review 后进入 `harness/skills/reviewed/`。 |
| `Tool` | `harness/tools/` 中对应 tool asset。 |
| `Template` | `harness/templates/` 中对应模板。 |
| `Governance` | `harness/governance/` 中对应 policy。 |
| `Architecture` | `harness/architecture/HarnessEngineering.md`，必须用户明确批准。 |
| `Report` | `harness/reports/` 或项目 reports。 |
| `RAG` | 机制进入 `harness/rag/`；运行态进入 `var/rag/`；知识正文进入 `user/knowledge/`。 |

## 3. Closeout 记录

任务收口使用：

```text
harness/templates/governance/GovernanceCloseoutTemplate.md
```

每个 candidate 必须记录 source evidence、target asset、disposition、approval requirement、sensitive risk 和 next action。

## 4. 禁止自动晋升

不得直接晋升 workflow evidence、report conclusion、RAG chunks、runtime logs、status JSON 正文、old raw vault files、settings、auth、credentials 或 private repository paths。
