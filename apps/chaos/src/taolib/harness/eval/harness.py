"""评估治具核心 - 端到端的 Agent 评估编排。

提供 :class:`EvalHarness` 装载数据集、并发执行 Agent、收集指标并
生成 :class:`EvalResult` 列表；:class:`EvalSuite` 作为多组评估的
批量管理器，便于跨 Agent / 跨数据集的对比实验。
"""

from __future__ import annotations

import asyncio
import json
import math
import time
import uuid
from collections.abc import Awaitable, Callable, Iterable, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..runtime.executor import (
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    ExecutorBackend,
    UnifiedExecutor,
)
from .metrics import (
    Metric,
    MetricAggregator,
    MetricRegistry,
    MetricSummary,
)

__all__ = [
    "EvalCase",
    "EvalConfig",
    "EvalHarness",
    "EvalOutputFormat",
    "EvalResult",
    "EvalSuite",
    "EvalSummary",
    "ProgressCallback",
]


type ProgressCallback = Callable[[int, int, "EvalResult"], Awaitable[None] | None]
"""进度回调签名：``(已完成数, 总数, 最近一条结果)``。"""


class EvalOutputFormat(StrEnum):
    """评估输出格式。"""

    JSON = "json"
    JSONL = "jsonl"
    MARKDOWN = "markdown"
    CONSOLE = "console"


class EvalConfig(BaseModel):
    """评估配置。"""

    model_config = ConfigDict(extra="allow")

    dataset_path: Path | None = None
    metrics: list[str] = Field(default_factory=lambda: ["exact_match"])
    concurrency: int = Field(default=4, ge=1)
    timeout_seconds: float | None = Field(default=None, gt=0)
    output_format: EvalOutputFormat = EvalOutputFormat.JSON
    output_path: Path | None = None
    backend: ExecutorBackend = ExecutorBackend.GRAPH
    fail_fast: bool = False


class EvalCase(BaseModel):
    """单条评估用例。"""

    model_config = ConfigDict(extra="allow")

    case_id: str = Field(default_factory=lambda: f"case-{uuid.uuid4().hex[:10]}")
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected: Any = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalResult(BaseModel):
    """单条评估结果。"""

    model_config = ConfigDict(extra="allow")

    case_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected: Any = None
    output: Any = None
    scores: dict[str, float] = Field(default_factory=dict)
    latency_seconds: float = 0.0
    tokens: dict[str, float] = Field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.SUCCEEDED
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalSummary(BaseModel):
    """整组评估的聚合摘要。"""

    model_config = ConfigDict(extra="allow")

    total: int
    succeeded: int
    failed: int
    metrics: dict[str, MetricSummary] = Field(default_factory=dict)
    started_at: float
    finished_at: float
    duration_seconds: float


def _extract_tokens(output: Any, exec_meta: dict[str, Any] | None) -> dict[str, float]:
    """尽力从输出/执行元数据中抽取 token 用量。"""
    candidates: list[Any] = []
    if isinstance(output, dict):
        for key in ("usage", "token_usage", "tokens"):
            if key in output:
                candidates.append(output[key])
    if exec_meta:
        for key in ("usage", "token_usage", "tokens"):
            if key in exec_meta:
                candidates.append(exec_meta[key])
    for candidate in candidates:
        if isinstance(candidate, dict):
            return {
                k: float(v) for k, v in candidate.items() if isinstance(v, int | float)
            }
    return {}


