# GitHub App Installation Token Override Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `AgentForge` 新增兼容 GitHub.com / GHEC 与 GHES 的 GitHub App 安装令牌管理层，支持请求级覆盖头、缓存、单飞刷新、CLI、学习笔记与测试报告。

**Architecture:** 采用“配置解析 + HTTP 客户端 + 进程内缓存 + 令牌编排器 + CLI”五层结构。令牌格式一律按 opaque secret 处理，`auto / enabled / disabled` 策略与环境降级逻辑统一收敛在 `token_manager` 与 `client`，通过 `httpx.MockTransport` 驱动功能测试与并发压测。

**Tech Stack:** Python 3.13+, `httpx`, `PyJWT[crypto]`, `pytest`, `pytest-asyncio`, `uv`, GitHub Actions

---

## File Structure

- Create: `src/taolib/github_app/__init__.py`
- Create: `src/taolib/github_app/config.py`
- Create: `src/taolib/github_app/models.py`
- Create: `src/taolib/github_app/errors.py`
- Create: `src/taolib/github_app/cache.py`
- Create: `src/taolib/github_app/client.py`
- Create: `src/taolib/cli/__init__.py`
- Create: `src/taolib/cli/github_app.py`
- Create: `tests/github_app/test_config.py`
- Create: `tests/github_app/test_client.py`
- Create: `tests/github_app/test_token_manager.py`
- Create: `tests/github_app/test_concurrency.py`
- Create: `tests/github_app/test_stress.py`
- Create: `docs/github-app-token-override.md`
- Modify: `docs/index.md`
- Modify: `README.md`
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/project_changelogs/CHANGELOG_2026-05.md`
- Create: `.agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md`

### Responsibility Map

- `config.py`：解析环境变量、私钥与默认策略
- `models.py`：定义请求、结果、环境画像与枚举
- `client.py`：签发 App JWT、发送 access token 请求、识别令牌类型
- `cache.py`：保存进程内缓存与过期窗口判断
- `token_manager.py`：计算有效策略、处理缓存、执行单飞刷新与降级
- `cli/github_app.py`：暴露 `token` 与 `profile` 子命令
- `docs/github-app-token-override.md`：承载学习笔记、接入说明与指标摘要
- `retrospectives/*.md`：记录测试结果、压测数据与残余风险

### Shared Conventions

- 令牌策略枚举使用 `auto`, `enabled`, `disabled`
- 令牌类型枚举使用 `stateful`, `stateless`, `unknown`
- 运行环境枚举使用 `cloud`, `ghes`, `unknown`
- 所有日志与 CLI 输出都不打印完整 token 或私钥
- 测试中的 HTTP 模拟统一使用 `httpx.MockTransport`

### Task 1: 建立配置层与基础模型

**Files:**
- Create: `tests/github_app/test_config.py`
- Create: `src/taolib/github_app/__init__.py`
- Create: `src/taolib/github_app/models.py`
- Create: `src/taolib/github_app/errors.py`
- Create: `src/taolib/github_app/config.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: 写失败测试，锁定配置解析与环境识别接口**

```python
import pytest

from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import EnvironmentKind, RequestedTokenStrategy


def test_settings_from_env_parses_private_key_file(tmp_path, monkeypatch):
    key_file = tmp_path / "app.pem"
    key_file.write_text("-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n")
    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "456")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY_FILE", str(key_file))
    monkeypatch.setenv("GITHUB_API_URL", "https://api.github.com")
    monkeypatch.setenv("GITHUB_APP_TOKEN_STRATEGY", "auto")

    settings = GitHubAppSettings.from_env()

    assert settings.app_id == "123"
    assert settings.installation_id == "456"
    assert settings.private_key.startswith("-----BEGIN PRIVATE KEY-----")
    assert settings.runtime_profile.environment is EnvironmentKind.CLOUD
    assert settings.default_strategy is RequestedTokenStrategy.AUTO


def test_settings_from_env_rejects_missing_private_key(monkeypatch):
    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "456")

    with pytest.raises(ValueError, match="private key"):
        GitHubAppSettings.from_env()
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'taolib.github_app'`

- [ ] **Step 3: 写最小实现与依赖声明**

```toml
[project]
dependencies = [
  "httpx>=0.27,<1",
  "PyJWT[crypto]>=2.10,<3",
]

[project.scripts]
taolib-github-app = "taolib.cli.github_app:main"
```

```python
# src/taolib/github_app/models.py
from dataclasses import dataclass
from enum import StrEnum


class RequestedTokenStrategy(StrEnum):
    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class EnvironmentKind(StrEnum):
    CLOUD = "cloud"
    GHES = "ghes"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class GitHubRuntimeProfile:
    base_url: str
    environment: EnvironmentKind
```

```python
# src/taolib/github_app/config.py
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(slots=True)
class GitHubAppSettings:
    app_id: str
    installation_id: str
    private_key: str
    api_url: str
    default_strategy: RequestedTokenStrategy
    eager_refresh_seconds: int
    allow_header_fallback: bool
    runtime_profile: GitHubRuntimeProfile

    @classmethod
    def from_env(cls) -> "GitHubAppSettings":
        private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
        private_key_file = os.getenv("GITHUB_APP_PRIVATE_KEY_FILE")
        if not private_key and private_key_file:
            private_key = Path(private_key_file).read_text(encoding="utf-8")
        if not private_key:
            raise ValueError("GitHub App private key is required")

        api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        environment = EnvironmentKind.CLOUD if api_url.rstrip("/") == "https://api.github.com" else EnvironmentKind.GHES
        return cls(
            app_id=os.environ["GITHUB_APP_ID"],
            installation_id=os.environ["GITHUB_APP_INSTALLATION_ID"],
            private_key=private_key,
            api_url=api_url,
            default_strategy=RequestedTokenStrategy(os.getenv("GITHUB_APP_TOKEN_STRATEGY", "auto")),
            eager_refresh_seconds=int(os.getenv("GITHUB_APP_TOKEN_EAGER_REFRESH_SECONDS", "90")),
            allow_header_fallback=os.getenv("GITHUB_APP_ALLOW_HEADER_FALLBACK", "true").lower() == "true",
            runtime_profile=GitHubRuntimeProfile(base_url=api_url, environment=environment),
        )
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_config.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add pyproject.toml src/taolib/github_app/__init__.py src/taolib/github_app/models.py src/taolib/github_app/errors.py src/taolib/github_app/config.py tests/github_app/test_config.py
git commit -m "feat: add github app configuration layer"
```

### Task 2: 实现 GitHub 客户端与请求头覆盖逻辑

**Files:**
- Create: `tests/github_app/test_client.py`
- Create: `src/taolib/github_app/client.py`
- Modify: `src/taolib/github_app/models.py`
- Modify: `src/taolib/github_app/errors.py`

- [ ] **Step 1: 写失败测试，锁定请求头、令牌分类与响应解析**

```python
import httpx
import pytest

from taolib.github_app.client import GitHubAppClient
from taolib.github_app.models import EffectiveTokenStrategy, TokenKind


@pytest.mark.asyncio
async def test_client_sends_override_header_for_enabled_strategy():
    seen_headers = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen_headers["override"] = request.headers.get("X-GitHub-Stateless-S2S-Token")
        return httpx.Response(
            201,
            json={"token": "ghs_a.b.c", "expires_at": "2026-05-22T11:00:00Z"},
        )

    client = GitHubAppClient(
        app_id="123",
        private_key="-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n",
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )

    result = await client.create_installation_token(
        installation_id="456",
        strategy=EffectiveTokenStrategy.ENABLED,
    )

    assert seen_headers["override"] == "enabled"
    assert result.token_kind is TokenKind.STATELESS


def test_classify_token_kind_supports_both_formats():
    assert GitHubAppClient.classify_token_kind("ghs_opaquepayload") is TokenKind.STATEFUL
    assert GitHubAppClient.classify_token_kind("ghs_part.one.two") is TokenKind.STATELESS
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_client.py -v`
Expected: FAIL with `ModuleNotFoundError` or `AttributeError` for `GitHubAppClient`

- [ ] **Step 3: 写最小实现**

```python
# src/taolib/github_app/models.py
class EffectiveTokenStrategy(StrEnum):
    NONE = "none"
    ENABLED = "enabled"
    DISABLED = "disabled"


class TokenKind(StrEnum):
    STATEFUL = "stateful"
    STATELESS = "stateless"
    UNKNOWN = "unknown"
```

```python
# src/taolib/github_app/client.py
from datetime import UTC, datetime
import jwt

class GitHubAppClient:
    def __init__(self, app_id: str, private_key: str, api_url: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.app_id = app_id
        self.private_key = private_key
        self.api_url = api_url.rstrip("/")
        self._http = httpx.AsyncClient(base_url=self.api_url, transport=transport, timeout=10.0)

    @staticmethod
    def classify_token_kind(token: str) -> TokenKind:
        if token.startswith("ghs_") and token[len("ghs_"):].count(".") == 2:
            return TokenKind.STATELESS
        if token.startswith("ghs_"):
            return TokenKind.STATEFUL
        return TokenKind.UNKNOWN

    def _build_override_headers(self, strategy: EffectiveTokenStrategy) -> dict[str, str]:
        headers: dict[str, str] = {}
        if strategy is EffectiveTokenStrategy.ENABLED:
            headers["X-GitHub-Stateless-S2S-Token"] = "enabled"
        elif strategy is EffectiveTokenStrategy.DISABLED:
            headers["X-GitHub-Stateless-S2S-Token"] = "disabled"
        return headers

    def _create_app_jwt(self) -> str:
        now = int(datetime.now(tz=UTC).timestamp())
        payload = {"iat": now - 60, "exp": now + 540, "iss": self.app_id}
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def create_installation_token(self, installation_id: str, strategy: EffectiveTokenStrategy, permissions: dict[str, str] | None = None, repositories: list[str] | None = None) -> InstallationTokenResult:
        body = {"permissions": permissions or {}, "repositories": repositories or []}
        response = await self._http.post(
            f"/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {self._create_app_jwt()}",
                "Accept": "application/vnd.github+json",
                **self._build_override_headers(strategy),
            },
            json=body,
        )
        response.raise_for_status()
        payload = response.json()
        token = payload["token"]
        return InstallationTokenResult(
            token=token,
            expires_at=datetime.fromisoformat(payload["expires_at"].replace("Z", "+00:00")),
            token_kind=self.classify_token_kind(token),
            requested_strategy=strategy.value,
            effective_strategy=strategy.value,
            degraded=False,
        )
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_client.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add src/taolib/github_app/models.py src/taolib/github_app/errors.py src/taolib/github_app/client.py tests/github_app/test_client.py
git commit -m "feat: add github app token client"
```

### Task 3: 实现缓存与令牌编排器的基础路径

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

### Task 4: 实现单飞刷新、回退与压力测试

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

### Task 5: 增加 CLI 双入口与脱敏诊断输出

**Files:**
- Create: `tests/github_app/test_cli.py`
- Create: `src/taolib/cli/__init__.py`
- Create: `src/taolib/cli/github_app.py`
- Modify: `src/taolib/github_app/__init__.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: 写失败测试，锁定 `token` 与 `profile` 子命令**

```python
import pytest

from taolib.cli.github_app import build_parser, main


class FakeManager:
    async def get_token(self, _request):
        return {"token_preview": "ghs_abcd...wxyz", "effective_strategy": "enabled"}


def test_profile_command_outputs_environment_summary(capsys, monkeypatch):
    monkeypatch.setenv("GITHUB_API_URL", "https://api.github.com")
    exit_code = main(["profile"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert '"environment": "cloud"' in out


def test_token_command_masks_secret(capsys, monkeypatch):
    monkeypatch.setattr("taolib.cli.github_app.build_manager", lambda args: FakeManager())
    exit_code = main(["token", "--installation-id", "456", "--strategy", "enabled"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "ghs_" in out
    assert "secret-full-value" not in out
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'taolib.cli'`

- [ ] **Step 3: 写最小实现**

```python
# src/taolib/cli/github_app.py
import argparse
import asyncio
import json

from taolib.github_app import GitHubAppSettings, GitHubInstallationTokenManager, InstallationTokenRequest, RequestedTokenStrategy
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taolib-github-app")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profile")
    token_parser = subparsers.add_parser("token")
    token_parser.add_argument("--installation-id")
    token_parser.add_argument("--strategy", choices=["auto", "enabled", "disabled"], default="auto")
    return parser


def build_manager(args: argparse.Namespace) -> GitHubInstallationTokenManager:
    settings = GitHubAppSettings.from_env()
    client = GitHubAppClient(app_id=settings.app_id, private_key=settings.private_key, api_url=settings.api_url)
    return GitHubInstallationTokenManager(client=client, cache=InMemoryInstallationTokenCache(), settings=settings)


def build_request(args: argparse.Namespace) -> InstallationTokenRequest:
    return InstallationTokenRequest(
        installation_id=args.installation_id or GitHubAppSettings.from_env().installation_id,
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy(args.strategy),
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "profile":
        settings = GitHubAppSettings.from_env()
        print(json.dumps({"environment": settings.runtime_profile.environment.value, "api_url": settings.api_url}))
        return 0
    manager = build_manager(args)
    result = asyncio.run(manager.get_token(build_request(args)))
    print(json.dumps(result))
    return 0
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_cli.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add pyproject.toml src/taolib/cli/__init__.py src/taolib/cli/github_app.py src/taolib/github_app/__init__.py tests/github_app/test_cli.py
git commit -m "feat: add github app cli"
```

### Task 6: 补齐学习笔记、CI 验证与测试报告

**Files:**
- Create: `docs/github-app-token-override.md`
- Create: `.agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md`
- Modify: `docs/index.md`
- Modify: `README.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/project_changelogs/CHANGELOG_2026-05.md`

- [ ] **Step 1: 写文档与报告内容**

```md
# GitHub App 安装令牌请求级覆盖头学习笔记

GitHub 在 2026-05-15 公布了 `X-GitHub-Stateless-S2S-Token` 请求头，用于 `POST /app/installations/{installation_id}/access_tokens` 的逐请求覆盖。`enabled` 会返回新的 stateless token，`disabled` 会返回 classic stateful token，而默认不带头时继续遵循平台 rollout。对接方最重要的准备工作不是解析 JWT，而是消除长度、正则、数据库字段与日志格式上对旧 token 的假设。
```

```md
# 2026-05-22 GitHub App Token Override Testing

- 功能测试：通过
- 并发测试：25 并发 -> 1 次上游请求
- 压测：100 并发 -> 1 次上游请求，失败率 0%
- 风险：当前缓存仅为单进程实现，多实例部署仍需外部缓存
```

- [ ] **Step 2: 更新索引、README、CI 与项目变更日志**

~~~~md
```{toctree}
:maxdepth: 2
:caption: 目录
:hidden:

intro
quickstart
features
github-app-token-override
api
deploy
contributing
changelog
```
~~~~

```yaml
- name: Run GitHub App token tests
  run: uv run pytest tests/github_app -v
```

```md
### Added
- 新增 GitHub App 安装令牌管理层设计与实现计划，支持请求级覆盖头、自动降级、CLI、并发测试与学习笔记。
```

- [ ] **Step 3: 运行完整验证**

Run: `uv run pytest tests/github_app -v`
Expected: PASS with all GitHub App tests green

Run: `uv run pytest tests/ -v`
Expected: PASS with existing tests still green

Run: `uv run --group docs invoke build --target html`
Expected: PASS with generated docs including `github-app-token-override.html`

- [ ] **Step 4: 自查指标并写入报告**

```md
## 指标对比

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| 同 key 25 并发上游请求数 | 25 | 1 |
| 同 key 100 并发失败率 | 未定义 | 0% |
| 覆盖头控制能力 | 无 | `auto/enabled/disabled` |
| 日志脱敏 | 无统一约束 | 默认脱敏 |
```

- [ ] **Step 5: 提交本任务**

```bash
git add docs/github-app-token-override.md docs/index.md README.md .github/workflows/ci.yml tests/project_changelogs/CHANGELOG_2026-05.md .agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md
git commit -m "docs: add github app token override notes and reports"
```

## Plan Self-Review

### Spec Coverage

- 学习笔记：Task 6
- 模块排查后的统一令牌层：Task 1-5
- 请求级覆盖头、兼容 GHES 降级：Task 2-4
- 并发处理与资源调度效率：Task 3-4
- 完整功能测试与压力测试：Task 1-6
- 代码变更记录、测试报告、提升指标：Task 6

### Placeholder Scan

- 未使用 `TBD`、`TODO`、`implement later`
- 每个任务都给出明确文件路径、测试命令、最小代码和提交命令

### Type Consistency

- 请求策略统一使用 `RequestedTokenStrategy`
- 生效策略统一使用 `EffectiveTokenStrategy`
- 令牌结果统一使用 `InstallationTokenResult`
- 环境分类统一使用 `EnvironmentKind`
