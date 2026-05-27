"""缓存与并发路径性能基准测试。"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.models import InstallationTokenResult, TokenKind


def _make_result(
    token: str = "ghs_bench", hours_until_expire: int = 1
) -> InstallationTokenResult:
    """构造测试用令牌结果。"""
    return InstallationTokenResult(
        token=token,
        expires_at=datetime.now(tz=UTC) + timedelta(hours=hours_until_expire),
        token_kind=TokenKind.STATEFUL,
        requested_strategy="auto",
        effective_strategy="none",
        degraded=False,
    )


def _make_expired_result(token: str = "ghs_expired") -> InstallationTokenResult:
    """构造已过期的令牌结果。"""
    return InstallationTokenResult(
        token=token,
        expires_at=datetime.now(tz=UTC) - timedelta(hours=1),
        token_kind=TokenKind.STATEFUL,
        requested_strategy="auto",
        effective_strategy="none",
        degraded=False,
    )


@pytest.mark.slow
class TestCacheBenchmarks:
    """缓存操作性能基准。"""

    def test_cache_set_get(self, benchmark):
        """测量单次 set+get 操作的吞吐量。"""
        cache = InMemoryInstallationTokenCache(maxsize=1000)
        result = _make_result()

        async def op():
            await cache.set("bench-key", result)
            await cache.get("bench-key")

        benchmark(lambda: asyncio.run(op()))

    def test_cache_maxsize_eviction(self, benchmark):
        """测量满容量下写入触发 LRU 淘汰的开销。"""
        cache = InMemoryInstallationTokenCache(maxsize=100)
        result = _make_result()

        # 预填充至满容量
        async def prefill():
            for i in range(100):
                await cache.set(f"prefill-{i}", result)

        asyncio.run(prefill())

        counter = [0]

        async def op():
            # 每次写入新 key 触发淘汰
            await cache.set(f"evict-{counter[0]}", result)
            counter[0] += 1

        benchmark(lambda: asyncio.run(op()))

    def test_purge_expired_performance(self, benchmark):
        """测量大量条目中清理过期项的耗时。"""
        cache = InMemoryInstallationTokenCache(maxsize=2000)
        valid = _make_result()
        expired = _make_expired_result()

        # 填充 500 有效 + 500 过期
        async def prefill():
            for i in range(500):
                await cache.set(f"valid-{i}", valid)
            for i in range(500):
                await cache.set(f"expired-{i}", expired)

        asyncio.run(prefill())

        async def _refill_expired(c, e):
            for i in range(500):
                await c.set(f"expired-{i}", e)

        def op():
            # purge_expired 是同步方法
            cache.purge_expired()
            # 重新填充过期条目以便下次迭代
            asyncio.run(_refill_expired(cache, expired))

        benchmark(op)

    def test_singleflight_concurrent_access(self, benchmark):
        """测量多协程 gather 争抢同一 key 的延迟。"""
        import asyncio as _asyncio

        lock_dict: dict[str, _asyncio.Lock] = {}

        async def singleflight_sim():
            key = "shared-key"
            lock = lock_dict.setdefault(key, _asyncio.Lock())
            async with lock:
                await _asyncio.sleep(0)  # 模拟最小 IO
            if not lock.locked():
                lock_dict.pop(key, None)

        async def concurrent_access():
            await _asyncio.gather(*[singleflight_sim() for _ in range(10)])

        benchmark(lambda: _asyncio.run(concurrent_access()))
