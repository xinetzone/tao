"""报告生成器 - 多种格式输出评估摘要。

提供 :class:`Reporter` 协议与三个内置实现：

* :class:`ConsoleReporter` - 纯文本表格；
* :class:`JsonReporter` - 结构化 JSON；
* :class:`MarkdownReporter` - Markdown 表格 + 建议列表。
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable

from ..harness import EvalHarness, EvalResult, EvalSummary
from ..metrics import MetricSummary

__all__ = [
    "ConsoleReporter",
    "JsonReporter",
    "MarkdownReporter",
    "Reporter",
    "build_recommendations",
]


@runtime_checkable
class Reporter(Protocol):
    """报告生成器接口。"""

    name: str

    def generate(self, results: Sequence[EvalResult]) -> str | dict[str, Any]:
        """生成报告内容（字符串或可序列化字典）。"""
        ...


def build_recommendations(summary: EvalSummary) -> list[str]:
    """根据摘要给出启发式建议。"""
    tips: list[str] = []
    if summary.total == 0:
        return ["数据集为空，请检查 EvalConfig.dataset_path 或传入 EvalCase 列表。"]
    failure_rate = summary.failed / summary.total
    if failure_rate >= 0.2:
        tips.append(
            f"失败率 {failure_rate:.0%} 偏高，建议检查 Agent 异常处理或缩短超时时间。"
        )
    latency = summary.metrics.get("latency")
    if latency and latency.p95 > 5.0:
        tips.append(f"P95 延迟 {latency.p95:.2f}s 偏高，可能需要并发提升或缓存优化。")
    accuracy = summary.metrics.get("exact_match") or summary.metrics.get(
        "contains_match"
    )
    if accuracy and accuracy.mean < 0.6:
        tips.append(
            f"匹配指标均值仅 {accuracy.mean:.2%}，建议检查 Prompt 质量或扩充示例。"
        )
    if not tips:
        tips.append("整体表现良好，可考虑加入更多边界用例继续迭代。")
    return tips


def _fmt_score(value: float) -> str:
    if math.isnan(value):
        return "n/a"
    return f"{value:.4f}"


def _build_table(rows: Sequence[Sequence[str]], header: Sequence[str]) -> str:
    cols = list(zip(header, *rows, strict=False)) if rows else [(h,) for h in header]
    widths = [max(len(str(cell)) for cell in col) for col in cols]
    divider = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def _line(cells: Sequence[str]) -> str:
        return (
            "| "
            + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths, strict=False))
            + " |"
        )

    out: list[str] = [divider, _line(header), divider]
    for row in rows:
        out.append(_line(row))
    out.append(divider)
    return "\n".join(out)


class ConsoleReporter:
    """控制台表格报告。"""

    name = "console"

    def __init__(self, *, max_cases: int = 20) -> None:
        self._max_cases = max_cases

    def generate(self, results: Sequence[EvalResult]) -> str:
        summary = EvalHarness.summarize(results)
        sections: list[str] = []
        sections.append(self._render_overview(summary))
        sections.append(self._render_metric_table(summary.metrics))
        sections.append(self._render_case_table(results))
        sections.append("建议:")
        sections.extend(f"  - {tip}" for tip in build_recommendations(summary))
        return "\n\n".join(sections)

    @staticmethod
    def _render_overview(summary: EvalSummary) -> str:
        return (
            f"评估概览: total={summary.total} succeeded={summary.succeeded} "
            f"failed={summary.failed} duration={summary.duration_seconds:.2f}s"
        )

    @staticmethod
    def _render_metric_table(metrics: dict[str, MetricSummary]) -> str:
        if not metrics:
            return "指标分布: (无)"
        header = ("metric", "count", "mean", "stdev", "p50", "p95", "p99", "min", "max")
        rows = [
            (
                m.name,
                str(m.count),
                _fmt_score(m.mean),
                _fmt_score(m.stdev),
                _fmt_score(m.p50),
                _fmt_score(m.p95),
                _fmt_score(m.p99),
                _fmt_score(m.minimum),
                _fmt_score(m.maximum),
            )
            for m in metrics.values()
        ]
        return "指标分布:\n" + _build_table(rows, header)

    def _render_case_table(self, results: Sequence[EvalResult]) -> str:
        if not results:
            return "用例明细: (空)"
        header = ("case_id", "status", "latency", "scores", "error")
        rows: list[tuple[str, ...]] = []
        for r in results[: self._max_cases]:
            scores = ", ".join(f"{k}={_fmt_score(v)}" for k, v in r.scores.items())
            rows.append(
                (
                    r.case_id,
                    str(r.status.value),
                    f"{r.latency_seconds:.3f}s",
                    scores or "-",
                    (r.error or "")[:40],
                )
            )
        suffix = (
            f"\n... 共 {len(results)} 条，仅展示前 {self._max_cases} 条"
            if len(results) > self._max_cases
            else ""
        )
        return "用例明细:\n" + _build_table(rows, header) + suffix


class JsonReporter:
    """JSON 结构化报告。"""

    name = "json"

    def __init__(self, *, indent: int | None = 2) -> None:
        self._indent = indent

    def generate(self, results: Sequence[EvalResult]) -> dict[str, Any]:
        summary = EvalHarness.summarize(results)
        return {
            "summary": summary.model_dump(mode="json"),
            "results": [r.model_dump(mode="json") for r in results],
            "recommendations": build_recommendations(summary),
        }

    def to_string(self, results: Sequence[EvalResult]) -> str:
        """便捷方法：直接序列化为 JSON 字符串。"""
        return json.dumps(
            self.generate(results), ensure_ascii=False, indent=self._indent
        )


class MarkdownReporter:
    """Markdown 表格报告。"""

    name = "markdown"

    def generate(self, results: Sequence[EvalResult]) -> str:
        summary = EvalHarness.summarize(results)
        lines: list[str] = ["# 评估报告", "", "## 总体"]
        lines.extend(
            (
                f"- 用例总数: **{summary.total}**",
                f"- 成功: **{summary.succeeded}**",
                f"- 失败: **{summary.failed}**",
                f"- 总耗时: **{summary.duration_seconds:.2f}s**",
                "",
                "## 指标分布",
                "",
                "| 指标 | 数量 | 均值 | 标准差 | P50 | P95 | P99 | Min | Max |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            )
        )
        for m in summary.metrics.values():
            lines.append(
                f"| {m.name} | {m.count} | {_fmt_score(m.mean)} | {_fmt_score(m.stdev)} "
                f"| {_fmt_score(m.p50)} | {_fmt_score(m.p95)} | {_fmt_score(m.p99)} "
                f"| {_fmt_score(m.minimum)} | {_fmt_score(m.maximum)} |"
            )
        lines.extend(
            (
                "",
                "## 用例明细",
                "",
                "| case_id | 状态 | 延迟 (s) | 指标 | 错误 |",
                "| --- | --- | --- | --- | --- |",
            )
        )
        for r in results:
            scores = (
                "; ".join(f"{k}={_fmt_score(v)}" for k, v in r.scores.items()) or "-"
            )
            err = (r.error or "").replace("|", "\\|")
            lines.append(
                f"| {r.case_id} | {r.status.value} | {r.latency_seconds:.3f} | {scores} | {err} |"
            )
        lines.extend(("", "## 建议"))
        lines.extend(f"- {tip}" for tip in build_recommendations(summary))
        return "\n".join(lines)
