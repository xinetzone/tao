"""P2 改进项的单元测试：锁清理与缓存 maxsize。"""

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.models import (
    EffectiveTokenStrategy,
    EnvironmentKind,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
    TokenKind,
)
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.token_manager import GitHubInstallationTokenManager


def _make_result(token: str = "ghs_abc") -> InstallationTokenResult:
    return InstallationTokenResult(
        token=token,
        expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
        token_kind=TokenKind.STATEFUL,
        requested_strategy=RequestedTokenStrategy.AUTO.value,
        effective_strategy=EffectiveTokenStrategy.NONE.value,
        degraded=False,
    )


def _make_manager(call_count_box: list[int] | None = None):
    """创建一个用于测试的 manager，client 使用 mock。"""
    settings = GitHubAppSettings.from_env.__func__  # 不调用，手动构建
    # 手动构建 settings
    from taolib.github_app.models import GitHubRuntimeProfile
    profile = GitHubRuntimeProfile(
        base_url="https://api.github.com",
        environment=EnvironmentKind.CLOUD,
    )
    settings = SimpleNamespace(
        app_id="123",
        installation_id="456",
        private_key="fake",
        api_url="https://api.github.com",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=False,
        runtime_profile=profile,
    )

    async def fake_create_token(**kwargs):
        if call_count_box is not None:
            call_count_box[0] += 1
        return _make_result()

    client = SimpleNamespace(create_installation_token=fake_create_token)
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings
    )
    return manager


@pytest.mark.asyncio
async def test_refresh_locks_cleaned_after_use():
    """验证 _refresh_locks 在刷新完成后被清理，不会无限增长。"""
    call_count = [0]
    manager = _make_manager(call_count)

    request = InstallationTokenRequest(
        installation_id="456",
        permissions={"contents": "read"},
        repositories=["repo1"],
        strategy=RequestedTokenStrategy.AUTO,
    )

    # 第一次调用后，锁应被清理
    await manager.get_token(request)
    assert len(manager._refresh_locks) == 0, (
        "_refresh_locks should be cleaned after refresh completes"
    )


@pytest.mark.asyncio
async def test_refresh_locks_not_cleaned_while_contended():
    """验证在并发争用时锁不会被过早清理。"""
    call_count = [0]
    manager = _make_manager(call_count)

    request = InstallationTokenRequest(
        installation_id="456",
        permissions={"contents": "read"},
        repositories=["repo1"],
        strategy=RequestedTokenStrategy.AUTO,
    )

    # 多个并发请求不会导致多次 API 调用
    results = await asyncio.gather(*(manager.get_token(request) for _ in range(10)))
    assert all(r.token == "ghs_abc" for r in results)
    assert call_count[0] == 1  # singleflight 仍然有效


@pytest.mark.asyncio
async def test_cache_maxsize_evicts_lru():
    """验证缓存超过 maxsize 时淘汰最久未访问的条目（LRU）。"""
    cache = InMemoryInstallationTokenCache(maxsize=3)

    for i in range(3):
        await cache.set(f"key{i}", _make_result(f"token{i}"))

    # 访问 key0，使其成为最近访问，不应被淘汰
    await cache.get("key0")

    # 缓存已满，写入第 4 个应淘汰 key1（最久未访问）
    await cache.set("key3", _make_result("token3"))

    assert await cache.get("key0") is not None, "recently accessed key0 should survive"
    assert await cache.get("key1") is None, "least recently used key1 should be evicted"
    assert await cache.get("key2") is not None
    assert await cache.get("key3") is not None


@pytest.mark.asyncio
async def test_cache_maxsize_update_existing_no_eviction():
    """验证更新已有 key 不会触发淘汰。"""
    cache = InMemoryInstallationTokenCache(maxsize=2)

    await cache.set("key0", _make_result("token0"))
    await cache.set("key1", _make_result("token1"))

    # 更新已有 key，不应淘汰
    await cache.set("key0", _make_result("token0_updated"))

    assert await cache.get("key0") is not None
    assert await cache.get("key1") is not None
    result = await cache.get("key0")
    assert result.token == "token0_updated"


@pytest.mark.asyncio
async def test_cache_default_maxsize():
    """验证默认 maxsize 为 256。"""
    cache = InMemoryInstallationTokenCache()
    assert cache._maxsize == 256
