"""性能剖析器 - 节点耗时、LLM 延迟、Token 吞吐与内存峰值的统一采集。

提供 :class:`PerformanceProfiler` 作为入口，搭配 :func:`profiled` 装饰器
对函数级别打点，最后由 :class:`HotspotAnalyzer` 识别耗时热点。
"""

from __future__ import annotations

import asyncio
import functools
import statistics
import time
import tracemalloc
import uuid
from collections.abc import Awaitable, Callable, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ClassVar, ParamSpec, TypeVar

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "HotspotAnalyzer",
    "HotspotEntry",
    "PerformanceProfiler",
    "ProfileConfig",
    "ProfileResult",
    "ProfileSample",
    "profiled",
]


P = ParamSpec("P")
R = TypeVar("R")


class ProfileConfig(BaseModel):
    """剖析配置。"""

    model_config = ConfigDict(extra="allow")

    sample_rate: float = Field(default=1.0, gt=0, le=1.0)
    collect_memory: bool = True
    collect_tokens: bool = True
    collect_llm: bool = True
    output_path: Path | None = None


class ProfileSample(BaseModel):
    """单条耗时打点。"""

    model_config = ConfigDict(extra="allow")

    label: str
    category: str = "node"
    started_at: float
    finished_at: float
    duration_seconds: float
    metadata: dict[str, Any] = Field(default_factory=dict)
    tokens: dict[str, float] = Field(default_factory=dict)


class HotspotEntry(BaseModel):
    """热点条目。"""

    model_config = ConfigDict(extra="allow")

    label: str
    category: str
    count: int
    total_seconds: float
    mean_seconds: float
    max_seconds: float
    share: float = Field(description="占总耗时比例")


class ProfileResult(BaseModel):
    """剖析结果。"""

    model_config = ConfigDict(extra="allow")

    profile_id: str = Field(default_factory=lambda: f"prof-{uuid.uuid4().hex[:10]}")
    started_at: float
    finished_at: float
    samples: list[ProfileSample] = Field(default_factory=list)
    total_duration_seconds: float = 0.0
    memory_peak_bytes: int = 0
    token_throughput: float = 0.0
    llm_call_count: int = 0
    llm_latency_p95: float = 0.0

    @property
    def sample_count(self) -> int:
        """打点总数。"""
        return len(self.samples)


