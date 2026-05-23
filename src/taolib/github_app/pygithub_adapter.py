"""PyGithub 客户端适配器。

本模块将安装令牌管理器产出的令牌注入到 ``PyGithub`` 的 :class:`Github`
客户端，使调用方能用成熟的 SDK 访问 GitHub REST API。
"""

from github import Auth, Github

from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import InstallationTokenRequest
from taolib.github_app.token_manager import GitHubInstallationTokenManager


class PyGithubInstallationClientFactory:
    """以安装令牌为身份创建 PyGithub 客户端的工厂。

    依赖 :class:`GitHubInstallationTokenManager` 获取令牌，并以
    :class:`GitHubAppSettings.api_url` 作为 PyGithub 的 ``base_url``。
    """

    def __init__(
        self,
        settings: GitHubAppSettings,
        manager: GitHubInstallationTokenManager,
    ) -> None:
        """初始化工厂。

        Args:
            settings: GitHub App 运行时配置。
            manager: 安装令牌管理器。
        """
        self.settings = settings
        self.manager = manager

    async def create(self, request: InstallationTokenRequest) -> Github:
        """为一次令牌请求创建 PyGithub 客户端。

        Args:
            request: 安装令牌请求。

        Returns:
            以令牌身份贴近调用的 :class:`Github` 客户端。

        Raises:
            GitHubAppClientError: 令牌获取失败。
        """
        result = await self.manager.get_token(request)
        auth = Auth.Token(result.token)
        return Github(auth=auth, base_url=self.settings.api_url)


async def build_pygithub_client(
    settings: GitHubAppSettings,
    manager: GitHubInstallationTokenManager,
    request: InstallationTokenRequest,
) -> Github:
    """一口调用创建 PyGithub 客户端的便捷函数。

    适用于不需要复用工厂对象的一次性场景。

    Args:
        settings: GitHub App 运行时配置。
        manager: 安装令牌管理器。
        request: 安装令牌请求。

    Returns:
        以令牌身份贴近调用的 :class:`Github` 客户端。
    """
    factory = PyGithubInstallationClientFactory(settings=settings, manager=manager)
    return await factory.create(request)
