---
documentName: harness/reports/redacted/H9-5EngineeringReliabilityFeedback.md
version: v1.2.0-harness-git-delivery
updatedAt: 2026-10-28
status: active
purpose: 记录真实项目长期落地经验反向优化Harness的分类、候选、门禁修复、验证及用户审核边界。
scope: [h9-5-feedback, skill-patches, tool-reliability, candidate-review]
prerequisites: [../../governance/ProjectHarnessFeedbackPolicy.md]
relatedDocuments:
  - ../../skills/SkillIndex.md
  - ../../skills/reviewed/stateful-algorithm-validation/SKILL.md
  - ../../tools/docs/command-surfaces/ArtifactCleanupTool.md
  - ../../architecture/PLANS.md
outputTo: [harness/reports/redacted/H9-5EngineeringReliabilityFeedback.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy:
dependsOn: [../../governance/SkillGovernance.md]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: explicit-conditional-approval-tests-passed-assets-promoted
---
# H9-5工程可靠性沉淀审核包

## 1. 来源与范围

用户明确要求沉淀项目长期开发中反复使用的skills/tools/scripts。来源为项目用户反馈、已通过的文档整理和当前稳定工具/技能代码。
项目任务证据留在项目工作流；这里只保留通用流程与工具结论，不保留数据、算法模式名、识别率、阈值或宿主设置。
来源追踪：[项目反馈证据](../../../projects/lfms-decision/docs/project/workflow/20261028-h9-5-motionfact-harness-feedback.md)；
不要求通用工具或迁移后的项目在运行时读取此文档。
本轮不是自动创建或自动晋升：用户明确要求脚本测试通过后按规则晋升，测试通过后才迁入正式目录、合入补丁。
未改业务源码/参数；已有reviewed Skill只增量引入专题reference，不覆盖用户已有修改。

已检查现有code-review、code-implementation、algorithm-performance-analysis、simulation-failure-triage：
常规审查/实现/性能/失败归因已有能力，选择补丁而非再造大Skill；跨轮在线与独立参考的验证契约仍有独立缺口。

## 2. Candidate Table / 治理候选

| ID | 信号与落点 | 处置与当前状态 | 验证/审批 |
|---|---|---|---|
| HF-01 | 配置、状态、参考、指标及性能边界反复返工 | 已合入code-implementation/code-review/algorithm-performance-analysis的专题reference及入口；原补丁归archive | 范围/引用/结构走查；usage只记本次实际修订 |
| HF-02 | 在线算法与离线标签天然不同 | `skills/reviewed/stateful-algorithm-validation/`，候选活跃副本已清理 | 结构、职责与行为反例走查；不冒充多个独立项目已实测 |
| HF-03 | 清理阶段文件易误删执行依赖 | `tools/scripts/stable/verify-artifact-cleanup.py`及stable/tests；契约同步 | 单测、真实junction、CLI正反例通过；无自动删除 |
| HF-04 | 中文、编码与验收状态检查不充分 | 两份stable门禁支持中文/UTF-8/LF/CRLF；标题不代表批准，failed复查/partial修复不允许闭环 | 两种PowerShell的自测与实际CLI反例通过 |
| HF-07 | 总治理先递归再排除，仍进入项目长路径 | 扫描前剪枝，私有区/reparse不遍历；仅项目根Git标记 | 双PowerShell扫描自测、完整治理通过 |
| HF-05 | 用临时模拟/标注脚本替代稳定入口或耦合Harness | 保留现有Java/Maven工具；便携运行规范纳HF-01，不复制项目启动器、绘图或标注代码 | 项目专属程序留项目，不另建通用运行时依赖 |
| HF-06 | 项目常数、标签、模式和验收结论 | no-action；只留项目权威文档 | 禁止晋升为通用Skill/Memory；不追溯捏造历史使用次数 |

表内路径以harness/为基准。晋升批准来自用户本轮“测试通过后完成晋升”的明确指令，不挪用项目文档归并批准。

## 3. 门禁修复事实

原两个门禁依赖英文段落标识，使中文任务简报、检查轨迹、执行计划、验证报告和治理候选不能被识别。
加入有限中文标题别名，英文/参数保持可用；PowerShell源码ASCII，中文正则/夹具用Unicode转义，读取显式UTF-8。
本轮实际CLI正例进一步复现并修复CRLF状态行误拒；验收标题/历史批准不能盖过pending/rejected最终状态。
代码闭环要求明确成功复查和fixed/not-required处置，failed或partial会失败；未移除私有路径/凭据检查。

code-review自测新增调用真实验证函数的英文/中文合格样例，以及未接受、最终pending、复查pending、缺检查轨迹反例。
lifecycle自测增加中文workflow/report、缺验证、未接受反例。门禁仅是结构/状态检查，不能鉴别文字真实性或代替人审。

完整治理初次失败于本应排除的项目数据长路径；修复不是忽略异常，而是目录进入前排除项目/运行态和私有区，
保留正常区域的占位文件/构建产物/文本检查及项目根Git边界提示。独立registry门禁继续执行，原有用户工具改动保留。

## 4. Validation / 验证结果

- 两份稳定门禁在Windows PowerShell与PowerShell 7的`-SelfTest`通过。
- 四个reviewed Skill经`python -X utf8 .../quick_validate.py`验证；不以结构检查冒充算法效果。
- 清理工具测试覆盖只读快照、不自动删除、精确删除、保护文件丢失/改动、同尺寸内容变化、路径越界/NTFS流/路径别名、
  重复/交叉、目录/空保护、损坏回执、中文路径、CLI退出/旧回执保护/可移植摘要。
- 正式目录统一测试：`python -B -m unittest discover -s harness/tools/scripts/stable/tests -v`。
  Python 3.11/3.12各25项：24通过、1因宿主符号链接权限skip。15项为清理工具测试，10项CLI测试均分别调用PowerShell 5.1/7。
- Windows真实junction拒绝及目标内容保留通过；符号链接/reparse拒绝分支另有不依赖权限的测试通过。
- 实际创建符号链接的测试依赖宿主权限；无权限时明确skip，另以mock验证拒绝分支；不宣称所有Windows reparse类型均实测。
- 项目已批准整理的闭环门禁、本轮证据门禁、完整Harness治理检查通过（0 error/0 warning，1条独立项目Git提示）；
  文档/引用与受保护源码/夹具复核结果见项目反馈工作流。
- 晋升后重新校验元数据/引用、usage唯一性、候选清理、正式文件Git识别及3份PowerShell ASCII内容，保留既有BOM。

不运行新算法/性能试验，不为本轮工具修复新增识别率或性能结论。

## 5. Approval And Disposition / 审核与处置

用户明确条件批准→加强正反例并测试→新Skill迁reviewed/新工具迁stable→三个补丁增量合入→移除候选活跃路由→更新usage/索引/证据。
HF-04/HF-07是已有工具修复，不再创建一份同名工具。新增正式资产与必要索引/审核记录按限定路径纳管。
资产晋升时保留先前staged与混合修改，仅纳管相关新资产；当时未提交或推送。
后续Git交付依据用户单独授权执行，范围和验证见第7节，不挪用晋升批准自动发布。

## 6. Non-Promotion / 非晋升边界

本报告只记录验证/批准和去向；规则以已吸收的reviewed/stable目标为准。
不发布新Harness总架构、不宣布H9-5/H10完成，不迁移真实项目代码，也不替项目决定默认开关、指标或容差。
工具v1不推断依赖闭包、不做恢复/删除、不覆盖回执；新独立项目上的Skill效果仍需实际应用验证。

## 7. Harness Git交付

Task Brief：用户2026-10-28明确要求提交Harness相关变更，并另行批准推送到既有`origin/agent-git`。
目标是将已批准的技能、稳定工具、数值治理门禁、索引和审核记录作为完整资产包提交；不修改或提交受管项目。
风险为混入项目源码/历史、私有配置或运行产物；无目标分支/范围等关键缺失，禁止强推或自动覆盖远端历史。

范围核验：Harness与项目的Git目录、origin不同；仅纳入`harness/`下31份变更，
补纳已被技能/治理调用的test-java-magic-values.ps1，避免发布缺依赖；项目副本、target/class/运行态及私有设置不进入提交。
项目提交身份和tracked工作区状态只做前后摘要核对，不读取或改写业务内容。

提交前复核：正式测试25项（24通过、1项宿主符号链接权限skip）、数值扫描自测、性能统计自测、治理及暂存差异/敏感边界检查。
稳定发布脚本commit模式会执行全根`git add .`并刷新base；本次采用限定文件清单的等价Git操作，仍保留全部提交前门禁。
完成标准：单一Harness提交内容清晰、普通推送成功、远端分支与本地HEAD一致、无项目文件/变更或私有资产混入。
实际提交哈希和远端结果以Git记录及交付回复为准，不把自身提交哈希回写造成第二次提交。
