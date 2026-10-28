---
documentName: harness/tools/docs/command-surfaces/ArtifactCleanupTool.md
version: v1.1.0-stable-promotion
updatedAt: 2026-10-28
status: active
purpose: 定义精确文件清理回执稳定工具的输入、输出、安全边界及验证，不提供自动删除功能。
scope: [stable-tool, artifact-cleanup, protection-receipt]
prerequisites: [../../ToolsIndex.md]
relatedDocuments: [../../scripts/stable/README.md]
outputTo: [harness/tools/docs/command-surfaces/ArtifactCleanupTool.md]
owner: mixed
reviewAfter: 2026-11-11
supersededBy:
dependsOn: [../../scripts/stable/verify-artifact-cleanup.py]
review:
  reviewedBy: user
  reviewedAt: 2026-10-28
  decision: approved-stable-promotion-after-validation
---
# 文件清理核验稳定工具

正式路径：`harness/tools/scripts/stable/verify-artifact-cleanup.py`。Python 3.9+，仅标准库；不依赖项目、Harness运行态或文档目录。
经用户授权并验证后于2026-10-28晋升；不执行删除/移动、不扫描私有设置、不生成业务数据。

## 1. 契约

| 项目 | 定义 |
|---|---|
| 输入 | `snapshot --root --manifest --receipt`；`verify --root --receipt` |
| manifest | schemaVersion固定为`harness.artifact-cleanup.v1`；remove和protect为精确相对文件路径数组；至少保护一个文件 |
| 输出 | snapshot只创建新的本地receipt；verify只输出JSON，含status、计数和相对路径findings；退出0通过、1失败、2命令错误 |
| 状态回执 | receipt保存相对路径、SHA-256和字节数，不保存文件正文、绝对根路径或用户设置；调用者放ignored运行目录 |
| 日志 | 无另设日志文件；stdout为可审计摘要，调用者按需重定向到运行态目录 |
| 失败模式 | invalid-input-or-filesystem、removalTargetStillPresent、protectedFileMissing、protectedFileChanged |
| 修复建议 | 核对显式清单/权限；从真实快照或Git恢复误改文件；使用新receipt路径，不覆盖旧证据 |
| 敏感边界 | 不把私有文件加入清单；相对名称也可能敏感，回执仍默认不入库；不输出OS异常内的绝对路径 |

```json
{
  "schemaVersion": "harness.artifact-cleanup.v1",
  "remove": ["docs/stage-obsolete.json"],
  "protect": ["tests/fixtures/current.json", "src/engine.java"]
}
```

```text
python -B harness/tools/scripts/stable/verify-artifact-cleanup.py snapshot --root <workspace> --manifest <local-plan.json> --receipt <new-runtime-receipt.json>
python -B harness/tools/scripts/stable/verify-artifact-cleanup.py verify --root <workspace> --receipt <runtime-receipt.json>
python -B -m unittest discover -s harness/tools/scripts/stable/tests -v
```

## 2. 使用顺序与限制

1. 先人工检索源码默认路径、传递引用、冻结证据及外部入口，迁移未结风险；不能按扩展名/日期直接判临时文件。
2. 用户授权清理后编制精确清单，在改动前生成receipt和独立恢复快照；工具只做身份回执，不提供备份。
3. 人工按批准清单编辑/删除；运行verify核对已删项和保护字节，再检查链接、风险迁移及Git范围。
4. 禁止绝对路径、越界、`..`、目录目标、重复/角色交叉、NTFS流与尾点/尾空格别名、符号链接/junction；无递归删除或自动修复。
5. v1仅核验列举文件，不能发现未列举的误改、动态依赖或新增文件，不能替代依赖审查/完整Git diff。
   receipt不是防篡改签名或跨时点原子快照；快照过程中保持工作区静止，保护原receipt和恢复证据。
6. 本次晋升不增加自动删除权限；后续功能只按真实重复需求扩展，不把项目临时清理脚本整份搬进stable。

## 3. 验证边界

测试包含实际CLI成功/失败退出、损坏回执、旧回执保护、保护文件变化/丢失、中文和越界路径，
以及Windows真实junction拒绝与目标内容保留。符号链接创建受宿主权限限制时明确skip，另测拒绝分支。
不宣称覆盖所有文件系统或不可信并发攻击；工作区应保持静止，receipt不是签名。
