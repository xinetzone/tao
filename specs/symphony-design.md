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

#### A. CLI 接口 (`cli.py`)

基于 Typer，函数签名即命令定义：

```python
import typer
from pathlib import Path
from typing import Any, Callable

app = typer.Typer(name="symphony", help="Symphony orchestration service")

# 依赖注入：可替换的运行时依赖（便于测试）
class CLIDeps:
    """可替换的运行时依赖（参考 Elixir CLI deps 模式）"""
    file_exists: Callable[[Path], bool] = lambda p: p.is_file()
    set_workflow_path: Callable[[Path], None] = ...
    set_logs_root: Callable[[Path], None] = ...
    set_server_port: Callable[[int | None], None] = ...
    ensure_started: Callable[[], Any] = ...

_default_deps = CLIDeps()

@app.command()
def run(
    workflow: Path = typer.Argument(
        Path("./WORKFLOW.md"),
        help="Path to WORKFLOW.md",
    ),
    port: int | None = typer.Option(None, help="Enable HTTP server on this port"),
    logs_root: Path = typer.Option(Path("./log"), help="Log output directory"),
    config: Path | None = typer.Option(None, help="Path to symphony.toml"),
    accept_risks: bool = typer.Option(False,
        "--accept-risks",
        help="Acknowledge that Codex will run without the usual guardrails",
    ),
    deps: CLIDeps = typer.Option(None, hidden=True),  # 测试注入点
):
    """Start the Symphony orchestration service."""
    deps = deps or _default_deps

    # 安全确认：非限制模式需显式确认（参考 Elixir acknowledgement 开关）
    if not accept_risks:
        codex_policy = ...  # 从配置读取 approval_policy
        if codex_policy in ("never", "on-failure"):
            typer.echo(
                "WARNING: Codex will run with minimal guardrails.\n"
                "To proceed, start with --accept-risks",
                err=True,
            )
            raise typer.Exit(code=1)

    # 验证 workflow 文件存在
    if not deps.file_exists(workflow):
        typer.echo(f"Error: workflow file not found: {workflow}", err=True)
        raise typer.Exit(code=1)
    # 启动服务...
```

#### B. Workflow Loader (`config/loader.py`)

```python
@dataclass(frozen=True)
class WorkflowDefinition:
    config: dict          # YAML 前置数据根对象
    prompt_template: str  # 去除首尾空白的 Markdown 正文

def load_workflow(path: Path) -> WorkflowDefinition:
    """
    解析规则（§5.2）：
    1. 文件以 --- 开头 → 解析直到下一个 --- 之间为 YAML 前置数据
    2. 剩余行为 prompt_template（strip）
    3. 无前置数据 → config={}, 全文为 prompt_template
    4. YAML 必须解码为映射，否则报 workflow_front_matter_not_a_map
    """
```

#### C. Config Layer — 双层配置架构

**层级关系（优先级高→低）：**
```
CLI 参数 > 环境变量 $VAR > WORKFLOW.md YAML > symphony.toml [defaults] > 内置默认值
```

**symphony.toml 示例：**
```toml
[server]
port = 4000
bind = "127.0.0.1"

[logging]
level = "info"
format = "json"
output = "stderr"
file_path = "./log/symphony.log"

[logging.codex_sessions]
enabled = true
root = "./log/codex"

[defaults.polling]
interval_ms = 30000

[defaults.workspace]
root = "~/symphony_workspaces"

[defaults.agent]
max_concurrent_agents = 10
max_turns = 20
max_retry_backoff_ms = 300000

[defaults.codex]
command = "codex app-server"
turn_timeout_ms = 3600000
stall_timeout_ms = 300000
```

**Pydantic 配置 Schema (`config/schema.py`)：**

