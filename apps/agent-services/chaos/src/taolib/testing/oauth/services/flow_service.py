"""OAuth 流程服务模块。

编排 OAuth2 授权码流程：生成授权 URL、交换授权码、获取用户信息。
"""

from typing import Any

from ..cache.state_store import OAuthStateStore
from ..crypto.token_encryption import TokenEncryptor
from ..errors import OAuthCredentialNotFoundError, OAuthStateError
from ..models.profile import OAuthUserInfo
from ..providers import ProviderRegistry
from ..repository.credential_repo import OAuthAppCredentialRepository


class OAuthFlowService:
    """OAuth 流程服务。

    管理 OAuth2 授权码流程的完整生命周期。

    Args:
        credential_repo: 应用凭证仓储
        state_store: CSRF state 存储
        provider_registry: 提供商注册表
        token_encryptor: Token 加密器
    """

    def __init__(
        self,
        credential_repo: OAuthAppCredentialRepository,
        state_store: OAuthStateStore,
        provider_registry: ProviderRegistry,
        token_encryptor: TokenEncryptor,
    ) -> None:
        self._credential_repo = credential_repo
        self._state_store = state_store
        self._provider_registry = provider_registry
        self._token_encryptor = token_encryptor

    async def generate_authorize_url(
        self,
        provider: str,
        redirect_uri: str | None = None,
        extra_state: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """生成 OAuth 授权 URL。

        Args:
            provider: 提供商名称
            redirect_uri: 自定义回调 URI（可选）
            extra_state: 附加到 state 的数据（如 link_to_user_id）

        Returns:
            (authorize_url, state_token) 元组

        Raises:
            OAuthCredentialNotFoundError: 未找到凭证
        """
        credential = await self._credential_repo.find_by_provider(provider)
        if credential is None:
            raise OAuthCredentialNotFoundError(f"未找到 {provider} 的 OAuth 应用凭证")

        provider_impl = self._provider_registry.get(provider)
        state = await self._state_store.create_state(extra_state)
        effective_redirect = redirect_uri or credential.redirect_uri

        authorize_url = provider_impl.get_authorize_url(
            client_id=credential.client_id,
            redirect_uri=effective_redirect,
            state=state,
            scopes=credential.allowed_scopes,
        )

        return authorize_url, state

    async def exchange_code(
        self,
        provider: str,
        code: str,
        state: str,
    ) -> tuple[OAuthUserInfo, dict[str, Any]]:
        """交换授权码获取用户信息和 Token。

        Args:
            provider: 提供商名称
            code: 授权码
            state: CSRF state token

        Returns:
            (user_info, token_data) 元组，token_data 包含
            access_token、refresh_token、expires_in 等

        Raises:
            OAuthStateError: state 无效或已过期
            OAuthCredentialNotFoundError: 未找到凭证
        """
        state_data = await self._state_store.validate_and_consume(state)
        if state_data is None:
            raise OAuthStateError()

        credential = await self._credential_repo.find_by_provider(provider)
        if credential is None:
            raise OAuthCredentialNotFoundError(f"未找到 {provider} 的 OAuth 应用凭证")

        client_secret = self._token_encryptor.decrypt(
            credential.client_secret_encrypted
        )

        provider_impl = self._provider_registry.get(provider)
        token_data = await provider_impl.exchange_code(
            code=code,
            client_id=credential.client_id,
            client_secret=client_secret,
            redirect_uri=credential.redirect_uri,
        )

        access_token = token_data.get("access_token", "")
        user_info = await provider_impl.fetch_user_info(access_token)

        return user_info, token_data


