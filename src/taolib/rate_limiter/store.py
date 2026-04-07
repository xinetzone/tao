"""Rate limit storage backends.

Provides Protocol definition, Redis implementation, and in-memory implementation for testing.
"""
import time
from typing import Any, Protocol

from .keys import (
    make_stats_realtime_key,
    make_stats_top_users_key,
    make_window_key,
)


class RateLimitStoreProtocol(Protocol):
    """限流存储接口。"""

    async def record_request(
        self,
        identifier: str,
        path: str,
        method: str,
        timestamp: float,
        window_seconds: int,
    ) -> int:
        """记录请求并返回当前窗口内请求数。

        Args:
            identifier: 用户标识符
            path: 请求路径
            method: HTTP 方法
            timestamp: 请求时间戳
            window_seconds: 窗口大小

        Returns:
            当前窗口内请求数
        """
        ...

    async def get_request_count(
        self,
        identifier: str,
        path: str,
        method: str,
        window_seconds: int,
    ) -> int:
        """获取当前窗口内请求数。

        Args:
            identifier: 用户标识符
            path: 请求路径
            method: HTTP 方法
            window_seconds: 窗口大小

        Returns:
            请求数
        """
        ...

    async def get_oldest_in_window(
        self,
        identifier: str,
        path: str,
        method: str,
        window_seconds: int,
    ) -> float | None:
        """获取窗口内最早的请求时间戳。

        Args:
            identifier: 用户标识符
            path: 请求路径
            method: HTTP 方法
            window_seconds: 窗口大小

        Returns:
            最早请求的时间戳，如果窗口为空则返回 None
        """
        ...

    async def increment_stats(self, identifier: str, path: str) -> None:
        """增加统计计数。

        Args:
            identifier: 用户标识符
            path: 请求路径
        """
        ...

    async def get_top_users(self, limit: int = 20) -> list[tuple[str, int]]:
        """获取请求量最大的用户列表。

        Args:
            limit: 返回数量限制

        Returns:
            [(identifier, count), ...] 列表
        """
        ...

    async def get_realtime_requests(self, window_seconds: int = 60) -> dict[str, Any]:
        """获取实时请求统计。

        Args:
            window_seconds: 统计窗口

        Returns:
            实时统计数据
        """
        ...


class RedisRateLimitStore:
    """基于 Redis Sorted Set 的滑动窗口实现。

    使用 Sorted Set 存储请求时间戳：
    - Score: 请求时间戳
    - Member: "{timestamp}:{unique_id}" 保证唯一性

    Args:
        redis_client: Redis 异步客户端（redis.asyncio.Redis）
    """

    def __init__(self, redis_client: Any) -> None:
        self._redis = redis_client

    async def record_request(
        self,
        identifier: str,
        path: str,
        method: str,
        timestamp: float,
        window_seconds: int,
    ) -> int:
        import uuid

        key = make_window_key(identifier, path, method)
        member = f"{timestamp}:{uuid.uuid4().hex[:8]}"

        pipe = self._redis.pipeline()
        # Add to sorted set
        pipe.zadd(key, {member: timestamp})
        # Remove expired entries
        window_start = timestamp - window_seconds
        pipe.zremrangebyscore(key, "-inf", window_start)
        # Set TTL
        pipe.expire(key, window_seconds * 2)
        # Get count
        pipe.zcard(key)

        results = await pipe.execute()
        return results[-1]  # Last result is ZCARD

    async def get_request_count(
        self,
        identifier: str,
        path: str,
        method: str,
        window_seconds: int,
    ) -> int:
        key = make_window_key(identifier, path, method)
        now = time.time()
        window_start = now - window_seconds

        # Clean expired and get count
        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zcard(key)
        results = await pipe.execute()
        return results[-1]

    async def get_oldest_in_window(
        self,
        identifier: str,
        path: str,
        method: str,
        window_seconds: int,
    ) -> float | None:
        key = make_window_key(identifier, path, method)
        now = time.time()
        window_start = now - window_seconds

        # Get oldest entry in current window
        oldest = await self._redis.zrangebyscore(
            key, window_start, now, start=0, num=1, withscores=True
        )
        if oldest:
            return oldest[0][1]  # (member, score)
        return None

    async def increment_stats(self, identifier: str, path: str) -> None:
        # Increment top users counter
        top_key = make_stats_top_users_key()
        await self._redis.zincrby(top_key, 1, identifier)

        # Add to realtime stats
        realtime_key = make_stats_realtime_key()
        now = time.time()
        await self._redis.zadd(realtime_key, {f"{now}:{path}": now})
        # Keep only last 60 seconds
        await self._redis.zremrangebyscore(realtime_key, "-inf", now - 60)

    async def get_top_users(self, limit: int = 20) -> list[tuple[str, int]]:
        top_key = make_stats_top_users_key()
        # Get top users by request count (descending)
        users = await self._redis.zrevrange(top_key, 0, limit - 1, withscores=True)
        return [(identifier, int(count)) for identifier, count in users]

    async def get_realtime_requests(self, window_seconds: int = 60) -> dict[str, Any]:
        realtime_key = make_stats_realtime_key()
        now = time.time()
        window_start = now - window_seconds

        # Clean expired
        await self._redis.zremrangebyscore(realtime_key, "-inf", window_start)
        # Get count
        active_requests = await self._redis.zcard(realtime_key)

        # Get all entries to analyze paths
        entries = await self._redis.zrangebyscore(
            realtime_key, window_start, now, withscores=True
        )

        # Count requests per path
        path_counts: dict[str, int] = {}
        for member, _ in entries:
            # member format: "{timestamp}:{path}"
            if ":" in str(member):
                parts = str(member).split(":", 1)
                if len(parts) == 2:
                    path = parts[1]
                    path_counts[path] = path_counts.get(path, 0) + 1

        top_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        rps = active_requests / window_seconds if window_seconds > 0 else 0

        return {
            "active_requests": active_requests,
            "requests_per_second": round(rps, 2),
            "top_paths": [{"path": p, "count": c} for p, c in top_paths],
        }


