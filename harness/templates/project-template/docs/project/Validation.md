---
documentName: harness/templates/project-template/docs/project/Validation.md
version: v0.4.0-command-surface-main-program
updatedAt: 2026-06-23 18:54:52.291 +08:00
status: active
purpose: 项目验证命令面、证据规则和验收门禁模板。
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
  - harness/templates/project-template/docs/project/Validation.md
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
# Validation Template（验证模板）

## 目的

定义受管项目的稳定验证命令面、证据规则、验收门禁和已知验证缺口。

## 输出

- `projects/<project-id>/docs/project/Validation.md`
- validation profile map，中文解释是验证 profile 映射；
- command-to-evidence mapping，中文解释是命令到证据的映射；
- known validation gaps，中文解释是已知验证缺口。

## 敏感边界

可跟踪文档只记录验证摘要。原始日志、settings 正文、凭据文件、密钥、本机路径和未脱敏终端输出不得进入可跟踪文档。

## Validation Profiles（验证 Profile）

| Profile ID | Purpose | Stable Command | Required For |
|---|---|---|---|
| `<validation-profile-id>` | `<purpose>` | `<command-id>` | `<acceptance-stage>` |

## Command Surface（命令面）

| Scenario | Command ID | Tool | Evidence Location | Pass Criteria |
|---|---|---|---|---|
| Build | `<build-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |
| Unit test | `<unit-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |
| Integration test | `<integration-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |
| E2E or main program | `<main-program-command-id>` | `<stable-main-tool>` | `docs/project/workflow/` | Selected program exits successfully; scenario-specific output checks stay in workflow evidence until reviewed. |
| Static check | `<static-command-id>` | `<tool>` | `docs/project/workflow/` | `<criteria>` |

## 证据 Rules

1. 记录 command ID、mode、exit code、timestamp 和脱敏摘要。
2. 原始日志只保存到运行态目录或被忽略的项目输出目录。
3. 不粘贴凭据、settings XML、私有路径或未脱敏输出。
4. 被跳过的检查必须记录为 gap，不能记录为 success。
5. 单个 main program 或 E2E program 的固定输出、业务字段和验收判断默认只属于本次 workflow evidence；需要用户 review 后才能晋升为项目事实。

## Known Gaps

| Gap | Risk | Mitigation | Review Trigger |
|---|---|---|---|
| `<gap>` | `<risk>` | `<mitigation>` | `<trigger>` |
