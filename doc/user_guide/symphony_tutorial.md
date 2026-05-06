# Symphony 编排服务使用教程

Symphony 是 taolib 中的长期运行编排服务模块，能够轮询 Linear 等问题跟踪器，为每个活跃问题创建隔离工作区并运行 Codex 智能体会话。本教程将引导你完成从安装到实际使用的完整流程。

## 基本概念

### 什么是 Symphony

Symphony 是一个自动化编排引擎，核心功能是将问题跟踪器（如 Linear）中的活跃问题自动分派给 AI 智能体处理。其工作流程如下：

1. **轮询**：定期从问题跟踪器获取活跃状态的候选问题
2. **对账**：检查运行中的问题状态，检测停顿或外部状态变更
3. **分派**：将符合条件的问题分配给智能体 worker
4. **监控**：跟踪令牌消耗、轮次进度和运行时状态
5. **重试**：支持续运重试和故障指数退避重试

### 核心组件

| 组件 | 模块路径 | 说明 |
|------|----------|------|
| CLI | `taolib.symphony.cli` | 基于 Typer 的命令行接口 |
| 编排引擎 | `taolib.symphony.orchestrator.engine` | 轮询、对账、分派与重试的生命周期管理 |
| 调度器 | `taolib.symphony.orchestrator.scheduler` | 候选排序与并发控制 |
| 配置系统 | `taolib.symphony.config` | 多源配置合并（CLI > 环境变量 > WORKFLOW.md > TOML > 默认值） |
| 工作区管理 | `taolib.symphony.workspace` | 隔离文件系统工作区的创建与清理 |
| 智能体运行器 | `taolib.symphony.agent` | Codex app-server 进程管理与轮次循环 |
| 提示词引擎 | `taolib.symphony.prompt` | Jinja2 模板渲染与 PEP 750 内部模板 |
| 问题跟踪器 | `taolib.symphony.tracker` | Linear GraphQL 客户端与数据规范化 |
| HTTP 服务器 | `taolib.symphony.server` | REST API 与监控仪表板 |
| 可观测性 | `taolib.symphony.observability` | 结构化日志、令牌核算与状态快照 |

### 状态机

编排器维护一个内存中的状态机，问题经历以下生命周期：

```
候选 → 运行中 → 正常退出 → 续运重试 → 运行中
                  异常退出 → 退避重试 → 运行中
         → 终态 → 工作区清理
```

## 安装和环境配置

### 前置条件

- **Python 3.14+**：Symphony 使用了 PEP 750 t-string 语法，需要 Python 3.14 或更高版本
- **Codex CLI**：用于启动 `codex app-server` 智能体会话
- **Linear API Key**：用于访问 Linear GraphQL API

### 安装

```bash
# 开发模式安装（包含所有可选依赖）
pip install -e ".[dev,doc,test]"
```

Symphony 的核心依赖包括：

| 依赖 | 用途 |
|------|------|
| `typer` | CLI 框架 |
| `pydantic` v2 | 配置模型与校验 |
| `gql[httpx]` | Linear GraphQL 客户端 |
| `httpx` | 异步 HTTP 传输 |
| `asyncssh` | SSH 远程传输 |
| `jinja2` | 提示词模板渲染 |
| `structlog` | 结构化日志 |
| `fastapi` + `uvicorn` | HTTP 监控服务器 |
| `watchdog` | WORKFLOW.md 文件变更监视 |
| `pyyaml` | YAML 前置数据解析 |

### 环境变量

Symphony 配置中支持通过 `$VAR_NAME` 形式引用环境变量，建议在运行前设置：

```bash
# Linear API Key（必需）
export LINEAR_API_KEY="lin_api_your_key_here"

# 可选：覆盖默认端点
export LINEAR_ENDPOINT="https://api.linear.app/graphql"
```

### Python 环境

执行 Symphony 相关测试和代码运行时，默认使用路径为 `${PYTHON_ENV_DIR:-~/.conda/envs/py314}` 的 Python 3.14 环境。

## 创建和配置 WORKFLOW.md

WORKFLOW.md 是 Symphony 编排服务的工作流定义文件，采用 YAML 前置数据 + Markdown 正文的格式。前置数据用于配置参数，正文用作提示词模板（Jinja2 格式）。

