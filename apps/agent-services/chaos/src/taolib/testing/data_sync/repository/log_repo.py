"""同步日志 Repository。

提供 SyncLog 的 MongoDB 持久化操作。
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.data_sync.models.log import SyncLogDocument


class SyncLogRepository(AsyncRepository[SyncLogDocument]):
    """同步日志 Repository。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化。

        Args:
            collection: MongoDB 集合对象（sync_logs）
        """
        super().__init__(collection, SyncLogDocument)

    async def find_by_job(
        self,
        job_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SyncLogDocument]:
        """查找指定作业的日志。

        Args:
            job_id: 作业 ID
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            日志文档列表，按 started_at 降序
        """
        return await self.list(
            filters={"job_id": job_id},
            skip=skip,
            limit=limit,
            sort=[("started_at", -1)],
        )

    async def find_recent(
        self, skip: int = 0, limit: int = 50
    ) -> list[SyncLogDocument]:
        """查找最近的日志。

        Args:
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            最近的日志文档列表
        """
        return await self.list(
            skip=skip,
            limit=limit,
            sort=[("started_at", -1)],
        )

    async def get_aggregate_metrics(
        self,
        job_id: str,
        days: int = 7,
    ) -> dict[str, Any]:
        """获取聚合指标。

        Args:
            job_id: 作业 ID
            days: 天数

        Returns:
            聚合指标字典
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        pipeline = [
            {
                "$match": {
                    "job_id": job_id,
                    "started_at": {"$gte": cutoff},
                }
            },
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "avg_duration": {"$avg": "$duration_seconds"},
                }
            },
        ]
        results = await self._collection.aggregate(pipeline).to_list(length=None)
        return {"job_id": job_id, "days": days, "status_breakdown": results}

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index([("job_id", 1), ("started_at", -1)])
        # TTL 索引：90 天后自动删除
        await self._collection.create_index(
            "started_at",
            expireAfterSeconds=90 * 24 * 3600,
        )


