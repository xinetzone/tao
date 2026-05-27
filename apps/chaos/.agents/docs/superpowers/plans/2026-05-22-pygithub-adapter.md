# PyGithub Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为现有的 GitHub App 安装令牌管理器增加一个 `PyGithub` 薄适配层，方便业务使用对象化 API。

**Architecture:** 保留现有的 `httpx` 和 JWT 生成机制不变，在上方增加 `PyGithubInstallationClientFactory`，通过接收 `manager` 和 `settings`，获取到 token 后组装为 `github.Github` 对象并返回。

**Tech Stack:** Python 3.13+, `PyGithub`, `pytest`, `pytest-asyncio`

---

### Task 1: Update Dependencies

**Files:**
- Modify: `pyproject.toml:15-19`

- [ ] **Step 1: Write the failing dependency import test**

Create `tests/github_app/test_pygithub_adapter.py`:
```python
def test_pygithub_is_installed():
    import github
    assert github.__name__ == "github"
```

- [ ] **Step 2: Run test to verify it fails (or might pass if already installed globally, but we want it in project)**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`

- [ ] **Step 3: Modify `pyproject.toml`**

Modify `pyproject.toml` to include `PyGithub`:
```toml
[project.optional-dependencies]
github-app = [
  "httpx>=0.27,<1",
  "PyJWT[crypto]>=2.10,<3",
  "PyGithub>=2.5,<3",
]
```

- [ ] **Step 4: Sync dependencies and run test to verify it passes**

Run: `uv sync`
Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock tests/github_app/test_pygithub_adapter.py
git commit -m "build: add PyGithub to github-app optional dependencies"
```

---

### Task 2: Implement PyGithub Adapter

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

---

### Task 3: Expose Interfaces in `__init__.py`

**Files:**
- Modify: `tests/github_app/test_pygithub_adapter.py`
- Modify: `src/taolib/github_app/__init__.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/github_app/test_pygithub_adapter.py`:
```python
def test_module_exports():
    import taolib.github_app

    assert hasattr(taolib.github_app, "PyGithubInstallationClientFactory")
    assert hasattr(taolib.github_app, "build_pygithub_client")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py::test_module_exports -v`
Expected: FAIL (AssertionError)

- [ ] **Step 3: Write minimal implementation**

Modify `src/taolib/github_app/__init__.py` to import and expose the new classes/functions.

Append the imports to the existing imports block:
```python
from taolib.github_app.pygithub_adapter import (
    PyGithubInstallationClientFactory,
    build_pygithub_client,
)
```

Update `__all__` array to include the new symbols:
```python
__all__ = [
    "EffectiveTokenStrategy",
    "EnvironmentKind",
    "GitHubAppClient",
    "GitHubAppClientError",
    "GitHubAppConfigurationError",
    "GitHubAppError",
    "GitHubAppSettings",
    "GitHubInstallationTokenManager",
    "GitHubRuntimeProfile",
    "InMemoryInstallationTokenCache",
    "InstallationTokenRequest",
    "InstallationTokenResult",
    "PyGithubInstallationClientFactory",
    "RequestedTokenStrategy",
    "TokenKind",
    "build_pygithub_client",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/taolib/github_app/__init__.py tests/github_app/test_pygithub_adapter.py
git commit -m "feat: expose PyGithub adapter interfaces"
```
