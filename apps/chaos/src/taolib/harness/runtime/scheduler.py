"""混合调度器 - 管理 LangGraph 微任务和 Metaflow 宏任务的优先级路由。

调度策略：

* **短时/对话型** 任务（如 LLM 单步调用）路由到 LangGraph 通道；
* **长时/批处理** 任务（如向量索引、数据预处理）卸载到 Metaflow 通道。

支持基于优先级队列的任务出队、基于 ``depends_on`` 的拓扑排序与基于
``asyncio.Semaphore`` 的并发上限控制（限制 LLM API QPS）。
"""

from __future__ import annotations

import asyncio
import heapq
import time
import uuid
from collections.abc import Awaitable, Callable, Iterable
from enum import IntEnum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from .executor import (
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    ExecutorBackend,
    UnifiedExecutor,
)

__all__ = [
    "HybridScheduler",
    "SchedulableTask",
    "SchedulerConfig",
    "TaskDescriptor",
    "TaskPriority",
]


class TaskPriority(IntEnum):
    """任务优先级（数值越小优先级越高）。"""

    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100
    BACKGROUND = 1000


@runtime_checkable
class SchedulableTask(Protocol):
    """可调度任务统一抽象。

    实现者需暴露 ``task_id``、目标、后端类型、优先级与依赖列表。
    """

    task_id: str
    backend: ExecutorBackend
    priority: TaskPriority
    depends_on: tuple[str, ...]

    async def run(
        self, executor: UnifiedExecutor, context: ExecutionContext
    ) -> ExecutionResult: ...


