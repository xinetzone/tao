"""GitHub App 安装令牌的内存缓存实现。

本模块提供进程内、异步友好的轻量级缓存，适用于单进程场景。
如需跨进程共享，可另行实现同接口的 Redis / Memcached 适配器。
"""

import asyncio
from collections import OrderedDict
from datetime import UTC, datetime, timedelta

from taolib.github_app.models import InstallationTokenResult


class InMemoryInstallationTokenCache:
    """基于 OrderedDict 的异步安装令牌缓存（LRU 淘汰）。

    本实现支持 TTL 主动过期：通过 :meth:`purge_expired` 手动清理，
    或通过 :meth:`start_purge_task` 启动后台周期清理协程。
    过期识别与提前刷新需配合 :meth:`is_stale` 使用。
    """

    def __init__(self, maxsize: int = 256) -> None:
        """初始化一个空的内存缓存容器。

        Args:
            maxsize: 缓存最大条目数，超出时淘汰最久未访问的条目。
        """
        self._items: OrderedDict[str, InstallationTokenResult] = OrderedDict()
        self._maxsize = maxsize

    async def get(self, key: str) -> InstallationTokenResult | None:
        """读取缓存中给定键的令牌结果。

        命中时将该键移至末尾，实现 LRU 淘汰语义：
        最近被访问的 key 不会被优先淘汰。

        Args:
            key: 令牌管理器构建的缓存键。

        Returns:
            命中时返回 :class:`InstallationTokenResult`，未命中时返回 ``None``。
        """
        result = self._items.get(key)
        if result is not None:
            self._items.move_to_end(key)
        return result

    async def set(self, key: str, result: InstallationTokenResult) -> None:
        """写入或覆盖缓存中的令牌结果。

        当缓存已满且 key 为新键时，淘汰最久未访问的条目（LRU）。

        Args:
            key: 令牌管理器构建的缓存键。
            result: 待缓存的令牌结果。
        """
        if key not in self._items and len(self._items) >= self._maxsize:
            self._items.popitem(last=False)
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

    def purge_expired(self) -> int:
        """删除所有已过期的缓存条目。

        Returns:
            本次清理删除的条目数量。
        """
        now = datetime.now(tz=UTC)
        expired_keys = [k for k, v in self._items.items() if v.expires_at <= now]
        for k in expired_keys:
            del self._items[k]
        return len(expired_keys)

    def start_purge_task(self, interval_seconds: int = 300) -> "asyncio.Task[None]":
        """启动后台周期清理协程。

        Args:
            interval_seconds: 清理间隔秒数，默认 300 秒。

        Returns:
            后台清理任务的 asyncio.Task 对象。
        """

        async def _purge_loop() -> None:
            while True:
                await asyncio.sleep(interval_seconds)
                self.purge_expired()

        self._purge_task = asyncio.create_task(_purge_loop())
        return self._purge_task

    def stop_purge_task(self) -> None:
        """取消后台清理任务。"""
        if hasattr(self, "_purge_task") and self._purge_task is not None:
            self._purge_task.cancel()
            self._purge_task = None
