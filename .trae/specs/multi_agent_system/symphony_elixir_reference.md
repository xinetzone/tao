# Symphony Elixir 实现经验萃取报告

> 本报告从 OpenAI 官方 Symphony Elixir 参考实现中萃取架构经验，为 FlexLoop Python 实现提供对照参考。

---

## 1. 架构概览

### 1.1 技术栈

| 层面 | Elixir 实现 | FlexLoop Python 对照 |
|------|------------|---------------------|
| 运行时 | Elixir ~1.19 / Erlang BEAM | Python 3.14+ / asyncio |
| 并发模型 | OTP GenServer + Task.Supervisor | asyncio 单线程事件循环 |
| Web 框架 | Phoenix 1.8 + LiveView | FastAPI + 可选 HTML |
| HTTP 服务器 | Bandit | uvicorn |
| GraphQL 客户端 | Req + 手动查询 | gql[httpx] |
| YAML 解析 | yaml_elixir | PyYAML |
| 模板引擎 | Solid（Liquid 兼容） | Jinja2 (strict) |
| CLI | escript + OptionParser | Typer |
| 配置验证 | 手动 Struct + 模式匹配 | Pydantic v2 |
| 日志 | Logger (stdlib) | structlog |
| SSH | 系统 ssh 命令 | asyncssh |

### 1.2 OTP 监督树

```
SymphonyElixir.Supervisor (one_for_one)
├── Phoenix.PubSub
├── Task.Supervisor          # Agent 任务管理
├── WorkflowStore (GenServer) # 配置热重载
├── Orchestrator (GenServer)  # 核心调度循环
├── HttpServer               # Phoenix/Bandit
└── StatusDashboard (GenServer)
```

**FlexLoop 对照**：Python 无原生监督树，使用 asyncio 任务 + 异常处理替代。Orchestrator 的 GenServer 状态机对应 `OrchestratorState` dataclass。

---

## 2. 核心组件对照
（完整对照详见原始文件，此处为摘要）

- Orchestrator：GenServer 状态机 → dataclass + asyncio 单线程
- AgentRunner：Task.Supervisor.start_child → asyncio.create_task
- Workspace：PathSafety.canonicalize → _assert_within_root
- 配置热重载：轮询 → watchdog 事件
- SSH 传输：系统 ssh → asyncssh
- CLI：OptionParser → Typer
- 模板引擎：Solid → Jinja2 + t-string

## 3. 可观测性经验

Elixir 实现的状态仪表板（59KB status_dashboard.ex）提供：
- 终端 ANSI 彩色状态表（实时刷新）
- Phoenix LiveView Web 仪表板
- JSON API（`/api/v1/state`, `/api/v1/<id>`, `/api/v1/refresh`）
- PubSub 事件通知

## 4. 测试经验

- 100% 覆盖率目标，但排除外部集成模块
- 快照测试验证仪表板输出格式
- 完整 Live E2E 测试框架（Docker + 真实 Codex）
- 暴露 `*_for_test` 函数便于单元测试

## 5. 设计差异总结

### Elixir 优势（Python 需补偿）
| Elixir 特性 | Python 补偿方案 |
|------------|---------------|
| OTP 监督树（自动重启） | asyncio 异常处理 + 外部进程管理器 |
| 热代码重载 | watchdog + 配置热重载（仅 WORKFLOW.md） |
| 轻量进程（百万级） | asyncio Task（万级足够） |

### Python 优势
| Python 特性 | Elixir 缺失 |
|------------|-----------|
| Pydantic 类型化配置（自动校验） | 手动 Struct + 模式匹配 |
| asyncssh 原生 SSH | 依赖系统 ssh 命令 |
| Jinja2 丰富模板生态 | Solid 功能有限 |

## 6. 可操作性建议

### 立即可借鉴
- 续运提示词风格（简洁结构化指导，非重复原始提示词）
- 钩子输出截断（2KB 限制）
- workspace equals root 安全检查
- token 核算的多路径容错逻辑
- 日志 key=value 结构化格式

### 建议增强
- 路径安全：增加符号链接解析
- CLI 安全确认：非限制模式下添加确认开关
- 依赖注入：CLI 命令接受可替换的依赖参数
- 快照测试：终端仪表板输出快照验证
