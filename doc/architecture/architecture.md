# 架构说明

## `taolib.testing.doc` — 文档构建

通过 Invoke 的 `Collection` 封装 Sphinx 命令，提供 `sites()`、`multi_sites()` 和 `create_docs()` 等核心函数，支持单项目和多项目文档构建。

## `taolib.testing.remote` — 远程 SSH 探测

分层设计，包含 SSH 配置读取、连接管理、错误处理、探测命令执行等模块。核心功能是 `RemoteProber.probe()`，用于探测远程服务器的环境和状态。

## `taolib.testing.config_center` — 中心化配置管理

企业级配置管理系统，支持多环境统一配置管理，包含配置 CRUD、版本控制、缓存策略、事件推送、权限控制和配置验证等核心功能。

### 实时推送服务

高性能实时推送通知系统，基于 Redis PubSub 和 WebSocket，支持实时双向通信、HTTP 轮询回退、分布式多实例部署和 at-least-once 消息投递。

## `taolib.testing.data_sync` — MongoDB 数据同步管道

企业级 ETL 数据同步系统，支持从旧 MongoDB 实例同步数据到新实例，包含增量同步、自定义转换、检查点恢复和监控仪表板等功能。

## `taolib.testing.logging_config`

提供 `configure_logging()` 配置全局日志和 `get_logger(name)` 获取记录器功能。

## `taolib.testing.plot.configs` — Matplotlib 字体配置

解决 Matplotlib 中文文本渲染问题，通过 `configure_matplotlib_fonts()` 从指定目录加载自定义字体并设置为默认字体族。

## `taolib.testing.auth` — 统一认证授权

JWT + RBAC + API Key 认证系统，支持 Token 黑名单和 FastAPI 集成，提供双重认证、可插拔黑名单、通用 RBAC 和无状态设计等核心特性。

## `taolib.testing.analytics` — 用户行为分析

事件采集与聚合分析系统，包含零依赖 JavaScript SDK 和 FastAPI 后端，支持漏斗分析、会话追踪、导航路径分析和内置 HTML 仪表板。

## `taolib.testing.email_service` — 多提供商邮件服务

支持 SMTP/SendGrid/Mailgun/SES 四种提供商的邮件发送系统，具备自动故障转移、异步队列、模板引擎和退信处理等功能。

## `taolib.testing.file_storage` — 文件存储与 CDN

S3/本地双后端文件存储系统，支持分片上传、缩略图生成和 CDN 分发。

## `taolib.testing.oauth` — OAuth2 第三方登录

Google/GitHub OAuth2 授权码流程集成，支持 Token 加密存储和账户关联。

## `taolib.testing.rate_limiter` — API 限流中间件

基于滑动窗口算法的 API 限流系统，支持 TOML 配置和分布式部署。

## `taolib.testing.task_queue` — 后台任务队列

Redis 优先级队列 + Worker 池，支持自动重试和幂等执行。