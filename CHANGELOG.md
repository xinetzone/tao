# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.5] - 2026-04-06

本版本是一次重大功能扩展，将 taolib 从单一配置管理库升级为企业级全栈微服务平台。
新增 8 个后端服务模块，建立完整的认证体系、数据管道和容器化部署架构。

### Added

- **新增 `taolib.auth` 统一认证授权框架**
  - JWT 令牌服务（创建/验证）、API Key 静态认证
  - RBAC 角色权限控制（5 个预定义角色）
  - Token 黑名单（Redis / 内存双实现）
  - FastAPI 中间件、依赖注入、OAuth2 Scheme 集成
- **新增 `taolib.analytics` 用户行为分析系统**
  - 事件采集与聚合分析、会话追踪
  - 完整的 FastAPI 服务器架构，支持命令行启动
  - 内置前端分析仪表板
- **新增 `taolib.email_service` 多提供商邮件服务**
  - 4 个邮件提供商实现：SMTP、SendGrid、Mailgun、Amazon SES
  - ProviderFailoverManager 自动故障转移
  - Redis / 内存双队列、Jinja2 模板引擎、退信处理、Webhook 端点
- **新增 `taolib.file_storage` 文件存储与 CDN 系统**
  - S3 存储后端（aiobotocore）和本地文件系统后端
  - CDN 集成（CloudFront + 通用 CDN）
  - 图片处理管道（缩略图、验证）、分块上传、签名 URL、生命周期管理
  - 客户端 SDK 和 FastAPI 服务器
- **新增 `taolib.oauth` OAuth2 第三方登录系统**
  - Google 和 GitHub OAuth2 提供商
  - 完整的 OAuth 流程编排、Token 加密存储
  - 账户关联/解绑、会话管理、活动审计日志
  - 管理后台 API 和与 ConfigCenter 的集成
- **新增 `taolib.rate_limiter` API 限流中间件**
  - 滑动窗口限流算法（Redis 后端）、FastAPI 中间件集成
  - 违规追踪和管理 API
- **新增 `taolib.task_queue` 后台任务队列**
  - Redis 队列存储、Worker 进程管理、任务优先级
  - FastAPI 管理服务器和 CLI 接口
- **新增 `taolib.site` 博客/CMS 平台**
  - FastAPI + SQLAlchemy 架构、Markdown 渲染、RSS/Atom Feed 生成
- **新增 `taolib.config_center` 完整实现**：企业级配置管理系统
  - 角色管理 CRUD API、审计日志查询 API、版本历史与回滚 API
  - 健康检查端点（真实 MongoDB/Redis 连接检查）
  - 完整的 RBAC 权限控制（5 个预定义角色）
  - Redis 缓存层（TTL 300s）与内存缓存实现
  - 可扩展配置验证框架（JSON Schema、正则、范围验证）
  - WebSocket 实时推送机制（心跳、消息缓冲、在线状态、PubSub 桥接）
  - 轻量级客户端 SDK（同步/异步获取配置）
- **数据同步模块增强**：新增 FastAPI 服务器和监控仪表板
- **pyproject.toml**：新增 13 个可选依赖组（analytics、file-storage、oauth、email-service、rate-limiter、site 等）
- **部署架构**：Podman Compose 编排重构，容器文件迁移到 `deploy/services/`
- **测试套件扩展**：新增 analytics、oauth、file_storage、email_service、task_queue 测试模块（25+ 测试文件）
- 新增 Ruff 配置到 `pyproject.toml`（linting + formatting）
- 新增 pytest 和 coverage 配置到 `pyproject.toml`
- **CI/CD 增强**：添加测试覆盖率阈值检查（>= 80%）
- **性能基准测试增强**：`perf_remote_bench.py` 新增功能正确性验证和历史性能对比

### Changed

- 统一测试框架文档：CLAUDE.md 和 AGENTS.md 测试命令统一使用 pytest
- Sphinx 版本约束从 `==8.2.3` 改为 `>=8.2.3`（灵活版本）
- `config_center.client` HTTP 错误处理增加详细日志记录
- `config_center.cache.config_cache` 优化：模块级导入，增加 JSON 解码错误处理
- `config_center.server.config` 迁移到 Pydantic v2 配置模式
- **架构优化**：`doc.py` 模块解耦重构
  - 将 `_make_project_namespace` 提取为模块级函数
  - 新增 `ProjectConfigValidator` 类
  - 新增配置验证异常（`ValueError`、`TypeError`）
- 文件存储服务依赖注入和 API 路由结构重构

### Fixed

- **安全修复**：修复 RBAC 权限检查中 `user_roles` 为空列表的问题
- **安全修复**：添加缺失的 `JWTError` 导入（`dependencies.py`）
- 修复 `config_center` 模块中 16 个 TODO 标记，全部实现为完整功能
- 移除 `.pre-commit-config.yaml` 中不兼容的 Poetry hook（项目使用 PDM）
- 修复 `auth.py` 中登录和刷新令牌时角色未加载的问题

### Removed

- 移除 `.pre-commit-config.yaml` 中的 Poetry hook

### Security

- `remote/ssh.toml` 示例配置移除明文密码，改为占位符
- RBAC 系统现在正确执行基于角色的权限检查
- OAuth Token 使用 `cryptography` 库加密存储
- 文件存储支持签名 URL 访问控制
