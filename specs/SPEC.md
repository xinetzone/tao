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
- 从目标 Codex app-server 协议返回的每个轮次身份中提取 `turn_id`。
- 发出 `session_id = "<thread_id>-<turn_id>"`
- 在一个 worker 运行内的所有续运轮次中重用相同的 `thread_id`

### 10.3 流式轮次处理

客户端按照目标 Codex app-server 协议处理 app-server 更新，直到活跃轮次终止。

完成条件：

- 目标协议的轮次完成信号 -> 成功
- 目标协议的轮次失败信号 -> 失败
- 目标协议的轮次取消信号 -> 失败
- 轮次超时（`turn_timeout_ms`）-> 失败
- 子进程退出 -> 失败

续运处理：

- 如果 Worker 在成功轮次后决定继续，SHOULD 使用目标协议在同一活跃线程上启动另一个轮次。
- app-server 子进程 SHOULD 在这些续运轮次间保持存活，仅在 Worker 运行结束时才停止。

传输处理要求：

- 遵循目标 Codex app-server 版本的传输和帧规则。
- 对于基于 stdio 的传输，保持协议流处理与诊断 stderr 处理分离，除非目标协议另有规定。

### 10.4 发出的运行时事件（上行至调度器）

app-server 客户端向调度器回调发出结构化事件。每个事件 SHOULD 包含：

- `event`（枚举/字符串）
- `timestamp`（UTC 时间戳）
- `codex_app_server_pid`（如可用）
- OPTIONAL `usage` 映射（令牌计数）
- 所需的负载字段

重要的发出事件包括，例如：

- `session_started`
- `startup_failed`
- `turn_completed`
- `turn_failed`
- `turn_cancelled`
- `turn_ended_with_error`
- `turn_input_required`
- `approval_auto_approved`
- `unsupported_tool_call`
- `notification`
- `other_message`
- `malformed`

### 10.5 审批、工具调用和用户输入策略

审批、沙箱和用户输入行为是实现定义的。

策略要求：

- 每个实现 MUST 记录其选择的审批、沙箱和操作员确认立场。
- 审批请求和用户输入必需事件 MUST NOT 让运行无限期停顿。实现 MAY 满足它们、呈现给操作员、自动解决，或根据其文档化的策略使运行失败。

示例高信任行为：

- 自动批准会话的命令执行审批。
- 自动批准会话的文件变更审批。
- 将用户输入必需的轮次视为硬失败。

不支持的动态工具调用：

- 显式实现并由运行时通告的受支持动态工具调用 SHOULD 根据其扩展契约处理。
- 如果智能体请求不支持的动态工具调用，使用目标协议返回工具失败响应并继续会话。
- 这防止会话在不支持的工具执行路径上停顿。

可选客户端侧工具扩展：

- 实现 MAY 向 app-server 会话暴露有限的客户端侧工具集。
- 当前标准化的可选工具：`linear_graphql`。
- 如果实现，受支持的工具 SHOULD 在启动时使用目标 Codex app-server 版本支持的协议机制向 app-server 会话通告。
- 不支持的工具名称 SHOULD 仍使用目标协议返回失败结果并继续会话。

`linear_graphql` 扩展契约：

- 目的：使用 Symphony 为当前会话配置的跟踪器认证，对 Linear 执行原始 GraphQL 查询或变更。
- 可用性：仅在 `tracker.kind == "linear"` 且配置了有效的 Linear 认证时有意义。
- 首选输入形状：

  ```json
  {
    "query": "单个 GraphQL 查询或变更文档",
    "variables": {
      "optional": "graphql 变量对象"
    }
  }
  ```

- `query` MUST 是非空字符串。
- `query` MUST 恰好包含一个 GraphQL 操作。
- `variables` 是 OPTIONAL 的，当存在时 MUST 是 JSON 对象。
- 实现 MAY 额外接受原始 GraphQL 查询字符串作为简写输入。
- 每次工具调用执行一个 GraphQL 操作。
- 如果提供的文档包含多个操作，将工具调用作为无效输入拒绝。
- `operationName` 选择有意不在本扩展范围内。
- 重用活跃 Symphony 工作流/运行时配置中配置的 Linear 端点和认证；不要求编码智能体从磁盘读取原始令牌。
- 工具结果语义：
  - 传输成功 + 无顶层 GraphQL `errors` -> `success=true`
  - 存在顶层 GraphQL `errors` -> `success=false`，但保留 GraphQL 响应正文用于调试
  - 无效输入、缺失认证或传输失败 -> `success=false` 带错误负载
- 将 GraphQL 响应或错误负载作为结构化工具输出返回，供模型在会话中检查。

用户输入必需策略：

- 实现 MUST 记录目标协议的用户输入必需信号如何处理。
- 运行 MUST NOT 为等待用户输入而无限期停顿。
- 合规实现 MAY 使运行失败、将请求呈现给操作员、通过批准的操作员渠道满足，或根据其文档化的策略自动解决。
- 上述示例高信任行为立即使用户输入必需的轮次失败。

### 10.6 超时和错误映射

超时：

- `codex.read_timeout_ms`：启动和同步请求期间的请求/响应超时
- `codex.turn_timeout_ms`：总轮次流超时
- `codex.stall_timeout_ms`：由调度器基于事件不活跃强制执行

错误映射（RECOMMENDED 规范化类别）：

