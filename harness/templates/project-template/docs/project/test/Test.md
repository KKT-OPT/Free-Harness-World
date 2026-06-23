---
documentName: harness/templates/project-template/docs/project/test/Test.md
version: v0.2.0-command-surface-main-program
updatedAt: 2026-06-23 18:54:52.291 +08:00
status: active
purpose: 项目测试范围、质量门禁和证据策略模板。
scope:
  - project-template
  - project-doc-template
prerequisites:
  - AGENTS.md
  - harness/templates/project-template/README.md
relatedDocuments:
  - harness/templates/project-template/README.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
outputTo:
  - harness/templates/project-template/docs/project/test/Test.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/templates/project-template/README.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-23
  decision: h9-command-surface-main-program
---
# Test Template（测试模板）

## 目的

记录项目测试范围、质量门禁、验证命令、证据规则和已知缺口。

## 输入

- validation profile
- repository command surfaces，中文解释是仓库命令面；
- acceptance criteria，中文解释是验收标准；
- architecture and risk facts，中文解释是架构和风险事实；
- previous workflow evidence，中文解释是既有工作流证据。

## 输出

- `projects/<project-id>/docs/project/test/Test.md`
- test scope matrix，中文解释是测试范围矩阵；
- command and evidence map，中文解释是命令和证据映射；
- quality gates and known gaps，中文解释是质量门禁和已知缺口。

## 敏感边界

测试证据不得包含凭据文件正文、private settings、未脱敏日志、私有路径、真实私有仓库 URL 或原始生产数据。

## 实例化规则

1. 将本文件复制到 `projects/<project-id>/docs/project/test/Test.md`。
2. 优先使用稳定 Harness command surface，不使用临时命令作为默认验证方式。
3. 原始报告默认留在运行态或 ignored 输出目录，脱敏并 review 后才可进入 tracked docs。
4. 明确记录验证缺口，不把单个场景通过误写成全量覆盖。

## Test Scope

| Scope | Purpose | Command Surface | Required For Acceptance |
|---|---|---|---|
| unit | `<purpose>` | `<command-id>` | `<yes-no>` |
| integration | `<purpose>` | `<command-id>` | `<yes-no>` |
| e2e | Selected E2E or main programs. | `<stable-main-command-id>` | `<yes-no>` |
| docs | `<purpose>` | `<command-id>` | `<yes-no>` |

## Quality Gates

| Gate | Criteria | Evidence |
|---|---|---|
| `<gate>` | `<criteria>` | `<evidence>` |

## Known Gaps

| Gap | Risk | Mitigation | Owner |
|---|---|---|---|
| `<gap>` | `<risk>` | `<mitigation>` | `<owner>` |

## 证据 Rules

1. 摘要可以进入 workflow evidence。
2. 原始日志进入 tracked docs 前必须脱敏。
3. 生成输出不是 Project Facts，除非已经 review。
4. 单个 E2E/main program 的业务输出只在对应 workflow evidence 中记录；是否晋升为项目测试事实由用户或治理 review 决定。
