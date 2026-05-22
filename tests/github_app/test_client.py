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
    client._create_app_jwt = lambda: "app-jwt"

    result = await client.create_installation_token(
        installation_id="456",
        strategy=EffectiveTokenStrategy.ENABLED,
    )

    assert seen_headers["override"] == "enabled"
    assert result.token_kind is TokenKind.STATELESS


def test_classify_token_kind_supports_both_formats():
    assert GitHubAppClient.classify_token_kind("ghs_opaquepayload") is (
        TokenKind.STATEFUL
    )
    assert GitHubAppClient.classify_token_kind("ghs_part.one.two") is (
        TokenKind.STATELESS
    )