- `codex_not_found`
- `invalid_workspace_cwd`
- `response_timeout`
- `turn_timeout`
- `port_exit`
- `response_error`
- `turn_failed`
- `turn_cancelled`
- `turn_input_required`

### 10.7 智能体运行器契约

`Agent Runner` 封装工作区 + 提示词 + app-server 客户端。

行为：

1. 为问题创建/重用工作区。
2. 从工作流模板构建提示词。
3. 启动 app-server 会话。
4. 将 app-server 事件转发给调度器。
5. 在任何错误时，使 worker 尝试失败（调度器将重试）。

注意：

- 成功运行后工作区有意保留。

## 11. 问题跟踪器集成契约（Linear 兼容）

### 11.1 REQUIRED 操作

实现 MUST 支持以下跟踪器适配器操作：

1. `fetch_candidate_issues()`
   - 返回配置项目在配置活跃状态中的问题。

2. `fetch_issues_by_states(state_names)`
   - 用于启动终态清理。

3. `fetch_issue_states_by_ids(issue_ids)`
   - 用于活跃运行对账。

### 11.2 查询语义（Linear）

`tracker.kind == "linear"` 的 Linear 特定要求：

- `tracker.kind == "linear"`
- GraphQL 端点（默认 `https://api.linear.app/graphql`）
- 认证令牌在 `Authorization` 头中发送
- `tracker.project_slug` 映射到 Linear 项目的 `slugId`
- 候选问题查询使用 `project: { slugId: { eq: $projectSlug } }` 过滤项目
- 问题状态刷新查询使用 GraphQL 问题 ID，变量类型为 `[ID!]`
- 候选问题分页 REQUIRED
- 页面大小默认：`50`
- 网络超时：`30000 ms`

重要：

- Linear GraphQL schema 细节可能变化。保持查询构建隔离，并测试本规范 REQUIRED 的确切查询字段/类型。

非 Linear 实现 MAY 更改传输细节，但规范化输出 MUST 匹配第 4 节中的领域模型。

### 11.3 规范化规则

候选问题规范化 SHOULD 产生第 4.1.1 节中列出的字段。

额外规范化细节：

- `labels` -> 小写字符串
- `blocked_by` -> 从类型为 `blocks` 的反向关系中派生
- `priority` -> 仅整数（非整数变为 null）
- `created_at` 和 `updated_at` -> 解析 ISO-8601 时间戳

### 11.4 错误处理契约

RECOMMENDED 错误类别：

- `unsupported_tracker_kind`
- `missing_tracker_api_key`
- `missing_tracker_project_slug`
- `linear_api_request`（传输失败）
- `linear_api_status`（非 200 HTTP）
- `linear_graphql_errors`
- `linear_unknown_payload`
- `linear_missing_end_cursor`（分页完整性错误）

调度器对跟踪器错误的行为：

- 候选获取失败：记录日志并跳过此节拍的分派。
- 运行状态刷新失败：记录日志并保持活跃 worker 运行。
- 启动终态清理失败：记录警告并继续启动。

### 11.5 跟踪器写入（重要边界）

Symphony 不要求调度器中有一流的跟踪器写入 API。

- 工单变更（状态转换、评论、PR 元数据）通常由编码智能体使用工作流提示词定义的工具处理。
- 服务仍然是调度器/运行器和跟踪器读取器。
- 工作流特定的成功通常意味着"到达下一个交接状态"（例如 `Human Review`），而非跟踪器终态 `Done`。
- 如果实现了 `linear_graphql` 客户端侧工具扩展，它仍是智能体工具链的一部分，而非调度器业务逻辑。

## 12. 提示词构建和上下文组装

### 12.1 输入

提示词渲染的输入：

- `workflow.prompt_template`
- 规范化的 `issue` 对象
- OPTIONAL `attempt` 整数（重试/续运元数据）

### 12.2 渲染规则

- 使用严格变量检查渲染。
- 使用严格过滤器检查渲染。
- 将问题对象键转换为字符串以兼容模板。
- 保留嵌套数组/映射（标签、阻塞项），使模板可以迭代。

### 12.3 重试/续运语义

`attempt` SHOULD 传递给模板，因为工作流提示词可以为以下情况提供不同指令：

- 首次运行（`attempt` 为 null 或缺失）
- 成功前一会话后的续运运行
- 错误/超时/停顿后的重试

### 12.4 失败语义

如果提示词渲染失败：

- 立即使运行尝试失败。
- 让调度器将其视为任何其他 worker 失败并决定重试行为。

## 13. 日志、状态和可观测性

### 13.1 日志约定

问题相关日志的 REQUIRED 上下文字段：

- `issue_id`
- `issue_identifier`

编码智能体会话生命周期日志的 REQUIRED 上下文：

- `session_id`

消息格式要求：

- 使用稳定的 `key=value` 措辞。
- 包含动作结果（`completed`、`failed`、`retrying` 等）。
- 包含简洁的失败原因（如存在）。
- 避免记录大型原始负载，除非必要。

### 13.2 日志输出和接收器

本规范不规定日志写入位置（stderr、文件、远程接收器等）。

要求：

- 操作员 MUST 能够在不附加调试器的情况下看到启动/验证/分派失败。
- 实现 MAY 写入一个或多个接收器。
- 如果配置的日志接收器失败，服务 SHOULD 在可能时继续运行，并通过任何剩余接收器发出操作员可见的警告。

### 13.3 运行时快照 / 监控接口（OPTIONAL 但 RECOMMENDED）

如果实现暴露同步运行时快照（用于仪表板或监控），SHOULD 返回：

