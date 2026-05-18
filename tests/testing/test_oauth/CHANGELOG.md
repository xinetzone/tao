# OAuth 第三方登录模块 - 更新日志

本文件记录 OAuth 模块的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

### 新增

- **OAuth2 第三方登录系统**
  - Google 和 GitHub OAuth2 提供商
  - 完整的 OAuth 流程编排、Token 加密存储
  - 账户关联/解绑、会话管理、活动审计日志
  - 管理后台 API 和与 ConfigCenter 的集成

### 安全

- OAuth Token 使用 `cryptography` 库加密存储
