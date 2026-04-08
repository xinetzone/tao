"""同步失败记录 Repository。

提供 FailureRecord 的 MongoDB 持久化操作。
"""

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.data_sync.models.failure import FailureRecordDocument


class FailureRecordRepository(AsyncRepository[FailureRecordDocument]):
    """同步失败记录 Repository。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化。

        Args:
            collection: MongoDB 集合对象（sync_failures）
        """
        super().__init__(collection, FailureRecordDocument)

    async def bulk_create(
        self,
        records: list[dict],
    ) -> int:
        """批量创建失败记录。

        Args:
            records: 失败记录数据列表

        Returns:
            创建的记录数量
        """
        if not records:
            return 0
        result = await self._collection.insert_many(records)
        return len(result.inserted_ids)

    async def find_by_log(
        self,
        log_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FailureRecordDocument]:
        """查找指定日志的失败记录。

        Args:
            log_id: 日志 ID
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            失败记录文档列表
        """
        return await self.list(
            filters={"log_id": log_id},
            skip=skip,
            limit=limit,
        )

    async def count_by_job(self, job_id: str) -> int:
        """统计指定作业的失败数量。

        Args:
            job_id: 作业 ID

        Returns:
            失败记录数量
        """
        return await self.count(filters={"job_id": job_id})

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index([("job_id", 1), ("log_id", 1)])
        # TTL 索引：30 天后自动删除
        await self._collection.create_index(
            "created_at",
            expireAfterSeconds=30 * 24 * 3600,
        )