```python
class TrackerConfig(BaseModel):
    kind: Literal["linear"]
    endpoint: str = "https://api.linear.app/graphql"
    api_key: str                    # 支持 $VAR 解析
    project_slug: str
    active_states: list[str] = ["Todo", "In Progress"]
    terminal_states: list[str] = ["Closed", "Cancelled", "Canceled", "Duplicate", "Done"]

class PollingConfig(BaseModel):
    interval_ms: int = 30000

class WorkspaceConfig(BaseModel):
    root: str                       # 支持 ~ 和 $VAR 展开

class HooksConfig(BaseModel):
    after_create: str | None = None
    before_run: str | None = None
    after_run: str | None = None
    before_remove: str | None = None
    timeout_ms: int = 60000

class AgentConfig(BaseModel):
    max_concurrent_agents: int = 10
    max_turns: PositiveInt = 20
    max_retry_backoff_ms: int = 300000
    max_concurrent_agents_by_state: dict[str, int] = {}

class CodexConfig(BaseModel):
    command: str = "codex app-server"
    approval_policy: Any = None     # 透传 Codex
    thread_sandbox: Any = None      # 透传 Codex
    turn_sandbox_policy: Any = None # 透传 Codex
    turn_timeout_ms: int = 3600000
    read_timeout_ms: int = 5000
    stall_timeout_ms: int = 300000

class WorkerConfig(BaseModel):      # SSH 扩展（§附录A）
    ssh_hosts: list[str] = []
    max_concurrent_agents_per_host: int | None = None

class ServerConfig(BaseModel):
    port: int | None = None
    bind: str = "127.0.0.1"

class SymphonyConfig(BaseModel):
    tracker: TrackerConfig
    polling: PollingConfig = PollingConfig()
    workspace: WorkspaceConfig
    hooks: HooksConfig = HooksConfig()
    agent: AgentConfig = AgentConfig()
    codex: CodexConfig = CodexConfig()
    worker: WorkerConfig = WorkerConfig()
    server: ServerConfig = ServerConfig()
```

**配置合并逻辑 (`config/resolver.py`)：**

```python
import tomllib

def resolve_config(cli_args, toml_path: Path | None, workflow_path: Path) -> SymphonyConfig:
    # 1. 内置默认值（Pydantic model defaults）
    base = {}

    # 2. 加载 symphony.toml [defaults] 段
    if toml_path and toml_path.exists():
        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)
        base = deep_merge(base, toml_data.get("defaults", {}))

    # 3. 加载 WORKFLOW.md YAML 前置数据（权威来源）
    workflow = load_workflow(workflow_path)
    base = deep_merge(base, workflow.config)

    # 4. 解析 $VAR 间接引用
    base = resolve_env_vars(base)

    # 5. ~ 路径展开 + 相对路径解析
    base = resolve_paths(base, workflow_path.parent)

    # 6. CLI 参数覆盖
    if cli_args.port is not None:
        base.setdefault("server", {})["port"] = cli_args.port

    # 7. Pydantic 验证
    return SymphonyConfig.model_validate(base)
```

#### D. Issue Tracker Client (`tracker/linear/`)

基于 gql 库实现：

```python
from gql import gql, Client
from gql.transport.httpx import HTTPXAsyncTransport

# 查询文档定义（queries.py）
FETCH_CANDIDATES = gql("""
    query FetchCandidates($projectSlug: String!, $states: [String!]!, $after: String) {
        issues(
            filter: {
                project: { slugId: { eq: $projectSlug } }
                state: { name: { in: $states } }
            }
            first: 50
            after: $after
            orderBy: createdAt
        ) {
            pageInfo { hasNextPage endCursor }
            nodes {
                id identifier title description priority url
                createdAt updatedAt branchName
                state { name }
                labels { nodes { name } }
                relations(type: "blocks") {
                    nodes { relatedIssue { id identifier state { name } } }
                }
            }
        }
    }
""")

FETCH_STATES_BY_IDS = gql("""
    query FetchStatesByIds($ids: [ID!]!) {
        nodes(ids: $ids) {
            ... on Issue { id identifier state { name } priority updatedAt }
        }
    }
""")

# 客户端实现（client.py）
class LinearClient(TrackerClient):
    def __init__(self, config: TrackerConfig):
        transport = HTTPXAsyncTransport(
            url=config.endpoint,
            headers={"Authorization": config.api_key},
            timeout=30.0,
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=False)

    async def fetch_candidate_issues(self) -> list[Issue]:
        nodes = await self._paginated_query(FETCH_CANDIDATES, {...}, "issues")
        return [normalize_issue(n) for n in nodes]

    async def fetch_issue_states_by_ids(self, issue_ids: list[str]) -> list[Issue]:
        if not issue_ids:
            return []
        # 每批 50 个 ID
        ...
```

