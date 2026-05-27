from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import (
    EffectiveTokenStrategy,
    EnvironmentKind,
    GitHubRuntimeProfile,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
    TokenKind,
)
from taolib.github_app.token_manager import GitHubInstallationTokenManager


@pytest.mark.asyncio
async def test_manager_returns_cached_token_without_calling_upstream():
    cache = InMemoryInstallationTokenCache()
    client = AsyncMock()
    settings = GitHubAppSettings(
        app_id="123",
        installation_id="456",
        private_key="pem",
        api_url="https://api.github.com",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=True,
        runtime_profile=GitHubRuntimeProfile(
            base_url="https://api.github.com",
            environment=EnvironmentKind.CLOUD,
        ),
    )
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=cache,
        settings=settings,
    )
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    await cache.set(
        manager.build_cache_key(request),
        InstallationTokenResult(
            token="ghs_cached",
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=30),
            token_kind=TokenKind.STATEFUL,
            requested_strategy="auto",
            effective_strategy="none",
            degraded=False,
        ),
    )

    result = await manager.get_token(request)

    assert result.token == "ghs_cached"
    client.create_installation_token.assert_not_called()


@pytest.mark.asyncio
async def test_manager_reuses_ghes_cache_across_requested_strategies():
    call_count = 0

    async def create_installation_token(**_: object) -> InstallationTokenResult:
        nonlocal call_count
        call_count += 1
        return InstallationTokenResult(
            token="ghs_ghes",
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=30),
            token_kind=TokenKind.STATEFUL,
            requested_strategy="none",
            effective_strategy="none",
            degraded=False,
        )

    settings = GitHubAppSettings(
        app_id="123",
        installation_id="456",
        private_key="pem",
        api_url="https://github.example.com/api/v3",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=True,
        runtime_profile=GitHubRuntimeProfile(
            base_url="https://github.example.com/api/v3",
            environment=EnvironmentKind.GHES,
        ),
    )
    manager = GitHubInstallationTokenManager(
        client=AsyncMock(create_installation_token=create_installation_token),
        cache=InMemoryInstallationTokenCache(),
        settings=settings,
    )
    enabled_request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.ENABLED,
    )
    disabled_request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.DISABLED,
    )

    enabled_result = await manager.get_token(enabled_request)
    disabled_result = await manager.get_token(disabled_request)

    assert call_count == 1
    assert enabled_result.effective_strategy == "none"
    assert disabled_result.effective_strategy == "none"
    assert enabled_result.requested_strategy == "enabled"
    assert disabled_result.requested_strategy == "disabled"


def test_manager_disables_override_for_ghes():
    settings = GitHubAppSettings(
        app_id="123",
        installation_id="456",
        private_key="pem",
        api_url="https://github.example.com/api/v3",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=True,
        runtime_profile=GitHubRuntimeProfile(
            base_url="https://github.example.com/api/v3",
            environment=EnvironmentKind.GHES,
        ),
    )
    manager = GitHubInstallationTokenManager(
        client=AsyncMock(),
        cache=InMemoryInstallationTokenCache(),
        settings=settings,
    )

    effective = manager.resolve_effective_strategy(RequestedTokenStrategy.ENABLED)

    assert effective is EffectiveTokenStrategy.NONE
