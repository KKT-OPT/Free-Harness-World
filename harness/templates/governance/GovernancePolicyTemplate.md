---
documentName: harness/templates/governance/GovernancePolicyTemplate.md
version: v1.0.0-pre-h8-governance-template
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 提供 Governance Policy 文档模板。
scope:
  - governance-template
  - policy-template
prerequisites:
  - AGENTS.md
  - harness/governance/GovernanceIndex.md
relatedDocuments:
  - harness/governance/DocumentGovernance.md
outputTo:
  - harness/templates/governance/GovernancePolicyTemplate.md
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
# Governance Policy Template（治理策略模板）

## 元数据

```yaml
policyId: <stable-id>
assetState: draft | active | review | stale | deprecated | archived
owner: <human-or-team>
scope: <global | domain | project | harness-root>
sourceEvidence: <workflow-or-report-path>
reviewAfter: <date-or-condition>
relatedDocuments: []
```

## 目的

Describe why this policy exists.

## 范围

Describe where the policy applies and where it does not apply.

## 规则

1. `<rule>`
2. `<rule>`
3. `<rule>`

## 验收标准

- `<criterion>`
- `<criterion>`

## 敏感边界

State what must not be recorded in tracked docs, prompts, workflow summaries, reports or candidate assets.

## 治理

| Field | Value |
|---|---|
| owner | `<owner>` |
| reviewAfter | `<date-or-condition>` |
| promotionRequirement | `<approval-or-review-rule>` |
| archiveRule | `<archive-rule>` |

## 相关文档

- `<path>`
