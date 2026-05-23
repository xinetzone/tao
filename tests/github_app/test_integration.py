"""TokenManager -> Client -> HTTP 全链路集成测试。

使用 ``httpx.MockTransport`` 模拟 GitHub API 响应，验证缓存、刷新、
Singleflight 与事件 hook 的端到端行为。
"""

import asyncio
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.errors import GitHubAppClientError
from taolib.github_app.models import (
    EnvironmentKind,
    GitHubRuntimeProfile,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
    TokenKind,
)
from taolib.github_app.token_manager import GitHubInstallationTokenManager


def _generate_private_key() -> str:
    """生成临时 RSA 私钥（PEM 格式），供 JWT 签名使用。"""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def _make_settings(private_key: str) -> GitHubAppSettings:
    """构造测试用的 GitHubAppSettings。"""
    return GitHubAppSettings(
        app_id="123",
        installation_id="456",
        private_key=private_key,
        api_url="https://api.github.com",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=True,
        runtime_profile=GitHubRuntimeProfile(
            base_url="https://api.github.com",
            environment=EnvironmentKind.CLOUD,
        ),
    )


class RecordingEventHook:
    """记录令牌刷新事件供断言使用的内存 hook 实现。"""

    def __init__(self) -> None:
        self.refreshed: list[tuple[str, InstallationTokenResult]] = []
        self.failed: list[tuple[str, Exception]] = []

    async def on_token_refreshed(
        self, cache_key: str, result: InstallationTokenResult
    ) -> None:
        self.refreshed.append((cache_key, result))

    async def on_token_refresh_failed(self, cache_key: str, error: Exception) -> None:
        self.failed.append((cache_key, error))


async def test_first_request_hits_network_and_second_uses_cache():
    """场景 1：首次获取令牌走 HTTP，第二次命中缓存不再发请求。"""
    call_count = 0
    pk = _generate_private_key()

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            201,
            json={"token": "ghs_a.b.c", "expires_at": "2099-01-01T00:00:00Z"},
        )

    client = GitHubAppClient(
        app_id="123",
        private_key=pk,
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    settings = _make_settings(pk)
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    result1 = await manager.get_token(request)
    assert result1.token == "ghs_a.b.c"
    assert call_count == 1

    result2 = await manager.get_token(request)
    assert result2.token == "ghs_a.b.c"
    assert call_count == 1


async def test_expired_token_triggers_auto_refresh():
    """场景 2：缓存中的令牌已过期，get_token 自动触发刷新。"""
    call_count = 0
    pk = _generate_private_key()

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            201,
            json={"token": "ghs_fresh", "expires_at": "2099-01-01T00:00:00Z"},
        )

    client = GitHubAppClient(
        app_id="123",
        private_key=pk,
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    settings = _make_settings(pk)
    settings.eager_refresh_seconds = 0
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )
    cache_key = manager.build_cache_key(request)

    await cache.set(
        cache_key,
        InstallationTokenResult(
            token="ghs_old",
            expires_at=datetime.now(tz=UTC) - timedelta(minutes=1),
            token_kind=TokenKind.STATEFUL,
            requested_strategy="auto",
            effective_strategy="none",
            degraded=False,
        ),
    )

    result = await manager.get_token(request)
    assert result.token == "ghs_fresh"
    assert call_count == 1


async def test_api_error_propagates_as_github_app_client_error():
    """场景 3：GitHub API 返回 500 时，异常正确包装为 GitHubAppClientError。"""
    pk = _generate_private_key()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "Internal Server Error"})

    client = GitHubAppClient(
        app_id="123",
        private_key=pk,
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    settings = _make_settings(pk)
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    with pytest.raises(GitHubAppClientError):
        await manager.get_token(request)


async def test_singleflight_dedups_concurrent_requests():
    """场景 4：并发调用 get_token 时，Singleflight 仅发起一次 HTTP 请求。"""
    call_count = 0
    pk = _generate_private_key()

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            201,
            json={"token": "ghs_single", "expires_at": "2099-01-01T00:00:00Z"},
        )

    client = GitHubAppClient(
        app_id="123",
        private_key=pk,
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    settings = _make_settings(pk)
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    results = await asyncio.gather(
        manager.get_token(request),
        manager.get_token(request),
        manager.get_token(request),
    )

    assert all(r.token == "ghs_single" for r in results)
    assert call_count == 1


async def test_event_hook_fires_on_refresh_success():
    """场景 5a：刷新成功时 on_token_refreshed 被正确触发。"""
    pk = _generate_private_key()
    hook = RecordingEventHook()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={"token": "ghs_hook_ok", "expires_at": "2099-01-01T00:00:00Z"},
        )

    client = GitHubAppClient(
        app_id="123",
        private_key=pk,
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    settings = _make_settings(pk)
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings, event_hook=hook
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    await manager.get_token(request)

    assert len(hook.refreshed) == 1
    assert hook.refreshed[0][1].token == "ghs_hook_ok"
    assert len(hook.failed) == 0


async def test_event_hook_fires_on_refresh_failure():
    """场景 5b：刷新失败时 on_token_refresh_failed 被正确触发。"""
    pk = _generate_private_key()
    hook = RecordingEventHook()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"message": "Service Unavailable"})

    client = GitHubAppClient(
        app_id="123",
        private_key=pk,
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    settings = _make_settings(pk)
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings, event_hook=hook
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    with pytest.raises(GitHubAppClientError):
        await manager.get_token(request)

    assert len(hook.refreshed) == 0
    assert len(hook.failed) == 1
    assert isinstance(hook.failed[0][1], GitHubAppClientError)
