# Auth 认证授权模块 - 更新日志

本文件记录 Auth 模块的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

### 新增

- **统一认证授权框架**
  - JWT 令牌服务（创建/验证）、API Key 静态认证
  - RBAC 角色权限控制（5 个预定义角色）
  - Token 黑名单（Redis / 内存双实现）
  - FastAPI 中间件、依赖注入、OAuth2 Scheme 集成

### 修复

- **安全修复**：修复 RBAC 权限检查中 `user_roles` 为空列表的问题
- **安全修复**：添加缺失的 `JWTError` 导入（`taolib.testing.auth/fastapi/dependencies.py`）
- 修复 `taolib.testing.auth` 中登录和刷新令牌时角色未加载的问题

### 安全

- RBAC 系统现在正确执行基于角色的权限检查
