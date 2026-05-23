"""CLI 对象构建工具。

本模块负责从环境变量与命令行参数中装配核心业务对象，
包括令牌管理器与令牌请求。
"""

import argparse
import os

from taolib.github_app import (
    GitHubAppSettings,
    GitHubInstallationTokenManager,
    InstallationTokenRequest,
)
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient

from ._parsers import _resolve_strategy


def build_manager(args: argparse.Namespace) -> GitHubInstallationTokenManager:
    """从环境变量装配出可用的令牌管理器。

    Args:
        args: 仅为接口一致性保留，不参与现有逻辑。

    Returns:
        依赖内存缓存与默认客户端的 :class:`GitHubInstallationTokenManager` 实例。
    """
    del args
    settings = GitHubAppSettings.from_env()
    client = GitHubAppClient(
        app_id=settings.app_id,
        private_key=settings.private_key,
        api_url=settings.api_url,
    )
    return GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=settings,
    )


def build_request(args: argparse.Namespace) -> InstallationTokenRequest:
    """根据命令行参数与环境变量拼装令牌请求。

    Args:
        args: 已解析的命令行参数。

    Returns:
        可用于 :meth:`GitHubInstallationTokenManager.get_token` 的请求对象。
    """
    installation_id = args.installation_id or os.environ["GITHUB_APP_INSTALLATION_ID"]
    return InstallationTokenRequest(
        installation_id=installation_id,
        permissions={},
        repositories=[],
        strategy=_resolve_strategy(args),
    )