class PerformanceProfiler:
    """性能剖析器。"""

    _ACTIVE: ClassVar[list[PerformanceProfiler]] = []

    def __init__(self, *, config: ProfileConfig | None = None) -> None:
        self._config = config or ProfileConfig()
        self._samples: list[ProfileSample] = []
        self._started_at: float | None = None
        self._finished_at: float | None = None
        self._memory_started = False

    # ------------------------------------------------------------------
    # 启停控制
    # ------------------------------------------------------------------
    def start(self) -> None:
        """启动剖析（清空缓冲并开启内存追踪）。"""
        self._samples.clear()
        self._started_at = time.perf_counter()
        if self._config.collect_memory and not tracemalloc.is_tracing():
            tracemalloc.start()
            self._memory_started = True
        if self not in PerformanceProfiler._ACTIVE:
            PerformanceProfiler._ACTIVE.append(self)

    def stop(self) -> ProfileResult:
        """停止剖析并生成结果。"""
        self._finished_at = time.perf_counter()
        peak = 0
        if self._memory_started and tracemalloc.is_tracing():
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self._memory_started = False
        if self in PerformanceProfiler._ACTIVE:
            PerformanceProfiler._ACTIVE.remove(self)
        return self._build_result(peak)

    # ------------------------------------------------------------------
    # 上下文与剖析入口
    # ------------------------------------------------------------------
    @contextmanager
    def session(self) -> Any:
        """上下文管理器：``with profiler.session(): ...``。"""
        self.start()
        try:
            yield self
        finally:
            self._finished_at = time.perf_counter()

    def profile(
        self,
        execution: Callable[[], R],
        *,
        label: str = "execution",
    ) -> tuple[R, ProfileResult]:
        """同步剖析单次执行。"""
        self.start()
        try:
            with self.measure(label, category="execution"):
                value = execution()
        finally:
            result = self.stop()
        return value, result

    async def aprofile(
        self,
        execution: Callable[[], Awaitable[R]],
        *,
        label: str = "execution",
    ) -> tuple[R, ProfileResult]:
        """异步剖析单次执行。"""
        self.start()
        try:
            async with self.ameasure(label, category="execution"):
                value = await execution()
        finally:
            result = self.stop()
        return value, result

    # ------------------------------------------------------------------
    # 打点 API
    # ------------------------------------------------------------------
    @contextmanager
    def measure(
        self,
        label: str,
        *,
        category: str = "node",
        metadata: Mapping[str, Any] | None = None,
        tokens: Mapping[str, float] | None = None,
    ) -> Any:
        """同步打点上下文。"""
        started = time.perf_counter()
        wall_start = time.time()
        try:
            yield
        finally:
            finished = time.perf_counter()
            self._record(
                label, category, wall_start, finished - started, metadata, tokens
            )

    class _AsyncMeasure:
        def __init__(
            self,
            profiler: PerformanceProfiler,
            label: str,
            category: str,
            metadata: Mapping[str, Any] | None,
            tokens: Mapping[str, float] | None,
        ) -> None:
            self._profiler = profiler
            self._label = label
            self._category = category
            self._metadata = metadata
            self._tokens = tokens
            self._started: float = 0.0
            self._wall_start: float = 0.0

        async def __aenter__(self) -> PerformanceProfiler._AsyncMeasure:
            self._started = time.perf_counter()
            self._wall_start = time.time()
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            duration = time.perf_counter() - self._started
            self._profiler._record(
                self._label,
                self._category,
                self._wall_start,
                duration,
                self._metadata,
                self._tokens,
            )

    def ameasure(
        self,
        label: str,
        *,
        category: str = "node",
        metadata: Mapping[str, Any] | None = None,
        tokens: Mapping[str, float] | None = None,
    ) -> PerformanceProfiler._AsyncMeasure:
        """异步打点上下文。"""
        return PerformanceProfiler._AsyncMeasure(
            self, label, category, metadata, tokens
        )

    def record_event(
        self,
        label: str,
        duration_seconds: float,
        *,
        category: str = "node",
        metadata: Mapping[str, Any] | None = None,
        tokens: Mapping[str, float] | None = None,
    ) -> None:
        """直接登记一条已知耗时的打点。"""
        self._record(label, category, time.time(), duration_seconds, metadata, tokens)

    def _record(
        self,
        label: str,
        category: str,
        wall_start: float,
        duration: float,
        metadata: Mapping[str, Any] | None,
        tokens: Mapping[str, float] | None,
    ) -> None:
        sample = ProfileSample(
            label=label,
            category=category,
            started_at=wall_start,
            finished_at=wall_start + duration,
            duration_seconds=max(duration, 0.0),
            metadata=dict(metadata or {}),
            tokens={k: float(v) for k, v in (tokens or {}).items()},
        )
        self._samples.append(sample)

    # ------------------------------------------------------------------
    # 结果与报告
    # ------------------------------------------------------------------
    def report(self) -> ProfileResult:
        """生成当前已收集样本的报告（不停止剖析）。"""
        peak = 0
        if self._memory_started and tracemalloc.is_tracing():
            _, peak = tracemalloc.get_traced_memory()
        return self._build_result(peak)

    def _build_result(self, memory_peak: int) -> ProfileResult:
        started = self._started_at or time.perf_counter()
        finished = self._finished_at or time.perf_counter()
        total = max(finished - started, 0.0)
        llm_samples = [s for s in self._samples if s.category == "llm"]
        llm_durations = sorted(s.duration_seconds for s in llm_samples)
        p95 = (
            llm_durations[max(0, int(0.95 * (len(llm_durations) - 1)))]
            if llm_durations
            else 0.0
        )
        total_tokens = sum(
            sum(v for v in s.tokens.values() if isinstance(v, int | float))
            for s in self._samples
        )
        throughput = total_tokens / total if total > 0 else 0.0
        result = ProfileResult(
            started_at=started,
            finished_at=finished,
            samples=list(self._samples),
            total_duration_seconds=total,
            memory_peak_bytes=int(memory_peak),
            token_throughput=throughput,
            llm_call_count=len(llm_samples),
            llm_latency_p95=p95,
        )
        if self._config.output_path is not None:
            self._dump(result)
        return result

    def _dump(self, result: ProfileResult) -> None:
        path = self._config.output_path
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def current(cls) -> PerformanceProfiler | None:
        """返回栈顶的活跃剖析器（若存在）。"""
        return cls._ACTIVE[-1] if cls._ACTIVE else None


def profiled(
    label: str | None = None,
    *,
    category: str = "node",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """函数装饰器：自动向当前活跃剖析器登记耗时。

    若调用时没有活跃剖析器则等同于直接调用。
    """

    def _decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or f"{func.__module__}.{func.__qualname__}"

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def _async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                profiler = PerformanceProfiler.current()
                if profiler is None:
                    return await func(*args, **kwargs)  # type: ignore[misc]
                async with profiler.ameasure(name, category=category):
                    return await func(*args, **kwargs)  # type: ignore[misc]

            return _async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def _sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            profiler = PerformanceProfiler.current()
            if profiler is None:
                return func(*args, **kwargs)
            with profiler.measure(name, category=category):
                return func(*args, **kwargs)

        return _sync_wrapper

    return _decorator


class HotspotAnalyzer:
    """热点分析器 - 从剖析样本中识别最耗时的标签。"""

    def __init__(self, *, top_k: int = 5) -> None:
        self._top_k = top_k

    def analyze(
        self,
        samples_or_result: Sequence[ProfileSample] | ProfileResult,
    ) -> list[HotspotEntry]:
        """聚合并按总耗时降序返回 ``top_k`` 个热点。"""
        if isinstance(samples_or_result, ProfileResult):
            samples = samples_or_result.samples
        else:
            samples = list(samples_or_result)
        if not samples:
            return []
        total = sum(s.duration_seconds for s in samples) or 1.0
        buckets: dict[tuple[str, str], list[float]] = {}
        for sample in samples:
            key = (sample.label, sample.category)
            buckets.setdefault(key, []).append(sample.duration_seconds)
        entries = [
            HotspotEntry(
                label=label,
                category=category,
                count=len(values),
                total_seconds=sum(values),
                mean_seconds=statistics.fmean(values),
                max_seconds=max(values),
                share=sum(values) / total,
            )
            for (label, category), values in buckets.items()
        ]
        entries.sort(key=lambda e: e.total_seconds, reverse=True)
        return entries[: self._top_k]