- `running`（运行中会话行列表）
- 每个运行行 SHOULD 包含 `turn_count`
- `retrying`（重试队列行列表）
- `codex_totals`
  - `input_tokens`
  - `output_tokens`
  - `total_tokens`
  - `seconds_running`（截至快照时间的聚合运行秒数，包括活跃会话）
- `rate_limits`（最新的编码智能体速率限制负载，如可用）

RECOMMENDED 的快照错误模式：

- `timeout`
- `unavailable`

### 13.4 OPTIONAL 人类可读状态展示面

人类可读的状态展示面（终端输出、仪表板等）是 OPTIONAL 且实现定义的。

如果存在，SHOULD 仅从调度器状态/指标提取数据，且 MUST NOT 成为正确性所 REQUIRED。

### 13.5 会话指标和令牌核算

令牌核算规则：

- 智能体事件可以在多种负载形状中包含令牌计数。
- 优先使用绝对线程总计（如可用），如：
  - `thread/tokenUsage/updated` 负载
  - 令牌计数包装事件中的 `total_token_usage`
- 对于仪表板/API 总计，忽略增量式负载（如 `last_token_usage`）。
- 从所选负载中的常见字段名称宽松提取 input/output/total 令牌计数。
- 对于绝对总计，跟踪相对于上次报告总计的增量以避免重复计数。
- 不要将通用 `usage` 映射视为累计总计，除非事件类型明确如此定义。
- 在调度器状态中累积聚合总计。

运行时核算：

- 运行时 SHOULD 在快照/渲染时作为活跃聚合报告。
- 实现 MAY 维护已结束会话的累计计数器，并在生成快照/状态视图时从 `running` 条目（例如 `started_at`）派生添加活跃会话的已用时间。
- 在会话结束时（正常退出或取消/终止）将运行时长秒数添加到累计已结束会话运行时。
- 不 REQUIRED 持续后台刷新运行时总计。

速率限制跟踪：

- 跟踪在任何智能体更新中看到的最新速率限制负载。
- 速率限制数据的任何人类可读呈现是实现定义的。

### 13.6 人性化智能体事件摘要（OPTIONAL）

原始智能体协议事件的人性化摘要是 OPTIONAL。

如果实现：

- 将其视为仅可观测性输出。
- 不要使调度器逻辑依赖于人性化字符串。

### 13.7 OPTIONAL HTTP 服务器扩展

本节定义了用于可观测性和运维控制的 OPTIONAL HTTP 接口。

如果实现：

- HTTP 服务器是扩展，不 REQUIRED 用于一致性。
- 实现 MAY 为仪表板提供服务器渲染的 HTML 或客户端应用。
- 仪表板/API MUST 仅是可观测性/控制展示面，且 MUST NOT 成为调度器正确性所 REQUIRED。

扩展配置：

- `server.port`（整数，OPTIONAL）
  - 启用 HTTP 服务器扩展。
  - `0` 请求临时端口用于本地开发和测试。
  - CLI `--port` 在两者同时存在时覆盖 `server.port`。

启用（扩展）：

- 当提供 CLI `--port` 参数时启动 HTTP 服务器。
- 当 `WORKFLOW.md` 前置数据中存在 `server.port` 时启动 HTTP 服务器。
- `server` 顶层键由此扩展拥有。
- 正 `server.port` 值绑定该端口。
- 实现 SHOULD 默认绑定环回地址（`127.0.0.1` 或等效主机），除非显式配置为其他值。
- HTTP 监听器设置的变更（例如 `server.port`）不需要热重绑定；需要重启的行为是合规的。

#### 13.7.1 人类可读仪表板（`/`）

- 在 `/` 托管人类可读仪表板。
- 返回的文档 SHOULD 描绘系统当前状态（例如活跃会话、重试延迟、令牌消耗、运行时总计、近期事件和健康/错误指标）。
- 实现可以选择这是服务器生成的 HTML 还是消费下方 JSON API 的客户端应用。

#### 13.7.2 JSON REST API（`/api/v1/*`）

在 `/api/v1/*` 下提供 JSON REST API，用于当前运行时状态和运维调试。

最少端点：

- `GET /api/v1/state`
  - 返回当前系统状态的摘要视图（运行中会话、重试队列/延迟、聚合令牌/运行时总计、最新速率限制以及任何额外跟踪的摘要字段）。
  - 建议的响应形状：

    ```json
    {
      "generated_at": "2026-02-24T20:15:30Z",
      "counts": {
        "running": 2,
        "retrying": 1
      },
      "running": [
        {
          "issue_id": "abc123",
          "issue_identifier": "MT-649",
          "state": "In Progress",
          "session_id": "thread-1-turn-1",
          "turn_count": 7,
          "last_event": "turn_completed",
          "last_message": "",
          "started_at": "2026-02-24T20:10:12Z",
          "last_event_at": "2026-02-24T20:14:59Z",
          "tokens": {
            "input_tokens": 1200,
            "output_tokens": 800,
            "total_tokens": 2000
          }
        }
      ],
      "retrying": [
        {
          "issue_id": "def456",
          "issue_identifier": "MT-650",
          "attempt": 3,
          "due_at": "2026-02-24T20:16:00Z",
          "error": "no available orchestrator slots"
        }
      ],
      "codex_totals": {
        "input_tokens": 5000,
        "output_tokens": 2400,
        "total_tokens": 7400,
        "seconds_running": 1834.2
      },
      "rate_limits": null
    }
    ```

