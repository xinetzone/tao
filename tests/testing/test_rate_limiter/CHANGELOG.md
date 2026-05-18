# Rate Limiter API 限流模块 - 更新日志

本文件记录 Rate Limiter 模块的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

### 新增

- **API 限流中间件**
  - 滑动窗口限流算法（Redis 后端）、FastAPI 中间件集成
  - 违规追踪和管理 API
