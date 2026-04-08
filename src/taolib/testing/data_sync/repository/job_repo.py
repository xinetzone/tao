"""同步作业 Repository。

提供 SyncJob 的 MongoDB 持久化操作。
"""

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.data_sync.models.job import SyncJobDocument


class SyncJobRepository(AsyncRepository[SyncJobDocument]):
    """同步作业 Repository。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化。

        Args:
            collection: MongoDB 集合对象（sync_jobs）
        """
        super().__init__(collection, SyncJobDocument)

    async def find_by_name(self, name: str) -> SyncJobDocument | None:
        """根据名称查找作业。

        Args:
            name: 作业名称

        Returns:
            作业文档，如果不存在则返回 None
        """
        return await self.get_by_id(name)

    async def find_enabled_jobs(self) -> list[SyncJobDocument]:
        """查找所有启用的作业。

        Returns:
            启用的作业文档列表
        """
        return await self.list(filters={"enabled": True})

    async def find_by_schedule(self) -> list[SyncJobDocument]:
        """查找所有有调度配置的作业。

        Returns:
            有 schedule_cron 的作业列表
        """
        return await self.list(filters={"schedule_cron": {"$ne": None}})

    async def update_last_run(
        self, job_id: str, status: str, timestamp
    ) -> SyncJobDocument | None:
        """更新最后运行状态。

        Args:
            job_id: 作业 ID
            status: 运行状态
            timestamp: 运行时间

        Returns:
            更新后的作业文档，如果不存在则返回 None
        """
        return await self.update(
            job_id,
            {"last_run_status": status, "last_run_at": timestamp},
        )

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("name", unique=True)
        await self._collection.create_index([("enabled", 1), ("schedule_cron", 1)])


