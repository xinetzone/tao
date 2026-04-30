# 项目经验总结

## 关键经验教训

### 类型标注最佳实践
- 在 Python 3.14 中，延迟注解已成为默认行为，不再需要 `from __future__ import annotations`
- 对于循环依赖的类型标注，使用字符串形式
- 对于类内部的方法返回类型标注，使用 `Self` 类型

### 测试环境配置
- 使用 `pytest.ini` 配置测试环境变量
- 为测试提供 mock 实现，避免依赖外部服务
- 确保测试数据库与生产数据库结构一致

### 依赖管理策略
- 使用 `pyproject.toml` 明确指定依赖版本范围
- 定期运行 `pip-audit` 检查安全漏洞
- 使用可选依赖组（extras）管理可选功能

## 成功案例分析

### 配置中心实时推送服务
- 基于 Redis PubSub 实现消息广播
- 使用 WebSocket 实现实时双向通信
- 实现 at-least-once 消息投递机制
- 支持 HTTP 轮询作为降级方案

### 数据同步管道优化
- 基于时间戳的增量同步策略
- 使用 Motor 的 `bulk_write` 批量加载
- 实现检查点恢复机制
- 支持自定义 Python 转换函数

## 常见问题解决方案

- **Python 2 遗留语法**：`except (ExceptionA, ExceptionB):`
- **pydantic-settings v2 配置语法**：使用 `model_config = SettingsConfigDict()`
- **Starlette TemplateResponse API 变更**：`TemplateResponse(request, name, context)`
- **Windows GBK 编码崩溃**：包装 `sys.stdout` 为 UTF-8 + `errors="replace"`
- **SQLAlchemy 2.0 废弃 API**：`db.get(Model, id)`
- **Redis Mock 数据结构**：扩展 `MockRedis` 支持 LIST、HASH、pipeline、scan 等命令
- **循环依赖类型标注**：使用字符串形式的类型标注

## 安全加固经验

- **密码哈希**：SHA-256 → bcrypt 迁移，支持存量用户无缝过渡
- **JWT 密钥验证**：配置验证器确保密钥长度 ≥ 32 字符
- **API 安全防护**：实现基于 IP 和用户的限流机制，使用 HTTPS 加密传输

## 最佳实践指南

- **代码组织**：模块化设计，清晰的目录结构，一致的命名规范
- **测试策略**：单元测试、集成测试、系统测试、端到端测试，测试覆盖率目标 ≥ 80%
- **文档管理**：使用 Google 风格的文档字符串，记录系统架构和设计决策
- **部署策略**：容器化，持续集成，环境分离，配置管理
- **性能优化**：数据库优化，缓存策略，异步处理，代码优化

## 项目里程碑总结

| 阶段 | 内容 | 状态 | 完成日期 |
|------|------|------|----------|
| Phase A | 安全修复（nul 清理、JWT 验证、bcrypt 迁移） | ✅ ${milestones.phase_a.status} | ${milestones.phase_a.date} |
| Phase B | Monorepo 基础设施（pnpm workspace、包重命名、QR 迁移） | ✅ ${milestones.phase_b.status} | ${milestones.phase_b.date} |
| Phase C | 共享前端包（@tao/shared、@tao/ui、@tao/api-client） | ✅ ${milestones.phase_c.status} | ${milestones.phase_c.date} |
| Phase D | 类型安全与质量提升（OpenAPI、测试、CI） | ✅ ${milestones.phase_d.status} | ${milestones.phase_d.date} |

## 参考链接

- [PyPI](${links.pypi})
- [文档](${links.documentation})
- [GitHub](${links.github})