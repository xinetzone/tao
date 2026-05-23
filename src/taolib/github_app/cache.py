"""GitHub App 安装令牌的内存缓存实现。

本模块提供进程内、异步友好的轻量级缓存，适用于单进程场景。
如需跨进程共享，可另行实现同接口的 Redis / Memcached 适配器。
"""

from datetime import UTC, datetime, timedelta

from taolib.github_app.models import InstallationTokenResult


class InMemoryInstallationTokenCache:
    """基于字典的异步安装令牌缓存。

    本实现不带过期清理任务。过期识别与提前刷新需配合
    :meth:`is_stale` 使用。
    """

    def __init__(self) -> None:
        """初始化一个空的内存缓存容器。"""
        self._items: dict[str, InstallationTokenResult] = {}

    async def get(self, key: str) -> InstallationTokenResult | None:
        """读取缓存中给定键的令牌结果。

        Args:
            key: 令牌管理器构建的缓存键。

        Returns:
            命中时返回 :class:`InstallationTokenResult`，未命中时返回 ``None``。
        """
        return self._items.get(key)

    async def set(self, key: str, result: InstallationTokenResult) -> None:
        """写入或覆盖缓存中的令牌结果。

        Args:
            key: 令牌管理器构建的缓存键。
            result: 待缓存的令牌结果。
        """
        self._items[key] = result

    def is_stale(
        self, result: InstallationTokenResult, eager_refresh_seconds: int
    ) -> bool:
        """判断令牌是否已进入“提前刷新窗口”。

        以当前 UTC 时间与 ``expires_at - eager_refresh_seconds`` 比较：
        当现在已到达或超过该阈值时，认为需要提前刷新。

        Args:
            result: 缓存中的令牌结果。
            eager_refresh_seconds: 提前刷新窗口的秒数。

        Returns:
            ``True`` 表示已进入提前刷新窗口，应触发刷新；否则为 ``False``。
        """
        refresh_at = result.expires_at - timedelta(seconds=eager_refresh_seconds)
        return datetime.now(tz=UTC) >= refresh_at
