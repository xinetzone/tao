"""GitHub App 安装令牌管理子模块。

本包集中提供 GitHub App 需要的三项能力：

1. 配置加载：:class:`GitHubAppSettings` 从环境变量拼装运行时参数。
2. 令牌生命周期管理：:class:`GitHubInstallationTokenManager`
   负责策略解析、缓存与 Singleflight 并发控制。
3. HTTP 调用：:class:`GitHubAppClient` 负责 JWT 签发与 GitHub REST API 交互。

本包还附带一个 PyGithub 适配器 :class:`PyGithubInstallationClientFactory`，
以帮助调用方快速在 PyGithub SDK 上复用令牌管理能力。
错误体系以 :class:`GitHubAppError` 为根。
"""

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.events import NullTokenEventHook, TokenEventHook
from taolib.github_app.errors import (
    GitHubAppClientError,
    GitHubAppConfigurationError,
    GitHubAppError,
)
from taolib.github_app.models import (
    EffectiveTokenStrategy,
    EnvironmentKind,
    GitHubRuntimeProfile,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
    TokenKind,
)
from taolib.github_app.pygithub_adapter import (
    PyGithubInstallationClientFactory,
    build_pygithub_client,
)
from taolib.github_app.token_manager import GitHubInstallationTokenManager

__all__ = [
    "EffectiveTokenStrategy",
    "EnvironmentKind",
    "GitHubAppClient",
    "GitHubAppClientError",
    "GitHubAppConfigurationError",
    "GitHubAppError",
    "GitHubAppSettings",
    "GitHubInstallationTokenManager",
    "GitHubRuntimeProfile",
    "InMemoryInstallationTokenCache",
    "InstallationTokenRequest",
    "InstallationTokenResult",
    "NullTokenEventHook",
    "PyGithubInstallationClientFactory",
    "RequestedTokenStrategy",
    "TokenEventHook",
    "TokenKind",
    "build_pygithub_client",
]
