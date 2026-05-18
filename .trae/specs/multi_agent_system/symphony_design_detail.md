# FlexLoop 编排子系统设计方案

FlexLoop 独立项目的编排子系统设计方案，参考 [SPEC.md](./SPEC.md) 规范。

---

## 1. 技术选型

### 1.1 编程语言：Python 3.14+

**理由：**
- `asyncio` 原生支持长期运行的异步守护进程，适合轮询+子进程编排场景
- 3.14 新特性带来性能和易用性提升（增量式 GC、asyncio 内省、t-string、PEP 758 等）
- 丰富的 YAML/GraphQL/HTTP 库生态，减少造轮子
- 与项目中 metaflow 技术栈一致，团队熟悉度高

### 1.2 核心依赖库

| 用途 | 库 | 理由 |
|------|------|------|
| 异步运行时 | `asyncio` (stdlib) | 标准库，零依赖；3.14 内省能力增强 |
| YAML 解析 | `PyYAML` | 解析 WORKFLOW.md 前置数据 |
| TOML 解析 | `tomllib` (stdlib) | 解析 symphony.toml 服务配置；3.11+ 标准库 |
| 模板引擎 | `Jinja2` (strict undefined) | 用户 WORKFLOW.md 模板；严格变量检查 |
| GraphQL 客户端 | `gql[httpx]` | 专业 GraphQL 客户端；查询 AST 校验；async 原生 |
| HTTP 服务器 | `uvicorn` + `FastAPI` | OPTIONAL HTTP 扩展（仪表板+JSON API） |
| 文件监视 | `watchdog` | 检测 WORKFLOW.md 变更，触发动态重载 |
| 进程管理 | `asyncio.subprocess` | 启动/管理 Codex app-server 子进程 |
| SSH 远程执行 | `asyncssh` | SSH Worker 扩展；原生 asyncio stdio 流 |
| 日志 | `structlog` | 结构化日志，支持 key=value 和 JSON 格式 |
| CLI | `typer` | 基于 type hints 的 CLI 框架；内置 Rich 美化 |
| 配置验证 | `pydantic>=2.0` | 类型化配置层，自动校验和默认值 |

### 1.3 Python 3.14 新特性应用

| PEP/特性 | 应用场景 | 说明 |
|----------|---------|------|
| PEP 750: t-string | 内部提示词构建、日志格式化、错误消息 | 用户 WORKFLOW.md 模板仍用 Jinja2 |
| PEP 758: except 无括号 | 全项目异常处理语法 | `except TransportError, TimeoutError as e:` |
| PEP 649/749: 迟延标注 | Pydantic 模型、类型定义 | 无需 `from __future__ import annotations` |
| asyncio 内省 | 可观测性/任务监控 | `asyncio.all_tasks()` 获取 worker 状态 |
| 增量式 GC | 长期运行守护进程 | 自动受益，减少延迟尖峰 |
| InterpreterPoolExecutor | 预留：大批量 JSON 解析 | 暂不使用，标记为未来优化点 |

### 1.4 数据存储方案

- **无持久化数据库**：本设计采用纯内存状态，重启通过跟踪器+文件系统恢复
- **内存状态**：Pydantic model + dataclass 持有 OrchestratorState
- **文件系统**：工作区目录 + 日志文件

### 1.5 网络通信协议

- **与 Linear API**：HTTPS + GraphQL（gql + httpx async transport）
- **与 Codex app-server**：stdio JSON 行协议（asyncio subprocess pipes / asyncssh）
- **OPTIONAL HTTP 服务器**：REST JSON API + 可选 HTML 仪表板

### 1.6 安全和认证机制

- `$VAR` 环境变量间接引用，不在日志中暴露密钥
- 工作区路径净化（`[A-Za-z0-9._-]`）+ 根目录包含检查
- 钩子超时强制执行，防止挂起
- Linear API key 通过 Authorization header 传递
- SSH 密钥认证（asyncssh，支持 agent forwarding）

---

## 2. 系统架构

### 2.1 整体架构（模块划分）

