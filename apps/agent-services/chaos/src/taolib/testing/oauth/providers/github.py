"""GitHub OAuth 提供商实现模块。

实现 GitHub OAuth2 标准流程。
"""

from typing import Any
from urllib.parse import urlencode

import httpx

from ..errors import (
    OAuthCodeExchangeError,
    OAuthRefreshNotSupported,
    OAuthUserInfoError,
)
from ..models.enums import OAuthProvider
from ..models.profile import OAuthUserInfo

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"
GITHUB_DEFAULT_SCOPES = ["user:email", "read:user"]
HTTP_TIMEOUT = 10.0


class GitHubOAuthProvider:
    """GitHub OAuth 提供商。"""

    provider_name: str = OAuthProvider.GITHUB

    def get_authorize_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str,
        scopes: list[str],
    ) -> str:
        """生成 GitHub 授权 URL。

        Args:
            client_id: GitHub Client ID
            redirect_uri: 回调 URI
            state: CSRF 防护 state 参数
            scopes: 请求的权限范围

        Returns:
            完整的 GitHub 授权 URL
        """
        effective_scopes = scopes or GITHUB_DEFAULT_SCOPES
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(effective_scopes),
        }
        return f"{GITHUB_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """用授权码交换 GitHub Token。

        Args:
            code: 授权码
            client_id: GitHub Client ID
            client_secret: GitHub Client Secret
            redirect_uri: 回调 URI

        Returns:
            Token 响应字典

        Raises:
            OAuthCodeExchangeError: 交换失败
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            if response.status_code != 200:
                raise OAuthCodeExchangeError(
                    f"GitHub 授权码交换失败: {response.status_code}"
                )
            data = response.json()
            if "error" in data:
                raise OAuthCodeExchangeError(
                    f"GitHub 授权码交换失败: {data.get('error_description', data['error'])}"
                )
            return data

    async def fetch_user_info(self, access_token: str) -> OAuthUserInfo:
        """获取 GitHub 用户信息。

        如果用户信息中没有邮箱，会额外调用邮箱 API 获取主邮箱。

        Args:
            access_token: GitHub Access Token

        Returns:
            标准化的用户信息

        Raises:
            OAuthUserInfoError: 获取失败
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(GITHUB_USER_URL, headers=headers)
            if response.status_code != 200:
                raise OAuthUserInfoError(
                    f"获取 GitHub 用户信息失败: {response.status_code}"
                )
            data = response.json()

            email = data.get("email")
            if not email:
                email = await self._fetch_primary_email(client, headers)

            return OAuthUserInfo(
                provider=OAuthProvider.GITHUB,
                provider_user_id=str(data.get("id", "")),
                email=email,
                display_name=data.get("name") or data.get("login", ""),
                avatar_url=data.get("avatar_url", ""),
                raw_data=data,
            )

    @staticmethod
    async def _fetch_primary_email(
        client: httpx.AsyncClient, headers: dict[str, str]
    ) -> str | None:
        """获取 GitHub 用户的主邮箱。

        Args:
            client: httpx 异步客户端
            headers: 请求头

        Returns:
            主邮箱地址，获取失败返回 None
        """
        try:
            response = await client.get(GITHUB_EMAILS_URL, headers=headers)
            if response.status_code == 200:
                emails = response.json()
                for email_entry in emails:
                    if email_entry.get("primary") and email_entry.get("verified"):
                        return email_entry["email"]
                if emails:
                    return emails[0].get("email")
        except Exception:
            pass
        return None

    async def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> dict[str, Any]:
        """GitHub 标准 OAuth 应用不支持 Token 刷新。

        Raises:
            OAuthRefreshNotSupported: 总是抛出
        """
        raise OAuthRefreshNotSupported("GitHub 标准 OAuth 应用不支持 Token 刷新")

    async def revoke_token(
        self,
        token: str,
        client_id: str,
        client_secret: str,
    ) -> bool:
        """撤销 GitHub Token。

        Args:
            token: 要撤销的令牌
            client_id: GitHub Client ID
            client_secret: GitHub Client Secret

        Returns:
            是否成功撤销
        """
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.delete(
                f"https://api.github.com/applications/{client_id}/token",
                auth=(client_id, client_secret),
                json={"access_token": token},
            )
            return response.status_code == 204


