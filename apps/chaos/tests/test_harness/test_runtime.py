"""运行时层单元测试 - 验证 executor、scheduler、checkpointer。

注：harness 运行时接口（ExecutionContext、Scheduler、MemoryCheckpointer）
当前为 stub 占位（见 Task #2）。本文件先建立测试结构，使用 ``has_attr``
fixture 在接口尚未落地时条件跳过；接口落地后即可直接通过。
"""

from __future__ import annotations

import importlib

import pytest

RUNTIME_EXECUTOR = "taolib.harness.runtime.executor"
RUNTIME_SCHEDULER = "taolib.harness.runtime.scheduler"
RUNTIME_CHECKPOINTER = "taolib.harness.runtime.checkpointer"


# ---------------------------------------------------------------------------
# 模块可导入性兜底
# ---------------------------------------------------------------------------


def test_runtime_modules_importable() -> None:
    """三个运行时模块必须始终可导入，且声明 ``__all__``。"""
    for name in (RUNTIME_EXECUTOR, RUNTIME_SCHEDULER, RUNTIME_CHECKPOINTER):
        module = importlib.import_module(name)
        assert hasattr(module, "__all__"), f"{name} 未声明 __all__"
        assert isinstance(module.__all__, list)


# ---------------------------------------------------------------------------
# ExecutionContext 构造
# ---------------------------------------------------------------------------


def test_execution_context_creation(
    mock_state: dict[str, object],
    has_attr,
) -> None:
    """验证执行上下文（ExecutionContext）的最小构造路径。"""
    if not has_attr(RUNTIME_EXECUTOR, "ExecutionContext"):
        pytest.skip("ExecutionContext 尚未实现，等待 Task #2 落地")

    executor_module = importlib.import_module(RUNTIME_EXECUTOR)
    ctx_cls = executor_module.ExecutionContext
    ctx = ctx_cls(
        session_id=mock_state["session_id"],
        state=mock_state,
    )

    assert getattr(ctx, "session_id", None) == mock_state["session_id"]
    assert getattr(ctx, "state", None) == mock_state

    # 上下文应支持基本元信息（开始时间、运行模式）若已暴露
    if hasattr(ctx, "started_at"):
        assert ctx.started_at is not None


# ---------------------------------------------------------------------------
# Scheduler 优先级排序
# ---------------------------------------------------------------------------


def test_scheduler_priority_ordering(has_attr) -> None:
    """验证 Scheduler 按优先级降序出队（数值大者优先）。"""
    if not has_attr(RUNTIME_SCHEDULER, "Scheduler"):
        pytest.skip("Scheduler 尚未实现，等待 Task #2 落地")

    scheduler_module = importlib.import_module(RUNTIME_SCHEDULER)
    scheduler = scheduler_module.Scheduler()

    # 入队顺序与优先级故意错开
    scheduler.submit(name="low", priority=1, payload={"v": 1})
    scheduler.submit(name="high", priority=10, payload={"v": 10})
    scheduler.submit(name="mid", priority=5, payload={"v": 5})

    # 出队应按 high -> mid -> low
    order: list[str] = []
    while True:
        task = scheduler.next() if hasattr(scheduler, "next") else scheduler.pop()
        if task is None:
            break
        order.append(getattr(task, "name", None) or task["name"])

    assert order == ["high", "mid", "low"], f"出队顺序异常: {order}"


# ---------------------------------------------------------------------------
# MemoryCheckpointer 存取
# ---------------------------------------------------------------------------


def test_memory_checkpointer_put_get(
    mock_state: dict[str, object],
    has_attr,
) -> None:
    """验证内存检查点的 put / get 往返一致。"""
    if not has_attr(RUNTIME_CHECKPOINTER, "MemoryCheckpointer"):
        pytest.skip("MemoryCheckpointer 尚未实现，等待 Task #2 落地")

    cp_module = importlib.import_module(RUNTIME_CHECKPOINTER)
    cp = cp_module.MemoryCheckpointer()

    key = mock_state["session_id"]
    cp.put(key, mock_state)
    fetched = cp.get(key)

    assert fetched == mock_state, "检查点取回内容与写入不一致"

    # 不存在的键应返回 None 或显式 KeyError，二者择一即可
    if hasattr(cp, "get"):
        try:
            missing = cp.get("__not_exist__")
        except KeyError:
            missing = None
        assert missing is None or missing != mock_state


# ---------------------------------------------------------------------------
# Scheduler 任务路由
# ---------------------------------------------------------------------------


def test_scheduler_task_routing(has_attr) -> None:
    """验证 Scheduler 按 ``kind`` 字段把任务路由到对应执行器。

    路由规则（落地前的约定）::

        kind == "agent"  -> 走 LangGraph 执行器
        kind == "flow"   -> 走 Metaflow 执行器
        kind == "tool"   -> 走 in-process 同步执行器
    """
    if not has_attr(RUNTIME_SCHEDULER, "Scheduler"):
        pytest.skip("Scheduler 尚未实现，等待 Task #2 落地")

    scheduler_module = importlib.import_module(RUNTIME_SCHEDULER)
    scheduler = scheduler_module.Scheduler()

    if not hasattr(scheduler, "route"):
        pytest.skip("Scheduler.route 尚未实现")

    assert scheduler.route(kind="agent") == "langgraph"
    assert scheduler.route(kind="flow") == "metaflow"
    assert scheduler.route(kind="tool") == "inprocess"

    with pytest.raises((ValueError, KeyError)):
        scheduler.route(kind="__unknown__")
