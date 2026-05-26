"""令牌核算和运行时统计。

跟踪 Codex 会话的令牌使用（input/output/total）和运行时间。
优先使用绝对线程总计（thread/tokenUsage/updated），跟踪增量避免重复计数。
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class TokenUsage:
    """令牌用量汇总。"""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> dict[str, int]:
        """转换为字典。"""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
        }


class MetricsCollector:
    """令牌和运行时聚合器。

    累计跟踪所有 Codex 会话的令牌消耗和总运行时间。
    支持从 Codex 事件流中提取绝对令牌值或增量累加。
    """

    def __init__(self) -> None:
        self._totals: TokenUsage = TokenUsage()
        self._last_reported_input: int = 0
        self._last_reported_output: int = 0
        self._last_reported_total: int = 0
        self._start_time: datetime = datetime.now(UTC)

    def update_from_event(self, event: dict[str, Any]) -> None:
        """从 Codex 事件更新令牌计数。

        支持两种事件格式：
        1. 绝对值格式（thread 级 tokenUsage.updated）：直接覆盖总计。
        2. 增量格式（单次 turn 的 input/output）：累加到当前总计。

        Args:
            event: Codex 事件字典，可能包含 "tokenUsage" 键。
        """
        if "tokenUsage" not in event:
            return

        usage = event["tokenUsage"]

        # 优先使用绝对值（如果事件携带 updated 标记或包含 total 字段）
        if usage.get("updated"):
            # 绝对值模式：替换总计，避免重复计数
            new_input = usage.get("input_tokens", self._totals.input_tokens)
            new_output = usage.get("output_tokens", self._totals.output_tokens)
            new_total = usage.get("total_tokens", self._totals.total_tokens)
            self._totals = TokenUsage(
                input_tokens=new_input,
                output_tokens=new_output,
                total_tokens=new_total,
            )
        else:
            # 增量模式：计算与上次报告的差值并累加
            input_delta = usage.get("input_tokens", 0) - self._last_reported_input
            output_delta = usage.get("output_tokens", 0) - self._last_reported_output
            total_delta = usage.get("total_tokens", 0) - self._last_reported_total

            # 只累加正增量，避免事件乱序导致负数
            if input_delta > 0:
                self._totals.input_tokens += input_delta
            if output_delta > 0:
                self._totals.output_tokens += output_delta
            if total_delta > 0:
                self._totals.total_tokens += total_delta

        # 记住当前报告值，用于下次增量计算
        self._last_reported_input = usage.get("input_tokens", self._last_reported_input)
        self._last_reported_output = usage.get("output_tokens", self._last_reported_output)
        self._last_reported_total = usage.get("total_tokens", self._last_reported_total)

    def update_from_thread(self, thread_data: dict[str, Any]) -> None:
        """从线程级别的 tokenUsage 数据更新总计（绝对值）。

        适用于 Codex thread 对象中的 tokenUsage 字段。

        Args:
            thread_data: 包含 tokenUsage 的线程数据。
        """
        usage = thread_data.get("tokenUsage")
        if usage is None:
            return

        self._totals = TokenUsage(
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )

    @property
    def totals(self) -> TokenUsage:
        """当前令牌用量汇总。"""
        return self._totals

    @property
    def seconds_running(self) -> float:
        """从启动到现在的运行秒数。"""
        return (datetime.now(UTC) - self._start_time).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """导出为字典，包含令牌用量和运行时间。"""
        return {
            **self._totals.to_dict(),
            "seconds_running": self.seconds_running,
        }

    def reset(self) -> None:
        """重置所有计数器和计时器。"""
        self._totals = TokenUsage()
        self._last_reported_input = 0
        self._last_reported_output = 0
        self._last_reported_total = 0
        self._start_time = datetime.now(UTC)
