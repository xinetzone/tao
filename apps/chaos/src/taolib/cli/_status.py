"""status 子命令业务逻辑。"""

import argparse
from datetime import UTC, datetime

from taolib.github_app import (
    GitHubAppSettings,
    GitHubInstallationTokenManager,
    InstallationTokenRequest,
)
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient

from ._parsers import _resolve_strategy


def check_status(args: argparse.Namespace) -> dict[str, object]:
    """检查缓存中令牌的状态（不执行网络请求）。"""
    settings = GitHubAppSettings.from_env()
    client = GitHubAppClient(
        app_id=settings.app_id,
        private_key=settings.private_key,
        api_url=settings.api_url,
    )
    cache = InMemoryInstallationTokenCache()
    manager = GitHubInstallationTokenManager(
        client=client, cache=cache, settings=settings
    )

    request = InstallationTokenRequest(
        installation_id=args.installation_id,
        permissions={},
        repositories=[],
        strategy=_resolve_strategy(args),
    )
    # 注意：status 命令只能检查当前进程内的缓存，如果是新进程则缓存为空
    import asyncio

    cached = asyncio.run(cache.get(manager.build_cache_key(request)))

    if cached is None:
        return {
            "cached": False,
            "expired": False,
            "expires_at": None,
            "token_kind": None,
        }

    now = datetime.now(tz=UTC)
    return {
        "cached": True,
        "expired": cached.expires_at <= now,
        "expires_at": cached.expires_at.isoformat(),
        "token_kind": cached.token_kind.value,
    }