- `GET /api/v1/<issue_identifier>`
  - 返回所标识问题的特定运行时/调试详情，包括实现跟踪的任何对调试有用的信息。
  - 建议的响应形状：

    ```json
    {
      "issue_identifier": "MT-649",
      "issue_id": "abc123",
      "status": "running",
      "workspace": {
        "path": "/tmp/symphony_workspaces/MT-649"
      },
      "attempts": {
        "restart_count": 1,
        "current_retry_attempt": 2
      },
      "running": {
        "session_id": "thread-1-turn-1",
        "turn_count": 7,
        "state": "In Progress",
        "started_at": "2026-02-24T20:10:12Z",
        "last_event": "notification",
        "last_message": "Working on tests",
        "last_event_at": "2026-02-24T20:14:59Z",
        "tokens": {
          "input_tokens": 1200,
          "output_tokens": 800,
          "total_tokens": 2000
        }
      },
      "retry": null,
      "logs": {
        "codex_session_logs": [
          {
            "label": "latest",
            "path": "/var/log/symphony/codex/MT-649/latest.log",
            "url": null
          }
        ]
      },
      "recent_events": [
        {
          "at": "2026-02-24T20:14:59Z",
          "event": "notification",
          "message": "Working on tests"
        }
      ],
      "last_error": null,
      "tracked": {}
    }
    ```

  - 如果问题对当前内存状态未知，返回 `404` 带错误响应（例如 `{"error":{"code":"issue_not_found","message":"..."}}`）。

- `POST /api/v1/refresh`
  - 排队一个即时的跟踪器轮询 + 对账周期（尽力触发；实现 MAY 合并重复请求）。
  - 建议的请求正文：空正文或 `{}`。
  - 建议的响应（`202 Accepted`）形状：

    ```json
    {
      "queued": true,
      "coalesced": false,
      "requested_at": "2026-02-24T20:15:30Z",
      "operations": ["poll", "reconcile"]
    }
    ```

API 设计说明：

- 上述 JSON 形状是互操作性和调试人体工学的 RECOMMENDED 基线。
- 实现 MAY 添加字段，但 SHOULD 避免在版本内破坏现有字段。
- 端点 SHOULD 是只读的，除了运维触发器如 `/refresh`。
- 已定义路由上不支持的方法 SHOULD 返回 `405 Method Not Allowed`。
- API 错误 SHOULD 使用 JSON 信封，如 `{"error":{"code":"...","message":"..."}}`。
- 如果仪表板是客户端应用，SHOULD 消费此 API 而非重复状态逻辑。

## 14. 失败模型和恢复策略

### 14.1 失败类别

1. `工作流/配置失败`
   - 缺失 `WORKFLOW.md`
   - 无效的 YAML 前置数据
   - 不支持的跟踪器类型或缺失的跟踪器凭据/项目 slug
   - 缺失编码智能体可执行文件

2. `工作区失败`
   - 工作区目录创建失败
   - 工作区填充/同步失败（实现定义；可能来自钩子）
   - 无效的工作区路径配置
   - 钩子超时/失败

3. `智能体会话失败`
   - 启动握手失败
   - 轮次失败/取消
   - 轮次超时
   - 用户输入请求被实现的文档化策略作为失败处理
   - 子进程退出
   - 会话停顿（无活动）

4. `跟踪器失败`
   - API 传输错误
   - 非 200 状态
   - GraphQL 错误
   - 格式错误的负载

5. `可观测性失败`
   - 快照超时
   - 仪表板渲染错误
   - 日志接收器配置失败

### 14.2 恢复行为

- 分派验证失败：
  - 跳过新分派。
  - 保持服务存活。
  - 在可能时继续对账。

- Worker 失败：
  - 转换为指数退避重试。

- 跟踪器候选获取失败：
  - 跳过此节拍。
  - 在下一个节拍重试。

- 对账状态刷新失败：
  - 保持当前 Worker。
  - 在下一个节拍重试。

- 仪表板/日志失败：
  - 不崩溃调度器。

### 14.3 部分状态恢复（重启）

当前设计有意将调度器状态保存在内存中。
重启恢复意味着服务可以通过轮询跟踪器状态和重用保留的工作区恢复有用操作。这并不意味着重试计时器、运行会话或活跃 worker 状态能在进程重启后存活。

重启后：

- 不会从先前进程内存恢复重试计时器。
- 不假设运行中会话可恢复。
- 服务通过以下方式恢复：
  - 启动终态工作区清理
  - 重新轮询活跃问题
  - 重新分派符合条件的工作

### 14.4 操作员干预点

操作员可以通过以下方式控制行为：

- 编辑 `WORKFLOW.md`（提示词和大多数运行时设置）。
- `WORKFLOW.md` 变更根据第 6.2 节自动检测并重新应用，无需重启。
- 在跟踪器中更改问题状态：
  - 终态 -> 运行中会话在对账时被停止且工作区被清理
  - 非活跃状态 -> 运行中会话被停止但不清理工作区
- 重启服务以进行进程恢复或部署（不是应用工作流配置变更的正常途径）。

## 15. 安全和运维安全

### 15.1 信任边界假设

每个实现定义自己的信任边界。

运维安全要求：

- 实现 SHOULD 清楚说明其目标是可信环境、更严格的环境还是两者兼顾。
- 实现 SHOULD 清楚说明其依赖自动批准的动作、操作员审批、更严格的沙箱还是这些控制的某种组合。
- 工作区隔离和路径验证是重要的基线控制，但它们不能替代实现选择的任何审批和沙箱策略。

