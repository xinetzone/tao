# AGENTS.md

本文档为在本代码仓库中工作的开发者提供使用指南。

## 项目概述

`taolib` 是一个 Python 库（Python >= 3.14），提供以下核心功能：
- **文档构建自动化**：基于 Sphinx 和 Invoke 的文档任务
- **远程 SSH 探测**：Conda 环境探测与远程命令执行
- **Matplotlib 字体配置**：中文文本渲染支持
- **中心化配置管理**：多环境配置管理、版本控制、审计日志和实时推送
- **MongoDB 数据同步**：ETL 管道、增量同步、自定义转换和定时调度
- **统一认证授权**：JWT + RBAC + API Key + Token 黑名单
- **用户行为分析**：事件采集、会话追踪、聚合分析
- **多提供商邮件服务**：SMTP/SendGrid/Mailgun/SES + 故障转移 + 模板引擎
- **文件存储与 CDN**：S3/本地存储 + CloudFront + 图片处理管道
- **OAuth2 第三方登录**：Google/GitHub + Token 加密 + 审计日志
- **API 限流中间件**：滑动窗口限流 + TOML 配置 + 违规追踪
- **后台任务队列**：Redis 优先级队列 + Worker 管理 + 重试策略
- **博客/CMS 平台**：FastAPI + SQLAlchemy + Markdown + RSS

核心设计理念：最小化核心依赖（`dependencies = []`），通过可选依赖组提供扩展功能。

## Python 环境

执行 Python 相关测试和代码运行时，默认使用路径为 `${PYTHON_ENV_DIR:-C:\Users\XMICUser\.conda\envs\py314}` 的 Python 环境（Python 3.14）。

### Python 3.14 新特性

- **PEP 649/PEP 749**：标注延迟求值，提高性能并简化前向引用
- **PEP 734**：标准库中的多解释器支持（`concurrent.interpreters` 模块）
- **PEP 750**：模板字符串字面值
- **PEP 758**：允许不带圆括号的 except 和 except* 表达式
- **PEP 765**：finally 代码块中的控制流
- **PEP 784**：标准库中的 Zstandard 支持（`compression.zstd` 模块）

## 常用命令

```bash
# 安装（开发模式）
pip install -e ".[dev,doc,test]"

# 运行所有测试
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_remote_interfaces.py -v

# 按名称模式运行测试
python -m pytest tests/ -k "test_probe" -v

# 带覆盖率
coverage run -m pytest tests/ && coverage report

# 性能基准测试
python tests/perf_remote_bench.py

# Lint/格式化
pre-commit run --all-files

# 构建文档
python -m invoke doc          # 默认 HTML
python -m invoke doc.build --nitpick   # 严格模式
python -m invoke doc.clean    # 清理输出
python -m invoke doc.build --language en  # 指定语言

# 打包
python -m build
```

## 架构说明

### `taolib.doc` — 文档构建

通过 Invoke 的 `Collection` 封装 Sphinx 命令，提供 `sites()`、`multi_sites()` 和 `create_docs()` 等核心函数，支持单项目和多项目文档构建。

### `taolib.remote` — 远程 SSH 探测

分层设计，包含 SSH 配置读取、连接管理、错误处理、探测命令执行等模块。核心功能是 `RemoteProber.probe()`，用于探测远程服务器的环境和状态。

### `taolib.config_center` — 中心化配置管理

企业级配置管理系统，支持多环境统一配置管理，包含配置 CRUD、版本控制、缓存策略、事件推送、权限控制和配置验证等核心功能。

#### 实时推送服务

高性能实时推送通知系统，基于 Redis PubSub 和 WebSocket，支持实时双向通信、HTTP 轮询回退、分布式多实例部署和 at-least-once 消息投递。

### `taolib.data_sync` — MongoDB 数据同步管道

企业级 ETL 数据同步系统，支持从旧 MongoDB 实例同步数据到新实例，包含增量同步、自定义转换、检查点恢复和监控仪表板等功能。

### `taolib.logging_config`

提供 `configure_logging()` 配置全局日志和 `get_logger(name)` 获取记录器功能。

### `taolib.plot.configs` — Matplotlib 字体配置

