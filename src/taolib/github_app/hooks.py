"""令牌事件回调的参考实现。

本模块提供两个开箱即用的 :class:`~taolib.github_app.events.TokenEventHook` 实现：

- :class:`LoggingTokenEventHook`：将事件写入 Python logging。
- :class:`MetricsTokenEventHook`：收集事件计数指标。
"""

import logging

from taolib.github_app.models import InstallationTokenResult


class LoggingTokenEventHook:
    """将令牌生命周期事件写入 Python logging。

    适用于开发调试与生产环境的审计日志。
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """初始化日志 hook。

        Args:
            logger: 自定义 Logger 实例，为 None 时使用默认 logger。
        """
        self._logger = logger or logging.getLogger("taolib.github_app")

    async def on_token_refreshed(
        self, cache_key: str, result: InstallationTokenResult
    ) -> None:
        """记录令牌刷新成功事件。

        Args:
            cache_key: 本次刷新对应的缓存键。
            result: 刷新后的令牌结果。
        """
        self._logger.info(
            "Token refreshed for %s (kind=%s, expires=%s)",
            cache_key,
            result.token_kind.value,
            result.expires_at.isoformat(),
        )

    async def on_token_refresh_failed(
        self, cache_key: str, error: Exception
    ) -> None:
        """记录令牌刷新失败事件。

        Args:
            cache_key: 本次刷新对应的缓存键。
            error: 导致刷新失败的异常。
        """
        self._logger.error("Token refresh failed for %s: %s", cache_key, error)


class MetricsTokenEventHook:
    """收集令牌事件计数指标。

    适用于 Prometheus 导出、测试断言或简易内存监控。

    Attributes:
        refresh_count: 刷新成功的累计次数。
        failure_count: 刷新失败的累计次数。
        last_refresh_key: 最近一次成功刷新的缓存键。
    """

    def __init__(self) -> None:
        """初始化计数器为零。"""
        self.refresh_count: int = 0
        self.failure_count: int = 0
        self.last_refresh_key: str | None = None

    async def on_token_refreshed(
        self, cache_key: str, result: InstallationTokenResult
    ) -> None:
        """递增刷新成功计数并记录缓存键。

        Args:
            cache_key: 本次刷新对应的缓存键。
            result: 刷新后的令牌结果。
        """
        self.refresh_count += 1
        self.last_refresh_key = cache_key

    async def on_token_refresh_failed(
        self, cache_key: str, error: Exception
    ) -> None:
        """递增刷新失败计数。

        Args:
            cache_key: 本次刷新对应的缓存键。
            error: 导致刷新失败的异常。
        """
        self.failure_count += 1