### 15.2 文件系统安全要求

强制：

- 工作区路径 MUST 保留在配置的工作区根内。
- 编码智能体 cwd MUST 是当前运行的每个问题的工作区路径。
- 工作区目录名 MUST 使用净化后的标识符。

RECOMMENDED 的移植额外加固：

- 在专用操作系统用户下运行。
- 限制工作区根权限。
- 如果可能，在工作区根上挂载专用卷。

### 15.3 密钥处理

- 在工作流配置中支持 `$VAR` 间接引用。
- 不记录 API 令牌或机密环境值。
- 验证密钥存在但不打印它们。

### 15.4 钩子脚本安全

工作区钩子是来自 `WORKFLOW.md` 的任意 shell 脚本。

影响：

- 钩子是完全可信的配置。
- 钩子在工作区目录内运行。
- 钩子输出 SHOULD 在日志中截断。
- 钩子超时是 REQUIRED 的，以避免调度器挂起。

### 15.5 执行线束加固指导

对可能包含敏感数据或外部控制内容的仓库、问题跟踪器和其他输入运行 Codex 智能体可能是危险的。宽松部署可能导致数据泄露、破坏性变更，或如果智能体被诱导执行有害命令或使用过于强大的集成，可能导致完全的机器入侵。

实现 SHOULD 明确评估自身的风险概况，并在适当的地方加固执行线束。本规范有意不强制单一的加固立场，但实现 SHOULD NOT 假设跟踪器数据、仓库内容、提示词输入或工具参数仅仅因为它们来自正常工作流内就是完全可信的。

可能的加固措施包括：

- 收紧本规范其他地方描述的 Codex 审批和沙箱设置，而非使用最大宽松配置运行。
- 添加外部隔离层，如操作系统/容器/VM 沙箱、网络限制，或超出内置 Codex 策略控制的独立凭据。
- 过滤哪些 Linear 问题、项目、团队、标签或其他跟踪器源有资格分派，使不受信任或超出范围的任务不会自动到达智能体。
- 缩窄 `linear_graphql` 工具使其只能读取或变更预期项目范围内的数据，而非暴露通用的工作区范围跟踪器访问。
- 将智能体可用的客户端侧工具、凭据、文件系统路径和网络目的地减少到工作流所需的最小集合。

正确的控制是部署特定的，但实现 SHOULD 清楚记录它们，并将线束加固视为核心安全模型的一部分，而非可选的事后考虑。

## 16. 参考算法（语言无关）

### 16.1 服务启动

```text
function start_service():
  configure_logging()
  start_observability_outputs()
  start_workflow_watch(on_change=reload_and_reapply_workflow)

  state = {
    poll_interval_ms: get_config_poll_interval_ms(),
    max_concurrent_agents: get_config_max_concurrent_agents(),
    running: {},
    claimed: set(),
    retry_attempts: {},
    completed: set(),
    codex_totals: {input_tokens: 0, output_tokens: 0, total_tokens: 0, seconds_running: 0},
    codex_rate_limits: null
  }

  validation = validate_dispatch_config()
  if validation is not ok:
    log_validation_error(validation)
    fail_startup(validation)

  startup_terminal_workspace_cleanup()
  schedule_tick(delay_ms=0)

  event_loop(state)
```

### 16.2 轮询和分派节拍

```text
on_tick(state):
  state = reconcile_running_issues(state)

  validation = validate_dispatch_config()
  if validation is not ok:
    log_validation_error(validation)
    notify_observers()
    schedule_tick(state.poll_interval_ms)
    return state

  issues = tracker.fetch_candidate_issues()
  if issues failed:
    log_tracker_error()
    notify_observers()
    schedule_tick(state.poll_interval_ms)
    return state

  for issue in sort_for_dispatch(issues):
    if no_available_slots(state):
      break

    if should_dispatch(issue, state):
      state = dispatch_issue(issue, state, attempt=null)

  notify_observers()
  schedule_tick(state.poll_interval_ms)
  return state
```

### 16.3 对账活跃运行

```text
function reconcile_running_issues(state):
  state = reconcile_stalled_runs(state)

  running_ids = keys(state.running)
  if running_ids is empty:
    return state

  refreshed = tracker.fetch_issue_states_by_ids(running_ids)
  if refreshed failed:
    log_debug("keep workers running")
    return state

  for issue in refreshed:
    if issue.state in terminal_states:
      state = terminate_running_issue(state, issue.id, cleanup_workspace=true)
    else if issue.state in active_states:
      state.running[issue.id].issue = issue
    else:
      state = terminate_running_issue(state, issue.id, cleanup_workspace=false)

  return state
```

### 16.4 分派一个问题

```text
function dispatch_issue(issue, state, attempt):
  worker = spawn_worker(
    fn -> run_agent_attempt(issue, attempt, parent_orchestrator_pid) end
  )

  if worker spawn failed:
    return schedule_retry(state, issue.id, next_attempt(attempt), {
      identifier: issue.identifier,
      error: "failed to spawn agent"
    })

  state.running[issue.id] = {
    worker_handle,
    monitor_handle,
    identifier: issue.identifier,
    issue,
    session_id: null,
    codex_app_server_pid: null,
    last_codex_message: null,
    last_codex_event: null,
    last_codex_timestamp: null,
    codex_input_tokens: 0,
    codex_output_tokens: 0,
    codex_total_tokens: 0,
    last_reported_input_tokens: 0,
    last_reported_output_tokens: 0,
    last_reported_total_tokens: 0,
    retry_attempt: normalize_attempt(attempt),
    started_at: now_utc()
  }

  state.claimed.add(issue.id)
  state.retry_attempts.remove(issue.id)
  return state
```

