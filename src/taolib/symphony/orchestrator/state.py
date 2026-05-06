"""Symphony 编排器状态与数据结构定义。

定义编排器运行时所需的内部数据结构，包括：
- RunningEntry：活跃 worker 的运行时跟踪条目
- RetryEntry：计划重试条目
- CodexTotals：聚合令牌消耗与运行时统计
- OrchestratorState：编排器单一权威内存状态

外部依赖的类型（Issue、SymphonyConfig 等）从各自子包导入，
此处仅定义编排器私有的运行时状态。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import asyncio


# ============================================================================
# 运行时数据结构
# ============================================================================


@dataclass
class RunningEntry:
    """活跃 worker 的运行时跟踪条目。

    对应规范 §4.1.6 Live Session 和 §4.1.5 Run Attempt 的组合。
    由编排器在分派时创建，在 worker 退出时移除。

    Attributes:
        worker_task: 关联的 asyncio.Task 实例（Python 3.14 命名 task 内省）
        identifier: 人类可读的问题标识符（如 ABC-123）
        issue_state: 跟踪器问题当前状态快照（用于每状态并发计数）
        session_id: 编码智能体会话 ID（<thread_id>-<turn_id>）
        codex_app_server_pid: Codex app-server 进程 PID
        last_codex_event: 最后接收的 Codex 事件类型
        last_codex_timestamp: 最后 Codex 事件的时间戳
        last_codex_message: 最后 Codex 事件的摘要消息
        codex_input_tokens: 当前会话累计输入令牌数
        codex_output_tokens: 当前会话累计输出令牌数
        codex_total_tokens: 当前会话累计总令牌数
        last_reported_input_tokens: 上次已报告的输入令牌（用于增量计算）
        last_reported_output_tokens: 上次已报告的输出令牌
        last_reported_total_tokens: 上次已报告的总令牌
        turn_count: 当前 worker 生命周期内已启动的编码智能体轮次数量
        retry_attempt: 当前重试尝试序号（首次为 None）
        started_at: worker 启动时间
    """

    worker_task: asyncio.Task = field(default=None)  # type: ignore[assignment]
    identifier: str = ""
    issue_state: str = ""
    session_id: str | None = None
    codex_app_server_pid: str | None = None
    last_codex_event: str | None = None
    last_codex_timestamp: datetime | None = None
    last_codex_message: str | None = None
    codex_input_tokens: int = 0
    codex_output_tokens: int = 0
    codex_total_tokens: int = 0
    last_reported_input_tokens: int = 0
    last_reported_output_tokens: int = 0
    last_reported_total_tokens: int = 0
    turn_count: int = 0
    retry_attempt: int | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetryEntry:
    """计划重试条目。

    对应规范 §4.1.7 Retry Entry。
    当 worker 退出后，编排器根据退出原因创建重试条目。

    Attributes:
        issue_id: 稳定的跟踪器内部 ID
        identifier: 人类可读标识符
        attempt: 重试尝试序号（从 1 开始）
        due_at_ms: 单调时钟时间戳（毫秒），重试到期时间
        timer_handle: asyncio 计时器句柄，用于取消重试
        error: 失败原因（None 表示续运重试）
    """

    issue_id: str = ""
    identifier: str = ""
    attempt: int = 1
    due_at_ms: float = 0.0  # 单调时钟时间戳
    timer_handle: asyncio.TimerHandle = field(default=None)  # type: ignore[assignment]
    error: str | None = None


@dataclass
class CodexTotals:
    """聚合令牌消耗与运行时统计。

    对应规范 §4.1.8 Orchestrator Runtime State 中的 codex_totals。

    Attributes:
        input_tokens: 累计输入令牌数
        output_tokens: 累计输出令牌数
        total_tokens: 累计总令牌数
        seconds_running: 聚合运行秒数（包括已结束会话）
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    seconds_running: float = 0.0


@dataclass
class OrchestratorState:
    """编排器单一权威内存状态。

    对应规范 §4.1.8。所有状态变更由编排器串行化执行，
    避免并发修改导致的重复分派或状态不一致。

    Attributes:
        poll_interval_ms: 当前有效轮询间隔
        max_concurrent_agents: 当前有效全局并发限制
        running: issue_id -> RunningEntry 映射
        claimed: 已保留/运行中/重试中的问题 ID 集合
        retry_attempts: issue_id -> RetryEntry 映射
        completed: 已完成的问题 ID 集合（仅记录，不控制分派）
        codex_totals: 聚合令牌 + 运行秒数
        codex_rate_limits: 来自智能体事件的最新速率限制快照
    """

    poll_interval_ms: int = 30_000
    max_concurrent_agents: int = 10
    running: dict[str, RunningEntry] = field(default_factory=dict)
    claimed: set[str] = field(default_factory=set)
    retry_attempts: dict[str, RetryEntry] = field(default_factory=dict)
    completed: set[str] = field(default_factory=set)
    codex_totals: CodexTotals = field(default_factory=CodexTotals)
    codex_rate_limits: dict[str, Any] | None = None