**错误映射（§11.4）：**
| gql 异常 | LinearError code |
|---------|---------|
| `TransportError` | `linear_api_request` |
| `TransportQueryError` (非200) | `linear_api_status` |
| `TransportQueryError` (有errors) | `linear_graphql_errors` |
| endCursor 缺失 | `linear_missing_end_cursor` |

#### E. Orchestrator (`orchestrator/engine.py`)

核心事件循环（asyncio 单线程串行化状态变更）：

```python
class Orchestrator:
    state: OrchestratorState
    config: SymphonyConfig
    _running: bool = True

    async def run(self):
        """§16.1: 服务启动"""
        self._validate_dispatch_config()
        await self._startup_terminal_cleanup()
        # 首次 tick 立即执行
        await self._tick()
        # 周期性 tick
        while self._running:
            interval = self.state.poll_interval_ms / 1000
            self.state.next_poll_due_at_ms = time.monotonic() * 1000 + self.state.poll_interval_ms
            await asyncio.sleep(interval)
            await self._tick()

    async def _tick(self):
        """§16.2: 轮询和分派节拍"""
        self.state.poll_check_in_progress = True
        self._notify_observers()

        # 每次 tick 刷新运行时配置（支持 WORKFLOW.md 热重载）
        self._refresh_runtime_config()

        # 对账：先检测停顿，再刷新 Issue 状态
        self.state = await self._reconcile_running_issues()

        validation = self._validate_dispatch_config()
        if not validation.ok:
            logger.error("dispatch_validation_failed", error=validation.error)
            self.state.poll_check_in_progress = False
            self._notify_observers()
            return

        try:
            issues = await self.tracker.fetch_candidate_issues()
        except LinearError as e:
            logger.error("tracker_fetch_failed", error=str(e))
            self.state.poll_check_in_progress = False
            self._notify_observers()
            return

        for issue in self._sort_for_dispatch(issues):
            if self._no_available_slots():
                break
            if self._should_dispatch(issue):
                self._dispatch_issue(issue, attempt=None)

        self.state.poll_check_in_progress = False
        self._notify_observers()

    def _dispatch_issue(self, issue: Issue, attempt: int | None,
                        preferred_worker_host: str | None = None):
        """§16.4: 分派一个问题"""
        # 分派前重新验证 Issue 状态（防止竞态调度）
        refreshed = self._revalidate_issue_for_dispatch(issue)
        if refreshed is None:
            return

        worker_host = self._select_worker_host(preferred_worker_host)
        if worker_host == :no_worker_capacity:
            logger.debug("no_worker_slots", issue=issue.identifier)
            return

        task = asyncio.create_task(
            self._run_worker(issue, attempt, worker_host=worker_host),
            name=f"worker:{issue.identifier}",  # 3.14 asyncio 内省
        )
        task.add_done_callback(lambda t: self._on_worker_exit(issue.id, t))

        self.state.running[issue.id] = RunningEntry(
            worker_task=task,
            identifier=issue.identifier,
            issue=issue,
            worker_host=worker_host,
            started_at=datetime.utcnow(),
        )
        self.state.claimed.add(issue.id)
        self.state.retry_attempts.pop(issue.id, None)

        logger.info("issue_dispatched",
            issue_id=issue.id, issue_identifier=issue.identifier,
            attempt=attempt, worker_host=worker_host or "local")

    def _on_worker_exit(self, issue_id: str, task: asyncio.Task):
        """Worker 退出处理：区分正常完成和异常退出"""
        entry = self.state.running.pop(issue_id, None)
        if entry is None:
            return

        self._record_session_completion_totals(entry)
        session_id = entry.session_id or "n/a"

        try:
            task.result()  # 如有异常会在此抛出
        except Exception as exc:
            # 异常退出 → 故障重试（指数退避）
            next_attempt = (entry.retry_attempt or 0) + 1
            logger.warning("agent_task_failed",
                issue_id=issue_id, session_id=session_id, error=str(exc))
            self._schedule_issue_retry(issue_id, next_attempt, RetryMeta(
                identifier=entry.identifier, error=f"agent exited: {exc}",
                worker_host=entry.worker_host, workspace_path=entry.workspace_path,
            ))
        else:
            # 正常退出 → 续运重试（固定 1s）
            # 正常完成 ≠ Issue 已 Done，需续运检查
            logger.info("agent_task_completed",
                issue_id=issue_id, session_id=session_id)
            self.state.completed.add(issue_id)
            self._schedule_issue_retry(issue_id, 1, RetryMeta(
                identifier=entry.identifier, delay_type="continuation",
                worker_host=entry.worker_host, workspace_path=entry.workspace_path,
            ))

        self._notify_observers()

    def _schedule_issue_retry(self, issue_id: str, attempt: int, meta: RetryMeta):
        """调度重试，使用 retry_token 防止过期重试触发"""
        # 取消已有的重试计时器
        old = self.state.retry_attempts.get(issue_id)
        if old and old.timer_handle:
            old.timer_handle.cancel()

        retry_token = uuid.uuid4()  # 防过期：仅 token 匹配时执行
        delay_ms = self._compute_retry_delay_ms(attempt, meta.delay_type == "continuation")
        due_at_ms = time.monotonic() * 1000 + delay_ms

        loop = asyncio.get_running_loop()
        timer_handle = loop.call_later(
            delay_ms / 1000,
            lambda: asyncio.create_task(
                self._on_retry_timer(issue_id, retry_token)
            ),
        )

        self.state.retry_attempts[issue_id] = RetryEntry(
            issue_id=issue_id,
            identifier=meta.identifier,
            attempt=attempt,
            due_at_ms=due_at_ms,
            timer_handle=timer_handle,
            retry_token=retry_token,
            delay_type=meta.delay_type,
            error=meta.error,
            worker_host=meta.worker_host,
            workspace_path=meta.workspace_path,
        )

        error_suffix = f" error={meta.error}" if meta.error else ""
        logger.warning("retry_scheduled",
            issue_id=issue_id, identifier=meta.identifier,
            attempt=attempt, delay_ms=delay_ms, **{k: v for k, v in [
                ("error", meta.error)] if v})

    async def _on_retry_timer(self, issue_id: str, retry_token: uuid.UUID):
        """重试计时器回调：token 不匹配则跳过（防止过期重试）"""
        entry = self.state.retry_attempts.get(issue_id)
        if entry is None or entry.retry_token != retry_token:
            return  # 过期或已被新重试替换
        # ... 查询 Issue 状态并决定重试/释放/清理

    def _refresh_runtime_config(self):
        """从最新配置刷新运行时参数（支持 WORKFLOW.md 热重载）"""
        # 配置由 WorkflowStore/Watcher 管理热重载
        self.state.poll_interval_ms = self.config.polling.interval_ms
        self.state.max_concurrent_agents = self.config.agent.max_concurrent_agents

    def snapshot(self) -> dict:
        """可观测性：生成当前状态快照（供 HTTP API 和仪表板使用）"""
        now = datetime.utcnow()
        now_ms = time.monotonic() * 1000
        return {
            "running": [
                {
                    "issue_id": eid, "identifier": e.identifier,
                    "state": e.issue.state,
                    "worker_host": e.worker_host,
                    "workspace_path": e.workspace_path,
                    "session_id": e.session_id,
                    "codex_input_tokens": e.codex_input_tokens,
                    "codex_output_tokens": e.codex_output_tokens,
                    "codex_total_tokens": e.codex_total_tokens,
                    "turn_count": e.turn_count,
                    "started_at": e.started_at.isoformat(),
                    "runtime_seconds": max(0, (now - e.started_at).seconds),
                    "last_codex_event": e.last_codex_event,
                    "last_codex_message": e.last_codex_message,
                    "last_codex_timestamp": e.last_codex_timestamp.isoformat() if e.last_codex_timestamp else None,
                }
                for eid, e in self.state.running.items()
            ],
            "retrying": [
                {
                    "issue_id": eid, "attempt": e.attempt,
                    "due_in_ms": max(0, e.due_at_ms - now_ms),
                    "identifier": e.identifier, "error": e.error,
                    "worker_host": e.worker_host,
                }
                for eid, e in self.state.retry_attempts.items()
            ],
            "codex_totals": dataclasses.asdict(self.state.codex_totals),
            "rate_limits": self.state.codex_rate_limits,
            "polling": {
                "checking": self.state.poll_check_in_progress,
                "next_poll_in_ms": max(0, (self.state.next_poll_due_at_ms or 0) - now_ms),
                "poll_interval_ms": self.state.poll_interval_ms,
            },
        }
```

