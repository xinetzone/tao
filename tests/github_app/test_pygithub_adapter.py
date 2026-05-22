def test_pygithub_is_installed():
    import github
    assert github.__name__ == "github"


from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from github import Github

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
from taolib.github_app.pygithub_adapter import (
    PyGithubInstallationClientFactory,
    build_pygithub_client,
)


@pytest.fixture
def mock_settings():
    return GitHubAppSettings(
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


@pytest.fixture
def mock_manager():
    manager = AsyncMock(spec=GitHubInstallationTokenManager)
    manager.get_token.return_value = InstallationTokenResult(
        token="ghs_dummy_token",
        expires_at=datetime.now(tz=UTC),
        token_kind=TokenKind.STATELESS,
        requested_strategy="auto",
        effective_strategy="none",
        degraded=False,
    )
    return manager


@pytest.mark.asyncio
async def test_factory_creates_github_client(mock_settings, mock_manager):
    factory = PyGithubInstallationClientFactory(settings=mock_settings, manager=mock_manager)
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    client = await factory.create(request)

    assert isinstance(client, Github)
    mock_manager.get_token.assert_awaited_once_with(request)


@pytest.mark.asyncio
async def test_build_pygithub_client_helper(mock_settings, mock_manager):
    request = InstallationTokenRequest(
        installation_id="456",
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy.AUTO,
    )

    client = await build_pygithub_client(
        settings=mock_settings,
        manager=mock_manager,
        request=request,
    )

    assert isinstance(client, Github)
    mock_manager.get_token.assert_awaited_once_with(request)