class InMemoryRateLimitStore:
    """内存版限流存储，用于测试。

    使用字典模拟 Sorted Set 行为。
    """

    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = {}
        self._stats: dict[str, int] = {}
        self._realtime: list[tuple[float, str]] = []

    async def record_request(
        self,
        identifier: str,
        path: str,
        method: str,
        timestamp: float,
        window_seconds: int,
    ) -> int:
        key = make_window_key(identifier, path, method)
        if key not in self._windows:
            self._windows[key] = []

        # Clean expired
        window_start = timestamp - window_seconds
        self._windows[key] = [ts for ts in self._windows[key] if ts > window_start]

        # Add new request
        self._windows[key].append(timestamp)
        return len(self._windows[key])

    async def get_request_count(
        self,
        identifier: str,
        path: str,
        method: str,
        window_seconds: int,
    ) -> int:
        key = make_window_key(identifier, path, method)
        if key not in self._windows:
            return 0

        now = time.time()
        window_start = now - window_seconds
        self._windows[key] = [ts for ts in self._windows[key] if ts > window_start]
        return len(self._windows[key])

    async def get_oldest_in_window(
        self,
        identifier: str,
        path: str,
        method: str,
        window_seconds: int,
    ) -> float | None:
        key = make_window_key(identifier, path, method)
        if key not in self._windows:
            return None

        now = time.time()
        window_start = now - window_seconds
        valid = [ts for ts in self._windows[key] if ts > window_start]
        return min(valid) if valid else None

    async def increment_stats(self, identifier: str, path: str) -> None:
        self._stats[identifier] = self._stats.get(identifier, 0) + 1
        self._realtime.append((time.time(), path))
        # Keep only last 60 seconds
        cutoff = time.time() - 60
        self._realtime = [(ts, p) for ts, p in self._realtime if ts > cutoff]

    async def get_top_users(self, limit: int = 20) -> list[tuple[str, int]]:
        sorted_users = sorted(self._stats.items(), key=lambda x: x[1], reverse=True)
        return sorted_users[:limit]

    async def get_realtime_requests(self, window_seconds: int = 60) -> dict[str, Any]:
        cutoff = time.time() - window_seconds
        recent = [(ts, p) for ts, p in self._realtime if ts > cutoff]

        path_counts: dict[str, int] = {}
        for _, path in recent:
            path_counts[path] = path_counts.get(path, 0) + 1

        top_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        rps = len(recent) / window_seconds if window_seconds > 0 else 0

        return {
            "active_requests": len(recent),
            "requests_per_second": round(rps, 2),
            "top_paths": [{"path": p, "count": c} for p, c in top_paths],
        }
