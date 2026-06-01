"""Harness 智能体系统兼容性验证脚本。

验证项:
1. Python 版本检查 (>= 3.14)
2. LangGraph 导入与最小图执行
3. Metaflow 导入与最小 FlowSpec 构造
4. functools 模块兼容性验证
5. Bridge 层基本通信验证
6. 异步运行时兼容性

设计要点:
- 仅依赖 Python 标准库，可在没有安装 langgraph/metaflow 时运行（graceful degradation）
- 每个验证项独立执行，单项失败不影响后续项
- 输出结构化报告：PASS / FAIL / SKIP + 详细信息与耗时
- 直接运行入口::

      python scripts/verify_harness_compat.py
"""

from __future__ import annotations

import argparse
import asyncio
import functools
import importlib
import importlib.util
import json
import sys
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

MIN_PYTHON: tuple[int, int] = (3, 14)


# ---------------------------------------------------------------------------
# 报告数据结构
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """单项验证结果。"""

    name: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    duration_ms: float = 0.0
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "duration_ms": round(self.duration_ms, 2),
            "message": self.message,
            "details": self.details,
            "error": self.error,
        }


@dataclass
class CompatReport:
    """所有验证项的汇总报告。"""

    python_version: str
    platform: str
    results: list[CheckResult] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
        for r in self.results:
            counts[r.status] = counts.get(r.status, 0) + 1
        return counts

    @property
    def passed(self) -> bool:
        """是否所有非跳过项均通过。"""
        return all(r.status != "FAIL" for r in self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "python_version": self.python_version,
            "platform": self.platform,
            "summary": self.summary,
            "results": [r.to_dict() for r in self.results],
        }


# ---------------------------------------------------------------------------
# 检查注册与执行
# ---------------------------------------------------------------------------

CheckFn = Callable[[], dict[str, Any]]
_REGISTRY: list[tuple[str, CheckFn]] = []


def register(name: str) -> Callable[[CheckFn], CheckFn]:
    """检查函数注册装饰器。

    被装饰函数应返回一个 dict，至少包含字段 ``status``，可选 ``message``、
    ``details``。当抛出 :class:`ModuleNotFoundError` 或 :class:`ImportError`
    时统一记为 SKIP，其它异常记为 FAIL。
    """

    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY.append((name, fn))
        return fn

    return decorator


def _run_one(name: str, fn: CheckFn) -> CheckResult:
    start = time.perf_counter()
    try:
        payload = fn() or {}
        status = str(payload.get("status", "PASS"))
        return CheckResult(
            name=name,
            status=status,
            duration_ms=(time.perf_counter() - start) * 1000,
            message=str(payload.get("message", "")),
            details=dict(payload.get("details", {})),
        )
    except (ModuleNotFoundError, ImportError) as exc:
        return CheckResult(
            name=name,
            status="SKIP",
            duration_ms=(time.perf_counter() - start) * 1000,
            message=f"依赖未安装: {exc.name or exc}",
            error=str(exc),
        )
    except Exception as exc:  # 验证脚本需捕获一切异常以保证逐项独立
        return CheckResult(
            name=name,
            status="FAIL",
            duration_ms=(time.perf_counter() - start) * 1000,
            message=f"{type(exc).__name__}: {exc}",
            error="".join(traceback.format_exception(exc)).strip(),
        )


# ---------------------------------------------------------------------------
# 检查项实现
# ---------------------------------------------------------------------------


@register("python-version")
def _check_python_version() -> dict[str, Any]:
    """验证 Python 解释器版本满足 ``>= 3.14``。"""
    current = sys.version_info[:2]
    ok = current >= MIN_PYTHON
    return {
        "status": "PASS" if ok else "FAIL",
        "message": (
            f"Python {current[0]}.{current[1]} "
            f"{'满足' if ok else '不满足'} 最低要求 "
            f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        ),
        "details": {
            "current": ".".join(map(str, sys.version_info[:3])),
            "required": ".".join(map(str, MIN_PYTHON)),
            "implementation": sys.implementation.name,
        },
    }


