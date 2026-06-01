"""实时状态检查器 - 订阅、对比与展示统一状态管理器中的状态。

依托 :class:`UnifiedStateManager` 暴露的快照 / 订阅能力，本模块提供：

* :class:`StateInspector.inspect` 一次性快照；
* :class:`StateInspector.watch` / :meth:`awatch` 推送式订阅；
* :class:`StateInspector.diff` 快照差分；
* :class:`StateInspector.history` 变更历史回放；
* 树形结构格式化展示嵌套状态。
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..core.state import (
    StateChangeEvent,
    StatePayload,
    StateSnapshot,
    UnifiedStateManager,
)

__all__ = [
    "InspectorConfig",
    "StateDiff",
    "StateInspector",
    "WatchCallback",
    "format_state_tree",
]


type WatchCallback = Callable[[StateChangeEvent], Awaitable[None] | None]
"""订阅回调签名：接收状态变更事件，可同步或异步处理。"""


class InspectorConfig(BaseModel):
    """状态检查器配置。"""

    model_config = ConfigDict(extra="allow")

    poll_interval_seconds: float = Field(default=1.0, gt=0)
    max_history: int = Field(default=100, ge=1)
    include_sources: list[str] = Field(default_factory=list)
    exclude_keys: list[str] = Field(default_factory=list)
    verbosity: int = Field(
        default=1, ge=0, le=3, description="0=简略 1=常规 2=详细 3=全量"
    )


class StateDiff(BaseModel):
    """两个状态快照的差异报告。"""

    model_config = ConfigDict(extra="allow")

    thread_id: str
    added: dict[str, Any] = Field(default_factory=dict)
    removed: dict[str, Any] = Field(default_factory=dict)
    changed: dict[str, dict[str, Any]] = Field(default_factory=dict)
    version_from: int = 0
    version_to: int = 0

    @property
    def is_empty(self) -> bool:
        """差异是否为空。"""
        return not (self.added or self.removed or self.changed)


def _filter_payload(payload: StatePayload, cfg: InspectorConfig) -> StatePayload:
    if not cfg.exclude_keys:
        return payload
    return {k: v for k, v in payload.items() if k not in cfg.exclude_keys}


def format_state_tree(payload: Any, *, indent: int = 0, prefix: str = "") -> str:
    """将嵌套状态格式化为树形文本。"""
    pad = "  " * indent
    if isinstance(payload, dict):
        if not payload:
            return f"{pad}{prefix}{{}}"
        lines = [f"{pad}{prefix}{{"] if prefix else [f"{pad}{{"]
        for key, value in payload.items():
            child = format_state_tree(value, indent=indent + 1, prefix=f"{key}: ")
            lines.append(child)
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    if isinstance(payload, list | tuple):
        if not payload:
            return f"{pad}{prefix}[]"
        lines = [f"{pad}{prefix}["]
        for idx, item in enumerate(payload):
            lines.append(format_state_tree(item, indent=indent + 1, prefix=f"[{idx}] "))
        lines.append(f"{pad}]")
        return "\n".join(lines)
    return f"{pad}{prefix}{payload!r}"


class StateInspector:
    """状态检查器 - 提供同步/异步两种交互方式查看与监听状态。"""

    def __init__(
        self,
        manager: UnifiedStateManager,
        *,
        config: InspectorConfig | None = None,
    ) -> None:
        """构造检查器。

        Args:
            manager: 关联的统一状态管理器。
            config: 检查器配置，缺省采用默认值。
        """
        self._manager = manager
        self._config = config or InspectorConfig()
        self._history: dict[str, list[StateChangeEvent]] = {}
        self._unsubscribe = manager.subscribe(self._on_event)

    # ------------------------------------------------------------------
    # 快照与订阅
    # ------------------------------------------------------------------
    async def inspect(self, thread_id: str) -> StateSnapshot:
        """获取指定线程的当前聚合快照。"""
        snapshot = await self._manager.snapshot(thread_id)
        if not self._config.exclude_keys:
            return snapshot
        return snapshot.model_copy(
            update={"payload": _filter_payload(snapshot.payload, self._config)}
        )

    def watch(
        self,
        thread_id: str,
        callback: WatchCallback,
    ) -> Callable[[], None]:
        """同步订阅状态变更事件，返回取消订阅函数。"""

        def _filtered(event: StateChangeEvent) -> Awaitable[None] | None:
            if event.thread_id != thread_id:
                return None
            return callback(event)

        return self._manager.subscribe(_filtered)

    async def awatch(
        self,
        thread_id: str,
        callback: WatchCallback,
        *,
        stop: asyncio.Event | None = None,
    ) -> None:
        """异步监听：阻塞直到 ``stop`` 被设置后取消订阅。"""
        unsubscribe = self.watch(thread_id, callback)
        try:
            stopper = stop or asyncio.Event()
            await stopper.wait()
        finally:
            unsubscribe()

    # ------------------------------------------------------------------
    # 历史与差分
    # ------------------------------------------------------------------
    def history(
        self,
        thread_id: str,
        *,
        limit: int | None = None,
    ) -> list[StateChangeEvent]:
        """获取指定线程的状态变更历史。"""
        events = list(self._history.get(thread_id, []))
        if limit is None or limit >= len(events):
            return events
        return events[-limit:]

    @staticmethod
    def diff(
        snapshot_a: StateSnapshot,
        snapshot_b: StateSnapshot,
    ) -> StateDiff:
        """对比两个快照，返回结构化差异。"""
        a = snapshot_a.payload
        b = snapshot_b.payload
        keys_a = set(a)
        keys_b = set(b)
        added = {k: b[k] for k in keys_b - keys_a}
        removed = {k: a[k] for k in keys_a - keys_b}
        changed: dict[str, dict[str, Any]] = {}
        for key in keys_a & keys_b:
            if a[key] != b[key]:
                changed[key] = {"from": a[key], "to": b[key]}
        return StateDiff(
            thread_id=snapshot_b.thread_id,
            added=added,
            removed=removed,
            changed=changed,
            version_from=snapshot_a.version,
            version_to=snapshot_b.version,
        )

    # ------------------------------------------------------------------
    # 格式化
    # ------------------------------------------------------------------
    def format(self, snapshot: StateSnapshot) -> str:
        """以树形结构格式化快照。"""
        header = (
            f"<thread={snapshot.thread_id} version={snapshot.version} "
            f"source={snapshot.source}>"
        )
        body = format_state_tree(snapshot.payload)
        return f"{header}\n{body}"

    def close(self) -> None:
        """注销监听。"""
        self._unsubscribe()

    # ------------------------------------------------------------------
    # 内部回调
    # ------------------------------------------------------------------
    def _on_event(self, event: StateChangeEvent) -> None:
        bucket = self._history.setdefault(event.thread_id, [])
        bucket.append(event)
        overflow = len(bucket) - self._config.max_history
        if overflow > 0:
            del bucket[:overflow]

    @property
    def known_threads(self) -> Iterable[str]:
        """已观测到的线程 ID 集合。"""
        return tuple(self._history)