### 文件格式

```markdown
---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: my-project
  active_states:
    - Todo
    - In Progress
polling:
  interval_ms: 30000
agent:
  max_concurrent_agents: 5
  max_turns: 20
workspace:
  root: ./workspaces
hooks:
  after_create: ./scripts/setup-workspace.sh
  before_run: ./scripts/pre-run.sh
  after_run: ./scripts/post-run.sh
  before_remove: ./scripts/cleanup.sh
  timeout_ms: 60000
codex:
  command: codex app-server
  approval_policy: never
  turn_timeout_ms: 3600000
  stall_timeout_ms: 300000
server:
  port: 8080
  bind: 127.0.0.1
---

你正在处理一个 Linear 问题。

## 问题信息

- 标识符：{{ issue.identifier }}
- 标题：{{ issue.title }}
- 描述：{{ issue.description }}
- 优先级：{{ issue.priority }}
- 标签：{{ issue.labels | join(', ') }}
- 状态：{{ issue.state }}

## 当前尝试

这是第 {{ attempt }} 次尝试。

## 任务要求

请根据以上信息完成问题的解决。遵循以下步骤：
1. 分析问题描述，理解需求
2. 检查当前工作区中的代码状态
3. 实施解决方案
4. 确保所有测试通过
```

### YAML 前置数据说明

前置数据位于文件开头的 `---` 分隔符之间，支持以下配置段：

**tracker** — 问题跟踪器配置：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `kind` | `str` | `"linear"` | 跟踪器类型，当前仅支持 `linear` |
| `endpoint` | `str` | `"https://api.linear.app/graphql"` | GraphQL 端点地址 |
| `api_key` | `str` | `""` | API 密钥，推荐使用 `$VAR` 引用环境变量 |
| `project_slug` | `str` | `""` | Linear 项目 slug |
| `active_states` | `list[str]` | `["Todo", "In Progress"]` | 候选问题的活跃状态 |
| `terminal_states` | `list[str]` | `["Closed", "Cancelled", "Canceled", "Duplicate", "Done"]` | 终态状态列表 |

**polling** — 轮询配置：

| 字段 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `interval_ms` | `int` | `30000` | >= 1000 | 轮询间隔（毫秒） |

**workspace** — 工作区配置：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `root` | `str/Path` | `/tmp/symphony_workspaces` | 工作区根目录，支持 `~` 和相对路径 |

**hooks** — 钩子配置：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `after_create` | `str/null` | `None` | 工作区创建后执行的脚本 |
| `before_run` | `str/null` | `None` | 智能体运行前执行的脚本 |
| `after_run` | `str/null` | `None` | 智能体运行后执行的脚本 |
| `before_remove` | `str/null` | `None` | 工作区删除前执行的脚本 |
| `timeout_ms` | `int` | `60000` | 钩子执行超时（毫秒） |

**agent** — 智能体并发与重试配置：

| 字段 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `max_concurrent_agents` | `int` | `10` | >= 1 | 最大并发智能体数 |
| `max_turns` | `int` | `20` | >= 1 | 单次运行最大轮次数 |
| `max_retry_backoff_ms` | `int` | `300000` | >= 0 | 最大重试退避时间（毫秒） |
| `max_concurrent_agents_by_state` | `dict[str, int]` | `{}` | 按状态限制并发数，键自动小写规范化 |

**codex** — Codex app-server 配置：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `command` | `str` | `"codex app-server"` | 启动 app-server 的命令 |
| `approval_policy` | `str/null` | `None` | 审批策略 |
| `thread_sandbox` | `str/null` | `None` | 线程沙箱配置 |
| `turn_sandbox_policy` | `str/null` | `None` | 轮次沙箱策略 |
| `turn_timeout_ms` | `int` | `3600000` | 轮次超时（毫秒，默认 1 小时） |
| `read_timeout_ms` | `int` | `5000` | 读取超时（毫秒） |
| `stall_timeout_ms` | `int` | `300000` | 停顿检测超时（毫秒，默认 5 分钟） |

