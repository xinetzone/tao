"""OAuth 提供商协议模块。

定义所有 OAuth 提供商必须实现的协议接口。
"""

from typing import Any, Protocol

from ..models.profile import OAuthUserInfo


class OAuthProviderProtocol(Protocol):
    """OAuth 提供商协议。

    所有 OAuth 提供商实现必须遵循此协议接口。
    """

    provider_name: str

    def get_authorize_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str,
        scopes: list[str],
    ) -> str:
        """生成 OAuth 授权 URL。

        Args:
            client_id: 应用 Client ID
            redirect_uri: 回调 URI
            state: CSRF 防护 state 参数
            scopes: 请求的权限范围

        Returns:
            完整的授权 URL
        """
        ...

    async def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """用授权码交换 Token。

        Args:
            code: 授权码
            client_id: 应用 Client ID
            client_secret: 应用 Client Secret
            redirect_uri: 回调 URI

        Returns:
            Token 响应字典，包含 access_token、refresh_token、expires_in 等
        """
        ...

    async def fetch_user_info(self, access_token: str) -> OAuthUserInfo:
        """获取用户信息。

        Args:
            access_token: 访问令牌

        Returns:
            标准化的用户信息
        """
        ...

    async def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> dict[str, Any]:
        """刷新 Access Token。

        Args:
            refresh_token: 刷新令牌
            client_id: 应用 Client ID
            client_secret: 应用 Client Secret

        Returns:
            新的 Token 响应字典
        """
        ...

    async def revoke_token(
        self,
        token: str,
        client_id: str,
        client_secret: str,
    ) -> bool:
        """撤销 Token。

        Args:
            token: 要撤销的令牌
            client_id: 应用 Client ID
            client_secret: 应用 Client Secret

        Returns:
            是否成功撤销
        """
        ...


