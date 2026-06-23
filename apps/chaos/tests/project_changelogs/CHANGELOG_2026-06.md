# 2026-06 项目级变更日志

所有关于 **AgentForge** 项目级别的跨模块变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

### Added

- **archive-folder 技能升级至 v1.3.0**：归档能力四项增强。
  - P4：新增 `-LogFile` 参数，robocopy 通过 `/LOG+` 追加原生统计，脚本各阶段输出同步写入，结果对象新增 `LogFile` 字段。
  - P11：新增 `-LogDir` 参数，自动生成 `<src-name>-<yyyyMMdd>.log` 文件名，减少用户认知负担，适合每日定时归档。
  - P12：新增 `-LogAppend` switch，支持跨次调用追加到同一日志文件，用标记头（"===== 追加 =====" vs "===== 开始 ====="）区分首次与后续。
  - P14：新增 `-CheckDeclConsistency` switch，阶段 0.5 执行 HTML 声明一致性检查，结果对象新增 `DeclIssues` 字段（提示不阻断）。
- **asset-redundancy-analyzer 技能新建 v1.0.0**：静态资产冗余分析技能。
  - 6 阶段流程：参数校验 → 文件枚举 → 引用提取 → 缺失检测 → 未引用检测 → 重复检测。
  - 支持 `script`/`img`/`link`/`@font-face` 四类 HTML 引用提取。
  - 决策矩阵：保留/删除/归档三选一，含理由与风险。
  - 英文注释，避免 PowerShell 5.1 GBK 编码问题。
- **参考文档沉淀**：
  - 新增 [`.agents/docs/references/bypass-shouldprocess.md`](../../.agents/docs/references/bypass-shouldprocess.md)（P10）：.NET API 绕过 ShouldProcess 模式参考文档，跨技能复用。
  - 新增 [`.agents/docs/references/asset-declaration-matrix.md`](../../.agents/docs/references/asset-declaration-matrix.md)（P13）："声明但缺失"资源治理决策矩阵，采用文档形式避免与 asset-redundancy-analyzer 技能功能重叠。
- **归档日志索引**：新增 [`docs/tech/archive-log.md`](../../docs/tech/archive-log.md)，补录 react-survey 与 agent-insight 两条历史归档记录，形成"日志文件 + 索引文件"双层审计体系。

### Changed

- **任务总结文档更新**：更新 [`docs/tech/task-summary-archive-and-cleanup-20260622.md`](../../docs/tech/task-summary-archive-and-cleanup-20260622.md)，合并 P4/P7/P8/P10-P14 执行经验，报告版本升级至 standard v5.0（全合并版）。
  - 新增方法论 M12（技能功能边界评估矩阵）与 M13（归档前校验不阻断模式）。
  - 新增决策 D22-D26（沉淀形式/命名策略/分隔方式/技能 vs 文档/阻断策略）。
  - 五维雷达评分更新，综合评价补充 P10-P14 三个关键判断。

### Fixed

- **react-survey 字体缺失治理**（P7）：移除 `react-survey.html` 中 2 个无效 `@font-face` 声明（`NotoSansSC-Regular.ttf` 与 `NotoSansSC-Bold.ttf`），font-family 调整为 `'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif` 回退链。零体积消除 404，系统字体回退链覆盖主流平台。

## 版本映射

| 组件 | 旧版本 | 新版本 | 变更类型 |
|------|--------|--------|----------|
| archive-folder 技能 | v1.2.0 | v1.3.0 | feat（新增四个参数） |
| asset-redundancy-analyzer 技能 | — | v1.0.0 | feat（新建） |
| react-survey.html | — | — | fix（移除无效声明） |

## 提交记录

| 提交哈希 | 类型 | 提交信息 |
|----------|------|----------|
| `ab383d2` | fix | fix(react-survey): 移除无效 @font-face 声明,改用字体回退链 |
| `ab03a7d` | feat | feat(archive-folder): 升级至 v1.3.0,新增日志留存/自动命名/追加模式/HTML 声明一致性校验 |
| `a2d4633` | feat | feat(asset-redundancy-analyzer): 新增静态资产冗余分析技能 v1.0.0 |
| `c9c344e` | docs | docs(references): 沉淀 ShouldProcess 绕过模式与资源治理决策矩阵 |
| `b257bbb` | docs | docs: 更新任务总结,合并 P4/P7/P8/P10-P14 执行经验 |

## 验证结果

| 验证项 | 结果 | 说明 |
|--------|------|------|
| archive-folder -LogFile/-LogDir/-LogAppend | ✅ 通过 | WhatIf + 真实归档双模式验证，日志正确显示覆盖与追加两种头部标记 |
| archive-folder -CheckDeclConsistency | ✅ 通过 | react-survey 声明检查通过，`DeclIssues : {}` 返回空数组 |
| asset-redundancy-analyzer 健康检查 | ✅ 通过 | react-survey（2 文件/1 引用）与 agent-insight（12 文件/11 引用）均 0 缺失/0 未引用/0 重复 |
| react-survey.html 残留检查 | ✅ 通过 | Grep 验证无 `NotoSans`/`@font-face`/`_shared/fonts` 残留 |

## 衍生产物

| 产物 | 路径 | 说明 |
|------|------|------|
| archive-folder 技能 | [`.agents/skills/archive-folder/`](../../.agents/skills/archive-folder/) | 三段式归档 + 引用检查 + 日志留存 + HTML 声明一致性校验（v1.3.0） |
| asset-redundancy-analyzer 技能 | [`.agents/skills/asset-redundancy-analyzer/`](../../.agents/skills/asset-redundancy-analyzer/) | 静态资产冗余分析（v1.0.0） |
| ShouldProcess 绕过模式参考文档 | [`.agents/docs/references/bypass-shouldprocess.md`](../../.agents/docs/references/bypass-shouldprocess.md) | 跨技能复用的 .NET API 模式 |
| 资源治理决策矩阵 | [`.agents/docs/references/asset-declaration-matrix.md`](../../.agents/docs/references/asset-declaration-matrix.md) | 补全 vs 移除的成本评估框架 |
| 归档日志索引 | [`docs/tech/archive-log.md`](../../docs/tech/archive-log.md) | 历次归档元信息 |
| 任务总结文档 | [`docs/tech/task-summary-archive-and-cleanup-20260622.md`](../../docs/tech/task-summary-archive-and-cleanup-20260622.md) | standard v5.0 全合并版 |
