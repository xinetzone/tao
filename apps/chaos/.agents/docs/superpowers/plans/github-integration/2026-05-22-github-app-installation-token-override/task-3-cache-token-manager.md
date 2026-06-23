# Task 3: 实现缓存与令牌编排器的基础路径

**Files:**
- Create: `tests/github_app/test_token_manager.py`
- Create: `src/taolib/github_app/cache.py`
- Create: `src/taolib/github_app/token_manager.py`
- Modify: `src/taolib/github_app/models.py`
- Modify: `src/taolib/github_app/__init__.py`

- [ ] **Step 1: 写失败测试，锁定缓存命中、策略计算与基本降级**

```python
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import EffectiveTokenStrategy, EnvironmentKind, GitHubRuntimeProfile, InstallationTokenRequest, InstallationTokenResult, RequestedTokenStrategy, TokenKind
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
        runtime_profile=GitHubRuntimeProfile(base_url="https://api.github.com", environment=EnvironmentKind.CLOUD),
    )
    manager = GitHubInstallationTokenManager(client=client, cache=cache, settings=settings)
    request = InstallationTokenRequest(installation_id="456", permissions={}, repositories=[], strategy=RequestedTokenStrategy.AUTO)

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


def test_manager_disables_override_for_ghes():
    settings = GitHubAppSettings(
        app_id="123",
        installation_id="456",
        private_key="pem",
        api_url="https://github.example.com/api/v3",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=True,
        runtime_profile=GitHubRuntimeProfile(base_url="https://github.example.com/api/v3", environment=EnvironmentKind.GHES),
    )
    manager = GitHubInstallationTokenManager(client=AsyncMock(), cache=InMemoryInstallationTokenCache(), settings=settings)

    effective = manager.resolve_effective_strategy(RequestedTokenStrategy.ENABLED)

    assert effective is EffectiveTokenStrategy.NONE
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_token_manager.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `GitHubInstallationTokenManager`

- [ ] **Step 3: 写最小实现**

```python
# src/taolib/github_app/cache.py
from datetime import UTC, datetime, timedelta

class InMemoryInstallationTokenCache:
    def __init__(self) -> None:
        self._items: dict[str, InstallationTokenResult] = {}

    async def get(self, key: str) -> InstallationTokenResult | None:
        return self._items.get(key)

    async def set(self, key: str, result: InstallationTokenResult) -> None:
        self._items[key] = result

    def is_stale(self, result: InstallationTokenResult, eager_refresh_seconds: int) -> bool:
        refresh_at = result.expires_at - timedelta(seconds=eager_refresh_seconds)
        return datetime.now(tz=UTC) >= refresh_at
```

```python
# src/taolib/github_app/token_manager.py
class GitHubInstallationTokenManager:
    def build_cache_key(self, request: InstallationTokenRequest) -> str:
        return f"{request.installation_id}|{sorted(request.permissions.items())}|{request.repositories}|{request.strategy.value}"

    def resolve_effective_strategy(self, requested: RequestedTokenStrategy) -> EffectiveTokenStrategy:
        if self.settings.runtime_profile.environment is EnvironmentKind.GHES:
            return EffectiveTokenStrategy.NONE
        if requested is RequestedTokenStrategy.ENABLED:
            return EffectiveTokenStrategy.ENABLED
        if requested is RequestedTokenStrategy.DISABLED:
            return EffectiveTokenStrategy.DISABLED
        return EffectiveTokenStrategy.NONE

    async def get_token(self, request: InstallationTokenRequest) -> InstallationTokenResult:
        cache_key = self.build_cache_key(request)
        cached = await self.cache.get(cache_key)
        if cached and not self.cache.is_stale(cached, self.settings.eager_refresh_seconds):
            return cached
        effective = self.resolve_effective_strategy(request.strategy)
        result = await self.client.create_installation_token(
            installation_id=request.installation_id,
            strategy=effective,
            permissions=request.permissions,
            repositories=request.repositories,
        )
        await self.cache.set(cache_key, result)
        return result
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_token_manager.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add src/taolib/github_app/cache.py src/taolib/github_app/token_manager.py src/taolib/github_app/models.py src/taolib/github_app/__init__.py tests/github_app/test_token_manager.py
git commit -m "feat: add github app token manager"
```
