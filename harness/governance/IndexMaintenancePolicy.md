---
documentName: harness/governance/IndexMaintenancePolicy.md
version: v1.0.0-pre-h8-index-maintenance
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 定义 Harness 索引维护、旧路径清理和 stale route 自检规则。
scope:
  - governance
  - index-maintenance
  - stale-route
  - compatibility-cleanup
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/HarnessIndex.md
relatedDocuments:
  - harness/governance/DocumentGovernance.md
  - harness/tools/scripts/stable/test-harness-governance.ps1
outputTo:
  - harness/governance/IndexMaintenancePolicy.md
owner: mixed
reviewAfter: 2026-07-23
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: pre-h8-index-maintenance-aligned
---
# Index Maintenance Policy（索引维护策略）

新增、迁移、归档或删除任何长期文档后，必须同步对应层级索引。

## 1. 索引层级

| 索引 | 职责 |
|---|---|
| `INDEX.md` | 全局导航入口。 |
| `harness/HarnessIndex.md` | General Harness 资产分层索引。 |
| 分区 Index | 对应分区的长期资产入口。 |
| `projects/<project-id>/docs/project/ProjectIndex.md` | 项目事实入口。 |

## 2. 删除兼容文件的前置条件

兼容文件删除前必须确认：

1. 目标路径已存在；
2. 根索引和分区索引已指向目标路径；
3. active 文档不再把旧路径作为默认入口；
4. 自检脚本不再要求旧路径存在；
5. 历史上下文不依赖旧路径作为事实源。

## 3. 自检

运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File harness/tools/scripts/stable/test-harness-governance.ps1 -Root . -Registry user/registry/projects.local.json
```

检查 required routes、stale route、frontmatter、Git 边界、敏感边界和 legacy path 回流。
