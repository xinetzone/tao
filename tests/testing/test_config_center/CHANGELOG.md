# Config Center 配置中心模块 - 更新日志

本文件记录 Config Center 模块的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

### 新增

- **配置中心完整实现**：企业级配置管理系统
  - 角色管理 CRUD API、审计日志查询 API、版本历史与回滚 API
  - 健康检查端点（真实 MongoDB/Redis 连接检查）
  - 完整的 RBAC 权限控制（5 个预定义角色）
  - Redis 缓存层（TTL 300s）与内存缓存实现
  - 可扩展配置验证框架（JSON Schema、正则、范围验证）
  - WebSocket 实时推送机制（心跳、消息缓冲、在线状态、PubSub 桥接）
  - 轻量级客户端 SDK（同步/异步获取配置）

### 修改

- `taolib.testing.config_center.client` HTTP 错误处理增加详细日志记录
- `taolib.testing.config_center.cache.config_cache` 优化：模块级导入，增加 JSON 解码错误处理
- `taolib.testing.config_center.server.config` 迁移到 Pydantic v2 配置模式

### 修复

- 修复 `taolib.testing.config_center` 模块中 16 个 TODO 标记，全部实现为完整功能