**worker** — SSH Worker 扩展配置：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `ssh_hosts` | `list[str]` | `[]` | SSH 远程主机列表 |
| `max_concurrent_agents_per_host` | `int/null` | `None` | 每主机最大并发数 |

**server** — HTTP 服务器配置：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `port` | `int/null` | `None` | HTTP 服务端口 |
| `bind` | `str` | `"127.0.0.1"` | 绑定地址 |

### 提示词模板语法

WORKFLOW.md 正文部分使用 Jinja2 严格模式（`StrictUndefined`），可引用的变量包括：

- **`issue`**：问题对象字典，包含 `id`、`identifier`、`title`、`description`、`priority`、`url`、`state`、`labels`、`blocked_by`、`branch_name`、`created_at`、`updated_at` 等字段
- **`attempt`**：当前尝试序号（首次为 `None`，续运为 `1`，故障重试递增）

```jinja2
问题 {{ issue.identifier }}: {{ issue.title }}

{% if issue.labels %}
标签: {{ issue.labels | join(', ') }}
{% endif %}

{% if attempt and attempt > 1 %}
这是第 {{ attempt }} 次重试，请检查之前的进度。
{% endif %}
```

引用未定义的变量会触发 `PromptError`，而非静默渲染为空字符串。

### 环境变量引用

在 YAML 前置数据中，值为 `$VAR_NAME` 形式的字符串会被替换为对应环境变量：

```yaml
tracker:
  api_key: $LINEAR_API_KEY    # 替换为 LINEAR_API_KEY 环境变量
  endpoint: $LINEAR_ENDPOINT   # 替换为 LINEAR_ENDPOINT 环境变量
```

如果环境变量不存在或为空，则保留原始 `$VAR_NAME` 引用不变。

### 路径解析

配置中的路径字段（如 `workspace.root`）会进行以下处理：

1. 先展开 `$VAR_NAME` 环境变量引用
2. 展开 `~` 为用户主目录
3. 相对路径基于 WORKFLOW.md 所在目录解析为绝对路径

```yaml
workspace:
  root: ./workspaces        # 相对于 WORKFLOW.md 所在目录
  # root: ~/symphony-ws    # 展开为用户主目录下
  # root: /tmp/workspaces  # 绝对路径保持不变
```

## symphony.toml 配置文件

symphony.toml 用于提供跨工作流的默认配置，仅读取 `[defaults]` 段。

### 配置文件位置

通过 CLI 的 `--config` / `-c` 参数指定：

```bash
symphony run WORKFLOW.md --config ./symphony.toml
```

### 配置文件格式

```toml
[defaults]

[defaults.tracker]
kind = "linear"
api_key = "$LINEAR_API_KEY"
project_slug = "my-team"
active_states = ["Todo", "In Progress", "In Review"]
terminal_states = ["Done", "Cancelled", "Duplicate"]

[defaults.polling]
interval_ms = 30000

[defaults.workspace]
root = "/data/symphony/workspaces"

[defaults.hooks]
after_create = "./scripts/setup.sh"
timeout_ms = 60000

[defaults.agent]
max_concurrent_agents = 10
max_turns = 20
max_retry_backoff_ms = 300000

[defaults.agent.max_concurrent_agents_by_state]
"todo" = 3
"in progress" = 5

[defaults.codex]
command = "codex app-server"
approval_policy = "never"
turn_timeout_ms = 3600000
stall_timeout_ms = 300000

[defaults.worker]
ssh_hosts = ["user@worker1", "user@worker2"]
max_concurrent_agents_per_host = 3

[defaults.server]
port = 8080
bind = "127.0.0.1"
```

### 配置合并优先级

Symphony 采用多源配置合并机制，优先级从低到高为：

1. **Pydantic 默认值** — 代码中定义的默认值
2. **symphony.toml `[defaults]` 段** — 跨工作流默认配置
3. **WORKFLOW.md YAML 前置数据** — 工作流特定配置
4. **环境变量替换** — `$VAR_NAME` 形式的引用被替换
5. **路径解析** — 相对路径和 `~` 展开
6. **CLI 参数覆盖** — 命令行参数具有最高优先级

```
CLI --port 9090 > env $LINEAR_API_KEY > WORKFLOW.md > symphony.toml [defaults] > 默认值
```

