"""统一状态管理器 - 跨 LangGraph Checkpointer 和 Metaflow Artifact Store 的一致性状态视图。

本模块提供 Harness 系统的核心状态抽象，聚合 LangGraph 与 Metaflow 两侧的
状态源，对外暴露线程安全的、按 ``thread_id`` 分区的统一视图，并通过观察者
模式向上层广播状态变更事件。
"""

from __future__ import annotations

import asyncio
import copy
import time
from collections.abc import Awaitable, Callable, Iterable
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "StateChangeEvent",
    "StateChangeKind",
    "StateListener",
    "StateSnapshot",
    "StateView",
    "UnifiedStateManager",
]


type StatePayload = dict[str, Any]
"""状态负载的标准结构：键值对形式的可序列化字典。"""

type ThreadId = str
"""线程标识符：用于在多会话/多任务场景下隔离状态分区。"""


class StateChangeKind(StrEnum):
    """状态变更事件类型。"""

    CREATED = "created"
    UPDATED = "updated"
    SNAPSHOT = "snapshot"
    DELETED = "deleted"


class StateSnapshot(BaseModel):
    """状态快照 - 不可变的状态视图。

    用于持久化、调试与时间回溯，包含完整的状态负载、版本号与时间戳。
    """

    model_config = ConfigDict(frozen=True, extra="allow")

    thread_id: ThreadId
    version: int = Field(default=0, ge=0)
    payload: StatePayload = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    source: str = Field(default="unified", description="状态来源层标识")


class StateChangeEvent(BaseModel):
    """状态变更事件 - 由 :class:`UnifiedStateManager` 广播给所有监听器。"""

    model_config = ConfigDict(extra="allow")

    thread_id: ThreadId
    kind: StateChangeKind
    version: int
    snapshot: StateSnapshot
    timestamp: float = Field(default_factory=time.time)


@runtime_checkable
class StateView(Protocol):
    """状态视图接口 - 所有底层状态源（LangGraph/Metaflow）的统一抽象。

    实现者需提供按 ``thread_id`` 维度的读取、写入、快照能力。
    """

    async def read(self, thread_id: ThreadId) -> StatePayload:
        """读取指定线程的当前状态。"""
        ...

    async def write(self, thread_id: ThreadId, payload: StatePayload) -> None:
        """写入指定线程的状态。"""
        ...

    async def snapshot(self, thread_id: ThreadId) -> StateSnapshot:
        """生成指定线程的不可变快照。"""
        ...


type StateListener = Callable[[StateChangeEvent], Awaitable[None] | None]
"""状态监听器签名：接收变更事件，可同步或异步执行。"""


class _InMemoryStateView:
    """内存型 :class:`StateView` 默认实现，作为 LangGraph/Metaflow 未注入时的回退。"""

    def __init__(self, source: str = "memory") -> None:
        self._source = source
        self._store: dict[ThreadId, StatePayload] = {}
        self._versions: dict[ThreadId, int] = {}
        self._lock = asyncio.Lock()

    async def read(self, thread_id: ThreadId) -> StatePayload:
        async with self._lock:
            return copy.deepcopy(self._store.get(thread_id, {}))

    async def write(self, thread_id: ThreadId, payload: StatePayload) -> None:
        async with self._lock:
            self._store[thread_id] = copy.deepcopy(payload)
            self._versions[thread_id] = self._versions.get(thread_id, 0) + 1

    async def snapshot(self, thread_id: ThreadId) -> StateSnapshot:
        async with self._lock:
            return StateSnapshot(
                thread_id=thread_id,
                version=self._versions.get(thread_id, 0),
                payload=copy.deepcopy(self._store.get(thread_id, {})),
                source=self._source,
            )


