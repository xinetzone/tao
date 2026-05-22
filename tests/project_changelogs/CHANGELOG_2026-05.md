# 2026-05 项目级变更日志

所有关于 **AgentForge** 项目级别的跨模块变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]
### Added
- 引入模块化的变更日志管理机制，按照模块与时间（项目级）拆分 CHANGELOG。
- 新增 `taolib.github_app` GitHub App 安装令牌管理层，支持请求级覆盖头、环境降级、进程内缓存、单飞刷新与 CLI 诊断输出。
- 新增 `docs/github-app-token-override.md` 学习笔记，沉淀 GitHub App 安装令牌覆盖头的背景、迁移要点与工程启发。
- 新增 `.agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md`，记录专项测试、并发指标与残余风险。

### Changed
- 更新 `docs/index.md` 与 `README.md`，补充 GitHub App 令牌治理入口、专项测试入口与文档导航。
- 更新 `.github/workflows/ci.yml`，在全量测试前显式执行 `tests/github_app` 专项校验，提升 GitHub App 认证层回归可见性。