class EvalHarness:
    """评估治具 - 编排数据集装载、并发执行与指标采集。"""

    def __init__(
        self,
        *,
        executor: UnifiedExecutor | None = None,
        metric_registry: MetricRegistry | None = None,
    ) -> None:
        """构造评估治具。

        Args:
            executor: 复用上层注入的 :class:`UnifiedExecutor`，缺省自动创建。
            metric_registry: 自定义指标注册表，缺省加载内置默认集合。
        """
        self._executor = executor or UnifiedExecutor()
        self._registry = metric_registry or MetricRegistry.with_defaults()

    # ------------------------------------------------------------------
    # 数据集装载
    # ------------------------------------------------------------------
    def load_dataset(
        self,
        path_or_cases: str | Path | Iterable[EvalCase | dict[str, Any]],
    ) -> list[EvalCase]:
        """装载评估数据集。

        支持三种来源：

        * ``.json`` 文件：单个 JSON 数组。
        * ``.jsonl`` 文件：每行一条 JSON 对象。
        * 直接传入 :class:`EvalCase` 或字典构成的可迭代对象。
        """
        if isinstance(path_or_cases, str | Path):
            path = Path(path_or_cases)
            return self._load_from_file(path)
        return [self._coerce_case(item) for item in path_or_cases]

    def _load_from_file(self, path: Path) -> list[EvalCase]:
        if not path.exists():
            raise FileNotFoundError(f"评估数据集不存在: {path}")
        suffix = path.suffix.lower()
        text = path.read_text(encoding="utf-8")
        if suffix == ".jsonl":
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        else:
            data = json.loads(text)
            rows = data if isinstance(data, list) else [data]
        return [self._coerce_case(row) for row in rows]

    @staticmethod
    def _coerce_case(item: EvalCase | dict[str, Any]) -> EvalCase:
        if isinstance(item, EvalCase):
            return item
        return EvalCase.model_validate(item)

    # ------------------------------------------------------------------
    # 执行入口
    # ------------------------------------------------------------------
    def run(
        self,
        agent: Any,
        dataset: Iterable[EvalCase | dict[str, Any]] | str | Path,
        config: EvalConfig | None = None,
        *,
        progress: ProgressCallback | None = None,
    ) -> list[EvalResult]:
        """同步入口 - 在新事件循环中运行 :meth:`arun`。"""
        return asyncio.run(self.arun(agent, dataset, config, progress=progress))

    async def arun(
        self,
        agent: Any,
        dataset: Iterable[EvalCase | dict[str, Any]] | str | Path,
        config: EvalConfig | None = None,
        *,
        progress: ProgressCallback | None = None,
    ) -> list[EvalResult]:
        """异步执行评估，返回所有用例的 :class:`EvalResult` 列表。"""
        cfg = config or EvalConfig()
        cases = self._normalize_dataset(dataset, cfg)
        metrics = self._registry.resolve(cfg.metrics)
        semaphore = asyncio.Semaphore(cfg.concurrency)
        results: list[EvalResult | None] = [None] * len(cases)
        completed = 0
        completed_lock = asyncio.Lock()
        cancel_event = asyncio.Event()

        async def _worker(index: int, case: EvalCase) -> None:
            nonlocal completed
            if cancel_event.is_set():
                return
            async with semaphore:
                if cancel_event.is_set():
                    return
                result = await self._run_one(agent, case, cfg, metrics)
            results[index] = result
            async with completed_lock:
                completed += 1
                current = completed
            if progress is not None:
                await self._invoke_progress(progress, current, len(cases), result)
            if cfg.fail_fast and result.status != ExecutionStatus.SUCCEEDED:
                cancel_event.set()

        await asyncio.gather(*(_worker(i, c) for i, c in enumerate(cases)))
        finalized = [r for r in results if r is not None]

        if cfg.output_path is not None:
            self._dump(finalized, cfg)
        return finalized

    @staticmethod
    async def _invoke_progress(
        callback: ProgressCallback,
        done: int,
        total: int,
        latest: EvalResult,
    ) -> None:
        outcome = callback(done, total, latest)
        if isinstance(outcome, Awaitable):
            await outcome

    def _normalize_dataset(
        self,
        dataset: Iterable[EvalCase | dict[str, Any]] | str | Path,
        cfg: EvalConfig,
    ) -> list[EvalCase]:
        if isinstance(dataset, str | Path):
            return self.load_dataset(dataset)
        if cfg.dataset_path is not None:
            return self.load_dataset(cfg.dataset_path)
        return [self._coerce_case(item) for item in dataset]

    # ------------------------------------------------------------------
    # 单条执行
    # ------------------------------------------------------------------
    async def _run_one(
        self,
        agent: Any,
        case: EvalCase,
        cfg: EvalConfig,
        metrics: Sequence[Metric],
    ) -> EvalResult:
        ctx = ExecutionContext(
            config={"case_id": case.case_id},
            metadata={"tags": list(case.tags)},
            timeout_seconds=cfg.timeout_seconds,
        )
        started = time.perf_counter()
        exec_result = await self._executor.execute(
            agent,
            case.inputs,
            backend=cfg.backend,
            context=ctx,
        )
        latency = (
            exec_result.duration_seconds
            if exec_result.duration_seconds is not None
            else time.perf_counter() - started
        )
        return self._score(case, exec_result, metrics, latency)

    def _score(
        self,
        case: EvalCase,
        exec_result: ExecutionResult,
        metrics: Sequence[Metric],
        latency: float,
    ) -> EvalResult:
        tokens = _extract_tokens(exec_result.output, exec_result.metadata)
        scores: dict[str, float] = {}
        if exec_result.status == ExecutionStatus.SUCCEEDED:
            for metric in metrics:
                value = metric.compute(
                    exec_result.output,
                    case.expected,
                    latency=latency,
                    tokens=tokens,
                )
                scores[metric.name] = float(value)
        else:
            for metric in metrics:
                scores[metric.name] = math.nan
        return EvalResult(
            case_id=case.case_id,
            inputs=case.inputs,
            expected=case.expected,
            output=exec_result.output,
            scores=scores,
            latency_seconds=latency,
            tokens=tokens,
            status=exec_result.status,
            error=exec_result.error,
            metadata={**case.metadata, "run_id": exec_result.run_id},
        )

    # ------------------------------------------------------------------
    # 摘要 / 对比
    # ------------------------------------------------------------------
    @staticmethod
    def summarize(results: Sequence[EvalResult]) -> EvalSummary:
        """对一组评估结果计算指标聚合摘要。"""
        if not results:
            now = time.time()
            return EvalSummary(
                total=0,
                succeeded=0,
                failed=0,
                started_at=now,
                finished_at=now,
                duration_seconds=0.0,
            )
        succeeded = sum(1 for r in results if r.status == ExecutionStatus.SUCCEEDED)
        failed = len(results) - succeeded
        rows = [r.scores for r in results]
        latency_rows = [{"latency": r.latency_seconds} for r in results]
        summaries = MetricAggregator.aggregate_many(rows + latency_rows)
        started = min(
            (r.metadata.get("started_at", time.time()) for r in results),
            default=time.time(),
        )
        finished = time.time()
        return EvalSummary(
            total=len(results),
            succeeded=succeeded,
            failed=failed,
            metrics=summaries,
            started_at=started,
            finished_at=finished,
            duration_seconds=max(0.0, finished - started),
        )

    @staticmethod
    def compare(
        results_a: Sequence[EvalResult],
        results_b: Sequence[EvalResult],
    ) -> dict[str, dict[str, float]]:
        """对比两组评估结果，按指标输出 ``{metric: {a, b, delta}}``。"""
        summary_a = EvalHarness.summarize(results_a).metrics
        summary_b = EvalHarness.summarize(results_b).metrics
        keys = set(summary_a) | set(summary_b)
        diff: dict[str, dict[str, float]] = {}
        for key in sorted(keys):
            mean_a = summary_a[key].mean if key in summary_a else 0.0
            mean_b = summary_b[key].mean if key in summary_b else 0.0
            diff[key] = {
                "a": mean_a,
                "b": mean_b,
                "delta": mean_b - mean_a,
            }
        return diff

    # ------------------------------------------------------------------
    # 输出落盘
    # ------------------------------------------------------------------
    @staticmethod
    def _dump(results: Sequence[EvalResult], cfg: EvalConfig) -> None:
        path = cfg.output_path
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        match cfg.output_format:
            case EvalOutputFormat.JSON:
                payload = [r.model_dump(mode="json") for r in results]
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            case EvalOutputFormat.JSONL:
                lines = [
                    json.dumps(r.model_dump(mode="json"), ensure_ascii=False)
                    for r in results
                ]
                path.write_text("\n".join(lines), encoding="utf-8")
            case _:
                payload = [r.model_dump(mode="json") for r in results]
                path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                )


