import httpx
import jwt
import pytest

from taolib.cli.github_app import main
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.errors import GitHubAppClientError, GitHubAppConfigurationError
from taolib.github_app.models import EffectiveTokenStrategy


# ---------------------------------------------------------------------------
# 1. Invalid private key → JWT encoding error
# ---------------------------------------------------------------------------


def test_invalid_private_key_raises_jwt_error():
    client = GitHubAppClient(
        app_id="123",
        private_key="not-a-valid-key",
        api_url="https://api.github.com",
    )
    with pytest.raises(jwt.InvalidKeyError):
        client._create_app_jwt()


# ---------------------------------------------------------------------------
# 2. API 4xx → GitHubAppClientError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [401, 403, 404])
async def test_api_4xx_raises_client_error(status_code: int):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    client = GitHubAppClient(
        app_id="123",
        private_key="-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n",
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    client._create_app_jwt = lambda: "app-jwt"

    with pytest.raises(GitHubAppClientError):
        await client.create_installation_token(
            installation_id="456",
            strategy=EffectiveTokenStrategy.NONE,
        )


# ---------------------------------------------------------------------------
# 3. API 5xx → GitHubAppClientError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [500, 503])
async def test_api_5xx_raises_client_error(status_code: int):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    client = GitHubAppClient(
        app_id="123",
        private_key="-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n",
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    client._create_app_jwt = lambda: "app-jwt"

    with pytest.raises(GitHubAppClientError):
        await client.create_installation_token(
            installation_id="456",
            strategy=EffectiveTokenStrategy.NONE,
        )


# ---------------------------------------------------------------------------
# 4. Network timeout → GitHubAppClientError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_network_timeout_raises_client_error():
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("connection timed out")

    client = GitHubAppClient(
        app_id="123",
        private_key="-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n",
        api_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    client._create_app_jwt = lambda: "app-jwt"

    with pytest.raises(GitHubAppClientError):
        await client.create_installation_token(
            installation_id="456",
            strategy=EffectiveTokenStrategy.NONE,
        )


# ---------------------------------------------------------------------------
# 5. Missing private key → GitHubAppConfigurationError
# ---------------------------------------------------------------------------


def test_missing_private_key_raises_configuration_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY_FILE", raising=False)

    with pytest.raises(GitHubAppConfigurationError):
        GitHubAppSettings.from_env()


# ---------------------------------------------------------------------------
# 6. CLI configuration error → exit 1 + stderr JSON
# ---------------------------------------------------------------------------


def test_cli_configuration_error_returns_exit_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY_FILE", raising=False)

    exit_code = main(["token"])
    assert exit_code == 1

    captured = capsys.readouterr()
    import json

    payload = json.loads(captured.err)
    assert "error" in payload


# ---------------------------------------------------------------------------
# 7. CLI client error → exit 2 + stderr JSON
# ---------------------------------------------------------------------------


def test_cli_client_error_returns_exit_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "456")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n")

    from taolib.github_app.client import GitHubAppClient as _Client

    original_init = _Client.__init__

    def patched_init(self, *args, transport=None, **kwargs):
        transport = httpx.MockTransport(handler)
        original_init(self, *args, transport=transport, **kwargs)
        self._create_app_jwt = lambda: "app-jwt"

    monkeypatch.setattr(_Client, "__init__", patched_init)

    exit_code = main(["token"])
    assert exit_code == 2

    captured = capsys.readouterr()
    import json

    payload = json.loads(captured.err)
    assert "error" in payload