### 16.5 Worker 尝试（工作区 + 提示词 + 智能体）

```text
function run_agent_attempt(issue, attempt, orchestrator_channel):
  workspace = workspace_manager.create_for_issue(issue.identifier)
  if workspace failed:
    fail_worker("workspace error")

  if run_hook("before_run", workspace.path) failed:
    fail_worker("before_run hook error")

  session = app_server.start_session(workspace=workspace.path)
  if session failed:
    run_hook_best_effort("after_run", workspace.path)
    fail_worker("agent session startup error")

  max_turns = config.agent.max_turns
  turn_number = 1

  while true:
    prompt = build_turn_prompt(workflow_template, issue, attempt, turn_number, max_turns)
    if prompt failed:
      app_server.stop_session(session)
      run_hook_best_effort("after_run", workspace.path)
      fail_worker("prompt error")

    turn_result = app_server.run_turn(
      session=session,
      prompt=prompt,
      issue=issue,
      on_message=(msg) -> send(orchestrator_channel, {codex_update, issue.id, msg})
    )

    if turn_result failed:
      app_server.stop_session(session)
      run_hook_best_effort("after_run", workspace.path)
      fail_worker("agent turn error")

    refreshed_issue = tracker.fetch_issue_states_by_ids([issue.id])
    if refreshed_issue failed:
      app_server.stop_session(session)
      run_hook_best_effort("after_run", workspace.path)
      fail_worker("issue state refresh error")

    issue = refreshed_issue[0] or issue

    if issue.state is not active:
      break

    if turn_number >= max_turns:
      break

    turn_number = turn_number + 1

  app_server.stop_session(session)
  run_hook_best_effort("after_run", workspace.path)

  exit_normal()
```

### 16.6 Worker 退出和重试处理

```text
on_worker_exit(issue_id, reason, state):
  running_entry = state.running.remove(issue_id)
  state = add_runtime_seconds_to_totals(state, running_entry)

  if reason == normal:
    state.completed.add(issue_id)  # 仅用于记录
    state = schedule_retry(state, issue_id, 1, {
      identifier: running_entry.identifier,
      delay_type: continuation
    })
  else:
    state = schedule_retry(state, issue_id, next_attempt_from(running_entry), {
      identifier: running_entry.identifier,
      error: format("worker exited: %reason")
    })

  notify_observers()
  return state
```

```text
on_retry_timer(issue_id, state):
  retry_entry = state.retry_attempts.pop(issue_id)
  if missing:
    return state

  candidates = tracker.fetch_candidate_issues()
  if fetch failed:
    return schedule_retry(state, issue_id, retry_entry.attempt + 1, {
      identifier: retry_entry.identifier,
      error: "retry poll failed"
    })

  issue = find_by_id(candidates, issue_id)
  if issue is null:
    state.claimed.remove(issue_id)
    return state

  if available_slots(state) == 0:
    return schedule_retry(state, issue_id, retry_entry.attempt + 1, {
      identifier: issue.identifier,
      error: "no available orchestrator slots"
    })

  return dispatch_issue(issue, state, attempt=retry_entry.attempt)
```

## 17. 测试和验证矩阵

合规实现 SHOULD 包含覆盖本规范定义行为的测试。

验证配置：

- `Core Conformance`（核心一致性）：所有合规实现 REQUIRED 的确定性测试。
- `Extension Conformance`（扩展一致性）：仅对实现选择交付的 OPTIONAL 功能 REQUIRED。
- `Real Integration Profile`（真实集成配置）：生产使用前 RECOMMENDED 的环境依赖冒烟/集成检查。

除非另有说明，第 17.1 节至第 17.7 节为 `Core Conformance`。以 `If ... is implemented` 开头的项目点为 `Extension Conformance`。

### 17.1 工作流和配置解析

- 工作流文件路径优先级：
  - 提供显式运行时路径时使用该路径
  - 未提供显式运行时路径时，cwd 默认为 `WORKFLOW.md`
- 工作流文件变更被检测并触发重新读取/重新应用，无需重启
- 无效工作流重载保持最后已知的有效配置并发出操作员可见的错误
- 缺失 `WORKFLOW.md` 返回类型化错误
- 无效 YAML 前置数据返回类型化错误
- 前置数据非映射返回类型化错误
- OPTIONAL 值缺失时应用配置默认值
- `tracker.kind` 验证强制执行当前支持的类型（`linear`）
- `tracker.api_key` 可用（包括 `$VAR` 间接引用）
- `$VAR` 解析对跟踪器 API 密钥和路径值可用
- `~` 路径展开可用
- `codex.command` 作为 shell 命令字符串保留
- 每状态并发覆盖映射规范化状态名并忽略无效值
- 提示词模板渲染 `issue` 和 `attempt`
- 提示词渲染在未知变量时失败（严格模式）

### 17.2 工作区管理器和安全

