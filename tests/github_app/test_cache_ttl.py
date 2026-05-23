"""InMemoryInstallationTokenCache TTL 主动过期测试。"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.models import InstallationTokenResult, TokenKind


def _make_result(expires_at: datetime) -> InstallationTokenResult:
    """构造测试用 InstallationTokenResult。"""
    return InstallationTokenResult(
        token="ghs_test",
        expires_at=expires_at,
        token_kind=TokenKind.STATEFUL,
        requested_strategy="auto",
        effective_strategy="none",
        degraded=False,
    )


class TestPurgeExpired:
    """purge_expired 方法测试。"""

    async def test_removes_expired_entries(self) -> None:
        """已过期条目应被清除。"""
        cache = InMemoryInstallationTokenCache()
        past = datetime.now(tz=UTC) - timedelta(seconds=10)
        await cache.set("expired_key", _make_result(past))

        removed = cache.purge_expired()
        assert removed == 1
        assert await cache.get("expired_key") is None

    async def test_keeps_valid_entries(self) -> None:
        """未过期条目应保留。"""
        cache = InMemoryInstallationTokenCache()
        future = datetime.now(tz=UTC) + timedelta(hours=1)
        await cache.set("valid_key", _make_result(future))

        removed = cache.purge_expired()
        assert removed == 0
        assert await cache.get("valid_key") is not None

    async def test_mixed_entries(self) -> None:
        """混合场景：只清除过期条目，保留有效条目。"""
        cache = InMemoryInstallationTokenCache()
        past = datetime.now(tz=UTC) - timedelta(seconds=1)
        future = datetime.now(tz=UTC) + timedelta(hours=1)
        await cache.set("expired_1", _make_result(past))
        await cache.set("valid_1", _make_result(future))
        await cache.set("expired_2", _make_result(past))

        removed = cache.purge_expired()
        assert removed == 2
        assert await cache.get("expired_1") is None
        assert await cache.get("valid_1") is not None
        assert await cache.get("expired_2") is None


class TestPurgeTask:
    """start_purge_task / stop_purge_task 测试。"""

    async def test_purge_task_periodic_cleanup(self) -> None:
        """后台任务周期性清理过期条目。"""
        cache = InMemoryInstallationTokenCache()
        past = datetime.now(tz=UTC) - timedelta(seconds=1)
        future = datetime.now(tz=UTC) + timedelta(hours=1)
        await cache.set("expired_key", _make_result(past))
        await cache.set("valid_key", _make_result(future))

        # 使用很短的间隔以加速测试
        task = cache.start_purge_task(interval_seconds=1)
        await asyncio.sleep(1.5)

        assert await cache.get("expired_key") is None
        assert await cache.get("valid_key") is not None

        cache.stop_purge_task()
        # 给事件循环足够时间完成取消处理
        await asyncio.sleep(0.1)
        assert task.cancelled() or task.done()

    async def test_stop_purge_task_cancels(self) -> None:
        """stop_purge_task 能正确取消后台任务。"""
        cache = InMemoryInstallationTokenCache()
        task = cache.start_purge_task(interval_seconds=300)
        assert not task.done()

        cache.stop_purge_task()
        # 给事件循环足够时间完成取消处理
        await asyncio.sleep(0.1)
        assert task.cancelled() or task.done()

    async def test_stop_without_start(self) -> None:
        """未启动后台任务时调用 stop 不应报错。"""
        cache = InMemoryInstallationTokenCache()
        cache.stop_purge_task()  # 不应抛出异常
