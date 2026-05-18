# CHANGELOG 按功能模块拆分 Spec

## Why
项目 `CHANGELOG.md` 目前将所有模块的变更记录集中存储于单一文件中，随着版本迭代内容不断增加，文件体积持续膨胀，查阅和维护均变得困难。需要将其按功能模块拆分为多个文件，迁移至 `tests/` 目录下各模块测试子目录中；同时将项目级（跨模块）变更按时间拆分为独立文件，存放于 `tests/` 根目录下；并将根目录 `CHANGELOG.md` 改造为纯导航索引文件。

## What Changes
- **模块级拆分**：将 `CHANGELOG.md` 中按模块可归类的变更记录，拆分到对应测试子目录下的独立 `CHANGELOG.md` 文件
- **时间级拆分**：将项目级（跨模块）变更记录按时间拆分为独立文件（如 `tests/CHANGELOG_2026-05.md`）
- **导航索引**：根目录 `CHANGELOG.md` 改造为纯导航索引文件，包含模块索引和时间型文件索引
- **文档更新**：`doc/architecture/directory_structure.md` 中关于 CHANGELOG.md 的描述

## Impact
- Affected specs: 无（新建独立规格）
- Affected code: 
  - `CHANGELOG.md`（重写为纯导航文件）
  - `tests/project_changelogs/CHANGELOG_2026-05.md`（新建，项目级变更）
  - `tests/project_changelogs/CHANGELOG_2026-04.md`（新建，项目级变更）
  - `tests/testing/test_auth/CHANGELOG.md`（新建）
  - `tests/testing/test_analytics/CHANGELOG.md`（新建）
  - `tests/testing/test_email_service/CHANGELOG.md`（新建）
  - `tests/testing/test_file_storage/CHANGELOG.md`（新建）
  - `tests/testing/test_oauth/CHANGELOG.md`（新建）
  - `tests/testing/test_rate_limiter/CHANGELOG.md`（新建）
  - `tests/testing/test_task_queue/CHANGELOG.md`（新建）
  - `tests/testing/test_config_center/CHANGELOG.md`（新建）
  - `tests/testing/test_data_sync/CHANGELOG.md`（新建）
  - `tests/testing/test_multi_agent/CHANGELOG.md`（新建）
  - `tests/test_symphony/CHANGELOG.md`（新建）
  - `doc/architecture/directory_structure.md`（修改）

## ADDED Requirements

### Requirement: 按模块拆分的 CHANGELOG 文件
系统 SHALL 在 `tests/` 目录下已有测试子目录的每个功能模块目录中，创建独立的 `CHANGELOG.md` 文件，包含该模块相关的所有历史变更记录（从根 CHANGELOG.md 提取），并遵循 Keep a Changelog 格式。

拆分目标模块及其路径如下：

| 模块 | CHANGELOG 路径 |
|------|---------------|
| auth（认证授权） | `tests/testing/test_auth/CHANGELOG.md` |
| analytics（用户行为分析） | `tests/testing/test_analytics/CHANGELOG.md` |
| email_service（邮件服务） | `tests/testing/test_email_service/CHANGELOG.md` |
| file_storage（文件存储） | `tests/testing/test_file_storage/CHANGELOG.md` |
| oauth（OAuth2 第三方登录） | `tests/testing/test_oauth/CHANGELOG.md` |
| rate_limiter（API 限流） | `tests/testing/test_rate_limiter/CHANGELOG.md` |
| task_queue（后台任务队列） | `tests/testing/test_task_queue/CHANGELOG.md` |
| config_center（配置中心） | `tests/testing/test_config_center/CHANGELOG.md` |
| data_sync（数据同步） | `tests/testing/test_data_sync/CHANGELOG.md` |
| multi_agent（多智能体系统） | `tests/testing/test_multi_agent/CHANGELOG.md` |
| symphony（编排引擎） | `tests/test_symphony/CHANGELOG.md` |

#### Scenario: 模块 CHANGELOG 包含完整变更记录
- **WHEN** 用户打开 `tests/testing/test_auth/CHANGELOG.md`
- **THEN** 该文件包含 auth 模块的所有历史变更，按版本号分组，格式遵循 Keep a Changelog

#### Scenario: 无历史变更的模块
- **WHEN** 某模块（如 multi_agent、symphony）在当前 CHANGELOG 中没有对应条目
- **THEN** 该模块的 CHANGELOG.md 仅包含文件头部说明（遵循 Keep a Changelog 格式），注明该模块暂无历史记录

### Requirement: 按时间拆分的项目级 CHANGELOG 文件
系统 SHALL 将项目级别（跨模块）的变更记录按时间拆分为独立文件，存放于 `tests/project_changelogs/` 目录下。文件命名规范为 `tests/project_changelogs/CHANGELOG_<YYYY-MM>.md`。

#### Scenario: 时间型文件包含对应时段的项目级变更
- **WHEN** 用户打开 `tests/project_changelogs/CHANGELOG_2026-04.md`
- **THEN** 该文件包含 2026 年 4 月（v0.5.5）的所有项目级变更记录

### Requirement: 根目录 CHANGELOG.md 纯导航索引文件
系统 SHALL 将根目录 `CHANGELOG.md` 改造为纯导航索引文件，包含：
1. 说明文字（变更记录已按模块和时间拆分）
2. 模块变更日志索引表（11 个模块 + Markdown 链接）
3. 项目级变更日志索引表（按时间 + Markdown 链接）
4. 不包含任何具体变更记录内容

#### Scenario: 用户从根 CHANGELOG 导航到目标文件
- **WHEN** 用户打开根 `CHANGELOG.md`
- **THEN** 可以看到清晰的模块索引表和项目级时间索引表，点击链接即可跳转到对应文件

### Requirement: 更新目录结构文档引用
系统 SHALL 更新 `doc/architecture/directory_structure.md` 中关于 CHANGELOG.md 的描述，反映新的模块+时间双重拆分结构。

#### Scenario: 目录结构文档反映实际结构
- **WHEN** 用户查看 `doc/architecture/directory_structure.md`
- **THEN** 其中关于 CHANGELOG.md 的描述与新的拆分结构一致，并说明 tests/ 目录下存放了模块 CHANGELOG 和时间型 CHANGELOG 文件