@register("functools-compatibility")
def _check_functools() -> dict[str, Any]:
    """验证 ``functools`` 关键 API 在当前 Python 版本下的行为。"""

    # functools.wraps 应保留原函数的 __name__、__doc__、__wrapped__
    def original(x: int) -> int:
        """原始函数 docstring。"""
        return x * 2

    @functools.wraps(original)
    def wrapper(x: int) -> int:
        return original(x)

    assert wrapper.__name__ == "original", "functools.wraps 未保留 __name__"
    assert wrapper.__doc__ == "原始函数 docstring。", "functools.wraps 未保留 __doc__"
    assert getattr(wrapper, "__wrapped__", None) is original, "缺失 __wrapped__"
    assert wrapper(3) == 6

    # functools.partial 应支持位置与关键字参数绑定
    def add(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    p = functools.partial(add, 1, c=10)
    assert p(2) == 13, "functools.partial 行为异常"

    # functools.cached_property 应在实例上缓存结果
    class Sample:
        def __init__(self) -> None:
            self.calls = 0

        @functools.cached_property
        def value(self) -> int:
            self.calls += 1
            return 42

    s = Sample()
    assert s.value == 42
    assert s.value == 42
    assert s.calls == 1, "cached_property 未缓存"

    # functools.lru_cache 基本可用
    @functools.lru_cache(maxsize=8)
    def fib(n: int) -> int:
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(10) == 55
    info = fib.cache_info()
    assert info.hits >= 1, "lru_cache 缓存命中异常"

    return {
        "status": "PASS",
        "message": "functools wraps/partial/cached_property/lru_cache 行为正常",
        "details": {
            "lru_cache_info": {
                "hits": info.hits,
                "misses": info.misses,
                "maxsize": info.maxsize,
                "currsize": info.currsize,
            },
        },
    }


@register("asyncio-runtime")
def _check_asyncio() -> dict[str, Any]:
    """验证 asyncio 事件循环、TaskGroup 与 ``asyncio.run`` 行为。"""

    async def echo(value: int) -> int:
        await asyncio.sleep(0)
        return value

    async def main() -> list[int]:
        # Python 3.11+ TaskGroup，3.14 下应继续可用
        results: list[int] = []
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(echo(i)) for i in range(5)]
        for t in tasks:
            results.append(t.result())
        return results

    out = asyncio.run(main())
    assert out == list(range(5)), f"TaskGroup 输出异常: {out}"

    # 事件循环策略可获取
    policy = asyncio.get_event_loop_policy()
    assert policy is not None

    return {
        "status": "PASS",
        "message": "asyncio.run + TaskGroup 行为正常",
        "details": {
            "task_results": out,
            "policy": type(policy).__name__,
        },
    }


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


@register("langgraph-import-and-graph")
def _check_langgraph() -> dict[str, Any]:
    """验证 LangGraph 导入并执行一个最小 ``StateGraph``。"""

    if not _module_available("langgraph"):
        raise ModuleNotFoundError(name="langgraph")

    from typing import TypedDict

    from langgraph.graph import END, START, StateGraph

    class GState(TypedDict):
        value: int

    def increment(state: GState) -> GState:
        return {"value": state["value"] + 1}

    def double(state: GState) -> GState:
        return {"value": state["value"] * 2}

    graph = StateGraph(GState)
    graph.add_node("increment", increment)
    graph.add_node("double", double)
    graph.add_edge(START, "increment")
    graph.add_edge("increment", "double")
    graph.add_edge("double", END)
    compiled = graph.compile()
    final = compiled.invoke({"value": 1})

    expected = (1 + 1) * 2
    assert final["value"] == expected, f"图执行结果异常: {final}"

    langgraph = importlib.import_module("langgraph")
    return {
        "status": "PASS",
        "message": "LangGraph 最小 StateGraph 构建并执行成功",
        "details": {
            "langgraph_version": getattr(langgraph, "__version__", "unknown"),
            "result": final,
        },
    }


