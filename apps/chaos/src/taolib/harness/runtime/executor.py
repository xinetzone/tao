"""统一执行引擎 - 封装 LangGraph 图执行和 Metaflow Flow 运行的统一接口。

:class:`UnifiedExecutor` 根据任务类型路由到 :class:`GraphExecutor` 或
:class:`FlowExecutor`，并统一以 :class:`ExecutionResult` 返回执行产物。
LangGraph / Metaflow 在当前环境可能未安装，本模块通过 ``TYPE_CHECKING``
守卫与 duck typing 实现可插拔接入。
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:  # pragma: no cover
    pass  # type: ignore

__all__ = [
    "ExecutionContext",
    "ExecutionMode",
    "ExecutionResult",
    "ExecutionStatus",
    "ExecutorBackend",
    "FlowExecutor",
    "GraphExecutor",
    "UnifiedExecutor",
]


class ExecutionMode(StrEnum):
    """执行模式。"""

    LOCAL = "local"
    REMOTE = "remote"
    BATCH = "batch"


class ExecutionStatus(StrEnum):
    """执行状态。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutorBackend(StrEnum):
    """执行后端类型。"""

    GRAPH = "graph"
    FLOW = "flow"


class ExecutionContext(BaseModel):
    """执行上下文。

    携带 ``thread_id``、可序列化配置和任意元数据，贯穿单次执行的全生命周期。
    """

    model_config = ConfigDict(extra="allow")

    thread_id: str = Field(default_factory=lambda: f"thread-{uuid.uuid4().hex[:12]}")
    run_id: str = Field(default_factory=lambda: f"run-{uuid.uuid4().hex[:12]}")
    config: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    mode: ExecutionMode = ExecutionMode.LOCAL
    timeout_seconds: float | None = Field(default=None, gt=0)


class ExecutionResult(BaseModel):
    """执行结果。"""

    model_config = ConfigDict(extra="allow")

    run_id: str
    backend: ExecutorBackend
    status: ExecutionStatus
    output: Any = None
    error: str | None = None
    started_at: float
    finished_at: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> float | None:
        """执行耗时（秒）。"""
        if self.finished_at is None:
            return None
        return self.finished_at - self.started_at