合并策略为深度合并（`deep_merge`）：override 中的值覆盖 base 中的同名键，如果两边都是字典则递归合并。

## CLI 命令使用

Symphony 提供基于 Typer 的命令行接口，入口为 `symphony` 命令。

### symphony run

启动 Symphony 编排服务，这是最主要的命令。

```bash
symphony run WORKFLOW.md [OPTIONS]
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `workflow` | `Path` | 是 | WORKFLOW.md 文件路径 |
| `--port` / `-p` | `int` | 否 | HTTP 服务端口（覆盖配置文件中的 `server.port`） |
| `--config` / `-c` | `Path` | 否 | symphony.toml 配置文件路径 |
| `--logs-root` / `-l` | `Path` | 否 | 日志输出根目录（默认 `./log`） |

**示例：**

```bash
# 基本启动
symphony run ./WORKFLOW.md

# 指定配置文件和端口
symphony run ./WORKFLOW.md --config ./symphony.toml --port 9090

# 指定日志目录
symphony run ./WORKFLOW.md --logs-root /var/log/symphony
```

启动后会输出配置信息：

```
Symphony 编排服务启动中...
  工作流: ./WORKFLOW.md
  跟踪器: linear (my-project)
  工作区根目录: /tmp/symphony_workspaces
  轮询间隔: 30000ms
  最大并发 Agent: 10
  HTTP 端口: 8080
  日志目录: ./log
```

### symphony validate

验证 WORKFLOW.md 配置文件是否正确解析和校验。

```bash
symphony validate WORKFLOW.md
```

**示例：**

```bash
# 验证工作流配置
symphony validate ./WORKFLOW.md

# 成功输出
✅ WORKFLOW.md 解析成功
  前置数据键: tracker, polling, agent
  提示模板长度: 523 字符
✅ 配置校验通过
  跟踪器类型: linear
  轮询间隔: 30000ms
  最大并发: 10

# 失败输出
❌ 验证失败: tracker.api_key is required
```

### symphony version

显示版本信息。

```bash
symphony version
# 输出: symphony 0.1.0
```

### Python API 调用

除了 CLI，也可以通过 Python API 使用：

```python
from taolib.symphony import SymphonyConfig, Orchestrator
from taolib.symphony.cli import app as cli_app

# 加载配置
from taolib.symphony.config.loader import load_workflow
from taolib.symphony.config.resolver import resolve_config
from pathlib import Path

wf = load_workflow(Path("WORKFLOW.md"))
config = resolve_config(
    cli_args={"port": 8080},
    toml_path=Path("symphony.toml"),
    workflow_path=Path("WORKFLOW.md"),
)

# 访问配置段
print(config.tracker.kind)          # "linear"
print(config.tracker.project_slug)  # "my-project"
print(config.polling.interval_ms)   # 30000
print(config.agent.max_concurrent_agents)  # 10
```

## 与 Linear 问题跟踪器集成

### 获取 Linear API Key

1. 登录 [Linear](https://linear.app/)
2. 进入 Settings → API → Personal API Keys
3. 创建新的 API Key（以 `lin_api_` 开头）
4. 将 Key 保存为环境变量

### 配置项目 Slug

在 Linear 中，项目 slug 可在项目设置页面找到。例如项目 URL 为 `https://linear.app/my-team/project/MYPROJ-xxx`，则 slug 为 `MYPROJ`。

### 状态映射

Symphony 使用两种状态集合来管理问题生命周期：

- **活跃状态** (`active_states`)：这些问题被视为候选，会被分派给智能体处理
- **终态** (`terminal_states`)：这些问题不会被视为候选，且其工作区会被清理

默认配置：

```yaml
tracker:
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Closed
    - Cancelled
    - Canceled
    - Duplicate
    - Done
```

你可以根据团队的 Linear 工作流自定义这些状态：

```yaml
tracker:
  active_states:
    - Triage
    - Backlog
    - Todo
    - In Progress
    - In Review
  terminal_states:
    - Done
    - Cancelled
    - Duplicate
```

### 问题优先级排序

调度器按以下规则对候选问题排序（规范 §8.2）：