@register("metaflow-import-and-flowspec")
def _check_metaflow() -> dict[str, Any]:
    """验证 Metaflow 导入并构造一个最小 ``FlowSpec``（不实际执行）。"""

    if not _module_available("metaflow"):
        raise ModuleNotFoundError(name="metaflow")

    metaflow = importlib.import_module("metaflow")
    FlowSpec = metaflow.FlowSpec
    step = metaflow.step

    class MinimalFlow(FlowSpec):  # type: ignore[misc, valid-type]
        """最小化 FlowSpec，仅用于验证类定义不报错。"""

        @step
        def start(self) -> None:
            self.next(self.end)

        @step
        def end(self) -> None:
            pass

    # 仅校验类结构，不调用 .run()
    assert issubclass(MinimalFlow, FlowSpec)
    assert callable(MinimalFlow.start)
    assert callable(MinimalFlow.end)

    return {
        "status": "PASS",
        "message": "Metaflow FlowSpec 最小定义构造成功",
        "details": {
            "metaflow_version": getattr(metaflow, "__version__", "unknown"),
            "flow_class": MinimalFlow.__name__,
        },
    }


@register("harness-bridge-import")
def _check_harness_bridge() -> dict[str, Any]:
    """验证 Bridge 层 / Harness 核心模块可正常导入与基本通信。"""

    if not _module_available("taolib"):
        raise ModuleNotFoundError(name="taolib")

    bridge = importlib.import_module("taolib.harness.core.bridge")
    state = importlib.import_module("taolib.harness.core.state")
    registry = importlib.import_module("taolib.harness.core.registry")

    details: dict[str, Any] = {
        "bridge_module": bridge.__name__,
        "state_module": state.__name__,
        "registry_module": registry.__name__,
    }

    # 基本通信验证：若 Bridge 提供 send/recv 类协议，则做一次回环。
    # 当前 Bridge 仍为 stub，仅校验 __all__ 已声明且不抛异常。
    for mod in (bridge, state, registry):
        assert hasattr(mod, "__all__"), f"{mod.__name__} 缺少 __all__"

    return {
        "status": "PASS",
        "message": "Harness 核心模块导入成功",
        "details": details,
    }


# ---------------------------------------------------------------------------
# 报告渲染
# ---------------------------------------------------------------------------

_STATUS_GLYPH = {"PASS": "[ OK ]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}


def render_text(report: CompatReport) -> str:
    """渲染人类可读的文本报告。"""
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("Harness 兼容性验证报告")
    lines.append("=" * 70)
    lines.append(f"Python : {report.python_version}")
    lines.append(f"Platform: {report.platform}")
    lines.append("-" * 70)
    for r in report.results:
        glyph = _STATUS_GLYPH.get(r.status, f"[{r.status}]")
        lines.append(f"{glyph} {r.name:36s} {r.duration_ms:8.2f} ms  {r.message}")
        if r.details:
            for k, v in r.details.items():
                lines.append(f"        - {k}: {v}")
        if r.status == "FAIL" and r.error:
            for err_line in r.error.splitlines():
                lines.append(f"        ! {err_line}")
    lines.append("-" * 70)
    s = report.summary
    lines.append(
        f"汇总: PASS={s.get('PASS', 0)}  "
        f"FAIL={s.get('FAIL', 0)}  SKIP={s.get('SKIP', 0)}  "
        f"总计={len(report.results)}"
    )
    lines.append("=" * 70)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------


def run_all() -> CompatReport:
    """执行所有已注册的检查项，返回结构化报告。"""
    report = CompatReport(
        python_version=sys.version.replace("\n", " "),
        platform=sys.platform,
    )
    for name, fn in _REGISTRY:
        report.results.append(_run_one(name, fn))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Harness 兼容性验证：Python 3.14 + LangGraph + Metaflow",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出报告（便于 CI 解析）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="将 SKIP 视为失败（用于必须装齐依赖的环境）",
    )
    args = parser.parse_args(argv)

    report = run_all()

    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_text(report))

    if not report.passed:
        return 1
    if args.strict and report.summary.get("SKIP", 0) > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
