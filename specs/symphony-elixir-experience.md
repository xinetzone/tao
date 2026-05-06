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

### 2.1 Orchestrator 编排器

| 特性 | Elixir 实现 | FlexLoop 设计 | 差异要点 |
|------|------------|--------------|---------|
| 状态管理 | GenServer State defstruct | dataclass OrchestratorState | Elixir 通过消息传递串行化；Python 依赖 asyncio 单线程 |
| 轮询调度 | `Process.send_after` 定时器 + tick_token 防重入 | `asyncio.sleep` + tick 循环 | Elixir 使用 monotonic token 防止过期 tick 干扰 |
| Worker 监控 | `Process.monitor` + `:DOWN` 消息 | `asyncio.Task` + `add_done_callback` | 概念对称，Elixir 的 :DOWN 包含退出原因 |
| 重试机制 | `Process.send_after` + retry_token | `asyncio.call_later` + RetryEntry | 两者都用 token/ref 防止过期重试 |
| 对账 | `reconcile_running_issues` 每次 tick 执行 | `_reconcile_running_issues` 每次 tick | 逻辑一致 |

**关键经验**：

1. **tick_token 防重入模式**：Elixir 用 `make_ref()` 生成 tick_token，`handle_info({:tick, tick_token})` 仅在 token 匹配时处理。Python 实现中 asyncio 的 `asyncio.sleep` 天然串行，无需此机制，但应考虑 `request_refresh` 场景下的防重入。

2. **两阶段轮询**：Elixir 将 tick 分为 `{:tick, _}` 和 `:run_poll_cycle` 两阶段，中间有 `@poll_transition_render_delay_ms`（20ms）延迟让仪表板渲染 "checking now…" 状态。Python 实现可简化为单阶段。

3. **Worker 退出处理**：Elixir 的 `:DOWN` 消息携带退出原因（`:normal` / 异常），直接区分正常完成和异常退出。Python 的 `add_done_callback` 需要从 Task 结果中提取异常。

### 2.2 AgentRunner 智能体运行器

| 特性 | Elixir 实现 | FlexLoop 设计 |
|------|------------|--------------|
| 执行方式 | Task.Supervisor.start_child | asyncio.create_task |
| Codex 通信 | AppServer stdio JSON 协议 | AppServerClient stdio JSON 协议 |
| 轮次控制 | 递归 do_run_codex_turns | while True 循环 |
| 续运提示词 | 固定多行文本模板 | t-string 构建 |
| 事件上报 | `send(recipient, {:codex_worker_update, ...})` | `on_event` 回调 |

**关键经验**：

1. **续运提示词简洁原则**：Elixir 的续运提示词是一段简短的结构化指导（而非重复完整原始提示词），包含：当前轮次/总轮次、继续工作建议、不重述已有上下文。Python 设计中的 t-string 续运模板应参考此风格。

2. **Worker 运行时信息上报**：Elixir 通过 `send_worker_runtime_info` 主动上报 worker_host 和 workspace_path，而非等编排器查询。Python 实现可在 AgentRunner 中通过 on_event 回调上报。

3. **before_run/after_run 钩子语义**：Elixir 在 try/after 块中执行，after_run 无论是否异常都执行（best effort）。Python 设计中应使用 try/finally 确保同样语义。

### 2.3 Workspace 工作区管理

| 特性 | Elixir 实现 | FlexLoop 设计 |
|------|------------|--------------|
| 路径净化 | `String.replace(~r/[^a-zA-Z0-9._-]/, "_")` | `re.sub(r'[^A-Za-z0-9._-]', '_', identifier)` |
| 路径安全 | PathSafety.canonicalize（逐段解析符号链接） | `_assert_within_root` 前缀检查 |
| SSH 执行 | 系统 ssh 命令 + shell 脚本 | asyncssh 原生 |
| 钩子超时 | `Task.yield(task, timeout_ms)` + `Task.shutdown(task, :brutal_kill)` | asyncio.wait_for + timeout |
| 远程工作区标记 | `__SYMPHONY_WORKSPACE__` 制表符分隔输出 | 未定义 |

**关键经验**：

1. **路径安全纵深**：Elixir 的 `PathSafety.canonicalize` 逐段解析符号链接，比 Python 的 `resolve()` + 前缀检查更安全。**建议 FlexLoop 增强**：添加符号链接解析，防止通过符号链接逃逸工作区根目录。

2. **远程工作区协议**：Elixir 通过 `__SYMPHONY_WORKSPACE__` 标记 + 制表符分隔输出（created\tpath）实现远程工作区创建的可靠性确认。Python 的 asyncssh 实现可参考此协议。

3. **钩子输出截断**：Elixir 的 `sanitize_hook_output_for_log` 限制 2KB 日志输出，防止钩子输出淹没日志。Python 实现应增加类似截断。

4. **workspace equals root 检查**：Elixir 明确检查 `workspace == root` 并拒绝，防止误删根目录。Python 实现应补充此检查。

### 2.4 配置热重载