**状态模型 (`orchestrator/state.py`)：**

```python
@dataclass
class RunningEntry:
    worker_task: asyncio.Task
    identifier: str
    issue: Issue
    worker_host: str | None = None       # SSH 扩展：工作器主机
    workspace_path: str | None = None    # 工作区路径（运行时上报）
    session_id: str | None = None
    codex_app_server_pid: str | None = None
    last_codex_event: str | None = None
    last_codex_timestamp: datetime | None = None  # 停顿检测依据
    last_codex_message: str | None = None
    codex_input_tokens: int = 0
    codex_output_tokens: int = 0
    codex_total_tokens: int = 0
    last_reported_input_tokens: int = 0   # Token 增量核算
    last_reported_output_tokens: int = 0
    last_reported_total_tokens: int = 0
    turn_count: int = 0
    retry_attempt: int | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RetryMeta:
    """重试调度元数据（不存储在 state 中，仅在调度时传递）"""
    identifier: str
    delay_type: str = "failure"           # "continuation" | "failure"
    error: str | None = None
    worker_host: str | None = None
    workspace_path: str | None = None

@dataclass
class RetryEntry:
    issue_id: str
    identifier: str
    attempt: int
    due_at_ms: float                      # monotonic clock
    timer_handle: asyncio.TimerHandle
    retry_token: uuid.UUID                # 防过期重试（参考 Elixir retry_token）
    delay_type: str = "failure"           # "continuation" | "failure"
    error: str | None = None
    worker_host: str | None = None        # SSH 扩展：重试目标主机
    workspace_path: str | None = None     # 重试时复用工作区

@dataclass
class CodexTotals:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    seconds_running: float = 0.0

@dataclass
class OrchestratorState:
    poll_interval_ms: int
    max_concurrent_agents: int
    poll_check_in_progress: bool = False  # 仪表板渲染："checking now…"
    next_poll_due_at_ms: float | None = None  # 仪表板：下次轮询倒计时
    running: dict[str, RunningEntry] = field(default_factory=dict)
    claimed: set[str] = field(default_factory=set)
    retry_attempts: dict[str, RetryEntry] = field(default_factory=dict)
    completed: set[str] = field(default_factory=set)
    codex_totals: CodexTotals = field(default_factory=CodexTotals)
    codex_rate_limits: dict | None = None
```

