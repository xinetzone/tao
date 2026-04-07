"""Redis 客户端管理模块。

提供 Redis 连接池管理和客户端获取函数。
"""

import redis.asyncio as aioredis

_redis_client: aioredis.Redis | None = None


async def get_redis_client(redis_url: str = "redis://localhost:6379") -> aioredis.Redis:
    """获取 Redis 客户端（单例模式）。

    Args:
        redis_url: Redis 连接字符串

    Returns:
        Redis 异步客户端实例
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            redis_url,
            decode_responses=True,
            encoding="utf-8",
        )
    return _redis_client


async def close_redis_client() -> None:
    """关闭 Redis 连接。"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