- 每个问题标识符的确定性工作区路径
- 缺失的工作区目录被创建
- 现有的工作区目录被重用
- 工作区位置的现有非目录路径被安全处理（按实现策略替换或失败）
- OPTIONAL 工作区填充/同步错误被暴露
- `after_create` 钩子仅在新工作区创建时运行
- `before_run` 钩子在每次尝试前运行，失败/超时中止当前尝试
- `after_run` 钩子在每次尝试后运行，失败/超时仅记录并忽略
- `before_remove` 钩子在清理时运行，失败/超时被忽略
- 工作区路径净化和根包含不变量在智能体启动前强制执行
- 智能体启动使用每个问题的工作区路径作为 cwd，拒绝根外路径

### 17.3 问题跟踪器客户端

- 候选问题获取使用活跃状态和项目 slug
- Linear 查询使用指定的项目过滤字段（`slugId`）
- 空 `fetch_issues_by_states([])` 不发 API 调用直接返回空
- 分页在多页间保持顺序
- 阻塞项从类型为 `blocks` 的反向关系规范化
- 标签规范化为小写
- 问题状态按 ID 刷新返回最小规范化问题
- 问题状态刷新查询使用 GraphQL ID 类型（`[ID!]`）如第 11.2 节所指定
- 请求错误、非 200、GraphQL 错误、格式错误负载的错误映射

### 17.4 调度器分派、对账和重试

- 分派排序顺序为优先级然后最旧创建时间
- 有非终态阻塞项的 `Todo` 问题不符合条件
- 有终态阻塞项的 `Todo` 问题符合条件
- 活跃状态问题刷新更新运行条目状态
- 非活跃状态停止运行中智能体但不清理工作区
- 终态停止运行中智能体并清理工作区
- 无运行中问题的对账是空操作
- 正常 Worker 退出安排短续运重试（attempt 1）
- 异常 Worker 退出以 10 秒为基的指数退避递增重试
- 重试退避上限使用配置的 `agent.max_retry_backoff_ms`
- 重试队列条目包含 attempt、due time、identifier 和 error
- 停顿检测终止停顿会话并安排重试
- 槽位耗尽以显式错误原因重新排队重试
- 如果实现快照 API，返回运行行、重试行、令牌总计和速率限制
- 如果实现快照 API，timeout/unavailable 情况被暴露

### 17.5 编码智能体 App-Server 客户端

- 启动命令使用工作区 cwd 并调用 `bash -lc <codex.command>`
- 会话启动遵循目标 Codex app-server 协议
- 客户端身份/能力负载在目标 Codex app-server 协议要求时有效
- 策略相关的启动负载使用实现文档化的审批/沙箱设置
- 目标协议暴露的线程和轮次身份被提取并用于发出 `session_started`
- 请求/响应读取超时被强制执行
- 轮次超时被强制执行
- 目标协议要求的传输帧被正确处理
- 对于基于 stdio 的传输，诊断 stderr 处理与协议流保持分离
- 命令/文件变更审批根据实现文档化的策略处理
- 不支持的动态工具调用被拒绝且不使会话停顿
- 用户输入请求根据实现文档化的策略处理且不无限期停顿
- 目标协议暴露的使用和速率限制遥测被提取
- 审批、用户输入必需、使用和速率限制信号根据目标协议解释
- 如果实现客户端侧工具，会话启动使用目标 app-server 协议通告受支持的工具规格
- 如果实现了 `linear_graphql` 客户端侧工具扩展：
  - 工具向会话通告
  - 有效的 `query`/`variables` 输入使用配置的 Linear 认证执行
  - 顶层 GraphQL `errors` 产生 `success=false` 同时保留 GraphQL 正文
  - 无效参数、缺失认证和传输失败返回结构化失败负载
  - 不支持的工具名称仍失败且不使会话停顿

### 17.6 可观测性

- 验证失败对操作员可见
- 结构化日志包含问题/会话上下文字段
- 日志接收器失败不崩溃编排
- 令牌/速率限制聚合在重复的智能体更新间保持正确
- 如果实现人类可读状态展示面，它从调度器状态驱动且不影响正确性
- 如果实现人性化事件摘要，它们覆盖关键包装器/智能体事件类而不改变调度器行为

### 17.7 CLI 和主机生命周期

- CLI 接受位置工作流路径参数（`path-to-WORKFLOW.md`）
- 未提供工作流路径参数时 CLI 使用 `./WORKFLOW.md`
- CLI 在不存在的显式工作流路径或缺失默认 `./WORKFLOW.md` 时报错
- CLI 干净地显示启动失败
- CLI 在应用正常启动和关闭时以成功退出
- CLI 在启动失败或主机进程异常退出时以非零退出

### 17.8 真实集成配置（RECOMMENDED）

这些检查为生产就绪而 RECOMMENDED，当凭据、网络访问或外部服务权限不可用时 MAY 在 CI 中跳过。

- 真实跟踪器冒烟测试可以使用由 `LINEAR_API_KEY` 或文档化的本地引导机制（例如 `~/.linear_api_key`）提供的有效凭据运行。
- 真实集成测试 SHOULD 使用隔离的测试标识符/工作区，并在实际可行时清理跟踪器产物。
- 跳过的真实集成测试 SHOULD 报告为跳过，而非静默视为通过。
- 如果真实集成配置在 CI 或发布验证中显式启用，失败 SHOULD 使该作业失败。

## 18. 实现检查清单（完成定义）

使用与第 17 节相同的验证配置：

- 第 18.1 节 = `Core Conformance`
- 第 18.2 节 = `Extension Conformance`
- 第 18.3 节 = `Real Integration Profile`

