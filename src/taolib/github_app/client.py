from datetime import UTC, datetime

import httpx
import jwt

from taolib.github_app.errors import GitHubAppClientError
from taolib.github_app.models import (
    EffectiveTokenStrategy,
    InstallationTokenResult,
    TokenKind,
)


class GitHubAppClient:
    def __init__(
        self,
        app_id: str,
        private_key: str,
        api_url: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.app_id = app_id
        self.private_key = private_key
        self.api_url = api_url.rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.api_url,
            transport=transport,
            timeout=10.0,
        )

    @staticmethod
    def classify_token_kind(token: str) -> TokenKind:
        if token.startswith("ghs_") and token[len("ghs_") :].count(".") == 2:
            return TokenKind.STATELESS
        if token.startswith("ghs_"):
            return TokenKind.STATEFUL
        return TokenKind.UNKNOWN

    def _build_override_headers(
        self, strategy: EffectiveTokenStrategy
    ) -> dict[str, str]:
        if strategy is EffectiveTokenStrategy.ENABLED:
            return {"X-GitHub-Stateless-S2S-Token": "enabled"}
        if strategy is EffectiveTokenStrategy.DISABLED:
            return {"X-GitHub-Stateless-S2S-Token": "disabled"}
        return {}

    def _create_app_jwt(self) -> str:
        now = int(datetime.now(tz=UTC).timestamp())
        payload = {"iat": now - 60, "exp": now + 540, "iss": self.app_id}
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def create_installation_token(
        self,
        installation_id: str,
        strategy: EffectiveTokenStrategy,
        permissions: dict[str, str] | None = None,
        repositories: list[str] | None = None,
    ) -> InstallationTokenResult:
        try:
            response = await self._http.post(
                f"/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {self._create_app_jwt()}",
                    "Accept": "application/vnd.github+json",
                    **self._build_override_headers(strategy),
                },
                json={
                    "permissions": permissions or {},
                    "repositories": repositories or [],
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GitHubAppClientError(
                "Failed to create a GitHub App installation token."
            ) from exc

        payload = response.json()
        token = payload["token"]
        return InstallationTokenResult(
            token=token,
            expires_at=datetime.fromisoformat(
                payload["expires_at"].replace("Z", "+00:00")
            ),
            token_kind=self.classify_token_kind(token),
            requested_strategy=strategy.value,
            effective_strategy=strategy.value,
            degraded=False,
        )