1. **priority 升序**：1-4 优先，null/未知排最后（映射为 999）
2. **created_at 最旧优先**：null 映射为 `datetime.max`
3. **identifier 字典序**：决胜排序

### 并发控制

Symphony 提供两级并发控制：

**全局限制**：

```yaml
agent:
  max_concurrent_agents: 10  # 最多 10 个智能体同时运行
```

**每状态限制**：

```yaml
agent:
  max_concurrent_agents: 10
  max_concurrent_agents_by_state:
    "todo": 3           # Todo 状态最多 3 个并发
    "in progress": 5    # In Progress 状态最多 5 个并发
```

状态键自动进行小写规范化，因此 `"Todo"` 和 `"todo"` 等价。

### Linear GraphQL 工具

Symphony 内置了 `LinearGraphQLTool`，允许 Codex 智能体在工作区内查询 Linear API：

```python
from taolib.symphony.agent.tools import LinearGraphQLTool

tool = LinearGraphQLTool(
    api_key="lin_api_xxx",
    endpoint="https://api.linear.app/graphql"
)

# 工具定义（传给 Codex）
definition = tool.to_tool_definition()
# {
#   "name": "linear_graphql",
#   "description": "查询 Linear GraphQL API，获取 Issue、项目等信息",
#   "parameters": {
#     "type": "object",
#     "properties": {
#       "query": {"type": "string", "description": "GraphQL 查询字符串"},
#       "variables": {"type": "object", "description": "GraphQL 查询变量"}
#     },
#     "required": ["query"]
#   }
# }
```

## 工作区管理和钩子脚本

### 工作区结构

Symphony 为每个问题创建隔离的文件系统工作区：

```
/tmp/symphony_workspaces/       ← 工作区根目录 (workspace.root)
├── MYPROJ-123/                 ← 问题 MYPROJ-123 的工作区
│   ├── src/
│   ├── tests/
│   └── ...
├── MYPROJ-456/                 ← 问题 MYPROJ-456 的工作区
└── MYPROJ-789/
```

工作区键名通过 `sanitize_identifier()` 净化，仅保留 `[A-Za-z0-9._-]` 范围内的字符，其余替换为 `_`，并去除首尾的 `.` 和 `-`。

### 路径安全

Symphony 通过 `assert_within_root()` 检查确保所有工作区路径在授权根目录内，防止路径遍历攻击。递归解析符号链接后进行比较。

### 钩子脚本

钩子是在工作区生命周期的关键节点执行的 shell 命令，支持四个时机：

| 钩子 | 触发时机 | 典型用途 |
|------|----------|----------|
| `after_create` | 工作区目录创建后 | 初始化 Git 仓库、安装依赖 |
| `before_run` | 智能体运行前 | 同步最新代码、设置环境 |
| `after_run` | 智能体运行后 | 收集日志、发送通知 |
| `before_remove` | 工作区删除前 | 归档产物、清理资源 |

**配置示例：**

```yaml
hooks:
  after_create: |
    git clone git@github.com:myorg/repo.git .
    npm install
  before_run: |
    git pull origin main
  after_run: |
    tar czf /archive/{{ identifier }}.tar.gz .
  before_remove: |
    rm -rf node_modules
  timeout_ms: 60000
```

钩子以 shell 子进程方式执行，工作目录为对应的工作区路径。超时控制由 `timeout_ms` 配置（默认 60 秒），超时后进程会被强制终止并抛出 `HookTimeoutError`。

### 传输层

Symphony 支持两种传输层实现：

**本地传输** (`LocalTransport`)：在本机以 asyncio 子进程方式启动智能体和执行钩子。

**SSH 传输** (`SSHTransport`)：通过 asyncssh 连接远程主机，在远端启动智能体和执行钩子。配置 `worker.ssh_hosts` 后自动启用。

```yaml
worker:
  ssh_hosts:
    - user@worker1.example.com
    - user@worker2.example.com
  max_concurrent_agents_per_host: 3
```

### 工作区清理

工作区在以下时机被清理：