| 特性 | Elixir 实现 | FlexLoop 设计 |
|------|------------|--------------|
| 文件监视 | 轮询（1s）+ mtime/size/hash stamp | watchdog 文件事件 |
| 失败策略 | 保留最后有效配置 + 日志告警 | 同 |
| 重载触发 | WorkflowStore GenServer 缓存 | Config.watcher |

**关键经验**：

1. **轮询 vs 事件**：Elixir 选择 1 秒轮询（mtime + size + content hash 三元组），而非文件系统事件。理由是跨平台兼容性和简单性。FlexLoop 的 watchdog 方案更高效，但需注意跨平台兼容。

2. **stamp 计算**：Elixir 使用 `{mtime, size, erlang.phash2(content)}` 三元组作为文件指纹，避免仅靠 mtime 的精度问题。Python 实现若用 watchdog，也应考虑内容哈希校验。

### 2.5 SSH 传输

| 特性 | Elixir 实现 | FlexLoop 设计 |
|------|------------|--------------|
| 方式 | 系统 ssh 命令 | asyncssh 库 |
| 命令构造 | `ssh -T host bash -lc 'command'` | asyncssh.create_process |
| Shell 转义 | 单引号包裹 + `'\"'\"'` 转义 | shlex.quote |
| Host:Port 解析 | 正则解析 + IPv6 支持 | asyncssh 内置 |
| 配置文件 | SYMPHONY_SSH_CONFIG 环境变量 | 未定义 |

**关键经验**：

1. **系统 ssh vs 库**：Elixir 选择系统 ssh 命令（依赖外部二进制），Python 选择 asyncssh（纯 Python）。asyncssh 更可靠，但需注意 SSH agent forwarding 支持。

2. **Shell 转义一致性**：Elixir 的 `shell_escape` 和 Python 的 `shlex.quote` 实现相同语义（单引号包裹），但 Elixir 额外处理了远程 ~ 展开（`remote_shell_assign`）。Python 的 asyncssh 不需要此处理，因为工作目录通过 API 设置。

### 2.6 CLI 接口

| 特性 | Elixir 实现 | FlexLoop 设计 |
|------|------------|--------------|
| 框架 | OptionParser (stdlib) | Typer |
| 打包 | escript 单文件可执行 | pip install / Docker |
| 安全确认 | `--i-understand-that-this-will-be-running-without-the-usual-guardrails` | 未定义 |
| 进程等待 | `Process.monitor(Supervisor)` 等待关闭 | 信号处理 |

**关键经验**：

1. **安全确认开关**：Elixir 要求用户显式确认无防护运行，这是一个重要的安全实践。**建议 FlexLoop 考虑**：在 codex.approval_policy 为非限制模式时，添加类似的确认机制。

2. **依赖注入**：Elixir CLI 的 `evaluate/2` 接受 `deps` 参数（函数字典），便于测试时替换文件系统/应用启动。Python 的 Typer + dependency injection 可参考此模式。

### 2.7 模板引擎

| 特性 | Elixir 实现 | FlexLoop 设计 |
|------|------------|--------------|
| 用户模板 | Solid（Liquid 兼容）+ strict | Jinja2 StrictUndefined |
| 语法 | `{{ issue.identifier }}` / `{% if ... %}` | `{{ issue.identifier }}` / `{% if ... %}` |
| 内部模板 | 硬编码多行字符串 | t-string (PEP 750) |

**关键经验**：

1. **Liquid vs Jinja2**：语法高度相似，迁移成本低。Solid 的 `strict_variables: true, strict_filters: true` 对应 Jinja2 的 `StrictUndefined`。

2. **DateTime 序列化**：Elixir 在 `to_solid_map` 中将 DateTime/Date/Time 统一转为 ISO 8601 字符串。Python 的 Jinja2 渲染时也需确保 Pydantic model 的日期字段被正确序列化。

---

## 3. 可观测性经验

### 3.1 状态仪表板

Elixir 实现了一个 59KB 的 `status_dashboard.ex`，提供：
- 终端 ANSI 彩色状态表（实时刷新）
- Phoenix LiveView Web 仪表板
- JSON API（`/api/v1/state`, `/api/v1/<id>`, `/api/v1/refresh`）
- PubSub 事件通知

**FlexLoop 可参考**：
- 终端仪表板用 Rich Live 实现（而非 ANSI 转义）
- JSON API 端点设计保持一致
- Web 仪表板可后期扩展

### 3.2 日志规范

Elixir 的日志模式：
```
Logger.info("Dispatching issue to agent: #{issue_context(issue)} pid=#{inspect(pid)} attempt=#{inspect(attempt)} worker_host=#{worker_host || "local"}")
```

**统一为 key=value 结构化格式**，与 FlexLoop 的 structlog 风格一致。

### 3.3 Token 核算

Elixir 的 token 增量核算逻辑非常健壮（`extract_token_delta` / `compute_token_delta`）：
- 支持多种 JSON 路径格式（snake_case / camelCase / 嵌套路径）
- 增量计算：`delta = max(next_reported - prev_reported, 0)`
- 容错：非整数值回退为 0