**调度排序（§8.2）：**
```python
def _sort_for_dispatch(self, issues: list[Issue]) -> list[Issue]:
    """priority 升序(1..4, null最后) → created_at 最旧 → identifier 字典序"""
    return sorted(issues, key=lambda i: (
        i.priority if i.priority is not None else 999,
        i.created_at or datetime.max,
        i.identifier,
    ))
```

**重试退避（§8.4）：**
```python
def _compute_retry_delay_ms(self, attempt: int, is_continuation: bool) -> int:
    if is_continuation:
        return 1000  # 续运重试固定 1s
    # 故障重试：指数退避
    delay = min(10000 * (2 ** (attempt - 1)), self.config.agent.max_retry_backoff_ms)
    return delay
```

#### F. Workspace Manager (`workspace/manager.py`)

```python
import re
import shutil

class WorkspaceManager:
    def __init__(self, config: WorkspaceConfig, hooks_config: HooksConfig):
        self._root = Path(config.root).resolve()
        self._hooks = hooks_config

    async def create_for_issue(self, identifier: str) -> Workspace:
        """§9.2: 工作区创建和重用"""
        workspace_key = self._sanitize(identifier)
        workspace_path = self._root / workspace_key

        # 安全不变量：路径必须在根内
        self._assert_within_root(workspace_path)

        created_now = not workspace_path.exists()
        workspace_path.mkdir(parents=True, exist_ok=True)

        if created_now and self._hooks.after_create:
            await self._run_hook(self._hooks.after_create, workspace_path)

        return Workspace(path=workspace_path, workspace_key=workspace_key, created_now=created_now)

    def _sanitize(self, identifier: str) -> str:
        """§4.2: 仅允许 [A-Za-z0-9._-]，其余替换为 _"""
        return re.sub(r'[^A-Za-z0-9._-]', '_', identifier)

    def _assert_within_root(self, path: Path):
        """安全不变量：路径规范化后必须在根内（含符号链接解析）"""
        canonical_path = canonicalize(path)
        canonical_root = canonicalize(self._root)

        if canonical_path == canonical_root:
            raise WorkspaceSecurityError(f"Workspace equals root: {path}")
        if not str(canonical_path).startswith(str(canonical_root) + os.sep):
            # 检查是否通过符号链接逃逸
            expanded_path = path.resolve()
            if not str(expanded_path).startswith(str(self._root) + os.sep):
                raise WorkspaceSecurityError(
                    f"Path escapes workspace root via symlink: {path}")
            raise WorkspaceSecurityError(f"Path escapes workspace root: {path}")

def canonicalize(path: Path) -> Path:
    """逐段解析符号链接，返回规范化绝对路径（参考 Elixir PathSafety.canonicalize）

    与 Path.resolve() 的区别：resolve() 仅解析最终目标，
    本函数逐段解析，确保中间符号链接不逃逸根目录。
    """
    parts = path.resolve().parts
    resolved = Path(parts[0])  # 根路径（/ 或 C:\）
    for segment in parts[1:]:
        candidate = resolved / segment
        if candidate.is_symlink():
            target = Path(os.readlink(candidate))
            if not target.is_absolute():
                target = resolved / target
            resolved = canonicalize(target)  # 递归解析符号链接链
        elif candidate.exists():
            resolved = candidate
        else:
            resolved = candidate  # 不存在的路径段保持原样
    return resolved
```