1. **启动清理**：服务启动时，扫描跟踪器中处于终态的问题并清理其工作区
2. **对账清理**：运行中的问题被外部转为终态时，终止 worker 并清理工作区
3. **手动清理**：通过 `WorkspaceManager.cleanup_workspace()` 主动清理

```python
from taolib.symphony.workspace.manager import WorkspaceManager, HooksConfig

hooks = HooksConfig(
    before_remove="echo 'Cleaning up...'",
    timeout_ms=30000,
)
mgr = WorkspaceManager(root=Path("/data/workspaces"), hooks_config=hooks)

# 列出所有工作区
print(mgr.list_workspaces())

# 检查工作区是否存在
print(mgr.workspace_exists("MYPROJ-123"))

# 清理工作区（执行 before_remove 钩子后删除目录）
await mgr.cleanup_workspace("MYPROJ-123")
```

## HTTP 监控服务器

Symphony 可选提供 HTTP 服务器，用于监控编排状态。

### 启动 HTTP 服务

在 WORKFLOW.md 中配置 `server.port` 或通过 CLI `--port` 参数启用：

```yaml
server:
  port: 8080
  bind: "127.0.0.1"
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/state` | GET | 获取系统状态快照 |
| `/api/v1/{issue_identifier}` | GET | 获取单个问题详情 |
| `/api/v1/refresh` | POST | 触发即时轮询 |
| `/dashboard` | GET | 监控仪表板 |

**获取系统状态：**

```bash
curl http://localhost:8080/api/v1/state | python -m json.tool
```

响应示例：

```json
{
  "running": [
    {
      "issue_id": "abc-123",
      "identifier": "MYPROJ-456",
      "turn_count": 3,
      "tokens": {
        "input_tokens": 12000,
        "output_tokens": 8500,
        "total_tokens": 20500
      },
      "last_event": "turn_completed",
      "started_at": "2026-05-06T10:30:00Z",
      "session_id": "thread-1-turn-3"
    }
  ],
  "retrying": [],
  "completed_count": 15,
  "codex_totals": {
    "input_tokens": 150000,
    "output_tokens": 98000,
    "total_tokens": 248000,
    "seconds_running": 3600.5
  },
  "rate_limits": null,
  "poll_interval_ms": 30000,
  "max_concurrent_agents": 10,
  "generated_at": "2026-05-06T11:30:00Z"
}
```

**查询特定问题：**

```bash
curl http://localhost:8080/api/v1/MYPROJ-456 | python -m json.tool
```

**触发即时轮询：**

```bash
curl -X POST http://localhost:8080/api/v1/refresh
# 返回 202 Accepted
```

### 监控仪表板

访问 `http://localhost:8080/dashboard` 可打开内置的 HTML 仪表板，显示：

- 运行中的 worker 列表（标识符、轮次数、令牌用量、最后事件）
- 重试队列
- 令牌汇总与运行时间
- 手动触发轮询按钮
- 每 30 秒自动刷新

## 文件变更监视

Symphony 提供基于 watchdog 的 WORKFLOW.md 文件变更监视器，变更时自动重新加载并验证配置。

```python
from pathlib import Path
from taolib.symphony.config.watcher import WorkflowWatcher

def on_success(config):
    print(f"配置重新加载成功: {config.tracker.kind}")

def on_error(exc):
    print(f"配置重新加载失败: {exc}")

watcher = WorkflowWatcher(
    workflow_path=Path("WORKFLOW.md"),
    on_reload_success=on_success,
    on_reload_error=on_error,
)
watcher.start()

# ... 服务运行 ...

watcher.stop()
```

特性：
- **防抖**：收到变更事件后等待 500ms，期间有新变更则重置计时器
- **容错**：验证失败时保持最后有效配置，不会使服务崩溃
- **线程安全**：watchdog observer 以守护线程方式运行

## 实际使用示例

### 示例 1：基础 Bug 修复编排

创建 `WORKFLOW.md`：

