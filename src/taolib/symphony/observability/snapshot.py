"""运行时快照生成。

生成系统状态的完整快照，用于 HTTP API 和调试。
快照包含运行中的 worker、重试队列、令牌汇总和配置参数。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class SystemSnapshot:
    """系统运行时快照。

    Attributes:
        running: 运行中的 worker 信息列表。
        retrying: 重试队列条目列表。
        completed_count: 已完成的问题数。
        codex_totals: 令牌用量与运行时间汇总。
        rate_limits: 当前速率限制状态（可能为 None）。
        poll_interval_ms: 当前轮询间隔（毫秒）。
        max_concurrent_agents: 最大并发代理数。
        generated_at: 快照生成时间（ISO 8601）。
    """

    running: list[dict[str, Any]]
    retrying: list[dict[str, Any]]
    completed_count: int
    codex_totals: dict[str, Any]
    rate_limits: dict[str, Any] | None
    poll_interval_ms: int
    max_concurrent_agents: int
    generated_at: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于 JSON 序列化）。"""
        return asdict(self)


@dataclass
class RunningEntry:
    """运行中 worker 的摘要信息。"""

    issue_id: str
    identifier: str
    turn_count: int = 0
    codex_total_tokens: int = 0
    last_codex_event: str | None = None
    started_at: str = ""
    session_id: str | None = None
    codex_input_tokens: int = 0
    codex_output_tokens: int = 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return asdict(self)


@dataclass
class RetryEntry:
    """重试队列条目。"""

    issue_id: str
    identifier: str
    attempt: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return asdict(self)


class SnapshotGenerator:
    """从 OrchestratorState 生成快照。

    SnapshotGenerator 接收编排器的运行时状态，将其投影为
    可 JSON 序列化的 SystemSnapshot 对象，供 HTTP API 和仪表板使用。
    """

    def generate(self, state: Any) -> SystemSnapshot:
        """从编排器状态生成系统快照。

        Args:
            state: 编排器运行时状态对象，需要包含以下属性：
                - running: dict[str, RunningEntry] — 运行中的 worker 映射
                - retry_attempts: dict[str, RetryEntry] — 重试队列映射
                - completed: set[str] — 已完成的问题 ID 集合
                - codex_totals: TokenUsage — 令牌用量汇总
                - codex_rate_limits: dict | None — 速率限制
                - poll_interval_ms: int — 轮询间隔
                - max_concurrent_agents: int — 最大并发数

        Returns:
            SystemSnapshot 实例。
        """
        running = [
            {
                "issue_id": issue_id,
                "identifier": entry.identifier,
                "turn_count": getattr(entry, "turn_count", 0),
                "tokens": {
                    "input_tokens": getattr(entry, "codex_input_tokens", 0),
                    "output_tokens": getattr(entry, "codex_output_tokens", 0),
                    "total_tokens": getattr(entry, "codex_total_tokens", 0),
                },
                "last_event": getattr(entry, "last_codex_event", None),
                "started_at": self._format_datetime(getattr(entry, "started_at", None)),
                "session_id": getattr(entry, "session_id", None),
            }
            for issue_id, entry in state.running.items()
        ]

        retrying = [
            {
                "issue_id": getattr(entry, "issue_id", ""),
                "identifier": getattr(entry, "identifier", ""),
                "attempt": getattr(entry, "attempt", 0),
                "error": getattr(entry, "error", None),
            }
            for entry in state.retry_attempts.values()
        ]

        # 提取令牌汇总
        codex_totals = self._extract_codex_totals(state)

        return SystemSnapshot(
            running=running,
            retrying=retrying,
            completed_count=len(state.completed),
            codex_totals=codex_totals,
            rate_limits=getattr(state, "codex_rate_limits", None),
            poll_interval_ms=getattr(state, "poll_interval_ms", 0),
            max_concurrent_agents=getattr(state, "max_concurrent_agents", 0),
        )

    @staticmethod
    def _format_datetime(value: Any) -> str | None:
        """将日期时间值格式化为 ISO 8601 字符串。"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(value, str):
            return value
        return str(value)

    @staticmethod
    def _extract_codex_totals(state: Any) -> dict[str, Any]:
        """从编排器状态提取令牌汇总。"""
        totals = getattr(state, "codex_totals", None)
        if totals is None:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "seconds_running": 0,
            }

        # 如果 totals 有 to_dict 方法（MetricsCollector 实例）
        if hasattr(totals, "to_dict"):
            return totals.to_dict()

        # 如果是 dataclass
        if hasattr(totals, "__dataclass_fields__"):
            return asdict(totals)

        # 如果是普通对象
        return {
            "input_tokens": getattr(totals, "input_tokens", 0),
            "output_tokens": getattr(totals, "output_tokens", 0),
            "total_tokens": getattr(totals, "total_tokens", 0),
            "seconds_running": getattr(totals, "seconds_running", 0),
        }
