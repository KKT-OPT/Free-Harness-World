---
documentName: harness/governance/DocumentGovernance.md
version: v1.0.0-pre-h8-document-governance
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义受 Git 管控重要 Markdown 文档的 frontmatter、语言、状态、reviewAfter 和归档规则。
scope:
  - governance
  - document-governance
  - frontmatter
  - document-language
prerequisites:
  - AGENTS.md
relatedDocuments:
  - AGENTS.md
  - harness/architecture/HarnessEngineering.md
  - harness/governance/IndexMaintenancePolicy.md
outputTo:
  - harness/governance/DocumentGovernance.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-document-governance-aligned
---
# Document Governance

受 Git 管控的重要 Harness Markdown 文档必须包含基础 YAML frontmatter，并以中文作为文档主题说明语言。专业词、命令、路径、代码标识和通用技术名词可以保留英文。

## 1. 状态规则

`frontmatter.status` 只表示文档状态，必须使用：

```text
draft | review | active | stale | deprecated | archived | superseded
```

候选资产状态不得写入 `frontmatter.status`，应写入正文或 review 字段。

## 2. 归档规则

archived、deprecated、stale 文档不作为默认上下文。被替代文档应填写 `supersededBy`，并在安全时删除兼容 stub 或移动到 archive。

## 3. 敏感边界

补齐 frontmatter 或维护文档时，不得引入 settings、auth、token、password、本机绝对路径、私有仓库 URL 或未脱敏 raw logs。
