"""Bridge 层 - 实现 LangGraph 与 Metaflow 之间的双向适配和通信。

本模块提供两侧执行单元（LangGraph Node ↔ Metaflow Step）的双向适配器、
跨层事件总线以及统一的桥接配置/错误模型。设计目标是让两类异构运行时
能以最小耦合互调：图节点可将耗时任务卸载到 Metaflow，Flow 步骤的产出
也可注入回 LangGraph 的子图继续推进。
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "BridgeConfig",
    "BridgeError",
    "BridgeEvent",
    "BridgeEventBus",
    "BridgeEventKind",
    "NodeOutput",
    "NodeToStepAdapter",
    "SerializationFormat",
    "StepResult",
    "StepToGraphAdapter",
]


T_out = TypeVar("T_out")


class SerializationFormat(StrEnum):
    """序列化格式枚举。"""

    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"


class BridgeEventKind(StrEnum):
    """桥接事件类型。"""

    NODE_DISPATCHED = "node_dispatched"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    GRAPH_RESUMED = "graph_resumed"


class BridgeError(Exception):
    """桥接层统一错误类型。

    Attributes:
        layer: 错误来源层（``langgraph`` / ``metaflow`` / ``bridge``）。
        cause: 触发本异常的原始异常对象（可为 None）。
    """

    def __init__(
        self, message: str, *, layer: str = "bridge", cause: BaseException | None = None
    ) -> None:
        super().__init__(message)
        self.layer = layer
        self.cause = cause

    def __str__(self) -> str:
        base = super().__str__()
        return f"[{self.layer}] {base}"


class BridgeConfig(BaseModel):
    """桥接配置。"""

    model_config = ConfigDict(extra="forbid")

    timeout_seconds: float = Field(
        default=300.0, gt=0, description="单次桥接调用超时时间（秒）"
    )
    max_retries: int = Field(default=3, ge=0, description="失败后最大重试次数")
    retry_backoff_seconds: float = Field(
        default=1.0, ge=0, description="重试退避基数（线性递增）"
    )
    serialization: SerializationFormat = Field(
        default=SerializationFormat.JSON, description="跨层数据交换序列化格式"
    )
    enable_async_offload: bool = Field(
        default=True, description="是否允许异步卸载到 Metaflow"
    )
    event_buffer_size: int = Field(default=1024, ge=1, description="事件总线缓冲区大小")


class NodeOutput(BaseModel, Generic[T_out]):
    """LangGraph 节点输出的标准包装。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    node_name: str
    payload: Any = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel, Generic[T_out]):
    """Metaflow Step 结果的标准包装。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    step_name: str
    flow_name: str
    run_id: str | None = None
    payload: Any = None
    success: bool = True
    error: str | None = None
    started_at: float = Field(default_factory=time.time)
    finished_at: float | None = None


class BridgeEvent(BaseModel):
    """跨层事件。"""

    model_config = ConfigDict(extra="allow")

    kind: BridgeEventKind
    source: str
    target: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


@runtime_checkable
class _StepCallable(Protocol):
    """异步可调用 Step 接口。"""

    async def __call__(self, payload: Any, /, **kwargs: Any) -> Any: ...


@runtime_checkable
class _NodeCallable(Protocol):
    """异步可调用 Node 接口。"""

    async def __call__(self, payload: Any, /, **kwargs: Any) -> Any: ...


type EventListener = Callable[[BridgeEvent], Awaitable[None] | None]


class BridgeEventBus:
    """跨层事件总线。

    内部使用 :class:`asyncio.Queue` 缓冲事件，并将其分发给所有已订阅的
    监听器。支持背压（队列满时阻塞 ``publish``）与广播取消。
    """

    def __init__(self, *, buffer_size: int = 1024) -> None:
        self._queue: asyncio.Queue[BridgeEvent] = asyncio.Queue(maxsize=buffer_size)
        self._listeners: list[EventListener] = []
        self._dispatcher: asyncio.Task[None] | None = None
        self._closed = False

    def subscribe(self, listener: EventListener) -> Callable[[], None]:
        """订阅事件，返回用于取消订阅的回调。"""
        self._listeners.append(listener)

        def _unsubscribe() -> None:
            try:
                self._listeners.remove(listener)
            except ValueError:
                pass

        return _unsubscribe

    async def publish(self, event: BridgeEvent) -> None:
        """发布一个事件到总线。"""
        if self._closed:
            raise BridgeError("事件总线已关闭", layer="bridge")
        await self._queue.put(event)
        if self._dispatcher is None or self._dispatcher.done():
            self._dispatcher = asyncio.create_task(self._dispatch_loop())

    async def _dispatch_loop(self) -> None:
        while not self._closed:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.5)
            except TimeoutError:
                if self._queue.empty():
                    return
                continue
            for listener in list(self._listeners):
                try:
                    result = listener(event)
                    if isinstance(result, Awaitable):
                        await result
                except Exception:
                    continue

    async def close(self) -> None:
        """关闭总线并等待事件分发完成。"""
        self._closed = True
        if self._dispatcher is not None:
            try:
                await self._dispatcher
            except asyncio.CancelledError:
                pass


class NodeToStepAdapter:
    """将 LangGraph Node 输出适配为 Metaflow Step 输入并触发执行。

    适配器负责：

    1. 序列化 Node 输出 → 调用 Step；
    2. 在 ``BridgeConfig`` 控制下做超时/重试；
    3. 通过 :class:`BridgeEventBus` 广播事件。
    """

    def __init__(
        self,
        *,
        config: BridgeConfig | None = None,
        event_bus: BridgeEventBus | None = None,
    ) -> None:
        self._config = config or BridgeConfig()
        self._event_bus = event_bus or BridgeEventBus(
            buffer_size=self._config.event_buffer_size
        )

    @property
    def event_bus(self) -> BridgeEventBus:
        """关联的事件总线。"""
        return self._event_bus

    async def dispatch(
        self,
        step: _StepCallable,
        node_output: NodeOutput[Any],
        *,
        step_name: str,
        flow_name: str = "harness-flow",
        **kwargs: Any,
    ) -> StepResult[Any]:
        """将节点输出转换为参数并异步触发 Step 执行。

        Args:
            step: 实现 ``_StepCallable`` 协议的异步函数（占位 Metaflow Step）。
            node_output: 上游 LangGraph Node 的输出。
            step_name: 目标 Step 名称。
            flow_name: 所属 Flow 名称。
            **kwargs: 额外透传给 Step 的参数。
        """
        await self._event_bus.publish(
            BridgeEvent(
                kind=BridgeEventKind.NODE_DISPATCHED,
                source=node_output.node_name,
                target=f"{flow_name}.{step_name}",
                payload={"metadata": node_output.metadata},
            )
        )
        started = time.time()
        last_error: BaseException | None = None
        for attempt in range(self._config.max_retries + 1):
            try:
                payload = await asyncio.wait_for(
                    step(node_output.payload, **kwargs),
                    timeout=self._config.timeout_seconds,
                )
                result = StepResult(
                    step_name=step_name,
                    flow_name=flow_name,
                    payload=payload,
                    success=True,
                    started_at=started,
                    finished_at=time.time(),
                )
                await self._event_bus.publish(
                    BridgeEvent(
                        kind=BridgeEventKind.STEP_COMPLETED,
                        source=f"{flow_name}.{step_name}",
                        target=node_output.node_name,
                        payload={"attempt": attempt},
                    )
                )
                return result
            except (TimeoutError, Exception) as exc:
                last_error = exc
                if attempt >= self._config.max_retries:
                    break
                await asyncio.sleep(self._config.retry_backoff_seconds * (attempt + 1))

        await self._event_bus.publish(
            BridgeEvent(
                kind=BridgeEventKind.STEP_FAILED,
                source=f"{flow_name}.{step_name}",
                target=node_output.node_name,
                payload={"error": str(last_error)},
            )
        )
        raise BridgeError(
            f"Step {flow_name}.{step_name} 执行失败",
            layer="metaflow",
            cause=last_error,
        )


class StepToGraphAdapter:
    """将 Metaflow Step 结果注入回 LangGraph 子图继续执行。"""

    def __init__(
        self,
        *,
        config: BridgeConfig | None = None,
        event_bus: BridgeEventBus | None = None,
    ) -> None:
        self._config = config or BridgeConfig()
        self._event_bus = event_bus or BridgeEventBus(
            buffer_size=self._config.event_buffer_size
        )

    @property
    def event_bus(self) -> BridgeEventBus:
        """关联的事件总线。"""
        return self._event_bus

    async def resume(
        self,
        node: _NodeCallable,
        step_result: StepResult[Any],
        *,
        node_name: str,
        **kwargs: Any,
    ) -> NodeOutput[Any]:
        """将 ``step_result`` 注入到 ``node`` 中并执行，返回新的 ``NodeOutput``。

        Args:
            node: 接收 Step 结果的 LangGraph 节点（异步可调用）。
            step_result: 上游 Step 的执行结果。
            node_name: 当前节点名称（用于事件追踪）。
        """
        if not step_result.success:
            raise BridgeError(
                f"Step {step_result.flow_name}.{step_result.step_name} 失败: {step_result.error}",
                layer="metaflow",
            )
        try:
            payload = await asyncio.wait_for(
                node(step_result.payload, **kwargs),
                timeout=self._config.timeout_seconds,
            )
        except Exception as exc:
            raise BridgeError(
                f"节点 {node_name} 处理失败", layer="langgraph", cause=exc
            ) from exc
        output = NodeOutput(
            node_name=node_name,
            payload=payload,
            metadata={
                "from_step": step_result.step_name,
                "from_flow": step_result.flow_name,
                "run_id": step_result.run_id,
            },
        )
        await self._event_bus.publish(
            BridgeEvent(
                kind=BridgeEventKind.GRAPH_RESUMED,
                source=f"{step_result.flow_name}.{step_result.step_name}",
                target=node_name,
                payload={"run_id": step_result.run_id},
            )
        )
        return output
