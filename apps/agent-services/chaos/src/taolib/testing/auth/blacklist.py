"""令牌黑名单模块。

提供令牌吊销功能的 Protocol 接口和多种实现。
"""

import time
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TokenBlacklistProtocol(Protocol):
    """令牌黑名单 Protocol。

    定义令牌黑名单的标准接口，支持多种存储后端。
    """

    async def add(self, jti: str, ttl_seconds: int) -> None:
        """将令牌加入黑名单。

        Args:
            jti: 令牌的唯一标识（JWT ID）
            ttl_seconds: 黑名单条目的存活时间（秒），应与令牌剩余有效期对齐
        """
        ...

    async def is_blacklisted(self, jti: str) -> bool:
        """检查令牌是否在黑名单中。

        Args:
            jti: 令牌的唯一标识

        Returns:
            如果令牌已被吊销返回 True
        """
        ...


class RedisTokenBlacklist:
    """基于 Redis 的令牌黑名单。

    使用 Redis SET + EX 命令存储，TTL 自动过期确保黑名单不会无限增长。

    Args:
        redis_client: ``redis.asyncio.Redis`` 客户端实例
        key_prefix: Redis 键前缀
    """

    def __init__(
        self, redis_client: Any, key_prefix: str = "taolib:auth:blacklist:"
    ) -> None:
        self._redis = redis_client
        self._prefix = key_prefix

    async def add(self, jti: str, ttl_seconds: int) -> None:
        """将令牌加入 Redis 黑名单。"""
        if ttl_seconds <= 0:
            return
        key = f"{self._prefix}{jti}"
        await self._redis.set(key, "1", ex=ttl_seconds)

    async def is_blacklisted(self, jti: str) -> bool:
        """检查令牌是否在 Redis 黑名单中。"""
        if not jti:
            return False
        key = f"{self._prefix}{jti}"
        result = await self._redis.get(key)
        return result is not None


class InMemoryTokenBlacklist:
    """基于内存的令牌黑名单。

    使用字典存储，检查时自动清理过期条目。适用于测试和单进程开发环境。
    """

    def __init__(self) -> None:
        self._store: dict[str, float] = {}

    async def add(self, jti: str, ttl_seconds: int) -> None:
        """将令牌加入内存黑名单。"""
        if ttl_seconds <= 0:
            return
        self._store[jti] = time.monotonic() + ttl_seconds

    async def is_blacklisted(self, jti: str) -> bool:
        """检查令牌是否在内存黑名单中。"""
        if not jti:
            return False
        expire_at = self._store.get(jti)
        if expire_at is None:
            return False
        if time.monotonic() > expire_at:
            del self._store[jti]
            return False
        return True


class NullTokenBlacklist:
    """空操作黑名单。

    不执行任何操作，``is_blacklisted`` 始终返回 ``False``。
    用于不需要黑名单功能的场景。
    """

    async def add(self, jti: str, ttl_seconds: int) -> None:
        """空操作。"""

    async def is_blacklisted(self, jti: str) -> bool:
        """始终返回 False。"""
        return False
