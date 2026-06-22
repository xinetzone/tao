# 归档日志索引 (Archive Log)

本文件记录 AgentForge 仓库历次正式归档操作的元信息,用于审计追溯。每次使用 `archive-folder` 技能(启用 `-LogFile`)执行归档后,应在此追加一条记录。

## 字段说明

| 字段 | 说明 |
|---|---|
| 日期 | 归档执行日期(YYYY-MM-DD) |
| 源路径 | 归档前源文件夹路径(已删除则标注) |
| 目标路径 | 归档目标路径 |
| 文件数 / 目录数 | 验证阶段统计 |
| 体积 | 复制字节数(可读格式) |
| 校验方式 | Size+MTime 或 Size+MTime+SHA256 |
| 验证结果 | ✅ 通过 / ❌ 失败 |
| 源处理 | 保留 / 已删除 / 引用阻止 |
| 日志文件 | robocopy + 脚本日志路径(若启用 `-LogFile`) |
| 备注 | 其他需要追溯的信息 |

## 归档记录

### 2026-06-22 — react-survey 静态站点归档

| 字段 | 值 |
|---|---|
| 日期 | 2026-06-22 |
| 源路径 | `.archive/react-survey/`(已删除) |
| 目标路径 | `apps/chaos/docs/react-survey/` |
| 文件数 / 目录数 | 4 文件 / 5 目录 |
| 体积 | 3.63 MB |
| 校验方式 | Size + MTime |
| 验证结果 | ✅ 通过(0 不一致) |
| 源处理 | 已删除(用户确认) |
| 日志文件 | 未启用 `-LogFile`(本次归档发生在 P4 落地前) |
| 备注 | 使用 `robocopy /E /COPY:DAT /DCOPY:DAT`;后续冗余清理删除 2 个未引用 JS + 3 个空目录,最终体积 0.20 MB |

### 2026-06-22 — agent-insight 静态站点归档

| 字段 | 值 |
|---|---|
| 日期 | 2026-06-22 |
| 源路径 | `.archive/agent-insight/`(已删除) |
| 目标路径 | `apps/chaos/docs/agent-insight/` |
| 文件数 / 目录数 | 14 文件 / 4 目录 |
| 体积 | 5.37 MB |
| 校验方式 | Size + MTime |
| 验证结果 | ✅ 通过(0 不一致) |
| 源处理 | 已删除(沿用上次偏好) |
| 日志文件 | 未启用 `-LogFile`(本次归档发生在 P4 落地前) |
| 备注 | 后续冗余清理删除 2 个未引用 JS + 1 个空目录,最终体积 1.94 MB;`hero_1280x720.jpg` 与 react-survey 同名但内容不同,通过 SHA256 区分 |

## 维护说明

- **追加规则**:新归档完成后,在「归档记录」章节末尾追加一条表格
- **日志留存策略**:`-LogFile` 文件建议放在 `apps/chaos/docs/logs/` 或与归档目标同根目录,文件名含日期与源名(如 `react-survey-20260622.log`)
- **历史回溯**:如需查看 robocopy 原生统计,直接 `Get-Content` 对应日志文件
- **关联文档**:归档方法论见 [task-summary-archive-and-cleanup-20260622.md](./task-summary-archive-and-cleanup-20260622.md),技能定义见 [`archive-folder/SKILL.md`](../../.agents/skills/archive-folder/SKILL.md)

---

*最后更新:2026-06-22(P4 落地,建立本索引并补录历史归档)*
