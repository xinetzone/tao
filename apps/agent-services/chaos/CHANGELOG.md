# 更新日志

本文件为项目变更日志的导航索引。变更记录按层级拆分至以下位置：

- **各功能模块**的详细变更记录 → `tests/testing/<模块>/CHANGELOG.md`
- **项目级别**（跨模块）变更记录 → `tests/project_changelogs/CHANGELOG_<年月>.md`（按时间拆分）

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## 模块变更日志索引

| 模块 | 说明 | CHANGELOG 路径 |
|------|------|---------------|
| Auth | 认证授权框架 | [tests/testing/test_auth/CHANGELOG.md](tests/testing/test_auth/CHANGELOG.md) |
| Analytics | 用户行为分析系统 | [tests/testing/test_analytics/CHANGELOG.md](tests/testing/test_analytics/CHANGELOG.md) |
| Email Service | 多提供商邮件服务 | [tests/testing/test_email_service/CHANGELOG.md](tests/testing/test_email_service/CHANGELOG.md) |
| File Storage | 文件存储与 CDN 系统 | [tests/testing/test_file_storage/CHANGELOG.md](tests/testing/test_file_storage/CHANGELOG.md) |
| OAuth | OAuth2 第三方登录系统 | [tests/testing/test_oauth/CHANGELOG.md](tests/testing/test_oauth/CHANGELOG.md) |
| Rate Limiter | API 限流中间件 | [tests/testing/test_rate_limiter/CHANGELOG.md](tests/testing/test_rate_limiter/CHANGELOG.md) |
| Task Queue | 后台任务队列 | [tests/testing/test_task_queue/CHANGELOG.md](tests/testing/test_task_queue/CHANGELOG.md) |
| Config Center | 企业级配置管理系统 | [tests/testing/test_config_center/CHANGELOG.md](tests/testing/test_config_center/CHANGELOG.md) |
| Data Sync | 数据同步模块 | [tests/testing/test_data_sync/CHANGELOG.md](tests/testing/test_data_sync/CHANGELOG.md) |
| Multi Agent | 多智能体系统 | [tests/testing/test_multi_agent/CHANGELOG.md](tests/testing/test_multi_agent/CHANGELOG.md) |
| Symphony | 编排引擎 | [tests/test_symphony/CHANGELOG.md](tests/test_symphony/CHANGELOG.md) |

## 项目级变更日志索引

项目级别（跨模块）的变更记录按时间拆分，存放在 `tests/project_changelogs/` 目录下：

| 时间 | 说明 | CHANGELOG 路径 |
|------|------|---------------|
| 2026-05 | 2026年5月项目级变更（[未发布]） | [tests/project_changelogs/CHANGELOG_2026-05.md](tests/project_changelogs/CHANGELOG_2026-05.md) |
| 2026-04 | 2026年4月项目级变更（v0.5.5） | [tests/project_changelogs/CHANGELOG_2026-04.md](tests/project_changelogs/CHANGELOG_2026-04.md) |
