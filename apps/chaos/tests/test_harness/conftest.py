"""Harness 测试配置与 fixtures。

集中提供 :mod:`taolib.harness` 测试套件所需的通用 fixture：

- ``mock_state``: 最小化的 StateView 字典模拟体
- ``mock_bridge_config``: BridgeConfig 默认值快照
- ``mock_registry``: 干净的内存注册表实例
- ``harness_module``: 按需导入 harness 模块，未实现时跳过

测试使用 ``pytest-asyncio`` 的 auto 模式（见 ``pyproject.toml``），
异步测试函数无需显式 ``@pytest.mark.asyncio``。
"""

from __future__ import annotations

import importlib
from collections.abc import Iterator
from typing import Any

import pytest


@pytest.fixture
def mock_state() -> dict[str, Any]:
    """最小化的状态字典，模拟 StateView 协议的载荷。"""
    return {
        "session_id": "test-session-0001",
        "step": 0,
        "messages": [],
        "metadata": {"source": "unit-test"},
    }


@pytest.fixture
def mock_bridge_config() -> dict[str, Any]:
    """BridgeConfig 的预期默认值，供未实现接口前的对照断言使用。"""
    return {
        "timeout_seconds": 300.0,
        "max_retries": 3,
        "retry_backoff_seconds": 1.0,
        "enable_async_offload": True,
        "event_buffer_size": 1024,
    }


@pytest.fixture
def mock_registry_entries() -> list[dict[str, Any]]:
    """注册表测试样本数据。"""
    return [
        {"name": "agent-alpha", "kind": "agent", "tags": ["llm", "chat"]},
        {"name": "flow-beta", "kind": "flow", "tags": ["batch"]},
        {"name": "agent-gamma", "kind": "agent", "tags": ["tool"]},
    ]


@pytest.fixture
def harness_core() -> Iterator[Any]:
    """按需导入 ``taolib.harness.core``；不可用时跳过依赖该 fixture 的测试。"""
    try:
        module = importlib.import_module("taolib.harness.core")
    except ImportError as exc:
        pytest.skip(f"taolib.harness.core 不可用: {exc}")
    yield module


@pytest.fixture
def harness_runtime() -> Iterator[Any]:
    """按需导入 ``taolib.harness.runtime``；不可用时跳过测试。"""
    try:
        module = importlib.import_module("taolib.harness.runtime")
    except ImportError as exc:
        pytest.skip(f"taolib.harness.runtime 不可用: {exc}")
    yield module


def _has_attr(module_name: str, attr: str) -> bool:
    """安全地探测某模块是否已暴露指定属性。"""
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return False
    return hasattr(module, attr)


@pytest.fixture
def has_attr() -> Any:
    """暴露 :func:`_has_attr`，便于测试根据接口实现状态条件跳过。"""
    return _has_attr