#### G. Agent Runner + Transport 抽象 (`agent/`)

**统一本地/SSH 执行接口 (`agent/transport.py`)：**

```python
from abc import ABC, abstractmethod
import asyncssh

class AgentTransport(ABC):
    """智能体执行传输层抽象（§附录A）"""

    @abstractmethod
    async def start_process(self, command: str, cwd: str) -> AgentProcess:
        ...

    @abstractmethod
    async def run_hook(self, script: str, cwd: str, timeout_ms: int) -> int:
        ...

class LocalTransport(AgentTransport):
    async def start_process(self, command: str, cwd: str) -> AgentProcess:
        proc = await asyncio.create_subprocess_exec(
            "bash", "-lc", command,
            cwd=cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return LocalAgentProcess(proc)

class SSHTransport(AgentTransport):
    """SSH 远程执行（asyncssh）"""
    def __init__(self, host: str, **ssh_opts):
        self._host = host
        self._ssh_opts = ssh_opts
        self._conn: asyncssh.SSHClientConnection | None = None

    async def connect(self):
        self._conn = await asyncssh.connect(self._host, **self._ssh_opts)

    async def start_process(self, command: str, cwd: str) -> AgentProcess:
        full_cmd = f"cd {shlex.quote(cwd)} && bash -lc {shlex.quote(command)}"
        process = await self._conn.create_process(full_cmd)
        return SSHAgentProcess(process)
```

**Agent Runner (`agent/runner.py`)：**

