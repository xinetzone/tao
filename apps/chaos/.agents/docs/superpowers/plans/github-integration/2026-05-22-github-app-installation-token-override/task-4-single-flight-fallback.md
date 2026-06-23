# Task 4: 实现单飞刷新、回退与压力测试

**Files:**
- Create: `tests/github_app/test_concurrency.py`
- Create: `tests/github_app/test_stress.py`
- Modify: `src/taolib/github_app/token_manager.py`
- Modify: `src/taolib/github_app/cache.py`
- Modify: `src/taolib/github_app/models.py`

- [ ] **Step 1: 写失败测试，锁定单飞刷新与高并发上游压缩率**

```python
import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import EnvironmentKind, GitHubRuntimeProfile, InstallationTokenRequest, InstallationTokenResult, RequestedTokenStrategy, TokenKind
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
        runtime_profile=GitHubRuntimeProfile(base_url="https://api.github.com", environment=EnvironmentKind.CLOUD),
    )
    return GitHubInstallationTokenManager(client=client, cache=InMemoryInstallationTokenCache(), settings=settings)

@pytest.mark.asyncio
async def test_singleflight_refresh_collapses_parallel_requests():
    call_count = 0

    async def create_installation_token(**_: object):
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
    request = InstallationTokenRequest(installation_id="456", permissions={}, repositories=[], strategy=RequestedTokenStrategy.AUTO)

    results = await asyncio.gather(*(manager.get_token(request) for _ in range(25)))

    assert {item.token for item in results} == {"ghs_parallel"}
    assert call_count == 1


@pytest.mark.asyncio
@pytest.mark.slow
async def test_stress_path_keeps_failure_rate_at_zero():
    call_count = 0

    async def create_installation_token(**_: object):
        nonlocal call_count
        call_count += 1
        return InstallationTokenResult(
            token="ghs_stress",
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=30),
            token_kind=TokenKind.STATEFUL,
            requested_strategy="auto",
            effective_strategy="none",
            degraded=False,
        )

    client = SimpleNamespace(create_installation_token=create_installation_token)
    manager = build_manager(client)
    request = InstallationTokenRequest(installation_id="456", permissions={}, repositories=[], strategy=RequestedTokenStrategy.AUTO)

    results = await asyncio.gather(*(manager.get_token(request) for _ in range(100)))

    assert len(results) == 100
    assert call_count == 1
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_concurrency.py tests/github_app/test_stress.py -v`
Expected: FAIL with assertion errors because multiple upstream calls occur

- [ ] **Step 3: 写最小实现**

```python
# src/taolib/github_app/token_manager.py
class GitHubInstallationTokenManager:
    def __init__(self, client: GitHubAppClient, cache: InMemoryInstallationTokenCache, settings: GitHubAppSettings) -> None:
        self.client = client
        self.cache = cache
        self.settings = settings
        self._locks: dict[str, asyncio.Lock] = {}

    async def _refresh_with_singleflight(self, cache_key: str, request: InstallationTokenRequest) -> InstallationTokenResult:
        lock = self._locks.setdefault(cache_key, asyncio.Lock())
        async with lock:
            cached = await self.cache.get(cache_key)
            if cached and not self.cache.is_stale(cached, self.settings.eager_refresh_seconds):
                return cached
            return await self._request_and_store(cache_key, request)
```

```python
# src/taolib/github_app/cache.py
def is_stale(self, result: InstallationTokenResult, eager_refresh_seconds: int) -> bool:
    refresh_at = result.expires_at - timedelta(seconds=eager_refresh_seconds)
    return datetime.now(tz=UTC) >= refresh_at
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_concurrency.py tests/github_app/test_stress.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add src/taolib/github_app/token_manager.py src/taolib/github_app/cache.py src/taolib/github_app/models.py tests/github_app/test_concurrency.py tests/github_app/test_stress.py
git commit -m "feat: add token refresh deduplication"
```
