"""令牌生命周期事件协议与默认实现。

本模块定义了令牌管理器在令牌刷新成功或失败时的回调协议，
调用方可实现 :class:`TokenEventHook` 以接入审计日志、监控等场景。
"""

from typing import Protocol

from taolib.github_app.models import InstallationTokenResult


class TokenEventHook(Protocol):
    """令牌事件回调协议。

    调用方实现此协议并注入到
    :class:`~taolib.github_app.token_manager.GitHubInstallationTokenManager`，
    即可在令牌刷新成功或失败时收到通知。
    """

    async def on_token_refreshed(
        self, cache_key: str, result: InstallationTokenResult
    ) -> None:
        """令牌刷新成功时触发。

        Args:
            cache_key: 本次刷新对应的缓存键。
            result: 刷新后的令牌结果。
        """
        ...

    async def on_token_refresh_failed(
        self, cache_key: str, error: Exception
    ) -> None:
        """令牌刷新失败时触发。

        Args:
            cache_key: 本次刷新对应的缓存键。
            error: 导致刷新失败的异常。
        """
        ...


class NullTokenEventHook:
    """空操作实现，默认注入，不产生任何副作用。"""

    async def on_token_refreshed(
        self, cache_key: str, result: InstallationTokenResult
    ) -> None:
        """空操作：令牌刷新成功时不执行任何动作。"""

    async def on_token_refresh_failed(
        self, cache_key: str, error: Exception
    ) -> None:
        """空操作：令牌刷新失败时不执行任何动作。"""