class EvalSuite:
    """多组评估的批量管理器。"""

    def __init__(self, *, harness: EvalHarness | None = None) -> None:
        self._harness = harness or EvalHarness()
        self._jobs: list[tuple[str, Any, list[EvalCase], EvalConfig]] = []

    def add(
        self,
        name: str,
        agent: Any,
        dataset: Iterable[EvalCase | dict[str, Any]] | str | Path,
        config: EvalConfig | None = None,
    ) -> None:
        """登记一个评估任务。"""
        cases = (
            self._harness.load_dataset(dataset)
            if isinstance(dataset, str | Path)
            else [EvalHarness._coerce_case(item) for item in dataset]
        )
        self._jobs.append((name, agent, cases, config or EvalConfig()))

    @property
    def harness(self) -> EvalHarness:
        """底层评估治具。"""
        return self._harness

    def run_all(self) -> dict[str, list[EvalResult]]:
        """同步执行全部已登记的任务。"""
        return asyncio.run(self.arun_all())

    async def arun_all(
        self,
        *,
        progress: ProgressCallback | None = None,
    ) -> dict[str, list[EvalResult]]:
        """异步执行全部已登记的任务。"""
        outputs: dict[str, list[EvalResult]] = {}
        for name, agent, cases, cfg in self._jobs:
            outputs[name] = await self._harness.arun(
                agent, cases, cfg, progress=progress
            )
        return outputs

    def summaries(
        self,
        outputs: dict[str, list[EvalResult]],
    ) -> dict[str, EvalSummary]:
        """对每组评估结果生成摘要。"""
        return {
            name: EvalHarness.summarize(results) for name, results in outputs.items()
        }
