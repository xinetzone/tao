"""OAuth 提供商注册表模块。"""

from .base import OAuthProviderProtocol
from .github import GitHubOAuthProvider
from .google import GoogleOAuthProvider

__all__ = [
    "GitHubOAuthProvider",
    "GoogleOAuthProvider",
    "OAuthProviderProtocol",
    "ProviderRegistry",
]


class ProviderRegistry:
    """OAuth 提供商注册表。

    管理所有已注册的 OAuth 提供商，支持动态注册和查找。
    """

    def __init__(self) -> None:
        """初始化注册表，预注册 Google 和 GitHub 提供商。"""
        self._providers: dict[str, OAuthProviderProtocol] = {}
        self.register(GoogleOAuthProvider())
        self.register(GitHubOAuthProvider())

    def register(self, provider: OAuthProviderProtocol) -> None:
        """注册一个 OAuth 提供商。

        Args:
            provider: 实现 OAuthProviderProtocol 的提供商实例
        """
        self._providers[provider.provider_name] = provider

    def get(self, provider_name: str) -> OAuthProviderProtocol:
        """获取指定的提供商。

        Args:
            provider_name: 提供商名称

        Returns:
            提供商实例

        Raises:
            KeyError: 如果提供商未注册
        """
        if provider_name not in self._providers:
            msg = f"OAuth 提供商未注册: {provider_name}"
            raise KeyError(msg)
        return self._providers[provider_name]

    def list_providers(self) -> list[str]:
        """列出所有已注册的提供商名称。"""
        return list(self._providers.keys())


