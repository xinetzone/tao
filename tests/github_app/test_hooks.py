"""令牌事件 hook 参考实现测试。"""

import logging
from datetime import UTC, datetime, timedelta

import pytest

from taolib.github_app.events import TokenEventHook
from taolib.github_app.hooks import LoggingTokenEventHook, MetricsTokenEventHook
from taolib.github_app.models import InstallationTokenResult, TokenKind


def _make_result() -> InstallationTokenResult:
    """构造测试用 InstallationTokenResult。"""
    return InstallationTokenResult(
        token="ghs_test",
        expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
        token_kind=TokenKind.STATEFUL,
        requested_strategy="auto",
        effective_strategy="none",
        degraded=False,
    )


class TestLoggingTokenEventHook:
    """LoggingTokenEventHook 测试。"""

    async def test_on_token_refreshed_logs_info(self, caplog: pytest.LogCaptureFixture) -> None:
        """on_token_refreshed 应记录 info 级别日志。"""
        logger = logging.getLogger("test.refreshed")
        hook = LoggingTokenEventHook(logger=logger)
        result = _make_result()

        with caplog.at_level(logging.INFO, logger="test.refreshed"):
            await hook.on_token_refreshed("key_1", result)

        assert len(caplog.records) >= 1
        record = caplog.records[-1]
        assert record.levelno == logging.INFO
        assert "key_1" in record.message
        assert "stateful" in record.message

    async def test_on_token_refresh_failed_logs_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """on_token_refresh_failed 应记录 error 级别日志。"""
        logger = logging.getLogger("test.failed")
        hook = LoggingTokenEventHook(logger=logger)
        error = RuntimeError("timeout")

        with caplog.at_level(logging.ERROR, logger="test.failed"):
            await hook.on_token_refresh_failed("key_2", error)

        assert len(caplog.records) >= 1
        record = caplog.records[-1]
        assert record.levelno == logging.ERROR
        assert "key_2" in record.message
        assert "timeout" in record.message


class TestMetricsTokenEventHook:
    """MetricsTokenEventHook 测试。"""

    async def test_refresh_count_increments(self) -> None:
        """on_token_refreshed 应递增 refresh_count。"""
        hook = MetricsTokenEventHook()
        result = _make_result()

        assert hook.refresh_count == 0
        await hook.on_token_refreshed("k1", result)
        assert hook.refresh_count == 1
        await hook.on_token_refreshed("k2", result)
        assert hook.refresh_count == 2

    async def test_failure_count_increments(self) -> None:
        """on_token_refresh_failed 应递增 failure_count。"""
        hook = MetricsTokenEventHook()
        error = RuntimeError("fail")

        assert hook.failure_count == 0
        await hook.on_token_refresh_failed("k1", error)
        assert hook.failure_count == 1
        await hook.on_token_refresh_failed("k2", error)
        assert hook.failure_count == 2

    async def test_last_refresh_key_updated(self) -> None:
        """on_token_refreshed 应更新 last_refresh_key 为最近键。"""
        hook = MetricsTokenEventHook()
        result = _make_result()

        assert hook.last_refresh_key is None
        await hook.on_token_refreshed("first_key", result)
        assert hook.last_refresh_key == "first_key"
        await hook.on_token_refreshed("second_key", result)
        assert hook.last_refresh_key == "second_key"


class TestHookProtocolConformance:
    """验证两个 hook 满足 TokenEventHook Protocol。"""

    @staticmethod
    def _has_protocol_methods(obj: object) -> bool:
        """结构性检查对象是否满足 TokenEventHook 协议。"""
        return callable(getattr(obj, "on_token_refreshed", None)) and callable(
            getattr(obj, "on_token_refresh_failed", None)
        )

    def test_logging_hook_satisfies_protocol(self) -> None:
        """LoggingTokenEventHook 应满足 TokenEventHook 协议。"""
        hook = LoggingTokenEventHook()
        assert self._has_protocol_methods(hook)

    def test_metrics_hook_satisfies_protocol(self) -> None:
        """MetricsTokenEventHook 应满足 TokenEventHook 协议。"""
        hook = MetricsTokenEventHook()
        assert self._has_protocol_methods(hook)
