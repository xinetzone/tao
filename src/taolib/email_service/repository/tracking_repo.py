"""追踪事件 Repository。

提供邮件追踪事件的数据访问和聚合分析操作。
"""

from datetime import datetime

from taolib._base.repository import AsyncRepository
from taolib.email_service.models.enums import TrackingEventType
from taolib.email_service.models.tracking import TrackingEventDocument


class TrackingRepository(AsyncRepository[TrackingEventDocument]):
    """追踪事件 Repository。"""

    def __init__(self, collection) -> None:
        """初始化。"""
        super().__init__(collection, TrackingEventDocument)

    async def find_by_email_id(self, email_id: str) -> list[TrackingEventDocument]:
        """查找指定邮件的所有追踪事件。"""
        return await self.list(
            filters={"email_id": email_id},
            sort=[("timestamp", -1)],
        )

    async def find_by_event_type(
        self,
        event_type: TrackingEventType,
        start: datetime,
        end: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TrackingEventDocument]:
        """按事件类型和时间范围查询。"""
        return await self.list(
            filters={
                "event_type": str(event_type),
                "timestamp": {"$gte": start, "$lte": end},
            },
            skip=skip,
            limit=limit,
            sort=[("timestamp", -1)],
        )

    async def get_event_counts(self, start: datetime, end: datetime) -> dict[str, int]:
        """聚合统计各类事件数量。"""
        pipeline = [
            {"$match": {"timestamp": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        ]
        results: dict[str, int] = {}
        async for doc in self._collection.aggregate(pipeline):
            results[doc["_id"]] = doc["count"]
        return results

    async def get_daily_stats(self, start: datetime, end: datetime) -> list[dict]:
        """按天聚合统计。"""
        pipeline = [
            {"$match": {"timestamp": {"$gte": start, "$lte": end}}},
            {
                "$group": {
                    "_id": {
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp",
                            }
                        },
                        "event_type": "$event_type",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.date": 1}},
        ]
        results: list[dict] = []
        async for doc in self._collection.aggregate(pipeline):
            results.append(
                {
                    "date": doc["_id"]["date"],
                    "event_type": doc["_id"]["event_type"],
                    "count": doc["count"],
                }
            )
        return results

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("email_id")
        await self._collection.create_index("event_type")
        await self._collection.create_index([("timestamp", -1)])
        await self._collection.create_index("recipient")
        await self._collection.create_index(
            "created_at",
            expireAfterSeconds=7776000,  # 90 天 TTL
        )