解决 Matplotlib 中文文本渲染问题，通过 `configure_matplotlib_fonts()` 从指定目录加载自定义字体并设置为默认字体族。

### `taolib.auth` — 统一认证授权

JWT + RBAC + API Key 认证系统，支持 Token 黑名单和 FastAPI 集成，提供双重认证、可插拔黑名单、通用 RBAC 和无状态设计等核心特性。

### `taolib.analytics` — 用户行为分析

事件采集与聚合分析系统，包含零依赖 JavaScript SDK 和 FastAPI 后端，支持漏斗分析、会话追踪、导航路径分析和内置 HTML 仪表板。

### `taolib.email_service` — 多提供商邮件服务

支持 SMTP/SendGrid/Mailgun/SES 四种提供商的邮件发送系统，具备自动故障转移、异步队列、模板引擎和退信处理等功能。

### `taolib.file_storage` — 文件存储与 CDN

S3/本地双后端文件存储系统，支持分片上传、缩略图生成和 CDN 分发。

### `taolib.oauth` — OAuth2 第三方登录

Google/GitHub OAuth2 授权码流程集成，支持 Token 加密存储和账户关联。

### `taolib.rate_limiter` — API 限流中间件

基于滑动窗口算法的 API 限流系统，支持 TOML 配置和分布式部署。

### `taolib.task_queue` — 后台任务队列

Redis 优先级队列 + Worker 池，支持自动重试和幂等执行。

### `taolib.site` — 博客/CMS 平台

FastAPI + SQLAlchemy 构建的博客/CMS 系统，支持 Markdown 内容和 RSS 订阅。

## 模块导出

### `taolib.remote` 导出项

| 导出名称 | 类型 | 说明 |
|----------|------|------|
| `SshConfig` | 类 | SSH 配置数据类 |
| `load_ssh_config()` | 函数 | 加载 SSH 配置（带缓存） |
| `redact_ssh_config()` | 函数 | SSH 配置脱敏 |
| `RemoteProbeCommands` | 类 | 远程探测命令配置 |
| `RemoteProbeReport` | 类 | 探测结果报告 |
| `RemoteProbeRunOptions` | 类 | 探测运行选项 |
| `RemoteProber` | 类 | 远程探测器类 |
| `probe_remote()` | 函数 | 远程探测入口函数 |
| `remote_prefixes()` | 函数 | 命令前缀上下文管理器 |
| `RemoteConfigError` | 异常 | 配置错误 |
| `RemoteDependencyError` | 异常 | 依赖错误 |
| `RemoteExecutionError` | 异常 | 执行错误 |
| `DEFAULT_*` | 常量 | 默认命令和编码常量 |

### `taolib.plot.configs` 导出项

| 导出名称 | 类型 | 说明 |
|----------|------|------|
| `configure_matplotlib_fonts()` | 函数 | 配置 Matplotlib 中文字体 |

## 文档整合原则

### 1. 单一真实来源 (SSOT) 原则
- `src/taolib/_base/cache_keys.py` 文件作为所有 Redis 键命名规范的唯一权威来源
- 所有 Redis 键的定义、格式、用途说明必须在此文件中维护
- 其他任何地方不得重复定义相同的键名，只能引用此文件

### 2. 交叉引用机制
- 功能规格文档与架构文档之间建立明确的引用关联
- 规格文档中的技术细节应链接到架构文档中的相应实现说明

### 3. 避免重复原则
- **Phase 进度信息**仅在本文档中进行维护和更新
- 其他文档如需展示进度信息，必须通过引用或链接方式指向本文档

## 编码规范