class TaskDescriptor(BaseModel):
    """任务描述符 - :class:`SchedulableTask` 的标准实现。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    task_id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:12]}")
    name: str = ""
    target: Any = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    backend: ExecutorBackend = ExecutorBackend.GRAPH
    priority: TaskPriority = TaskPriority.NORMAL
    depends_on: tuple[str, ...] = Field(default_factory=tuple)
    estimated_duration_seconds: float | None = Field(default=None, gt=0)
    requires_llm: bool = Field(
        default=False, description="是否消耗受限的 LLM API 配额（用于并发控制）"
    )

    async def run(
        self, executor: UnifiedExecutor, context: ExecutionContext
    ) -> ExecutionResult:
        """通过统一执行器运行该任务。"""
        return await executor.execute(
            self.target, self.inputs, backend=self.backend, context=context
        )


class SchedulerConfig(BaseModel):
    """调度器配置。"""

    model_config = ConfigDict(extra="forbid")

    max_concurrency: int = Field(default=8, ge=1, description="全局最大并发任务数")
    max_llm_concurrency: int = Field(default=4, ge=1, description="LLM 通道并发上限")
    long_task_threshold_seconds: float = Field(
        default=30.0, gt=0, description="超过该阈值的任务自动路由至 Flow 后端"
    )
    auto_route: bool = Field(
        default=True, description="是否根据 estimated_duration 自动路由"
    )


type _PriorityKey = tuple[int, float, int]


class _PriorityQueue:
    """支持稳定排序的最小堆优先级队列。"""

    def __init__(self) -> None:
        self._heap: list[tuple[_PriorityKey, str, SchedulableTask]] = []
        self._counter = 0

    def push(self, task: SchedulableTask) -> None:
        self._counter += 1
        key: _PriorityKey = (int(task.priority), time.time(), self._counter)
        heapq.heappush(self._heap, (key, task.task_id, task))

    def pop(self) -> SchedulableTask:
        return heapq.heappop(self._heap)[2]

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)


class HybridScheduler:
    """混合调度器。

    将提交的任务排序后依次执行，遵守依赖、优先级与并发上限。
    通过 :meth:`submit` 注册任务，通过 :meth:`run_all` 等待全部完成。
    """

    def __init__(
        self,
        executor: UnifiedExecutor | None = None,
        config: SchedulerConfig | None = None,
    ) -> None:
        self._executor = executor or UnifiedExecutor()
        self._config = config or SchedulerConfig()
        self._tasks: dict[str, SchedulableTask] = {}
        self._results: dict[str, ExecutionResult] = {}
        self._global_sem = asyncio.Semaphore(self._config.max_concurrency)
        self._llm_sem = asyncio.Semaphore(self._config.max_llm_concurrency)
        self._task_listeners: list[
            Callable[[str, ExecutionResult], Awaitable[None] | None]
        ] = []

    # ------------------------------------------------------------------
    # 提交 / 监听
    # ------------------------------------------------------------------
    def submit(self, task: SchedulableTask) -> str:
        """提交任务到调度器。"""
        if task.task_id in self._tasks:
            raise ValueError(f"任务 ID 重复: {task.task_id}")
        self._maybe_auto_route(task)
        self._tasks[task.task_id] = task
        return task.task_id

    def submit_many(self, tasks: Iterable[SchedulableTask]) -> list[str]:
        """批量提交任务。"""
        return [self.submit(t) for t in tasks]

    def on_complete(
        self, listener: Callable[[str, ExecutionResult], Awaitable[None] | None]
    ) -> None:
        """注册任务完成回调。"""
        self._task_listeners.append(listener)

    # ------------------------------------------------------------------
    # 调度执行
    # ------------------------------------------------------------------
    async def run_all(
        self, *, base_context: ExecutionContext | None = None
    ) -> dict[str, ExecutionResult]:
        """运行已提交的全部任务，按拓扑顺序与优先级调度。"""
        order = self._topological_order()
        levels = self._group_by_level(order)
        for level in levels:
            queue = _PriorityQueue()
            for task_id in level:
                queue.push(self._tasks[task_id])
            await self._run_level(queue, base_context)
        return dict(self._results)

    async def _run_level(
        self, queue: _PriorityQueue, base_context: ExecutionContext | None
    ) -> None:
        coros: list[Awaitable[None]] = []
        while queue:
            task = queue.pop()
            coros.append(self._run_one(task, base_context))
        await asyncio.gather(*coros)

    async def _run_one(
        self, task: SchedulableTask, base_context: ExecutionContext | None
    ) -> None:
        ctx = self._derive_context(task, base_context)
        async with self._global_sem:
            sem = self._llm_sem if getattr(task, "requires_llm", False) else None
            if sem is not None:
                async with sem:
                    result = await task.run(self._executor, ctx)
            else:
                result = await task.run(self._executor, ctx)
        self._results[task.task_id] = result
        await self._notify(task.task_id, result)

    async def _notify(self, task_id: str, result: ExecutionResult) -> None:
        for listener in list(self._task_listeners):
            try:
                ret = listener(task_id, result)
                if isinstance(ret, Awaitable):
                    await ret
            except Exception:
                continue

    # ------------------------------------------------------------------
    # 路由与依赖排序
    # ------------------------------------------------------------------
    def _maybe_auto_route(self, task: SchedulableTask) -> None:
        if not self._config.auto_route:
            return
        duration = getattr(task, "estimated_duration_seconds", None)
        if duration is None:
            return
        if (
            duration >= self._config.long_task_threshold_seconds
            and task.backend is ExecutorBackend.GRAPH
        ):
            try:
                task.backend = ExecutorBackend.FLOW  # type: ignore[misc]
            except AttributeError:
                pass

    def _topological_order(self) -> list[str]:
        in_degree: dict[str, int] = dict.fromkeys(self._tasks, 0)
        adjacency: dict[str, list[str]] = {tid: [] for tid in self._tasks}
        for tid, task in self._tasks.items():
            for dep in task.depends_on:
                if dep not in self._tasks:
                    raise KeyError(f"任务 {tid} 依赖未提交的任务: {dep}")
                adjacency[dep].append(tid)
                in_degree[tid] += 1
        ready = [tid for tid, d in in_degree.items() if d == 0]
        order: list[str] = []
        while ready:
            ready.sort(key=lambda t: (int(self._tasks[t].priority), t))
            current = ready.pop(0)
            order.append(current)
            for nxt in adjacency[current]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    ready.append(nxt)
        if len(order) != len(self._tasks):
            raise ValueError("任务依赖存在循环，无法拓扑排序")
        return order

    def _group_by_level(self, order: list[str]) -> list[list[str]]:
        level_of: dict[str, int] = {}
        for tid in order:
            deps = self._tasks[tid].depends_on
            level_of[tid] = 0 if not deps else max(level_of[d] for d in deps) + 1
        max_level = max(level_of.values(), default=-1)
        levels: list[list[str]] = [[] for _ in range(max_level + 1)]
        for tid, lvl in level_of.items():
            levels[lvl].append(tid)
        return levels

    def _derive_context(
        self, task: SchedulableTask, base: ExecutionContext | None
    ) -> ExecutionContext:
        if base is None:
            return ExecutionContext(metadata={"task_id": task.task_id})
        meta = {**base.metadata, "task_id": task.task_id}
        return base.model_copy(update={"metadata": meta, "run_id": task.task_id})

    # ------------------------------------------------------------------
    @property
    def results(self) -> dict[str, ExecutionResult]:
        """已完成任务的结果映射。"""
        return dict(self._results)

    def succeeded(self) -> list[str]:
        """成功任务 ID 列表。"""
        return [
            tid
            for tid, r in self._results.items()
            if r.status is ExecutionStatus.SUCCEEDED
        ]

    def failed(self) -> list[str]:
        """失败任务 ID 列表。"""
        return [
            tid
            for tid, r in self._results.items()
            if r.status is ExecutionStatus.FAILED
        ]
