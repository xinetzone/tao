# Symphony 服务规范

原始规范见：[symphony SPEC](https://github.com/openai/symphony/blob/main/SPEC.md)。

状态：草案 v1（语言无关）

目的：定义一个编排编码智能体以完成项目工作的服务。

## 规范性语言

本文档中的关键术语 `MUST`（必须）、`MUST NOT`（必须不）、`REQUIRED`（必需）、`SHOULD`（应该）、`SHOULD NOT`（不应该）、`RECOMMENDED`（推荐）、`MAY`（可以）和 `OPTIONAL`（可选）应按照 RFC 2119 的描述进行解释。

`Implementation-defined`（实现定义）表示该行为属于实现契约的一部分，但本规范不规定统一策略。实现 MUST 记录其所选择的行为。

## 1. 问题陈述

Symphony 是一个长期运行的自动化服务，持续从问题跟踪器（本规范版本中为 Linear）读取工作，为每个问题创建隔离的工作区，并在工作区内为该问题运行编码智能体会话。

该服务解决四个运维问题：

- 将问题执行转变为可重复的守护进程工作流，而非手动脚本。
- 在每个问题的工作区中隔离智能体执行，使智能体命令仅在对应问题的工作区目录中运行。
- 将工作流策略保留在代码仓库中（`WORKFLOW.md`），使团队可以用代码版本化管理智能体提示词和运行时设置。
- 提供足够的可观测性，以操作和调试多个并发的智能体运行。

各实现应明确记录其信任和安全立场。本规范不要求单一的审批、沙箱或操作员确认策略；某些实现面向高信任配置的可信环境，而其他实现则需要更严格的审批或沙箱机制。

重要边界：

- Symphony 是调度器/运行器和跟踪器读取器。
- 工单写入（状态转换、评论、PR 链接）通常由编码智能体使用工作流/运行时环境中可用的工具来执行。
- 一次成功的运行可以在工作流定义的交接状态（例如 `Human Review`）结束，而不一定是 `Done`。

## 2. 目标与非目标

### 2.1 目标

- 以固定节奏轮询问题跟踪器，并在有界并发度下分派工作。
- 维护单一的权威调度器状态，用于分派、重试和对账。
- 创建确定性的每个问题的工作区，并在多次运行间保留。
- 当问题状态变更使其不再符合条件时，停止活跃运行。
- 通过指数退避从瞬态故障中恢复。
- 从仓库拥有的 `WORKFLOW.md` 契约加载运行时行为。
- 暴露操作员可见的可观测性（至少包含结构化日志）。
- 支持基于跟踪器/文件系统驱动的重启恢复，无需持久化数据库；确切的内存调度器状态不做恢复。

### 2.2 非目标

- 丰富的 Web UI 或多租户控制面板。
- 规定特定的仪表板或终端 UI 实现。
- 通用工作流引擎或分布式作业调度器。
- 内置关于如何编辑工单、PR 或评论的业务逻辑。（该逻辑存在于工作流提示词和智能体工具中。）
- 强制要求超出编码智能体和主机操作系统提供的强沙箱控制。
- 强制要求所有实现采用单一的默认审批、沙箱或操作员确认立场。

## 3. 系统概述

### 3.1 主要组件

1. `Workflow Loader`（工作流加载器）
   - 读取 `WORKFLOW.md`。
   - 解析 YAML 前置数据和提示词正文。
   - 返回 `{config, prompt_template}`。

2. `Config Layer`（配置层）
   - 为工作流配置值暴露类型化获取器。
   - 应用默认值和环境变量间接引用。
   - 执行调度器在分派前使用的验证。

3. `Issue Tracker Client`（问题跟踪器客户端）
   - 获取活跃状态的候选问题。
   - 获取特定问题 ID 的当前状态（对账）。
   - 在启动清理期间获取终态问题。
   - 将跟踪器负载规范化为稳定的问题模型。

4. `Orchestrator`（调度器）
   - 拥有轮询节拍。
   - 拥有内存中的运行时状态。
   - 决定哪些问题需要分派、重试、停止或释放。
   - 跟踪会话指标和重试队列状态。

5. `Workspace Manager`（工作区管理器）
   - 将问题标识符映射到工作区路径。
   - 确保每个问题的工作区目录存在。
   - 运行工作区生命周期钩子。
   - 清理终态问题的工作区。

6. `Agent Runner`（智能体运行器）
   - 创建工作区。
   - 从问题 + 工作流模板构建提示词。
   - 启动编码智能体 app-server 客户端。
   - 将智能体更新流式传回调度器。

7. `Status Surface`（状态展示面）（OPTIONAL）
   - 呈现人类可读的运行时状态（例如终端输出、仪表板或其他面向操作员的视图）。

8. `Logging`（日志）
   - 向一个或多个配置的接收器发出结构化运行时日志。

### 3.2 抽象层次

Symphony 在以下层次中最易于移植：

1. `Policy Layer`（策略层，仓库定义）
   - `WORKFLOW.md` 提示词正文。
   - 团队特定的工单处理、验证和交接规则。

2. `Configuration Layer`（配置层，类型化获取器）
   - 将前置数据解析为类型化的运行时设置。
   - 处理默认值、环境令牌和路径规范化。

3. `Coordination Layer`（协调层，调度器）
   - 轮询循环、问题资格、并发度、重试、对账。

4. `Execution Layer`（执行层，工作区 + 智能体子进程）
   - 文件系统生命周期、工作区准备、编码智能体协议。

5. `Integration Layer`（集成层，Linear 适配器）
   - 跟踪器数据的 API 调用和规范化。

6. `Observability Layer`（可观测性层，日志 + OPTIONAL 状态展示面）
   - 调度器和智能体行为的操作员可见性。

### 3.3 外部依赖

- 问题跟踪器 API（本规范版本中 `tracker.kind: linear` 对应 Linear）。
- 用于工作区和日志的本地文件系统。
- OPTIONAL 工作区填充工具（例如 Git CLI，如果使用）。
- 支持目标 Codex app-server 模式的编码智能体可执行文件。
- 问题跟踪器和编码智能体的主机环境认证。

## 4. 核心领域模型

### 4.1 实体

#### 4.1.1 Issue（问题）

由编排、提示词渲染和可观测性输出使用的规范化问题记录。

字段：

- `id`（字符串）
  - 稳定的跟踪器内部 ID。
- `identifier`（字符串）
  - 人类可读的工单键（例如：`ABC-123`）。
- `title`（字符串）
- `description`（字符串或 null）
- `priority`（整数或 null）
  - 在分派排序中数值越小优先级越高。
- `state`（字符串）
  - 当前的跟踪器状态名称。
- `branch_name`（字符串或 null）
  - 跟踪器提供的分支元数据（如可用）。
- `url`（字符串或 null）
- `labels`（字符串列表）
  - 规范化为小写。
- `blocked_by`（阻塞引用列表）
  - 每个阻塞引用包含：
    - `id`（字符串或 null）
    - `identifier`（字符串或 null）
    - `state`（字符串或 null）
- `created_at`（时间戳或 null）
- `updated_at`（时间戳或 null）

#### 4.1.2 Workflow Definition（工作流定义）

解析后的 `WORKFLOW.md` 负载：

- `config`（映射）
  - YAML 前置数据根对象。
- `prompt_template`（字符串）
  - 前置数据之后的 Markdown 正文，已去除首尾空白。

#### 4.1.3 Service Config (Typed View)（服务配置，类型化视图）

从 `WorkflowDefinition.config` 加环境解析派生的类型化运行时值。

示例：

- 轮询间隔
- 工作区根路径
- 活跃和终态问题状态
- 并发限制
- 编码智能体可执行文件/参数/超时
- 工作区钩子

#### 4.1.4 Workspace（工作区）

分配给一个问题标识符的文件系统工作区。

字段（逻辑）：

- `path`（绝对工作区路径）
- `workspace_key`（经过净化的问题标识符）
- `created_now`（布尔值，用于控制 `after_create` 钩子的执行）

#### 4.1.5 Run Attempt（运行尝试）

一个问题的一次执行尝试。

字段（逻辑）：

- `issue_id`
- `issue_identifier`
- `attempt`（整数或 null，首次运行为 `null`，重试/续运为 `>=1`）
- `workspace_path`
- `started_at`
- `status`
- `error`（OPTIONAL）

#### 4.1.6 Live Session (Agent Session Metadata)（活跃会话，智能体会话元数据）

编码智能体子进程运行时跟踪的状态。

字段：

- `session_id`（字符串，`<thread_id>-<turn_id>`）
- `thread_id`（字符串）
- `turn_id`（字符串）
- `codex_app_server_pid`（字符串或 null）
- `last_codex_event`（字符串/枚举或 null）
- `last_codex_timestamp`（时间戳或 null）
- `last_codex_message`（摘要化的负载）
- `codex_input_tokens`（整数）
- `codex_output_tokens`（整数）
- `codex_total_tokens`（整数）
- `last_reported_input_tokens`（整数）
- `last_reported_output_tokens`（整数）
- `last_reported_total_tokens`（整数）
- `turn_count`（整数）
  - 当前 worker 生命周期内已启动的编码智能体轮次数量。

#### 4.1.7 Retry Entry（重试条目）

问题的计划重试状态。

字段：

- `issue_id`
- `identifier`（用于状态展示面/日志的最佳努力人类可读 ID）
- `attempt`（整数，重试队列中从 1 开始）
- `due_at_ms`（单调时钟时间戳）
- `timer_handle`（运行时特定的计时器引用）
- `error`（字符串或 null）

#### 4.1.8 Orchestrator Runtime State（调度器运行时状态）

由调度器拥有的单一权威内存状态。

字段：

- `poll_interval_ms`（当前有效轮询间隔）
- `max_concurrent_agents`（当前有效全局并发限制）
- `running`（映射 `issue_id -> running entry`）
- `claimed`（已保留/运行中/重试中的问题 ID 集合）
- `retry_attempts`（映射 `issue_id -> RetryEntry`）
- `completed`（问题 ID 集合；仅用于记录，不控制分派）
- `codex_totals`（聚合令牌 + 运行秒数）
- `codex_rate_limits`（来自智能体事件的最新速率限制快照）

### 4.2 稳定标识符和规范化规则

- `Issue ID`
  - 用于跟踪器查找和内部映射键。
- `Issue Identifier`
  - 用于人类可读的日志和工作区命名。
- `Workspace Key`
  - 从 `issue.identifier` 派生，将不在 `[A-Za-z0-9._-]` 中的字符替换为 `_`。
  - 使用净化后的值作为工作区目录名。
- `Normalized Issue State`
  - 在 `lowercase` 后比较状态。
- `Session ID`
  - 从编码智能体的 `thread_id` 和 `turn_id` 组成为 `<thread_id>-<turn_id>`。

## 5. 工作流规范（仓库契约）

### 5.1 文件发现和路径解析

工作流文件路径优先级：

1. 显式的应用/运行时设置（由 CLI 启动路径设置）。
2. 默认：当前进程工作目录中的 `WORKFLOW.md`。

加载器行为：

- 如果文件无法读取，返回 `missing_workflow_file` 错误。
- 工作流文件应为仓库拥有且纳入版本控制。

### 5.2 文件格式

`WORKFLOW.md` 是一个带有 OPTIONAL YAML 前置数据的 Markdown 文件。

设计说明：

- `WORKFLOW.md` SHOULD 足够自包含，以描述和运行不同的工作流（提示词、运行时设置、钩子和跟踪器选择/配置），而不需要带外的服务特定配置。

解析规则：

- 如果文件以 `---` 开头，解析直到下一个 `---` 之间的行作为 YAML 前置数据。
- 其余行成为提示词正文。
- 如果没有前置数据，将整个文件视为提示词正文，使用空配置映射。
- YAML 前置数据 MUST 解码为映射/对象；非映射 YAML 为错误。
- 提示词正文在使用前去除首尾空白。

返回的工作流对象：

- `config`：前置数据根对象（不嵌套在 `config` 键下）。
- `prompt_template`：去除首尾空白的 Markdown 正文。

### 5.3 前置数据 Schema

顶层键：

- `tracker`
- `polling`
- `workspace`
- `hooks`
- `agent`
- `codex`

未知键 SHOULD 被忽略以支持前向兼容性。

注意：

- 工作流前置数据是可扩展的。扩展 MAY 定义额外的顶层键，而无需更改上述核心 schema。
- 扩展 SHOULD 记录其字段 schema、默认值、验证规则，以及变更是否动态应用还是需要重启。

#### 5.3.1 `tracker`（对象）

字段：

- `kind`（字符串）
  - 分派所 REQUIRED。
  - 当前支持的值：`linear`
- `endpoint`（字符串）
  - 当 `tracker.kind == "linear"` 时的默认值：`https://api.linear.app/graphql`
- `api_key`（字符串）
  - MAY 是字面令牌或 `$VAR_NAME`。
  - 当 `tracker.kind == "linear"` 时的规范环境变量：`LINEAR_API_KEY`。
  - 如果 `$VAR_NAME` 解析为空字符串，将键视为缺失。
- `project_slug`（字符串）
  - 当 `tracker.kind == "linear"` 时分派所 REQUIRED。
- `active_states`（字符串列表）
  - 默认值：`Todo`、`In Progress`
- `terminal_states`（字符串列表）
  - 默认值：`Closed`、`Cancelled`、`Canceled`、`Duplicate`、`Done`

#### 5.3.2 `polling`（对象）

字段：

- `interval_ms`（整数）
  - 默认值：`30000`
  - 变更 SHOULD 在运行时重新应用，并影响未来的节拍调度而无需重启。

#### 5.3.3 `workspace`（对象）

字段：

- `root`（路径字符串或 `$VAR`）
  - 默认值：`<system-temp>/symphony_workspaces`
  - `~` 会被展开。
  - 相对路径相对于包含 `WORKFLOW.md` 的目录解析。
  - 有效的工作区根路径在使用前规范化为绝对路径。

#### 5.3.4 `hooks`（对象）

字段：

- `after_create`（多行 shell 脚本字符串，OPTIONAL）
  - 仅在工作区目录新创建时运行。
  - 失败则中止工作区创建。
- `before_run`（多行 shell 脚本字符串，OPTIONAL）
  - 在工作区准备之后、启动编码智能体之前的每次智能体尝试运行。
  - 失败则中止当前尝试。
- `after_run`（多行 shell 脚本字符串，OPTIONAL）
  - 在每次智能体尝试之后运行（成功、失败、超时或取消），只要工作区存在。
  - 失败仅记录，忽略。
- `before_remove`（多行 shell 脚本字符串，OPTIONAL）
  - 在工作区删除之前运行（如果目录存在）。
  - 失败仅记录，忽略；清理仍继续。
- `timeout_ms`（整数，OPTIONAL）
  - 默认值：`60000`
  - 适用于所有工作区钩子。
  - 无效值导致配置验证失败。
  - 变更 SHOULD 在运行时重新应用，以影响未来的钩子执行。

#### 5.3.5 `agent`（对象）

字段：

- `max_concurrent_agents`（整数）
  - 默认值：`10`
  - 变更 SHOULD 在运行时重新应用，并影响后续分派决策。
- `max_turns`（正整数）
  - 默认值：`20`
  - 限制一个 worker 会话内的编码智能体轮次数量。
  - 无效值导致配置验证失败。
- `max_retry_backoff_ms`（整数）
  - 默认值：`300000`（5 分钟）
  - 变更 SHOULD 在运行时重新应用，并影响未来的重试调度。
- `max_concurrent_agents_by_state`（映射 `state_name -> 正整数`）
  - 默认值：空映射。
  - 状态键规范化（`lowercase`）后查找。
  - 无效条目（非正或非数字）被忽略。

#### 5.3.6 `codex`（对象）

字段：

对于 Codex 拥有的配置值，如 `approval_policy`、`thread_sandbox` 和 `turn_sandbox_policy`，支持的值由目标 Codex app-server 版本定义。实现者 SHOULD 将它们视为透传的 Codex 配置值，而非依赖本规范中手工维护的枚举。要检查已安装的 Codex schema，运行 `codex app-server generate-json-schema --out <dir>` 并检查 `v2/ThreadStartParams.json` 和 `v2/TurnStartParams.json` 引用的相关定义。实现 MAY 在本地验证这些字段，如果需要更严格的启动检查。

- `command`（字符串 shell 命令）
  - 默认值：`codex app-server`
  - 运行时通过 `bash -lc` 在工作区目录中启动此命令。
  - 启动的进程 MUST 通过 stdio 通信兼容的 app-server 协议。
- `approval_policy`（Codex `AskForApproval` 值）
  - 默认值：实现定义。
- `thread_sandbox`（Codex `SandboxMode` 值）
  - 默认值：实现定义。
- `turn_sandbox_policy`（Codex `SandboxPolicy` 值）
  - 默认值：实现定义。
- `turn_timeout_ms`（整数）
  - 默认值：`3600000`（1 小时）
- `read_timeout_ms`（整数）
  - 默认值：`5000`
- `stall_timeout_ms`（整数）
  - 默认值：`300000`（5 分钟）
  - 如果 `<= 0`，停顿检测被禁用。

### 5.4 提示词模板契约

`WORKFLOW.md` 的 Markdown 正文是每个问题的提示词模板。

渲染要求：

- 使用严格模板引擎（Liquid 兼容语义即足够）。
- 未知变量 MUST 导致渲染失败。
- 未知过滤器 MUST 导致渲染失败。

模板输入变量：

- `issue`（对象）
  - 包含所有规范化的问题字段，包括标签和阻塞项。
- `attempt`（整数或 null）
  - 首次尝试时为 `null`/缺失。
  - 重试或续运时为整数。

回退提示词行为：

- 如果工作流提示词正文为空，运行时 MAY 使用最小默认提示词（`You are working on an issue from Linear.`）。
- 工作流文件读取/解析失败是配置/验证错误，SHOULD NOT 静默回退到提示词。

### 5.5 工作流验证和错误面

错误类别：

- `missing_workflow_file`
- `workflow_parse_error`
- `workflow_front_matter_not_a_map`
- `template_parse_error`（提示词渲染期间）
- `template_render_error`（未知变量/过滤器，无效插值）

分派门控行为：

- 工作流文件读取/YAML 错误会阻止新分派，直到修复。
- 模板错误仅使受影响的运行尝试失败。

## 6. 配置规范

### 6.1 配置解析管线

配置按以下顺序解析：

1. 选择工作流文件路径（显式运行时设置，否则 cwd 默认）。
2. 将 YAML 前置数据解析为原始配置映射。
3. 为缺失的 OPTIONAL 字段应用内置默认值。
4. 仅对显式包含 `$VAR_NAME` 的配置值解析 `$VAR_NAME` 间接引用。
5. 强制转换和验证类型化值。

环境变量不会全局覆盖 YAML 值。仅在配置值显式引用它们时才使用。

值强制转换语义：

- 路径/命令字段支持：
  - `~` 主目录展开
  - `$VAR` 展开用于环境支持的路径值
  - 仅对旨在作为本地文件系统路径的值应用展开；不要重写 URI 或任意 shell 命令字符串。
- 相对 `workspace.root` 值相对于包含所选 `WORKFLOW.md` 的目录解析。

### 6.2 动态重载语义

动态重载是 REQUIRED：

- 软件 MUST 检测 `WORKFLOW.md` 变更。
- 在变更时，MUST 重新读取并重新应用工作流配置和提示词模板，无需重启。
- 软件 MUST 尝试将新配置调整到活跃行为（例如轮询节奏、并发限制、活跃/终态、codex 设置、工作区路径/钩子以及未来运行的提示词内容）。
- 重新加载的配置适用于未来的分派、重试调度、对账决策、钩子执行和智能体启动。
- 实现不 REQUIRED 在配置变更时自动重启进行中的智能体会话。
- 管理自己的监听器/资源的扩展（例如 HTTP 服务器端口变更）MAY 需要重启，除非实现显式支持热重绑定。
- 实现 SHOULD 在运行时操作期间（例如分派前）防御性地重新验证/重新加载，以防文件系统监视事件丢失。
- 无效重载 MUST NOT 导致服务崩溃；继续使用最后已知的有效配置运行，并发出操作员可见的错误。

### 6.3 分派预检验证

此验证是调度器在尝试分派新工作之前的预检运行。它验证轮询和启动 worker 所需的工作流/配置，而非对所有可能工作流行为的完整审计。

启动验证：

- 在启动调度循环之前验证配置。
- 如果启动验证失败，使启动失败并发出操作员可见的错误。

每节拍分派验证：

- 在每个分派周期前重新验证。
- 如果验证失败，跳过该节拍的分派，保持对账活跃，并发出操作员可见的错误。

验证检查：

- 工作流文件可以被加载和解析。
- `tracker.kind` 存在且受支持。
- `tracker.api_key` 在 `$` 解析后存在。
- 当所选跟踪器类型 REQUIRED 时，`tracker.project_slug` 存在。
- `codex.command` 存在且非空。

### 6.4 核心配置字段摘要（速查表）

本节故意冗余，以便编码智能体可以快速实现配置层。扩展字段在定义它们的扩展章节中记录。核心一致性不要求识别或验证扩展字段，除非实现了该扩展。

- `tracker.kind`：字符串，REQUIRED，当前为 `linear`
- `tracker.endpoint`：字符串，当 `tracker.kind=linear` 时默认 `https://api.linear.app/graphql`
- `tracker.api_key`：字符串或 `$VAR`，当 `tracker.kind=linear` 时规范环境变量 `LINEAR_API_KEY`
- `tracker.project_slug`：字符串，当 `tracker.kind=linear` 时 REQUIRED
- `tracker.active_states`：字符串列表，默认 `["Todo", "In Progress"]`
- `tracker.terminal_states`：字符串列表，默认 `["Closed", "Cancelled", "Canceled", "Duplicate", "Done"]`
- `polling.interval_ms`：整数，默认 `30000`
- `workspace.root`：解析为绝对路径的路径，默认 `<system-temp>/symphony_workspaces`
- `hooks.after_create`：shell 脚本或 null
- `hooks.before_run`：shell 脚本或 null
- `hooks.after_run`：shell 脚本或 null
- `hooks.before_remove`：shell 脚本或 null
- `hooks.timeout_ms`：整数，默认 `60000`
- `agent.max_concurrent_agents`：整数，默认 `10`
- `agent.max_turns`：整数，默认 `20`
- `agent.max_retry_backoff_ms`：整数，默认 `300000`（5 分钟）
- `agent.max_concurrent_agents_by_state`：正整数映射，默认 `{}`
- `codex.command`：shell 命令字符串，默认 `codex app-server`
- `codex.approval_policy`：Codex `AskForApproval` 值，默认实现定义
- `codex.thread_sandbox`：Codex `SandboxMode` 值，默认实现定义
- `codex.turn_sandbox_policy`：Codex `SandboxPolicy` 值，默认实现定义
- `codex.turn_timeout_ms`：整数，默认 `3600000`
- `codex.read_timeout_ms`：整数，默认 `5000`
- `codex.stall_timeout_ms`：整数，默认 `300000`

## 7. 编排状态机

调度器是唯一变更调度状态的组件。所有 worker 结果都报告回调度器并转换为显式状态转换。

### 7.1 问题编排状态

这与跟踪器状态（`Todo`、`In Progress` 等）不同。这是服务的内部声明状态。

1. `Unclaimed`（未声明）
   - 问题未运行且没有计划重试。

2. `Claimed`（已声明）
   - 调度器已保留该问题以防止重复分派。
   - 实际上，已声明的问题要么是 `Running`，要么是 `RetryQueued`。

3. `Running`（运行中）
   - Worker 任务存在且问题在 `running` 映射中被跟踪。

4. `RetryQueued`（重试排队）
   - Worker 未运行，但在 `retry_attempts` 中存在重试计时器。

5. `Released`（已释放）
   - 声明被移除，因为问题处于终态、非活跃、缺失，或重试路径完成但未重新分派。

重要细节：

- Worker 正常退出并不意味着问题永远完成。
- Worker MAY 在退出之前通过多个连续的编码智能体轮次继续工作。
- 每次正常轮次完成后，Worker 重新检查跟踪器问题状态。
- 如果问题仍处于活跃状态，Worker SHOULD 在同一活跃编码智能体线程的同一工作区中启动另一个轮次，最多到 `agent.max_turns`。
- 第一个轮次 SHOULD 使用完整渲染的任务提示词。
- 续运轮次 SHOULD 仅向现有线程发送续运指导，而非重新发送已在线程历史中的原始任务提示词。
- 一旦 Worker 正常退出，调度器仍会安排短暂的续运重试（约 1 秒），以便重新检查问题是否仍然活跃并需要另一个 worker 会话。

### 7.2 运行尝试生命周期

运行尝试经历以下阶段：

1. `PreparingWorkspace`
2. `BuildingPrompt`
3. `LaunchingAgentProcess`
4. `InitializingSession`
5. `StreamingTurn`
6. `Finishing`
7. `Succeeded`
8. `Failed`
9. `TimedOut`
10. `Stalled`
11. `CanceledByReconciliation`

区分终止原因很重要，因为重试逻辑和日志不同。

### 7.3 转换触发器

- `Poll Tick`（轮询节拍）
  - 对账活跃运行。
  - 验证配置。
  - 获取候选问题。
  - 分派直到槽位耗尽。

- `Worker Exit (normal)`（Worker 正常退出）
  - 移除运行条目。
  - 更新聚合运行时总计。
  - 在 Worker 耗尽或完成其进程内轮次循环后，安排续运重试（attempt `1`）。

- `Worker Exit (abnormal)`（Worker 异常退出）
  - 移除运行条目。
  - 更新聚合运行时总计。
  - 安排指数退避重试。

- `Codex Update Event`（Codex 更新事件）
  - 更新活跃会话字段、令牌计数器和速率限制。

- `Retry Timer Fired`（重试计时器触发）
  - 重新获取活跃候选并尝试重新分派，如果不再符合条件则释放声明。

- `Reconciliation State Refresh`（对账状态刷新）
  - 停止问题状态为终态或不再活跃的运行。

- `Stall Timeout`（停顿超时）
  - 终止 Worker 并安排重试。

### 7.4 幂等性和恢复规则

- 调度器通过单一权威串行化状态变更，以避免重复分派。
- 在启动任何 worker 之前，`claimed` 和 `running` 检查是 REQUIRED。
- 对账在每个节拍的分派之前运行。
- 重启恢复由跟踪器驱动和文件系统驱动（无需持久化调度器数据库）。
- 启动终态清理移除已处于终态的问题的陈旧工作区。

## 8. 轮询、调度和对账

### 8.1 轮询循环

启动时，服务验证配置、执行启动清理、安排即时节拍，然后每 `polling.interval_ms` 重复一次。

有效轮询间隔 SHOULD 在工作流配置变更重新应用时更新。

节拍序列：

1. 对账运行中的问题。
2. 运行分派预检验证。
3. 使用活跃状态从跟踪器获取候选问题。
4. 按分派优先级排序问题。
5. 在槽位可用时分派符合条件的问题。
6. 通知可观测性/状态消费者状态变更。

如果每节拍验证失败，该节拍跳过分派，但对账仍首先执行。

### 8.2 候选选择规则

问题仅在以下全部为真时可分派：

- 具有 `id`、`identifier`、`title` 和 `state`。
- 其状态在 `active_states` 中且不在 `terminal_states` 中。
- 不已在 `running` 中。
- 不已在 `claimed` 中。
- 全局并发槽位可用。
- 每状态并发槽位可用。
- `Todo` 状态的阻塞规则通过：
  - 如果问题状态为 `Todo`，当任何阻塞项为非终态时不分派。

排序顺序（稳定意图）：

1. `priority` 升序（1..4 优先；null/未知排在最后）
2. `created_at` 最旧优先
3. `identifier` 字典序决胜

### 8.3 并发控制

全局限制：

- `available_slots = max(max_concurrent_agents - running_count, 0)`

每状态限制：

- `max_concurrent_agents_by_state[state]`（如果存在，状态键已规范化）
- 否则回退到全局限制

运行时按其当前跟踪状态在 `running` 映射中计数问题。

### 8.4 重试和退避

重试条目创建：

- 取消同一问题的任何现有重试计时器。
- 存储 `attempt`、`identifier`、`error`、`due_at_ms` 和新的计时器句柄。

退避公式：

- 干净 Worker 退出后的正常续运重试使用 `1000` ms 的短固定延迟。
- 故障驱动的重试使用 `delay = min(10000 * 2^(attempt - 1), agent.max_retry_backoff_ms)`。
- 指数由配置的最大重试退避限制（默认 `300000` / 5 分钟）。

重试处理行为：

1. 获取活跃候选问题（不是所有问题）。
2. 按 `issue_id` 查找特定问题。
3. 如果未找到，释放声明。
4. 如果找到且仍符合候选条件：
   - 如果槽位可用则分派。
   - 否则以错误 `no available orchestrator slots` 重新排队。
5. 如果找到但不再活跃，释放声明。

注意：

- 终态工作区清理由启动清理和活跃运行对账（包括当前运行中问题的终态转换）处理。
- 重试处理主要操作活跃候选，并在问题缺失时释放声明，而非执行终态清理。

### 8.5 活跃运行对账

对账在每个节拍运行，包含两个部分。

部分 A：停顿检测

- 对于每个运行中的问题，计算 `elapsed_ms`，基于：
  - `last_codex_timestamp`（如果已看到任何事件），否则
  - `started_at`
- 如果 `elapsed_ms > codex.stall_timeout_ms`，终止 Worker 并排队重试。
- 如果 `stall_timeout_ms <= 0`，完全跳过停顿检测。

部分 B：跟踪器状态刷新

- 获取所有运行中问题 ID 的当前问题状态。
- 对于每个运行中的问题：
  - 如果跟踪器状态为终态：终止 Worker 并清理工作区。
  - 如果跟踪器状态仍为活跃：更新内存中的问题快照。
  - 如果跟踪器状态既非活跃也非终态：终止 Worker 但不清理工作区。
- 如果状态刷新失败，保持 Worker 运行并在下一个节拍重试。

### 8.6 启动终态工作区清理

当服务启动时：

1. 查询跟踪器中处于终态的问题。
2. 对于每个返回的问题标识符，移除对应的工作区目录。
3. 如果终态问题获取失败，记录警告并继续启动。

这防止了重启后陈旧终态工作区的累积。

## 9. 工作区管理和安全

### 9.1 工作区布局

工作区根路径：

- `workspace.root`（规范化后的绝对路径）

每个问题的工作区路径：

- `<workspace.root>/<sanitized_issue_identifier>`

工作区持久性：

- 工作区在同一问题的多次运行间重用。
- 成功运行不会自动删除工作区。

### 9.2 工作区创建和重用

输入：`issue.identifier`

算法摘要：

1. 将标识符净化为 `workspace_key`。
2. 计算工作区根下的工作区路径。
3. 确保工作区路径作为目录存在。
4. 仅当目录在此次调用中创建时标记 `created_now=true`；否则 `created_now=false`。
5. 如果 `created_now=true`，运行 `after_create` 钩子（如果已配置）。

注意：

- 本节不假设任何特定的仓库/VCS 工作流。
- 超出目录创建的工作区准备（例如依赖引导、检出/同步、代码生成）是实现定义的，通常通过钩子处理。

### 9.3 OPTIONAL 工作区填充（实现定义）

本规范不要求任何内置 VCS 或仓库引导行为。

实现 MAY 使用实现定义的逻辑和/或钩子（例如 `after_create` 和/或 `before_run`）来填充或同步工作区。

失败处理：

- 工作区填充/同步失败返回当前尝试的错误。
- 如果在创建全新工作区时发生失败，实现 MAY 移除部分准备的目录。
- 重用的工作区 SHOULD NOT 在填充失败时被破坏性重置，除非该策略被显式选择和记录。

### 9.4 工作区钩子

支持的钩子：

- `hooks.after_create`
- `hooks.before_run`
- `hooks.after_run`
- `hooks.before_remove`

执行契约：

- 在适合主机操作系统的本地 shell 上下文中执行，以工作区目录为 `cwd`。
- 在 POSIX 系统上，`sh -lc <script>`（或更严格的等效命令如 `bash -lc <script>`）是合规的默认方式。
- 钩子超时使用 `hooks.timeout_ms`；默认：`60000 ms`。
- 记录钩子启动、失败和超时。

失败语义：

- `after_create` 失败或超时对工作区创建是致命的。
- `before_run` 失败或超时对当前运行尝试是致命的。
- `after_run` 失败或超时仅记录并忽略。
- `before_remove` 失败或超时仅记录并忽略。

### 9.5 安全不变量

这是最重要的可移植性约束。

不变量 1：仅在对应问题的工作区路径中运行编码智能体。

- 在启动编码智能体子进程之前，验证：
  - `cwd == workspace_path`

不变量 2：工作区路径 MUST 保留在工作区根内。

- 将两个路径规范化为绝对路径。
- 要求 `workspace_path` 以 `workspace_root` 作为前缀目录。
- 拒绝任何在工作区根之外的路径。

不变量 3：工作区键经过净化。

- 工作区目录名仅允许 `[A-Za-z0-9._-]`。
- 将所有其他字符替换为 `_`。

## 10. 智能体运行器协议（编码智能体集成）

本节定义 Symphony 在集成 Codex app-server 时的语言无关职责。目标 Codex 版本的 Codex app-server 协议是协议 schema、消息负载、传输帧和方法名的权威来源。

协议权威来源：

- 实现 MUST 发送对目标 Codex app-server 版本有效的消息。
- 实现 MUST 查阅目标 Codex app-server 文档或生成的 schema，而非将本规范视为协议 schema。
- 如果本规范似乎与目标 Codex app-server 协议冲突，Codex 协议控制协议形状和传输行为。
- 本节中 Symphony 特有的要求仍控制编排行为、工作区选择、提示词构建、续运处理和可观测性提取。

### 10.1 启动契约

子进程启动参数：

- 命令：`codex.command`
- 调用：`bash -lc <codex.command>`
- 工作目录：工作区路径
- 传输/帧：目标 Codex app-server 版本要求的协议传输

注意：

- 默认命令是 `codex app-server`。
- 审批策略、沙箱策略、cwd、提示词输入和 OPTIONAL 工具声明使用目标 Codex app-server 版本支持的字段提供。

RECOMMENDED 的额外进程设置：

- 最大行大小：10 MB（用于安全缓冲）

### 10.2 会话启动职责

参考：https://developers.openai.com/codex/app-server/

启动 MUST 遵循目标 Codex app-server 契约。Symphony 额外要求客户端：

- 在对应问题的工作区中启动 app-server 子进程。
- 使用目标 Codex app-server 协议初始化 app-server 会话。
- 根据目标协议创建或恢复编码智能体线程。
- 在目标协议接受 cwd 的地方，提供绝对的问题专属工作区路径作为线程/轮次工作目录。
- 以渲染的问题提示词启动第一个轮次。
- 在同一活跃线程上启动后续的 worker 内续运轮次时，使用续运指导而非重新发送原始问题提示词。
- 使用目标协议支持的字段提供实现文档化的审批和沙箱策略。
- 当目标协议支持轮次或会话标题时，包含问题标识元数据，如 `<issue.identifier>: <issue.title>`。
- 使用目标协议向编码智能体通告已实现的客户端侧工具。

会话标识符：

- 从目标 Codex app-server 协议返回的线程身份中提取 `thread_id`。
- 从