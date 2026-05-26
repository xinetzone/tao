"""AppServer 事件解析与令牌核算。

将 Codex app-server 输出的原始 JSON 事件解析为结构化对象，
并跟踪增量令牌使用情况。
"""

from dataclasses import dataclass, field

__all__ = ["AppServerEvent", "TurnResult", "parse_event", "TokenAccounting"]


@dataclass(frozen=True)
class AppServerEvent:
    """AppServer 事件。"""

    type: str
    """事件类型（如 message, tool_call, turn_complete, error）。"""

    data: dict = field(default_factory=dict)
    """事件附加数据。"""

    raw: dict = field(default_factory=dict)
    """原始 JSON 字典。"""


@dataclass(frozen=True)
class TurnResult:
    """轮次执行结果。"""

    success: bool
    """轮次是否成功完成。"""

    token_usage: int = 0
    """本轮使用的令牌数。"""

    error: str | None = None
    """错误信息（如果轮次失败）。"""


def parse_event(raw: dict) -> AppServerEvent:
    """将原始 JSON 字典解析为 AppServerEvent。

    Args:
        raw: 从 app-server 接收的原始 JSON 行。

    Returns:
        结构化的事件对象。
    """
    event_type = raw.get("type", "unknown")
    # 提取嵌套的 data 字段，若无则使用整个 raw
    data = raw.get("data", {})
    if isinstance(data, str):
        data = {"text": data}
    return AppServerEvent(type=event_type, data=data, raw=raw)


class TokenAccounting:
    """令牌使用追踪器。

    增量跟踪每个轮次和会话的令牌消耗，
    支持按轮次和总量查询。
    """

    def __init__(self) -> None:
        self._per_turn: list[int] = []
        self._total: int = 0

    @property
    def total(self) -> int:
        """累计使用的令牌总数。"""
        return self._total

    @property
    def turns(self) -> int:
        """已记录的轮次数。"""
        return len(self._per_turn)

    def record(self, tokens: int) -> None:
        """记录一个轮次的令牌使用。

        Args:
            tokens: 本轮使用的令牌数。
        """
        if tokens < 0:
            return
        self._per_turn.append(tokens)
        self._total += tokens

    def get_turn_usage(self, turn_index: int) -> int:
        """获取指定轮次的令牌使用量。

        Args:
            turn_index: 轮次索引（从 0 开始）。

        Returns:
            令牌使用量，索引越界返回 0。
        """
        if 0 <= turn_index < len(self._per_turn):
            return self._per_turn[turn_index]
        return 0

    def reset(self) -> None:
        """重置所有计数。"""
        self._per_turn.clear()
        self._total = 0
