"""任务 Repository。

提供 Task 的 MongoDB 持久化操作。
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.testing.task_queue.models.task import TaskDocument


class TaskRepository(AsyncRepository[TaskDocument]):
    """任务 Repository。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化。

        Args:
            collection: MongoDB 集合对象（tasks）
        """
        super().__init__(collection, TaskDocument)

    async def find_by_status(
        self,
        status: TaskStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TaskDocument]:
        """根据状态查找任务。

        Args:
            status: 任务状态
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            任务文档列表
        """
        return await self.list(
            filters={"status": status},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_by_type(
        self,
        task_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TaskDocument]:
        """根据任务类型查找任务。

        Args:
            task_type: 任务类型
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            任务文档列表
        """
        return await self.list(
            filters={"task_type": task_type},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_failed_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TaskDocument]:
        """查找所有失败的任务。

        Returns:
            失败任务列表
        """
        return await self.find_by_status(TaskStatus.FAILED, skip=skip, limit=limit)

    async def find_running_tasks(self) -> list[TaskDocument]:
        """查找所有运行中的任务。

        Returns:
            运行中任务列表
        """
        return await self.find_by_status(TaskStatus.RUNNING)

    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        **extra_fields: Any,
    ) -> TaskDocument | None:
        """更新任务状态。

        Args:
            task_id: 任务 ID
            status: 新状态
            **extra_fields: 额外更新字段

        Returns:
            更新后的任务文档，如果不存在则返回 None
        """
        updates: dict[str, Any] = {"status": status, **extra_fields}
        return await self.update(task_id, updates)

    async def find_by_idempotency_key(
        self, idempotency_key: str
    ) -> TaskDocument | None:
        """根据幂等键查找任务。

        Args:
            idempotency_key: 幂等键

        Returns:
            任务文档，如果不存在则返回 None
        """
        docs = await self.list(filters={"idempotency_key": idempotency_key}, limit=1)
        return docs[0] if docs else None

    async def find_by_filters(
        self,
        status: TaskStatus | None = None,
        task_type: str | None = None,
        priority: TaskPriority | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TaskDocument]:
        """根据多个条件过滤查找任务。

        Args:
            status: 任务状态过滤
            task_type: 任务类型过滤
            priority: 优先级过滤
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            任务文档列表
        """
        filters: dict[str, Any] = {}
        if status is not None:
            filters["status"] = status
        if task_type is not None:
            filters["task_type"] = task_type
        if priority is not None:
            filters["priority"] = priority
        return await self.list(
            filters=filters,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("task_type")
        await self._collection.create_index([("status", 1), ("priority", 1)])
        await self._collection.create_index("idempotency_key", unique=True, sparse=True)
        await self._collection.create_index(
            "created_at", expireAfterSeconds=2592000
        )  # 30 days TTL


