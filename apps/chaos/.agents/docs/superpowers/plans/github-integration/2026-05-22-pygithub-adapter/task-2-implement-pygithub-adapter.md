# Task 2: Implement PyGithub Adapter

**Files:**
- Modify: `tests/github_app/test_pygithub_adapter.py`
- Create: `src/taolib/github_app/pygithub_adapter.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/github_app/test_pygithub_adapter.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`
Expected: FAIL (ImportError or ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

Create `src/taolib/github_app/pygithub_adapter.py`:
```python
from github import Auth, Github

from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import InstallationTokenRequest
from taolib.github_app.token_manager import GitHubInstallationTokenManager


class PyGithubInstallationClientFactory:
    def __init__(
        self,
        settings: GitHubAppSettings,
        manager: GitHubInstallationTokenManager,
    ) -> None:
        self.settings = settings
        self.manager = manager

    async def create(self, request: InstallationTokenRequest) -> Github:
        result = await self.manager.get_token(request)
        auth = Auth.Token(result.token)
        return Github(auth=auth, base_url=self.settings.api_url)


async def build_pygithub_client(
    settings: GitHubAppSettings,
    manager: GitHubInstallationTokenManager,
    request: InstallationTokenRequest,
) -> Github:
    factory = PyGithubInstallationClientFactory(settings=settings, manager=manager)
    return await factory.create(request)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/github_app/test_pygithub_adapter.py src/taolib/github_app/pygithub_adapter.py
git commit -m "feat: implement PyGithub adapter layer"
```