```markdown
---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: eng-platform
  active_states:
    - Todo
    - In Progress
polling:
  interval_ms: 60000
agent:
  max_concurrent_agents: 3
  max_turns: 10
workspace:
  root: ./workspaces
hooks:
  after_create: git clone git@github.com:myorg/platform.git . && npm install
  before_run: git pull origin main
codex:
  command: codex app-server
  approval_policy: never
  stall_timeout_ms: 600000
server:
  port: 8080
---

你是一个专业的软件工程师，负责修复 Linear 问题。

## 问题信息

- 问题：{{ issue.identifier }} - {{ issue.title }}
{% if issue.description %}

## 问题描述

{{ issue.description }}
{% endif %}

## 要求

1. 仔细阅读问题描述，理解 bug 的根本原因
2. 在代码中定位问题所在
3. 编写修复代码
4. 确保现有测试仍然通过
5. 如果合适，添加新的测试用例验证修复
```

启动服务：

```bash
export LINEAR_API_KEY="lin_api_xxx"
symphony run ./WORKFLOW.md --port 8080
```

### 示例 2：多状态并发控制

```markdown
---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: data-team
  active_states:
    - Triage
    - Backlog
    - Todo
    - In Progress
agent:
  max_concurrent_agents: 20
  max_concurrent_agents_by_state:
    "triage": 2
    "backlog": 3
    "todo": 5
    "in progress": 10
polling:
  interval_ms: 30000
workspace:
  root: /data/symphony/workspaces
---
```

### 示例 3：带完整钩子的工作流

```markdown
---
tracker:
  kind: linear
  api_key: $LINEAR_API_KEY
  project_slug: frontend
  active_states:
    - In Progress
  terminal_states:
    - Done
    - Cancelled
hooks:
  after_create: |
    set -e
    git clone git@github.com:myorg/frontend.git .
    cp .env.example .env
    npm ci
  before_run: |
    git fetch origin
    git reset --hard origin/main
  after_run: |
    if [ -f test-results.xml ]; then
      cp test-results.xml /archive/{{ identifier }}-results.xml
    fi
  before_remove: |
    echo "Removing workspace for {{ identifier }}" >> /var/log/symphony/cleanup.log
  timeout_ms: 120000
workspace:
  root: /data/symphony/workspaces
codex:
  command: codex app-server
  approval_policy: never
  turn_timeout_ms: 1800000
  stall_timeout_ms: 600000
---

修复前端问题 {{ issue.identifier }}: {{ issue.title }}

{% if issue.description %}
问题描述：
{{ issue.description }}
{% endif %}

请按照以下步骤操作：
1. 理解问题并分析影响范围
2. 实现修复
3. 运行相关测试
4. 提交代码
```

### 示例 4：最小化配置

如果没有 YAML 前置数据，整个文件内容将作为提示词模板，配置全部使用默认值：

```markdown
修复这个问题：{{ issue.identifier }} - {{ issue.title }}
```

此时需要通过环境变量提供必需的配置：

```bash
# 通过 symphony.toml 提供默认配置
cat > symphony.toml << 'EOF'
[defaults]
[defaults.tracker]
kind = "linear"
api_key = "$LINEAR_API_KEY"
project_slug = "my-project"
EOF

symphony run ./WORKFLOW.md --config ./symphony.toml
```

## 最佳实践

### 工作流设计

1. **提示词要具体**：包含明确的问题描述、解决步骤和验收标准
2. **合理设置轮次上限**：简单问题 `max_turns: 5-10`，复杂问题可设 `20-30`
3. **利用钩子保持环境一致性**：`before_run` 钩子确保每次运行从干净状态开始

### 并发调优

1. **从小开始**：初始设置 `max_concurrent_agents: 3`，观察令牌消耗后逐步调大
2. **按状态限制**：对低优先级状态（如 Triage、Backlog）设较低的并发数
3. **考虑 API 限制**：Linear API 和 Codex 都有速率限制，过大并发可能触发限流

### 安全考虑

1. **API Key 使用环境变量**：不要在 WORKFLOW.md 中硬编码密钥
2. **钩子脚本审查**：钩子以 shell 方式执行，确保脚本来源可信
3. **工作区隔离**：不同问题的工作区完全隔离，避免状态交叉污染
4. **绑定本地地址**：HTTP 服务器默认绑定 `127.0.0.1`，避免暴露到公网

### 监控与观测

