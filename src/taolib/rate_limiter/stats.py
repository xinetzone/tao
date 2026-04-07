"""Statistics aggregation and query service for rate limiter."""
from datetime import UTC, datetime, timedelta
from typing import Any

from .models import RealtimeStats, TopUserEntry, ViolationStatsEntry
from .store import RateLimitStoreProtocol


class RateLimitStatsService:
    """限流统计查询服务。

    提供：
    - Top Users 统计
    - 违规统计
    - 实时监控数据

    Args:
        store: 限流存储后端
        mongo_collection: MongoDB 违规记录集合（可选）
    """

    def __init__(
        self,
        store: RateLimitStoreProtocol,
        mongo_collection: Any = None,
    ) -> None:
        self._store = store
        self._mongo_collection = mongo_collection

    async def get_top_users(self, limit: int = 20) -> list[TopUserEntry]:
        """获取请求量最大的用户列表。

        Args:
            limit: 返回数量限制

        Returns:
            Top Users 列表
        """
        users = await self._store.get_top_users(limit)

        from .keys import parse_identifier_type

        return [
            TopUserEntry(
                identifier=identifier,
                request_count=count,
                identifier_type=parse_identifier_type(identifier),
            )
            for identifier, count in users
        ]

    async def get_violation_stats(
        self, period_hours: int = 24
    ) -> list[ViolationStatsEntry]:
        """获取违规统计。

        Args:
            period_hours: 统计时间范围（小时）

        Returns:
            违规统计列表
        """
        if self._mongo_collection is None:
            return []

        cutoff = datetime.now(UTC) - timedelta(hours=period_hours)

        # Aggregate violations by identifier
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {
                "$group": {
                    "_id": "$identifier",
                    "count": {"$sum": 1},
                    "identifier_type": {"$first": "$identifier_type"},
                    "last_violation": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 50},
        ]

        results = []
        async for doc in self._mongo_collection.aggregate(pipeline):
            results.append(
                ViolationStatsEntry(
                    identifier=doc["_id"],
                    count=doc["count"],
                    identifier_type=doc["identifier_type"],
                    last_violation=doc.get("last_violation"),
                )
            )

        return results

    async def get_realtime(self, window_seconds: int = 60) -> RealtimeStats:
        """获取实时请求统计。

        Args:
            window_seconds: 统计窗口（秒）

        Returns:
            实时统计数据
        """
        data = await self._store.get_realtime_requests(window_seconds)
        return RealtimeStats(**data)
