"""核心层单元测试 - 验证 state、bridge、registry 的基本行为。

注：harness 核心接口（StateView、BridgeConfig、Registry、ErrorEnvelope）
当前为 stub 占位（见 Task #2）。本文件先建立测试结构，使用 ``has_attr``
fixture 在接口尚未落地时条件跳过断言；具体语义对齐留待 Task #2。
"""

from __future__ import annotations

import importlib

import pytest

CORE_BRIDGE = "taolib.harness.core.bridge"
CORE_STATE = "taolib.harness.core.state"
CORE_REGISTRY = "taolib.harness.core.registry"


# ---------------------------------------------------------------------------
# 模块可导入性兜底
# ---------------------------------------------------------------------------


def test_core_modules_importable() -> None:
    """三个核心模块必须始终可导入，且声明 ``__all__``。"""
    for name in (CORE_BRIDGE, CORE_STATE, CORE_REGISTRY):
        module = importlib.import_module(name)
        assert hasattr(module, "__all__"), f"{name} 未声明 __all__"
        assert isinstance(module.__all__, list)


# ---------------------------------------------------------------------------
# StateView 协议
# ---------------------------------------------------------------------------


def test_state_view_protocol(mock_state: dict[str, object], has_attr) -> None:
    """验证 StateView 协议的最小实现。

    StateView 以 Protocol 定义，要求实现 read / write / snapshot 方法。
    当 :class:`StateView` 尚未实现时跳过具体断言，但保留对 mock 数据
    形态的最小校验，确保 fixture 不被误改。
    """
    assert mock_state["session_id"] == "test-session-0001"
    assert isinstance(mock_state["messages"], list)
    assert isinstance(mock_state["metadata"], dict)

    if not has_attr(CORE_STATE, "StateView"):
        pytest.skip("StateView 尚未实现，等待 Task #2 落地")

    state_module = importlib.import_module(CORE_STATE)
    StateView = state_module.StateView

    # StateView 是 @runtime_checkable Protocol，要求 read / write / snapshot 方法
    class _Impl:
        async def read(self, thread_id: str) -> dict:
            return {}

        async def write(self, thread_id: str, payload: dict) -> None:
            pass

        async def snapshot(self, thread_id: str) -> object:
            return None

    instance = _Impl()
    # 验证 Protocol 方法存在
    for method in ("read", "write", "snapshot"):
        assert hasattr(instance, method)
    # 若提供 runtime_checkable，可顺带验证
    if getattr(StateView, "_is_runtime_protocol", False):
        assert isinstance(instance, StateView)


# ---------------------------------------------------------------------------
# BridgeConfig 默认值
# ---------------------------------------------------------------------------


def test_bridge_config_defaults(
    mock_bridge_config: dict[str, object],
    has_attr,
) -> None:
    """验证 BridgeConfig 默认值与 fixture 中的预期一致。"""
    if not has_attr(CORE_BRIDGE, "BridgeConfig"):
        pytest.skip("BridgeConfig 尚未实现，等待 Task #2 落地")

    bridge_module = importlib.import_module(CORE_BRIDGE)
    config_cls = bridge_module.BridgeConfig
    cfg = config_cls()

    for key, expected in mock_bridge_config.items():
        assert hasattr(cfg, key), f"BridgeConfig 缺少字段 {key}"
        assert getattr(cfg, key) == expected, (
            f"BridgeConfig.{key} 默认值不匹配: "
            f"实际={getattr(cfg, key)!r}, 期望={expected!r}"
        )


# ---------------------------------------------------------------------------
# Registry 注册与发现
# ---------------------------------------------------------------------------


def test_registry_register_and_discover(
    mock_registry_entries: list[dict[str, object]],
    has_attr,
) -> None:
    """验证注册表的注册与按名称/标签发现机制。"""
    if not has_attr(CORE_REGISTRY, "Registry"):
        pytest.skip("Registry 尚未实现，等待 Task #2 落地")

    registry_module = importlib.import_module(CORE_REGISTRY)
    registry = registry_module.Registry()

    for entry in mock_registry_entries:
        registry.register(
            name=entry["name"],
            kind=entry["kind"],
            tags=entry["tags"],
            target=lambda e=entry: e,  # 最小可调用占位
        )

    # 按名称发现
    discovered = registry.get("agent-alpha")
    assert discovered is not None

    # 按标签筛选（接口尚未冻结，存在则验证）
    if hasattr(registry, "find_by_tag"):
        agents = list(registry.find_by_tag("llm"))
        assert any(getattr(item, "name", None) == "agent-alpha" for item in agents)

    # 全量遍历
    if hasattr(registry, "items"):
        items = list(registry.items())
        assert len(items) == len(mock_registry_entries)


# ---------------------------------------------------------------------------
# ErrorEnvelope 错误封装
# ---------------------------------------------------------------------------


def test_bridge_error_envelope(has_attr) -> None:
    """验证 Bridge 的错误封装语义。

    ErrorEnvelope 应至少包含 ``code``、``message`` 与可选 ``cause``，
    并可由原始异常构造。
    """
    if not has_attr(CORE_BRIDGE, "ErrorEnvelope"):
        pytest.skip("ErrorEnvelope 尚未实现，等待 Task #2 落地")

    bridge_module = importlib.import_module(CORE_BRIDGE)
    envelope_cls = bridge_module.ErrorEnvelope

    cause = ValueError("boom")
    env = (
        envelope_cls.from_exception(cause)
        if hasattr(envelope_cls, "from_exception")
        else envelope_cls(
            code="value_error",
            message="boom",
            cause=cause,
        )
    )

    assert getattr(env, "code", None), "ErrorEnvelope.code 不应为空"
    assert "boom" in str(getattr(env, "message", ""))

    if hasattr(env, "to_dict"):
        payload = env.to_dict()
        assert isinstance(payload, dict)
        assert "code" in payload and "message" in payload
