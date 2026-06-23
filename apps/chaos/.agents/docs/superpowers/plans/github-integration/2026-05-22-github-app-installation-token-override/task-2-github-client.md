# Task 2: 实现 GitHub 客户端与请求头覆盖逻辑

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