class UnifiedStateManager:
    """统一状态管理器 - 聚合多个 :class:`StateView` 并广播变更事件。

    典型用法::

        manager = UnifiedStateManager()
        manager.attach_view("langgraph", lg_view)
        manager.attach_view("metaflow", mf_view)
        manager.subscribe(my_listener)
        await manager.update("thread-1", {"step": "started"})
    """

    def __init__(
        self,
        *,
        primary_source: str = "langgraph",
        views: dict[str, StateView] | None = None,
    ) -> None:
        """构造统一状态管理器。

        Args:
            primary_source: 主状态源名称，``read`` 优先从该源读取。
            views: 初始注入的状态视图映射，键为来源名，值为 ``StateView`` 实现。
        """
        self._primary = primary_source
        self._views: dict[str, StateView] = dict(views or {})
        if primary_source not in self._views:
            self._views[primary_source] = _InMemoryStateView(source=primary_source)
        self._listeners: list[StateListener] = []
        self._versions: dict[ThreadId, int] = {}
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # 视图管理
    # ------------------------------------------------------------------
    def attach_view(self, name: str, view: StateView) -> None:
        """注册或替换一个底层状态视图。"""
        self._views[name] = view

    def detach_view(self, name: str) -> StateView | None:
        """注销指定的状态视图，返回原视图（若存在）。"""
        return self._views.pop(name, None)

    @property
    def sources(self) -> list[str]:
        """所有已注册的状态源名称。"""
        return list(self._views)

    # ------------------------------------------------------------------
    # 订阅 / 通知
    # ------------------------------------------------------------------
    def subscribe(self, listener: StateListener) -> Callable[[], None]:
        """订阅状态变更事件，返回用于取消订阅的回调。"""
        self._listeners.append(listener)

        def _unsubscribe() -> None:
            try:
                self._listeners.remove(listener)
            except ValueError:
                pass

        return _unsubscribe

    async def _emit(self, event: StateChangeEvent) -> None:
        for listener in list(self._listeners):
            result = listener(event)
            if isinstance(result, Awaitable):
                await result

    # ------------------------------------------------------------------
    # 读写接口
    # ------------------------------------------------------------------
    async def read(
        self,
        thread_id: ThreadId,
        *,
        source: str | None = None,
    ) -> StatePayload:
        """读取指定线程的状态。

        Args:
            thread_id: 线程分区标识。
            source: 指定状态源名称；缺省时使用主状态源。
        """
        view = self._resolve_view(source)
        return await view.read(thread_id)

    async def write(
        self,
        thread_id: ThreadId,
        payload: StatePayload,
        *,
        source: str | None = None,
        broadcast: bool = True,
    ) -> StateSnapshot:
        """写入指定线程的状态并广播事件。

        Args:
            thread_id: 线程分区标识。
            payload: 待写入的状态负载。
            source: 写入到哪个状态源；缺省写主源。
            broadcast: 是否广播变更事件。
        """
        view = self._resolve_view(source)
        async with self._lock:
            await view.write(thread_id, payload)
            self._versions[thread_id] = self._versions.get(thread_id, 0) + 1
            version = self._versions[thread_id]
        snapshot = StateSnapshot(
            thread_id=thread_id,
            version=version,
            payload=copy.deepcopy(payload),
            source=source or self._primary,
        )
        if broadcast:
            kind = StateChangeKind.CREATED if version == 1 else StateChangeKind.UPDATED
            await self._emit(
                StateChangeEvent(
                    thread_id=thread_id,
                    kind=kind,
                    version=version,
                    snapshot=snapshot,
                )
            )
        return snapshot

    async def update(
        self,
        thread_id: ThreadId,
        delta: StatePayload,
        *,
        source: str | None = None,
    ) -> StateSnapshot:
        """以增量方式合并状态：在原状态基础上做浅合并后写回。"""
        current = await self.read(thread_id, source=source)
        merged = {**current, **delta}
        return await self.write(thread_id, merged, source=source)

    async def snapshot(self, thread_id: ThreadId) -> StateSnapshot:
        """生成跨所有状态源聚合后的快照视图。"""
        aggregated: StatePayload = {}
        for name, view in self._views.items():
            partial = await view.read(thread_id)
            if partial:
                aggregated[name] = partial
        version = self._versions.get(thread_id, 0)
        snap = StateSnapshot(
            thread_id=thread_id,
            version=version,
            payload=aggregated,
            source="unified",
        )
        await self._emit(
            StateChangeEvent(
                thread_id=thread_id,
                kind=StateChangeKind.SNAPSHOT,
                version=version,
                snapshot=snap,
            )
        )
        return snap

    async def delete(self, thread_id: ThreadId) -> None:
        """删除指定线程在所有状态源中的记录（若底层支持）。"""
        for view in self._views.values():
            writer = getattr(view, "delete", None)
            if callable(writer):
                maybe = writer(thread_id)
                if isinstance(maybe, Awaitable):
                    await maybe
            else:
                await view.write(thread_id, {})
        version = self._versions.get(thread_id, 0)
        snap = StateSnapshot(
            thread_id=thread_id, version=version, payload={}, source="unified"
        )
        await self._emit(
            StateChangeEvent(
                thread_id=thread_id,
                kind=StateChangeKind.DELETED,
                version=version,
                snapshot=snap,
            )
        )

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------
    def _resolve_view(self, source: str | None) -> StateView:
        name = source or self._primary
        try:
            return self._views[name]
        except KeyError as exc:
            raise KeyError(f"未注册的状态源: {name!r}; 可用: {self.sources}") from exc

    def known_threads(self) -> Iterable[ThreadId]:
        """返回当前已记录版本号的所有线程 ID。"""
        return tuple(self._versions)
