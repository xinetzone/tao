"""指标收集器 - 评估指标的协议、预置实现、注册表与聚合工具。

本模块提供可扩展的指标体系：

* :class:`Metric` Protocol 定义统一接口；
* 预置 :class:`ExactMatch` / :class:`ContainsMatch` / :class:`LatencyMetric` /
  :class:`TokenUsageMetric` / :class:`CostMetric`；
* :class:`MetricRegistry` 支持自定义指标注册；
* :class:`MetricAggregator` 提供分布统计（均值、P50/P95/P99、标准差）；
* :class:`CompositeMetric` 支持多指标加权组合。
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "CompositeMetric",
    "ContainsMatch",
    "CostMetric",
    "ExactMatch",
    "LatencyMetric",
    "Metric",
    "MetricAggregator",
    "MetricRegistry",
    "MetricSummary",
    "TokenUsageMetric",
]


type MetricValue = float
"""单条指标得分的标准类型：浮点数。"""


@runtime_checkable
class Metric(Protocol):
    """指标接口 - 任意可计算评估指标的最小契约。"""

    name: str
    """指标名，用于在结果与报告中标识该指标。"""

    def compute(self, predicted: Any, expected: Any, /, **kwargs: Any) -> MetricValue:
        """计算单次指标得分。

        Args:
            predicted: Agent 实际输出。
            expected: 期望输出（可选，部分指标如延迟无需期望值）。
            **kwargs: 额外上下文（如 latency、tokens）。
        """
        ...


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        for key in ("output", "answer", "text", "content"):
            if key in value:
                return _as_text(value[key])
    return str(value)


class ExactMatch:
    """精确匹配指标 - 字符串完全一致返回 1.0，否则 0.0。"""

    name = "exact_match"

    def __init__(self, *, case_sensitive: bool = True, strip: bool = True) -> None:
        self._case_sensitive = case_sensitive
        self._strip = strip

    def compute(self, predicted: Any, expected: Any, /, **_: Any) -> MetricValue:
        a, b = _as_text(predicted), _as_text(expected)
        if self._strip:
            a, b = a.strip(), b.strip()
        if not self._case_sensitive:
            a, b = a.lower(), b.lower()
        return 1.0 if a == b else 0.0


class ContainsMatch:
    """包含匹配指标 - 期望文本是否被实际文本包含。"""

    name = "contains_match"

    def __init__(self, *, case_sensitive: bool = False) -> None:
        self._case_sensitive = case_sensitive

    def compute(self, predicted: Any, expected: Any, /, **_: Any) -> MetricValue:
        a, b = _as_text(predicted), _as_text(expected)
        if not self._case_sensitive:
            a, b = a.lower(), b.lower()
        return 1.0 if b and b in a else 0.0


class LatencyMetric:
    """延迟测量指标 - 直接读取 ``kwargs['latency']``（秒）。"""

    name = "latency"

    def compute(self, predicted: Any, expected: Any, /, **kwargs: Any) -> MetricValue:
        latency = kwargs.get("latency")
        if latency is None:
            return math.nan
        return float(latency)


class TokenUsageMetric:
    """Token 用量指标 - 读取 ``kwargs['tokens']`` 字典并按字段累加。"""

    name = "tokens"

    def __init__(self, *, field: str = "total") -> None:
        self._field = field

    def compute(self, predicted: Any, expected: Any, /, **kwargs: Any) -> MetricValue:
        tokens = kwargs.get("tokens") or {}
        if not isinstance(tokens, Mapping):
            return math.nan
        if self._field == "total":
            return float(sum(v for v in tokens.values() if isinstance(v, int | float)))
        value = tokens.get(self._field)
        return float(value) if isinstance(value, int | float) else math.nan


class CostMetric:
    """成本估算指标 - 按 prompt/completion 单价折算总成本（美元）。"""

    name = "cost"

    def __init__(
        self,
        *,
        prompt_price_per_1k: float = 0.0,
        completion_price_per_1k: float = 0.0,
    ) -> None:
        self._prompt = prompt_price_per_1k
        self._completion = completion_price_per_1k

    def compute(self, predicted: Any, expected: Any, /, **kwargs: Any) -> MetricValue:
        tokens = kwargs.get("tokens") or {}
        if not isinstance(tokens, Mapping):
            return 0.0
        prompt = float(tokens.get("prompt", 0) or 0)
        completion = float(tokens.get("completion", 0) or 0)
        return prompt / 1000.0 * self._prompt + completion / 1000.0 * self._completion


class CompositeMetric:
    """组合指标 - 对若干子指标按权重线性加权求总分。"""

    def __init__(
        self,
        name: str,
        components: Sequence[tuple[Metric, float]],
    ) -> None:
        if not components:
            raise ValueError("CompositeMetric 至少需要一个子指标")
        self.name = name
        self._components = list(components)

    def compute(self, predicted: Any, expected: Any, /, **kwargs: Any) -> MetricValue:
        total = 0.0
        weights = 0.0
        for metric, weight in self._components:
            score = metric.compute(predicted, expected, **kwargs)
            if not math.isnan(score):
                total += score * weight
                weights += weight
        if weights == 0.0:
            return math.nan
        return total / weights


class MetricRegistry:
    """指标注册表 - 支持按名称登记/查询/批量装配。"""

    def __init__(self) -> None:
        self._items: dict[str, Metric] = {}

    def register(self, metric: Metric, *, alias: str | None = None) -> None:
        """登记一个指标实例。"""
        key = alias or metric.name
        self._items[key] = metric

    def unregister(self, name: str) -> Metric | None:
        """注销并返回原指标。"""
        return self._items.pop(name, None)

    def get(self, name: str) -> Metric:
        """按名称获取指标，不存在则抛出 ``KeyError``。"""
        try:
            return self._items[name]
        except KeyError as exc:
            raise KeyError(f"未注册的指标: {name!r}; 可用: {self.names()}") from exc

    def names(self) -> list[str]:
        """所有已登记的指标名。"""
        return list(self._items)

    def resolve(self, names: Iterable[str]) -> list[Metric]:
        """按名称批量解析指标实例列表。"""
        return [self.get(n) for n in names]

    def __contains__(self, name: str) -> bool:
        return name in self._items

    @classmethod
    def with_defaults(cls) -> MetricRegistry:
        """构造内置默认指标的注册表。"""
        registry = cls()
        registry.register(ExactMatch())
        registry.register(ContainsMatch())
        registry.register(LatencyMetric())
        registry.register(TokenUsageMetric())
        registry.register(CostMetric())
        return registry


class MetricSummary(BaseModel):
    """单个指标在一组样本上的统计摘要。"""

    model_config = ConfigDict(extra="allow")

    name: str
    count: int = 0
    mean: float = 0.0
    stdev: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    minimum: float = 0.0
    maximum: float = 0.0
    samples: list[float] = Field(default_factory=list)


class MetricAggregator:
    """指标聚合器 - 对一系列样本计算均值、分位、标准差。"""

    @staticmethod
    def aggregate(name: str, values: Iterable[float]) -> MetricSummary:
        """聚合指定名称下的一组样本。"""
        cleaned = [float(v) for v in values if v is not None and not math.isnan(v)]
        if not cleaned:
            return MetricSummary(name=name)
        ordered = sorted(cleaned)
        return MetricSummary(
            name=name,
            count=len(cleaned),
            mean=statistics.fmean(cleaned),
            stdev=statistics.pstdev(cleaned) if len(cleaned) > 1 else 0.0,
            p50=MetricAggregator._percentile(ordered, 0.50),
            p95=MetricAggregator._percentile(ordered, 0.95),
            p99=MetricAggregator._percentile(ordered, 0.99),
            minimum=ordered[0],
            maximum=ordered[-1],
            samples=cleaned,
        )

    @staticmethod
    def aggregate_many(
        rows: Iterable[Mapping[str, float]],
    ) -> dict[str, MetricSummary]:
        """对每个指标列分别聚合，返回 ``{metric_name: summary}`` 映射。"""
        buckets: dict[str, list[float]] = {}
        for row in rows:
            for key, value in row.items():
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    continue
                buckets.setdefault(key, []).append(float(value))
        return {
            name: MetricAggregator.aggregate(name, values)
            for name, values in buckets.items()
        }

    @staticmethod
    def _percentile(ordered: Sequence[float], q: float) -> float:
        if not ordered:
            return 0.0
        if len(ordered) == 1:
            return ordered[0]
        idx = q * (len(ordered) - 1)
        lower = math.floor(idx)
        upper = math.ceil(idx)
        if lower == upper:
            return ordered[lower]
        weight = idx - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight
