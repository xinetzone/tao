"""评估层：治具核心、指标收集与报告生成。

本子包整合三大组件：

* :mod:`.harness` - :class:`EvalHarness` / :class:`EvalSuite` 编排执行；
* :mod:`.metrics` - 预置与自定义指标；
* :mod:`.reporters` - 控制台 / JSON / Markdown 报告生成器。
"""

from __future__ import annotations

from .harness import (
    EvalCase,
    EvalConfig,
    EvalHarness,
    EvalOutputFormat,
    EvalResult,
    EvalSuite,
    EvalSummary,
    ProgressCallback,
)
from .metrics import (
    CompositeMetric,
    ContainsMatch,
    CostMetric,
    ExactMatch,
    LatencyMetric,
    Metric,
    MetricAggregator,
    MetricRegistry,
    MetricSummary,
    TokenUsageMetric,
)
from .reporters import (
    ConsoleReporter,
    JsonReporter,
    MarkdownReporter,
    Reporter,
    build_recommendations,
)

__all__ = [
    "CompositeMetric",
    "ConsoleReporter",
    "ContainsMatch",
    "CostMetric",
    "EvalCase",
    "EvalConfig",
    "EvalHarness",
    "EvalOutputFormat",
    "EvalResult",
    "EvalSuite",
    "EvalSummary",
    "ExactMatch",
    "JsonReporter",
    "LatencyMetric",
    "MarkdownReporter",
    "Metric",
    "MetricAggregator",
    "MetricRegistry",
    "MetricSummary",
    "ProgressCallback",
    "Reporter",
    "TokenUsageMetric",
    "build_recommendations",
]