```python
class AgentRunner:
    def __init__(self, transport: AgentTransport, config: SymphonyConfig):
        self._transport = transport
        self._config = config

    async def run_attempt(
        self, issue: Issue, attempt: int | None, on_event: Callable
    ):
        """§16.5: Worker 尝试"""
        workspace = await self._workspace_mgr.create_for_issue(issue.identifier)

        # before_run 钩子
        if self._config.hooks.before_run:
            exit_code = await self._transport.run_hook(
                self._config.hooks.before_run,
                str(workspace.path),
                self._config.hooks.timeout_ms,
            )
            if exit_code != 0:
                raise HookError("before_run failed")

        # 启动 app-server
        app_server = AppServerClient(self._transport)
        session = await app_server.start(str(workspace.path), self._config.codex.command)

        max_turns = self._config.agent.max_turns
        turn_number = 1

        try:
            while True:
                prompt = self._build_turn_prompt(issue, attempt, turn_number, max_turns)
                turn_result = await app_server.run_turn(session, prompt, on_event)

                if not turn_result.success:
                    raise AgentTurnError(turn_result.error)

                # 检查问题状态
                refreshed = await self._tracker.fetch_issue_states_by_ids([issue.id])
                if refreshed and refreshed[0].state.lower() not in [
                    s.lower() for s in self._config.tracker.active_states
                ]:
                    break

                if turn_number >= max_turns:
                    break
                turn_number += 1
        finally:
            await app_server.stop(session)
            # after_run（best effort）
            if self._config.hooks.after_run:
                try:
                    await self._transport.run_hook(
                        self._config.hooks.after_run,
                        str(workspace.path),
                        self._config.hooks.timeout_ms,
                    )
                except Exception:
                    logger.warning("after_run_hook_failed", issue=issue.identifier)
```

#### H. 提示词渲染

**用户模板：Jinja2 strict（`prompt/renderer.py`）：**

```python
from jinja2 import Environment, StrictUndefined, TemplateSyntaxError

_env = Environment(undefined=StrictUndefined)

def render_prompt(template_str: str, issue: Issue, attempt: int | None) -> str:
    """§12: 严格变量检查渲染"""
    try:
        tmpl = _env.from_string(template_str)
    except TemplateSyntaxError as e:
        raise PromptError("template_parse_error", str(e))

    try:
        return tmpl.render(issue=issue.model_dump(), attempt=attempt)
    except Exception as e:
        raise PromptError("template_render_error", str(e))
```

**内部模板：t-string（`prompt/internal.py`）— PEP 750：**

```python
from string.templatelib import Template, Interpolation

def build_continuation_prompt(issue: Issue, turn: int, max_turns: int) -> str:
    """续运轮次使用 t-string 构建（非用户模板）"""
    template = t"""Continue working on {issue.identifier}: {issue.title}.
This is turn {turn}/{max_turns}. Review progress and continue from where you left off."""
    return _render(template)

def build_default_prompt(issue: Issue) -> str:
    """§5.4 回退提示词"""
    template = t"You are working on an issue from Linear. Issue: {issue.identifier} - {issue.title}"
    return _render(template)

def _render(template: Template) -> str:
    parts = []
    for part in template:
        if isinstance(part, Interpolation):
            parts.append(str(part.value))
        else:
            parts.append(part)
    return "".join(parts)
```

### 2.3 数据流和控制流

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator (asyncio event loop)          │
│                                                              │
│  ┌──── Tick Loop (§8.1) ──────────────────────────────────┐ │
│  │ 1. reconcile_stalled_runs()    [停顿检测]              │ │
│  │ 2. reconcile_tracker_states()  [← LinearClient]        │ │
│  │ 3. validate_dispatch_config()  [预检验证]              │ │
│  │ 4. fetch_candidates()          [← LinearClient]        │ │
│  │ 5. sort_for_dispatch()         [优先级+时间排序]       │ │
│  │ 6. dispatch_issues()           [→ spawn worker tasks]  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──── Worker Tasks (asyncio.Task per issue) ─────────────┐ │
│  │ AgentRunner.run_attempt()                              │ │
│  │   → WorkspaceManager.create_for_issue()                │ │
│  │   → transport.run_hook("before_run")                   │ │
│  │   → AppServerClient.start() [Local/SSH transport]      │ │
│  │   → turn loop (prompt → stream events → check state)  │ │
│  │   → events → Orchestrator._on_codex_update()           │ │
│  │   → transport.run_hook("after_run")                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──── Retry Timers (asyncio.call_later) ─────────────────┐ │
│  │ on_retry_timer() → fetch candidates → re-dispatch      │ │
│  │                    or release claim                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──── Config Watcher (watchdog) ─────────────────────────┐ │
│  │ WORKFLOW.md changed → debounce → reload + reapply      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──── HTTP Server (OPTIONAL, FastAPI) ───────────────────┐ │
│  │ GET /api/v1/state | GET /api/v1/<id> | POST /refresh   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 并发和调度机制

- **单线程 asyncio 事件循环**：调度器串行化所有状态变更，避免竞态（§7）
- **asyncio.Task per worker**：每个 issue 的 AgentRunner 作为命名 Task 运行
- **全局槽位**：`available = max(max_concurrent_agents - len(running), 0)`
- **每状态槽位**：`max_concurrent_agents_by_state[normalized_state]`（§8.3）
- **重试计时器**：`asyncio.get_event_loop().call_later(delay_s, callback)`
- **本地子进程**：`asyncio.create_subprocess_exec` with stdin/stdout pipes
- **SSH 远程进程**：`asyncssh.create_process()` 原生异步 stdio 流
- **asyncio 内省**（3.14）：通过 `asyncio.all_tasks()` 监控 worker 状态

### 2.5 错误处理和恢复策略

使用 PEP 758 新语法（无括号 except）：

```python
# 统一错误处理风格
try:
    result = await self.tracker.fetch_candidate_issues()
except TransportError, TransportQueryError as e:
    logger.error("tracker_fetch_failed", code=e.code, msg=str(e))
    return  # 跳过本节拍
```

| 错误类别 | 处理方式（§14） |
|---------|---------|
| 工作流/配置错误 | 启动时 fail_startup；运行时跳过分派但继续对账 |
| 工作区创建失败 | worker 失败 → 指数退避重试 |
| 钩子超时/失败 | after_create/before_run 致命；after_run/before_remove 仅记录 |
| Codex 启动失败 | worker 失败 → 指数退避重试 |
| 轮次超时/失败 | worker 失败 → 指数退避重试 |
| 停顿检测 | 终止 worker → 重试 |
| Linear API 失败 | 候选获取失败跳过本节拍；对账失败保持 worker |
| 无效重载 | 保持最后有效配置，日志告警 |

**退避公式（§8.4）：**
- 续运重试：固定 `1000ms`
- 故障重试：`min(10000 * 2^(attempt-1), agent.max_retry_backoff_ms)`

### 2.6 监控和可观测性设计

**结构化日志（structlog）：**
```python
import structlog

logger = structlog.get_logger()

# 所有问题相关日志携带上下文（§13.1）
logger.info("issue_dispatched",
    issue_id=issue.id,
    issue_identifier=issue.identifier,
    session_id=session_id,
)
```

**asyncio 任务内省（3.14）：**
```python
async def get_worker_tasks_info() -> list[dict]:
    """利用 3.14 asyncio introspection"""
    all_tasks = asyncio.all_tasks()
    return [
        {"name": t.get_name(), "done": t.done()}
        for t in all_tasks
        if t.get_name().startswith("worker:")
    ]
```

**OPTIONAL HTTP 服务器（FastAPI，§13.7）：**
- `GET /` → HTML 仪表板
- `GET /api/v1/state` → 系统状态 JSON（running/retrying/codex_totals/rate_limits）
- `GET /api/v1/{issue_identifier}` → 单问题详情（404 if unknown）
- `POST /api/v1/refresh` → 触发即时轮询（202 Accepted）

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

```python
# 1. except 不需要圆括号 (PEP 758)
except TransportError, TimeoutError as e:
    logger.error("request_failed", error=str(e))

# 2. 不需要 from __future__ import annotations (PEP 649)
class Orchestrator:
    state: OrchestratorState  # 前向引用直接写，无需字符串

# 3. 内部模板使用 t-string (PEP 750)
from string.templatelib import Template
msg = t"[{issue.identifier}] Turn {turn}/{max_turns} completed"

# 4. asyncio task 命名（利用 3.14 内省）
task = asyncio.create_task(coro, name=f"worker:{identifier}")

# 5. 标注迟延求值自动生效，Pydantic 模型更简洁
class RunningEntry:
    issue: Issue              # Issue 无需提前定义
    session: LiveSession | None
```

---

## 6. 实现路线图（建议顺序）

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