```
symphony/
├── __main__.py              # 入口点
├── cli.py                   # Typer CLI 定义
├── config/
│   ├── loader.py            # Workflow Loader（YAML前置数据+提示词分割）
│   ├── schema.py            # Pydantic 配置 Schema（类型化获取器）
│   ├── toml_config.py       # symphony.toml 解析
│   ├── resolver.py          # 双层配置合并+$VAR/~解析
│   └── watcher.py           # 文件监视+动态重载（仅 WORKFLOW.md）
├── tracker/
│   ├── base.py              # TrackerClient 抽象接口
│   ├── models.py            # 规范化 Issue 领域模型（Pydantic）
│   ├── errors.py            # LinearError 错误类型
│   └── linear/
│       ├── client.py        # LinearClient 主实现（gql）
│       ├── queries.py       # GraphQL 查询文档（gql() AST）
│       ├── normalize.py     # 响应 → Issue 规范化
│       └── transport.py     # httpx async transport 配置
├── orchestrator/
│   ├── state.py             # OrchestratorState 数据结构
│   ├── engine.py            # 轮询循环+分派+对账+重试
│   └── scheduler.py         # 候选排序+并发控制+槽位管理
├── workspace/
│   ├── manager.py           # 工作区创建/重用/清理
│   ├── hooks.py             # 钩子执行（超时控制）
│   └── security.py          # 路径净化+根包含验证
├── agent/
│   ├── runner.py            # Agent Runner（工作区+提示词+会话）
│   ├── appserver.py         # Codex app-server stdio 客户端
│   ├── events.py            # 事件解析+分类+令牌核算
│   ├── tools.py             # 客户端侧工具（linear_graphql）
│   └── transport.py         # AgentTransport 抽象（Local/SSH）
├── prompt/
│   ├── renderer.py          # Jinja2 严格模板渲染（用户模板）
│   └── internal.py          # t-string 内部模板（续运/默认提示词）
├── observability/
│   ├── logging.py           # structlog 配置
│   ├── metrics.py           # 令牌/运行时聚合
│   └── snapshot.py          # 运行时快照生成
├── server/                  # OPTIONAL HTTP 扩展
│   ├── app.py              # FastAPI 应用
│   ├── routes.py           # /api/v1/* 端点
│   └── dashboard.py        # / HTML 仪表板
└── errors.py                # 统一错误类别定义
```

### 2.2 核心组件详细设计

（完整设计内容见原始文件 - 此处省略以节约上下文，完整版本请在原 specs/symphony-design.md 中查阅）

### 2.3 数据流和控制流

### 2.4 并发和调度机制

### 2.5 错误处理和恢复策略

### 2.6 监控和可观测性设计

---

## 3. 关键设计决策

1. **单进程 asyncio**：本设计采用单一权威调度器串行化状态变更（参考 §7），asyncio 天然满足
2. **双层配置**：symphony.toml（服务级静态）+ WORKFLOW.md（工作流动态热重载）
3. **gql GraphQL 客户端**：查询定义时 AST 校验，异常层级清晰，原生 async
4. **Typer CLI**：type hints 驱动，零样板，内置 Rich 美化错误输出
5. **asyncssh SSH 扩展**：原生 asyncio stdio 流，与本地子进程接口对称
6. **Jinja2 + t-string 双模板**：用户模板用 Jinja2（参考 §12），内部模板用 t-string（3.14 新特性）
7. **AgentTransport 抽象**：统一 Local/SSH 执行接口，Agent Runner 不关心执行位置
8. **Pydantic v2 配置**：受益于 PEP 649 迟延标注，模块加载更快

---

## 4. 部署和运维考虑

- **打包**：`pyproject.toml` + `pip install -e .` → `symphony` CLI 命令
- **容器化**：Dockerfile 基于 `python:3.14-slim`，ENTRYPOINT 为 symphony CLI
- **信号处理**：SIGTERM/SIGINT 优雅关闭（停止新分派、等待活跃 worker、清理）
- **日志输出**：默认 stderr + 可配置文件接收器（symphony.toml [logging]）
- **健康检查**：HTTP `/api/v1/state` 端点（若启用 server）
- **symphony.toml 不热重载**：变更需重启；仅 WORKFLOW.md 支持运行时动态重载

---

## 5. 代码风格指南（3.14 新特性）

### 6. 实现路线图（建议顺序）

1. **基础框架**：Typer CLI + symphony.toml/WORKFLOW.md 配置加载 + structlog
2. **Linear 客户端**：gql 查询定义 + 分页 + 规范化 + 错误映射
3. **工作区管理**：路径净化 + 创建/清理 + 钩子执行（超时）
4. **调度器核心**：轮询循环 + 分派 + 对账 + 重试状态机
5. **Agent Runner**：app-server 子进程 + 流式事件 + 轮次循环
6. **提示词渲染**：Jinja2 严格模板（用户）+ t-string（内部续运）
7. **动态重载**：watchdog + 防抖 + 配置热应用
8. **SSH 扩展**：asyncssh AgentTransport + 主机调度
9. **HTTP 扩展**：FastAPI 仪表板 + JSON API
10. **linear_graphql 工具**：客户端侧工具扩展
11. **测试套件**：单元测试 + 集成测试 + 设计契约验证 + 快照测试（参考 Elixir status_dashboard_snapshot_test）
