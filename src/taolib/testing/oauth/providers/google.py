"""Google OAuth 提供商实现模块。

实现 Google OAuth2 + OpenID Connect 流程。
"""

from typing import Any
from urllib.parse import urlencode

import httpx

from ..errors import OAuthCodeExchangeError, OAuthUserInfoError
from ..models.enums import OAuthProvider
from ..models.profile import OAuthUserInfo

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GOOGLE_DEFAULT_SCOPES = ["openid", "email", "profile"]
HTTP_TIMEOUT = 10.0


class GoogleOAuthProvider:
    """Google OAuth 提供商。"""

    provider_name: str = OAuthProvider.GOOGLE

    def get_authorize_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str,
        scopes: list[str],
    ) -> str:
        """生成 Google 授权 URL。

        Args:
            client_id: Google Client ID
            redirect_uri: 回调 URI
            state: CSRF 防护 state 参数
            scopes: 请求的权限范围

        Returns:
            完整的 Google 授权 URL
        """
        effective_scopes = scopes or GOOGLE_DEFAULT_SCOPES
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(effective_scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """用授权码交换 Google Token。

        Args:
            code: 授权码
            client_id: Google Client ID
            client_secret: Google Client Secret
            redirect_uri: 回调 URI

        Returns:
            Token 响应字典

        Raises:
            OAuthCodeExchangeError: 交换失败
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if response.status_code != 200:
                raise OAuthCodeExchangeError(
                    f"Google 授权码交换失败: {response.status_code} {response.text}"
                )
            return response.json()

    async def fetch_user_info(self, access_token: str) -> OAuthUserInfo:
        """获取 Google 用户信息。

        Args:
            access_token: Google Access Token

        Returns:
            标准化的用户信息

        Raises:
            OAuthUserInfoError: 获取失败
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code != 200:
                raise OAuthUserInfoError(
                    f"获取 Google 用户信息失败: {response.status_code}"
                )
            data = response.json()
            return OAuthUserInfo(
                provider=OAuthProvider.GOOGLE,
                provider_user_id=str(data.get("id", "")),
                email=data.get("email"),
                display_name=data.get("name", ""),
                avatar_url=data.get("picture", ""),
                raw_data=data,
            )

    async def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> dict[str, Any]:
        """刷新 Google Access Token。

        Args:
            refresh_token: Refresh Token
            client_id: Google Client ID
            client_secret: Google Client Secret

        Returns:
            新的 Token 响应

        Raises:
            OAuthCodeExchangeError: 刷新失败
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "refresh_token",
                },
            )
            if response.status_code != 200:
                raise OAuthCodeExchangeError(
                    f"Google Token 刷新失败: {response.status_code}"
                )
            return response.json()

    async def revoke_token(
        self,
        token: str,
        client_id: str,
        client_secret: str,
    ) -> bool:
        """撤销 Google Token。

        Args:
            token: 要撤销的令牌
            client_id: Google Client ID（未使用）
            client_secret: Google Client Secret（未使用）

        Returns:
            是否成功撤销
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                GOOGLE_REVOKE_URL,
                params={"token": token},
            )
            return response.status_code == 200