@runtime_checkable
class _Executor(Protocol):
    """执行器统一协议。"""

    async def execute(
        self,
        target: Any,
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutionResult: ...


class GraphExecutor:
    """LangGraph 图执行器。

    支持两类目标：

    * 已编译的 ``CompiledGraph``（具有 ``ainvoke`` 方法）；
    * ``StateGraph`` 实例（先调用 ``compile()`` 再 ``ainvoke``）。

    若目标不具备上述能力，则回退到将其作为异步可调用对象直接调用。
    """

    backend = ExecutorBackend.GRAPH

    def __init__(self, *, compile_options: dict[str, Any] | None = None) -> None:
        self._compile_options = compile_options or {}

    async def execute(
        self,
        target: Any,
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutionResult:
        """执行 LangGraph 图。"""
        started = time.time()
        try:
            compiled = self._maybe_compile(target)
            invoke = self._resolve_invoke(compiled)
            cfg = {"configurable": {"thread_id": context.thread_id, **context.config}}
            coro = invoke(inputs, cfg)
            output = await self._with_timeout(coro, context.timeout_seconds)
            return ExecutionResult(
                run_id=context.run_id,
                backend=self.backend,
                status=ExecutionStatus.SUCCEEDED,
                output=output,
                started_at=started,
                finished_at=time.time(),
                metadata={"thread_id": context.thread_id},
            )
        except asyncio.CancelledError:
            return ExecutionResult(
                run_id=context.run_id,
                backend=self.backend,
                status=ExecutionStatus.CANCELLED,
                started_at=started,
                finished_at=time.time(),
            )
        except Exception as exc:
            return ExecutionResult(
                run_id=context.run_id,
                backend=self.backend,
                status=ExecutionStatus.FAILED,
                error=str(exc),
                started_at=started,
                finished_at=time.time(),
            )

    # ------------------------------------------------------------------
    def _maybe_compile(self, target: Any) -> Any:
        compile_fn = getattr(target, "compile", None)
        if callable(compile_fn) and not hasattr(target, "ainvoke"):
            return compile_fn(**self._compile_options)
        return target

    def _resolve_invoke(self, target: Any) -> Callable[[Any, Any], Awaitable[Any]]:
        if hasattr(target, "ainvoke"):
            return lambda payload, cfg: target.ainvoke(payload, cfg)
        if callable(target):

            async def _runner(payload: Any, cfg: Any) -> Any:
                result = target(payload, cfg)
                if isinstance(result, Awaitable):
                    return await result
                return result

            return _runner
        raise TypeError(f"无法解析图对象的执行入口: {type(target).__name__}")

    @staticmethod
    async def _with_timeout(coro: Awaitable[Any], timeout: float | None) -> Any:
        if timeout is None:
            return await coro
        return await asyncio.wait_for(coro, timeout=timeout)


class FlowExecutor:
    """Metaflow Flow 执行器。

    在真实环境中应通过 ``Runner`` API 触发 Flow，本实现为离线友好的占位：
    若目标暴露了异步 ``run`` / ``arun`` 方法则调用，否则将其作为可调用对象。
    """

    backend = ExecutorBackend.FLOW

    def __init__(self, *, mode: ExecutionMode = ExecutionMode.LOCAL) -> None:
        self._mode = mode

    async def execute(
        self,
        target: Any,
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutionResult:
        """执行 Metaflow Flow。"""
        started = time.time()
        try:
            invoker = self._resolve_invoker(target)
            coro = invoker(inputs, context)
            output = await GraphExecutor._with_timeout(coro, context.timeout_seconds)
            return ExecutionResult(
                run_id=context.run_id,
                backend=self.backend,
                status=ExecutionStatus.SUCCEEDED,
                output=output,
                started_at=started,
                finished_at=time.time(),
                metadata={"mode": self._mode.value},
            )
        except asyncio.CancelledError:
            return ExecutionResult(
                run_id=context.run_id,
                backend=self.backend,
                status=ExecutionStatus.CANCELLED,
                started_at=started,
                finished_at=time.time(),
            )
        except Exception as exc:
            return ExecutionResult(
                run_id=context.run_id,
                backend=self.backend,
                status=ExecutionStatus.FAILED,
                error=str(exc),
                started_at=started,
                finished_at=time.time(),
            )

    def _resolve_invoker(
        self, target: Any
    ) -> Callable[[dict[str, Any], ExecutionContext], Awaitable[Any]]:
        for method_name in ("arun", "run_async", "execute_async"):
            method = getattr(target, method_name, None)
            if callable(method):

                async def _runner(
                    inputs: dict[str, Any], ctx: ExecutionContext, _m: Any = method
                ) -> Any:
                    return await _m(inputs, ctx)

                return _runner

        run = getattr(target, "run", None)
        if callable(run):

            async def _sync_runner(
                inputs: dict[str, Any], ctx: ExecutionContext
            ) -> Any:
                return await asyncio.to_thread(run, inputs, ctx)

            return _sync_runner

        if callable(target):

            async def _callable_runner(
                inputs: dict[str, Any], ctx: ExecutionContext
            ) -> Any:
                result = target(inputs, ctx)
                if isinstance(result, Awaitable):
                    return await result
                return result

            return _callable_runner

        raise TypeError(f"无法解析 Flow 对象的执行入口: {type(target).__name__}")


class UnifiedExecutor:
    """统一执行入口。

    根据 ``backend`` 路由到 :class:`GraphExecutor` 或 :class:`FlowExecutor`。
    用户也可注入自定义后端实现。
    """

    def __init__(
        self,
        *,
        graph_executor: GraphExecutor | None = None,
        flow_executor: FlowExecutor | None = None,
    ) -> None:
        self._graph = graph_executor or GraphExecutor()
        self._flow = flow_executor or FlowExecutor()

    async def execute(
        self,
        target: Any,
        inputs: dict[str, Any] | None = None,
        *,
        backend: ExecutorBackend | str,
        context: ExecutionContext | None = None,
    ) -> ExecutionResult:
        """执行目标对象。

        Args:
            target: 待执行的图 / Flow 对象。
            inputs: 输入数据，缺省为空字典。
            backend: 后端类型（``graph`` 或 ``flow``）。
            context: 执行上下文，缺省自动生成。
        """
        ctx = context or ExecutionContext()
        payload = inputs or {}
        kind = ExecutorBackend(backend) if isinstance(backend, str) else backend
        match kind:
            case ExecutorBackend.GRAPH:
                return await self._graph.execute(target, payload, ctx)
            case ExecutorBackend.FLOW:
                return await self._flow.execute(target, payload, ctx)
            case _:
                raise ValueError(f"未知的执行后端: {backend!r}")

    @property
    def graph(self) -> GraphExecutor:
        """图执行器。"""
        return self._graph

    @property
    def flow(self) -> FlowExecutor:
        """Flow 执行器。"""
        return self._flow
