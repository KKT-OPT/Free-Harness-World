---
documentName: harness/templates/project-template/README.md
version: v1.0.0-pre-h8-clean-template-route
updatedAt: 2026-06-23 08:10:00.000 +08:00
status: active
purpose: 作为唯一目标项目模板入口，说明项目模板包结构、实例化映射和边界。
scope:
  - project-template
  - project-instantiation
  - template-index
prerequisites:
  - AGENTS.md
  - INDEX.md
  - harness/architecture/HarnessEngineering.md
relatedDocuments:
  - harness/templates/project-template/AGENTS.md
  - harness/templates/project-template/docs/project/ProjectIndex.md
  - harness/templates/project-template/model/StandardProjectPackage.md
outputTo:
  - harness/templates/project-template/README.md
owner: mixed
reviewAfter: 2026-07-18
supersededBy:
dependsOn:
  - harness/architecture/HarnessEngineering.md
  - harness/architecture/PLANS.md
review:
  reviewedBy: agent
  reviewedAt: 2026-06-18
  decision: pre-h8-compatibility-cleanup
---
# Project Template（项目模板）

`harness/templates/project-template/` 是可复用 Harness 项目模板资产的唯一目标路径。

模板包应复制或实例化到：

```text
projects/<project-id>/
  AGENTS.md
  docs/project/
```

模板文件只保存占位符和结构。它们不得包含真实项目事实、真实仓库 URL、真实分支名、真实构建命令、私有 settings 路径、凭据、auth 材料、原始日志、客户数据或本机绝对路径。

## 目标模板包

```text
harness/templates/project-template/
  README.md
  AGENTS.md
  docs/project/
    ProjectIndex.md
    ProjectProfile.example.yaml
    ValidationProfile.example.yaml
    SourceLayout.md
    Validation.md
    TestStrategy.md
    SensitiveBoundaries.md
    Acceptance.md
    prd/PRD.md
    architecture/Architecture.md
    dictionary/SemanticDictionary.md
    git/Repository.md
    api/Api.md
    data/Data.md
    test/Test.md
    workflow/README.md
    decision/ADR-0001.md
    model/README.md
    reports/README.md
  model/
    README.md
    ProjectTemplateGuide.md
    StandardProjectPackage.md
    ProjectInstanceModel.md
    ProjectRegistrationModel.md
    archive/
```

## 必需模板入口

| Area | Template Entry | Instantiated Target |
|---|---|---|
| project entry | `AGENTS.md` | `projects/<project-id>/AGENTS.md` |
| project index | `docs/project/ProjectIndex.md` | `projects/<project-id>/docs/project/ProjectIndex.md` |
| prd | `docs/project/prd/PRD.md` | `docs/project/prd/PRD.md` |
| architecture | `docs/project/architecture/Architecture.md` | `docs/project/architecture/Architecture.md` |
| dictionary | `docs/project/dictionary/SemanticDictionary.md` | `docs/project/dictionary/SemanticDictionary.md` |
| git | `docs/project/git/Repository.md` | `docs/project/git/Repository.md` |
| api | `docs/project/api/Api.md` | `docs/project/api/Api.md` |
| data | `docs/project/data/Data.md` | `docs/project/data/Data.md` |
| test | `docs/project/test/Test.md` | `docs/project/test/Test.md` |
| workflow | `docs/project/workflow/README.md` | `docs/project/workflow/README.md` |
| decision | `docs/project/decision/ADR-0001.md` | `docs/project/decision/ADR-0001.md` |
| model | `docs/project/model/README.md` | `docs/project/model/README.md` |
| reports | `docs/project/reports/README.md` | `docs/project/reports/README.md` |

## 实例化规则

1. 只能在 `projects/<project-id>/` 下实例化。
2. 将 `AGENTS.md` 复制到项目根目录。
3. 将 `docs/project/` 复制到项目的 `docs/project/` 目录。
4. 替换 `<project-id>`、`<project-name>`、`<project-type>`、`<repository-ref>`、`<branch-policy>`、`<validation-profile-id>`、`<command-id>`、`<owner>` 和 `<review-after>` 等占位符。
5. 未知项目事实记录为 `unknown` 或 `to-be-reviewed`；不要为了填空编造事实。
6. 项目事实保留在实例化后的项目中，不写入这个可复用模板包。
7. 任务 workflow evidence 保留在 `docs/project/workflow/`，不写入根 `AGENTS.md`。
8. 本地用户路由和私有执行细节保存在 `user/` 本地文件中，不写入模板。

## 旧路径规则

旧项目模板路径不再作为入口维护。新增或更新可复用项目模板时，只能写入：

```text
harness/templates/project-template/
```
