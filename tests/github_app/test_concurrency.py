import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import (
    EnvironmentKind,
    GitHubRuntimeProfile,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
    TokenKind,
)
from taolib.github_app.token_manager import GitHubInstallationTokenManager


def build_manager(client: object) -> GitHubInstallationTokenManager:
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
    return GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=settings,
    )


@pytest.mark.asyncio
async def test_singleflight_refresh_collapses_parallel_requests():
    call_count = 0

    async def create_installation_token(**_: object) -> InstallationTokenResult:
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        return InstallationTokenResult(
            token="ghs_parallel",
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=30),
            token_kind=TokenKind.STATEFUL,
            requested_strategy="auto",
            effective_strategy="none",
            degraded=False,
        )

    client = SimpleNamespace(create_installation_token=create_installation_token)
    manager = build_manager(client)
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    results = await asyncio.gather(*(manager.get_token(request) for _ in range(25)))

    assert {item.token for item in results} == {"ghs_parallel"}
    assert call_count == 1