- **类型注解**：所有公开 API 必须有类型提示，使用 Python 3.14 的延迟注解机制
- **前向引用**：标注中包含前向引用时不再需要将其包裹在字符串中
- **文档字符串**：Google 风格（sphinx.ext.napoleon 解析）
- **Lint**：ruff（格式化 + linting），通过 pre-commit 执行
- **编码**：UTF-8，LF 换行（见 `.editorconfig`）
- **测试覆盖率目标**：≥ 80%

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TAOLIB_REMOTE_TOOLS_ENV_CMD` | `:` | 工具环境命令 |
| `TAOLIB_REMOTE_CONDA_ACTIVATE_CMD` | `:` | Conda 激活命令 |
| `TAOLIB_REMOTE_PROBE_CMD` | `python -V` | 探测命令 |
| `TAOLIB_REMOTE_ENCODING` | `utf-8` | 远程输出编码 |
| `TAOLIB_VERSION` | `0.0.0` | 未安装时的版本回退 |
| `SITEMAP_URL_BASE` | - | 站点地图基础 URL（CI/本地设置） |

## 经验教训与最佳实践

### 使用 `typing.Self` 替代 `TypeVar` 进行自引用类型注解

`typing.Self`（Python 3.11+ 引入，PEP 673）用于表示"当前类的实例类型"，是对旧式 `TypeVar` 自引用模式的简洁替代。在方法返回 `self` 或通过 `classmethod` 返回当前类实例时，应优先使用 `Self`。

**适用场景**：
- 链式调用 (Builder/Fluent 模式)
- 工厂方法 / classmethod
- 上下文管理器 `__enter__`
- 子类继承中的类型精确推断

## 参考链接

- [PyPI](${links.pypi})
- [文档](${links.documentation})
- [GitHub](${links.github})

## 项目开发经验总结

### 关键经验教训

#### 类型标注最佳实践
- 在 Python 3.14 中，延迟注解已成为默认行为，不再需要 `from __future__ import annotations`
- 对于循环依赖的类型标注，使用字符串形式
- 对于类内部的方法返回类型标注，使用 `Self` 类型

#### 测试环境配置
- 使用 `pytest.ini` 配置测试环境变量
- 为测试提供 mock 实现，避免依赖外部服务
- 确保测试数据库与生产数据库结构一致

#### 依赖管理策略
- 使用 `pyproject.toml` 明确指定依赖版本范围
- 定期运行 `pip-audit` 检查安全漏洞
- 使用可选依赖组（extras）管理可选功能

### 成功案例分析

#### 配置中心实时推送服务
- 基于 Redis PubSub 实现消息广播
- 使用 WebSocket 实现实时双向通信
- 实现 at-least-once 消息投递机制
- 支持 HTTP 轮询作为降级方案

#### 数据同步管道优化
- 基于时间戳的增量同步策略
- 使用 Motor 的 `bulk_write` 批量加载
- 实现检查点恢复机制
- 支持自定义 Python 转换函数

### 常见问题解决方案

- **Python 2 遗留语法**：`except (ExceptionA, ExceptionB):`
- **pydantic-settings v2 配置语法**：使用 `model_config = SettingsConfigDict()`
- **Starlette TemplateResponse API 变更**：`TemplateResponse(request, name, context)`
- **Windows GBK 编码崩溃**：包装 `sys.stdout` 为 UTF-8 + `errors="replace"`
- **SQLAlchemy 2.0 废弃 API**：`db.get(Model, id)`
- **Redis Mock 数据结构**：扩展 `MockRedis` 支持 LIST、HASH、pipeline、scan 等命令
- **循环依赖类型标注**：使用字符串形式的类型标注

### 安全加固经验

- **密码哈希**：SHA-256 → bcrypt 迁移，支持存量用户无缝过渡
- **JWT 密钥验证**：配置验证器确保密钥长度 ≥ 32 字符
- **API 安全防护**：实现基于 IP 和用户的限流机制，使用 HTTPS 加密传输

### 最佳实践指南

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

## Qoder 规范

### Python 环境
执行 Python 测试和代码运行时，默认使用 `${PYTHON_ENV_DIR:-C:\Users\XMICUser\.conda\envs\py314}` 环境。

### 记忆管理
- **禁止重复存储**：`AGENTS.md`、`.qoder/rules/*.md`、`pyproject.toml` 每次会话自动加载为上下文，不得复制为记忆
- **创建前搜索**：使用 `search_memory` 确认无重复或需更新的记忆
- **合并优先**：找到相关内容优先 `update` 而非新建
- **一主题一条**：同一主题选最匹配单一类别存储
- **同步演进**：项目重大变化时更新已有记忆，而非保留过时内容