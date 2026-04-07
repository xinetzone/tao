"""同步检查点 Repository。

提供 Checkpoint 的 MongoDB 持久化操作。
"""

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

from taolib._base.repository import AsyncRepository
from taolib.data_sync.models.checkpoint import SyncCheckpoint


class CheckpointRepository(AsyncRepository[SyncCheckpoint]):
    """同步检查点 Repository。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化。

        Args:
            collection: MongoDB 集合对象（sync_checkpoints）
        """
        super().__init__(collection, SyncCheckpoint)

    async def get_or_create(
        self,
        job_id: str,
        collection_name: str,
    ) -> SyncCheckpoint:
        """获取或创建检查点。

        Args:
            job_id: 作业 ID
            collection_name: 集合名称

        Returns:
            检查点文档
        """
        doc_id = f"{job_id}:{collection_name}"
        doc = await self._collection.find_one_and_update(
            {"_id": doc_id},
            {
                "$setOnInsert": {
                    "_id": doc_id,
                    "job_id": job_id,
                    "collection_name": collection_name,
                    "last_synced_timestamp": None,
                    "last_synced_id": None,
                    "total_synced": 0,
                    "updated_at": datetime.now(UTC),
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        doc["_id"] = str(doc["_id"])
        return SyncCheckpoint(**doc)

    async def update_checkpoint(
        self,
        job_id: str,
        collection_name: str,
        last_ts: datetime,
        last_id: str,
        count: int,
    ) -> SyncCheckpoint | None:
        """更新检查点。

        Args:
            job_id: 作业 ID
            collection_name: 集合名称
            last_ts: 最后同步时间戳
            last_id: 最后同步文档 ID
            count: 本次同步文档数

        Returns:
            更新后的检查点文档，如果不存在则返回 None
        """
        doc_id = f"{job_id}:{collection_name}"
        return await self.update(
            doc_id,
            {
                "last_synced_timestamp": last_ts,
                "last_synced_id": last_id,
                "total_synced": {"$inc": count},
                "updated_at": datetime.now(UTC),
            },
        )

    async def delete_by_job(self, job_id: str) -> int:
        """删除指定作业的所有检查点。

        Args:
            job_id: 作业 ID

        Returns:
            删除的检查点数量
        """
        result = await self._collection.delete_many({"job_id": job_id})
        return result.deleted_count

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index(
            [("job_id", 1), ("collection_name", 1)],
            unique=True,
        )