**建议 FlexLoop 的 Python 实现**：参考此健壮性，特别是 Codex 事件中 token 使用量字段的多样性（不同版本的 app-server 可能使用不同的字段名）。

---

## 4. 测试经验

### 4.1 测试覆盖策略

Elixir 在 `mix.exs` 中设置了 `threshold: 100`（100% 覆盖率目标），但通过 `ignore_modules` 排除了与外部系统交互的模块：
- `Linear.Client`（网络调用）
- `Orchestrator`（进程管理）
- `AgentRunner`（Codex 集成）
- `CLI`（IO 操作）

**FlexLoop 参考**：单元测试覆盖率目标可设为高阈值，但排除外部集成模块，转用集成测试覆盖。

### 4.2 快照测试

Elixir 使用 `status_dashboard_snapshot_test.exs` + `fixtures/status_dashboard_snapshots/` 进行快照测试，确保仪表板输出格式不变。

**FlexLoop 参考**：若实现终端仪表板，可使用类似的快照测试方法。

### 4.3 Live E2E 测试

Elixir 提供了完整的 Live E2E 测试框架：
- Docker Compose 启动临时 SSH Worker
- 创建临时 Linear 项目和 Issue
- 运行真实 Codex 会话
- 验证工作区副作用

**FlexLoop 参考**：E2E 测试可作为可选的 CI 阶段，不在常规 PR 测试中运行。

### 4.4 测试辅助函数

Orchestrator 暴露了多个 `*_for_test` 函数：
- `reconcile_issue_states_for_test/2`
- `should_dispatch_issue_for_test/2`
- `sort_issues_for_dispatch_for_test/1`
- `select_worker_host_for_test/2`

**FlexLoop 参考**：在 Orchestrator 类中设计可测试的公共方法，避免为测试暴露过多内部状态。

---

## 5. 设计差异总结

### 5.1 Elixir 优势（Python 需补偿）

| Elixir 特性 | Python 补偿方案 |
|------------|---------------|
| OTP 监督树（自动重启） | asyncio 异常处理 + 外部进程管理器 |
| 热代码重载 | watchdog + 配置热重载（仅 WORKFLOW.md） |
| 轻量进程（百万级） | asyncio Task（万级足够） |
| 消息传递天然串行化 | asyncio 单线程事件循环 |
| Process.monitor 原生支持 | asyncio.Task + done_callback |

### 5.2 Python 优势

| Python 特性 | Elixir 缺失 |
|------------|-----------|
| Pydantic 类型化配置（自动校验） | 手动 Struct + 模式匹配 |
| asyncssh 原生 SSH | 依赖系统 ssh 命令 |
| Jinja2 丰富模板生态 | Solid 功能有限 |
| Typer 自动 CLI 文档 | OptionParser 手动 usage |
| t-string (PEP 750) 类型安全模板 | 硬编码字符串 |

### 5.3 需特别注意的移植点

1. **GenServer 状态机 → asyncio 协程**：Elixir 的 GenServer 是响应式消息处理，Python 的 asyncio 是过程式循环。需要确保 tick 循环中所有状态变更在单次 tick 内完成，避免竞态。

2. **Task.Supervisor → asyncio.create_task**：Elixir 的 Task.Supervisor 提供自动清理和重启，Python 需手动管理任务生命周期。

3. **Process.monitor :DOWN → Task done_callback**：Elixir 的 :DOWN 消息包含退出原因（:normal / 异常），Python 的 done_callback 需从 Task.result() 提取。

4. **WorkflowStore 轮询 → watchdog 事件**：Elixir 用 1s 轮询实现配置热重载，Python 用 watchdog 更高效，但需注意防抖。

5. **SSH 命令构造**：Elixir 依赖系统 ssh，Python 用 asyncssh。远程工作区的 shell 脚本需要从 `ssh -T host bash -lc 'script'` 适配为 asyncssh 的 `create_process`。

---

## 6. 可操作性建议

### 6.1 立即可借鉴

- [x] 续运提示词风格（简洁结构化指导，非重复原始提示词）
- [x] 钩子输出截断（2KB 限制）
- [x] workspace equals root 安全检查
- [x] token 核算的多路径容错逻辑
- [x] 日志 key=value 结构化格式

### 6.2 建议增强

- [x] 路径安全：增加符号链接解析（参考 PathSafety.canonicalize）→ 已落实至 symphony-design.md Workspace Manager
- [x] CLI 安全确认：非限制模式下添加确认开关 → 已落实至 symphony-design.md CLI 接口
- [x] 依赖注入：CLI 命令接受可替换的依赖参数，便于测试 → 已落实至 symphony-design.md CLIDeps
- [x] 快照测试：终端仪表板输出快照验证 → 已落实至 symphony-design.md 测试路线图

### 6.3 后期考虑

- [ ] Live E2E 测试框架（Docker + 真实 Codex）
- [ ] Phoenix LiveView 级别的 Web 仪表板
- [ ] OTP 监督树级别的高可用（需外部进程管理器）