1. **启用 HTTP 服务**：配置 `server.port` 以使用仪表板和 API
2. **关注令牌消耗**：定期检查 `codex_totals` 避免超支
3. **观察停顿检测**：调整 `stall_timeout_ms` 平衡灵敏度和误报率
4. **使用结构化日志**：Symphony 使用 structlog 输出 JSON 格式日志，便于集中分析

### 重试策略

1. **续运重试**：智能体正常退出后自动以 1 秒延迟重试（继续未完成的工作）
2. **故障重试**：异常退出后指数退避，公式为 `delay = min(10000 * 2^(attempt-1), max_retry_backoff_ms)`
3. **调整退避上限**：通过 `max_retry_backoff_ms` 控制最大退避时间（默认 5 分钟）

## 常见问题解答

### Q: 启动时报 "tracker.api_key is required"

**A**: 需要设置 Linear API Key。有两种方式：

1. 在 WORKFLOW.md 中使用环境变量引用：
   ```yaml
   tracker:
     api_key: $LINEAR_API_KEY
   ```
   然后设置环境变量：`export LINEAR_API_KEY="lin_api_xxx"`

2. 直接在配置中写入（不推荐，有安全风险）：
   ```yaml
   tracker:
     api_key: lin_api_xxx
   ```

### Q: 启动时报 "tracker.project_slug is required for linear tracker"

**A**: 使用 Linear 跟踪器时必须指定项目 slug。在 Linear 的项目设置页面找到 slug 并配置：

```yaml
tracker:
  project_slug: YOUR-PROJECT-SLUG
```

### Q: 工作区目录权限不足

**A**: 确保 `workspace.root` 指向的目录有写权限：

```bash
mkdir -p /data/symphony/workspaces
chmod 755 /data/symphony/workspaces
```

或在配置中使用用户可写路径：

```yaml
workspace:
  root: ~/symphony_workspaces
```

### Q: 钩子脚本执行超时

**A**: 默认超时为 60 秒。对于耗时较长的操作（如 `npm install`），增大超时：

```yaml
hooks:
  timeout_ms: 120000  # 2 分钟
```

### Q: 如何查看运行日志

**A**: Symphony 使用 structlog 输出结构化日志，默认输出到 stderr。可通过 `--logs-root` 参数指定日志目录。

### Q: 编排器重启后如何恢复

**A**: Symphony 设计为无持久化状态。重启后编排器会：
1. 清理跟踪器中终态问题的工作区
2. 重新轮询获取候选问题
3. 不依赖本地调度器数据库，由跟踪器驱动恢复

### Q: 如何在 Windows 上使用

**A**: Symphony 的智能体运行器默认使用 `bash -lc` 启动进程，Windows 上需要 WSL 或 Git Bash。工作区管理器使用纯 Python 实现，跨平台兼容。

### Q: 如何调试 WORKFLOW.md 解析问题

**A**: 使用 `symphony validate` 命令验证配置文件：

```bash
symphony validate ./WORKFLOW.md
```

该命令会报告 YAML 解析错误、配置校验失败等具体问题。

### Q: 如何限制特定状态的并发数

**A**: 使用 `max_concurrent_agents_by_state` 配置：

```yaml
agent:
  max_concurrent_agents: 20
  max_concurrent_agents_by_state:
    "todo": 5
    "in progress": 10
```

注意状态键不区分大小写，会自动规范化为小写。

## 异常层次参考

Symphony 定义了清晰的异常层次结构，便于精细化的错误处理：

```
SymphonyError                    所有 Symphony 错误的基类
├── ConfigError                  配置相关错误
│   └── WorkflowLoadError        WORKFLOW.md 解析失败
├── TrackerError                 问题跟踪器相关错误
│   └── LinearError              Linear API 相关错误
│       ├── LinearAPIRequestError   网络/传输层错误
│       ├── LinearAPIStatusError    非 2xx 响应状态码
│       ├── LinearGraphQLError      GraphQL errors 字段非空
│       └── LinearMissingCursorError  分页缺少 endCursor
├── WorkspaceError               工作区相关错误
├── AgentError                   智能体相关错误
│   ├── HookError                钩子执行失败
│   │   └── HookTimeoutError     钩子执行超时
│   └── TransportError           传输层失败
└── PromptError                  模板渲染失败
```
