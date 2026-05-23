"""与 GitHub API 交互的异步 HTTP 客户端。

本模块封装 JWT 签发、覆盖头下发与 GitHub REST API 调用，是跨越
令牌管理逻辑与 GitHub 远端服务的唯一负责者。
"""

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
    """与 GitHub API 直接交互的异步 HTTP 客户端。

    本类负责 JWT 签发、覆盖头拼装与安装令牌的 HTTP 调用，不参与缓存
    与并发控制，后者由 :class:`taolib.github_app.token_manager.GitHubInstallationTokenManager`
    负责。
    """

    def __init__(
        self,
        app_id: str,
        private_key: str,
        api_url: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """初始化客户端。

        Args:
            app_id: GitHub App 的 App ID。
            private_key: PEM 格式的 RSA 私钥内容。
            api_url: GitHub API 基地址，尾部斜杠会被自动去除。
            transport: 可选的 ``httpx`` 传输层，测试中可注入 mock。
        """
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
        """根据令牌字符串的前缀与结构特征判定令牌类型。

        Args:
            token: 安装令牌明文。

        Returns:
            - 以 ``ghs_`` 开头且后缀含恰好两个 ``.`` → :attr:`TokenKind.STATELESS`
            - 以 ``ghs_`` 开头但不含两个 ``.`` → :attr:`TokenKind.STATEFUL`
            - 其他 → :attr:`TokenKind.UNKNOWN`
        """
        if token.startswith("ghs_") and token[len("ghs_") :].count(".") == 2:
            return TokenKind.STATELESS
        if token.startswith("ghs_"):
            return TokenKind.STATEFUL
        return TokenKind.UNKNOWN

    def _build_override_headers(
        self, strategy: EffectiveTokenStrategy
    ) -> dict[str, str]:
        """根据生效策略构建 ``X-GitHub-Stateless-S2S-Token`` 头。

        Args:
            strategy: 实际生效的令牌策略。

        Returns:
            需要叠加的请求头字典；:attr:`EffectiveTokenStrategy.NONE` 返回空字典。
        """
        if strategy is EffectiveTokenStrategy.ENABLED:
            return {"X-GitHub-Stateless-S2S-Token": "enabled"}
        if strategy is EffectiveTokenStrategy.DISABLED:
            return {"X-GitHub-Stateless-S2S-Token": "disabled"}
        return {}

    def _create_app_jwt(self) -> str:
        """为当前 App 签发一个短期有效的 JWT。

        有效期为九分钟，``iat`` 提前 60 秒以容忍轻微时钟偏移。

        Returns:
            使用 RS256 算法签名的 JWT 字符串。
        """
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
        """携带 JWT 与策略覆盖头请求安装令牌。

        向 ``/app/installations/{installation_id}/access_tokens`` 发送
        ``POST`` 请求，并将响应转换为 :class:`InstallationTokenResult`。

        Args:
            installation_id: GitHub App 安装实例 ID。
            strategy: 实际生效的令牌策略，决定是否下发覆盖头。
            permissions: 限定令牌能力的权限映射，``None`` 会被平价为空字典。
            repositories: 限定令牌可访问的仓库列表，``None`` 会被平价为空列表。

        Returns:
            成功创建的 :class:`InstallationTokenResult`。

        Raises:
            GitHubAppClientError: HTTP 调用失败或返回非 2xx 状态码。
        """
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