### 18.1 一致性所 REQUIRED

- 工作流路径选择支持显式运行时路径和 cwd 默认
- `WORKFLOW.md` 加载器，支持 YAML 前置数据 + 提示词正文分割
- 带默认值和 `$` 解析的类型化配置层
- `WORKFLOW.md` 的动态监视/重载/重新应用，用于配置和提示词
- 具有单一权威可变状态的轮询调度器
- 带候选获取 + 状态刷新 + 终态获取的问题跟踪器客户端
- 带净化每个问题工作区的工作区管理器
- 工作区生命周期钩子（`after_create`、`before_run`、`after_run`、`before_remove`）
- 钩子超时配置（`hooks.timeout_ms`，默认 `60000`）
- 带 JSON 行协议的编码智能体 app-server 子进程客户端
- Codex 启动命令配置（`codex.command`，默认 `codex app-server`）
- 带 `issue` 和 `attempt` 变量的严格提示词渲染
- 带正常退出后续运重试的指数重试队列
- 可配置的重试退避上限（`agent.max_retry_backoff_ms`，默认 5 分钟）
- 在终态/非活跃跟踪器状态上停止运行的对账
- 终态问题的工作区清理（启动扫描 + 活跃转换）
- 带 `issue_id`、`issue_identifier` 和 `session_id` 的结构化日志
- 操作员可见的可观测性（结构化日志；OPTIONAL 快照/状态展示面）

### 18.2 RECOMMENDED 扩展（不 REQUIRED 用于一致性）

- HTTP 服务器扩展遵循 CLI `--port` 优先于 `server.port`，使用安全的默认绑定主机，如果交付则暴露第 13.7 节中的基线端点/错误语义。
- `linear_graphql` 客户端侧工具扩展通过 app-server 会话使用配置的 Symphony 认证暴露原始 Linear GraphQL 访问。
- TODO：跨进程重启持久化重试队列和会话元数据。
- TODO：使可观测性设置在工作流前置数据中可配置，而不规定 UI 实现细节。
- TODO：在调度器中添加一流的跟踪器写入 API（评论/状态转换），而非仅通过智能体工具。
- TODO：添加超出 Linear 的可插拔问题跟踪器适配器。

### 18.3 生产前运维验证（RECOMMENDED）

- 使用有效凭据和网络访问运行第 17.8 节中的 `Real Integration Profile`。
- 在目标主机操作系统/shell 环境上验证钩子执行和工作流路径解析。
- 如果交付 OPTIONAL HTTP 服务器，在目标环境上验证配置的端口行为和环回/默认绑定预期。

## 附录 A. SSH Worker 扩展（OPTIONAL）

本附录描述了一个常见扩展配置，其中 Symphony 保留一个中央调度器，但通过 SSH 在一个或多个远程主机上执行 worker 运行。

扩展配置：

- `worker.ssh_hosts`（SSH 主机字符串列表，OPTIONAL）
  - 省略时，工作在本地运行。
- `worker.max_concurrent_agents_per_host`（正整数，OPTIONAL）
  - 跨配置 SSH 主机应用的共享每主机上限。

### A.1 执行模型

- 调度器仍然是轮询、声明、重试和对账的单一事实来源。
- `worker.ssh_hosts` 提供远程执行的候选 SSH 目标。
- 每个 worker 运行一次分配到一个主机，该主机与问题工作区一起成为运行的有效执行身份的一部分。
- `workspace.root` 在远程主机上解释，而非调度器主机上。
- 编码智能体 app-server 通过 SSH stdio 启动而非本地子进程，因此调度器仍拥有会话生命周期，即使命令远程执行。
- 一个 worker 生命周期内的续运轮次 SHOULD 保留在同一主机和工作区。
- 远程主机 SHOULD 满足与本地 worker 环境相同的基本契约：可达的 shell、可写的工作区根、编码智能体可执行文件以及任何所需的认证或仓库前置条件。

### A.2 调度说明

- SSH 主机 MAY 被视为分派池。
- 实现 MAY 在重试时优先使用先前使用的主机（当该主机仍可用时）。
- `worker.max_concurrent_agents_per_host` 是跨配置 SSH 主机的 OPTIONAL 共享每主机上限。
- 当所有 SSH 主机达到容量时，分派 SHOULD 等待而非静默回退到不同的执行模式。
- 实现 MAY 在原始主机不可用且工作尚未有意义地开始时故障转移到另一主机。
- 一旦运行已产生副作用，在另一主机上的透明重运行 SHOULD 被视为新尝试，而非不可见故障转移。

### A.3 需要考虑的问题

- 远程环境漂移：
  - 每个主机需要预期的 shell 环境、编码智能体可执行文件、认证和仓库前置条件。
- 工作区局部性：
  - 工作区通常是主机本地的，因此将问题移到不同主机通常是冷重启，除非存在共享存储。
- 路径和命令安全：
  - 一旦执行跨越机器边界，远程路径解析、shell 引用和工作区边界检查更为重要。
- 启动和故障转移语义：
  - 实现 SHOULD 区分主机连接/启动失败和工作区内智能体失败，以避免同一工单在多个主机上被意外重复执行。
- 主机健康和饱和：
  - 死亡或过载的主机 SHOULD 减少可用容量，而非导致重复执行或意外回退到本地工作。
- 清理和可观测性：
  - 操作员需要知道哪个主机拥有运行、其工作区在哪里，以及清理是否发生在正确的机器上。
