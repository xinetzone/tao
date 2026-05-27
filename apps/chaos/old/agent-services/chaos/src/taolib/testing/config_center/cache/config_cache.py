"""配置缓存策略模块。

提供 Redis 缓存实现和内存缓存实现（用于测试）。
"""

import json
import logging
import time
from typing import Any, Protocol

import redis.asyncio as aioredis

from .keys import config_key, config_pattern

logger = logging.getLogger(__name__)


class ConfigCacheProtocol(Protocol):
    """配置缓存协议。"""

    async def get(self, environment: str, service: str, key: str) -> Any | None:
        """获取配置缓存。

        Args:
            environment: 环境类型
            service: 服务名称
            key: 配置键

        Returns:
            缓存的配置值，如果不存在则返回 None
        """
        ...

    async def set(
        self,
        environment: str,
        service: str,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        """设置配置缓存。

        Args:
            environment: 环境类型
            service: 服务名称
            key: 配置键
            value: 配置值
            ttl: 过期时间（秒）
        """
        ...

    async def delete(self, environment: str, service: str, key: str) -> None:
        """删除配置缓存。

        Args:
            environment: 环境类型
            service: 服务名称
            key: 配置键
        """
        ...

    async def delete_pattern(
        self, environment: str | None = None, service: str | None = None
    ) -> None:
        """批量删除配置缓存。

        Args:
            environment: 环境类型（可选）
            service: 服务名称（可选）
        """
        ...


class RedisConfigCache:
    """Redis 配置缓存实现。"""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        """初始化 Redis 缓存。

        Args:
            redis_client: Redis 异步客户端
        """
        self._redis = redis_client

    async def get(self, environment: str, service: str, key: str) -> Any | None:
        """获取配置缓存。"""
        cache_key = config_key(environment, service, key)
        value = await self._redis.get(cache_key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.warning(f"Redis 缓存数据解码失败: key={cache_key}, error={e}")
            return None

    async def set(
        self,
        environment: str,
        service: str,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        """设置配置缓存。"""
        cache_key = config_key(environment, service, key)
        await self._redis.set(cache_key, json.dumps(value, ensure_ascii=False), ex=ttl)

    async def delete(self, environment: str, service: str, key: str) -> None:
        """删除配置缓存。"""
        cache_key = config_key(environment, service, key)
        await self._redis.delete(cache_key)

    async def delete_pattern(
        self, environment: str | None = None, service: str | None = None
    ) -> None:
        """批量删除配置缓存。"""
        pattern = config_pattern(environment, service)
        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)


class InMemoryConfigCache:
    """内存配置缓存实现（用于测试）。"""

    def __init__(self) -> None:
        """初始化内存缓存。"""
        self._cache: dict[str, tuple[Any, float]] = {}

    async def get(self, environment: str, service: str, key: str) -> Any | None:
        """获取配置缓存。"""
        cache_key = config_key(environment, service, key)
        if cache_key not in self._cache:
            return None
        value, expire_at = self._cache[cache_key]
        if time.time() > expire_at:
            del self._cache[cache_key]
            return None
        return value

    async def set(
        self,
        environment: str,
        service: str,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        """设置配置缓存。"""
        cache_key = config_key(environment, service, key)
        self._cache[cache_key] = (value, time.time() + ttl)

    async def delete(self, environment: str, service: str, key: str) -> None:
        """删除配置缓存。"""
        cache_key = config_key(environment, service, key)
        self._cache.pop(cache_key, None)

    async def delete_pattern(
        self, environment: str | None = None, service: str | None = None
    ) -> None:
        """批量删除配置缓存。"""
        import fnmatch

        pattern = config_pattern(environment, service)
        keys_to_delete = [k for k in self._cache if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._cache[key]
