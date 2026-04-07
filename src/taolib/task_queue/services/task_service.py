"""任务服务层。

提供任务的业务逻辑操作。
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from taolib.task_queue.errors import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
)
from taolib.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.task_queue.models.task import TaskCreate, TaskDocument
from taolib.task_queue.queue.redis_queue import RedisTaskQueue
from taolib.task_queue.repository.task_repo import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务。

    提供任务提交、查询、重试、取消等业务逻辑。
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        redis_queue: RedisTaskQueue,
    ) -> None:
        """初始化。

        Args:
            task_repo: 任务 Repository
            redis_queue: Redis 任务队列
        """
        self._task_repo = task_repo
        self._redis_queue = redis_queue

    async def submit_task(self, task_create: TaskCreate) -> TaskDocument:
        """提交新任务。

        Args:
            task_create: 任务创建数据

        Returns:
            创建的任务文档

        Raises:
            TaskAlreadyExistsError: 幂等键冲突
        """
        # 幂等键检查
        if task_create.idempotency_key:
            existing = await self._task_repo.find_by_idempotency_key(
                task_create.idempotency_key
            )
            if existing is not None:
                raise TaskAlreadyExistsError(
                    f"Task with idempotency key '{task_create.idempotency_key}' "
                    f"already exists: {existing.id}"
                )

        # 生成任务 ID
        task_id = uuid4().hex

        # 构建文档数据
        now = datetime.now(UTC)
        doc_data = task_create.model_dump(by_alias=False)
        doc_data["_id"] = task_id
        doc_data["status"] = TaskStatus.PENDING
        doc_data["retry_count"] = 0
        doc_data["created_at"] = now

        # 写入 MongoDB
        task_doc = await self._task_repo.create(doc_data)

        # 入队 Redis
        task_meta = {
            "task_type": task_create.task_type,
            "priority": task_create.priority,
            "status": TaskStatus.PENDING,
        }
        await self._redis_queue.enqueue(task_id, task_create.priority, task_meta)

        logger.info(
            "Task submitted: %s (type=%s, priority=%s)",
            task_id,
            task_create.task_type,
            task_create.priority,
        )
        return task_doc

    async def get_task(self, task_id: str) -> TaskDocument:
        """获取任务详情。

        Args:
            task_id: 任务 ID

        Returns:
            任务文档

        Raises:
            TaskNotFoundError: 任务不存在
        """
        task = await self._task_repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return task

    async def retry_task(self, task_id: str) -> TaskDocument:
        """手动重试失败任务。

        重置任务状态并重新入队。

        Args:
            task_id: 任务 ID

        Returns:
            更新后的任务文档

        Raises:
            TaskNotFoundError: 任务不存在
            ValueError: 任务状态不是 FAILED
        """
        task = await self.get_task(task_id)

        if task.status != TaskStatus.FAILED:
            raise ValueError(
                f"Only failed tasks can be retried. Current status: {task.status}"
            )

        # 重置状态
        updated = await self._task_repo.update_status(
            task_id,
            TaskStatus.PENDING,
            retry_count=0,
            error_message=None,
            error_traceback=None,
            started_at=None,
            completed_at=None,
            next_retry_at=None,
        )

        # 从 Redis 失败集合中移除
        await self._redis_queue.remove_from_failed(task_id)

        # 重新入队
        task_meta = {
            "task_type": task.task_type,
            "priority": task.priority,
            "status": TaskStatus.PENDING,
        }
        await self._redis_queue.enqueue(task_id, task.priority, task_meta)

        logger.info("Task retried: %s", task_id)
        return updated

    async def cancel_task(self, task_id: str) -> TaskDocument:
        """取消任务。

        仅可取消 PENDING 或 RETRYING 状态的任务。

        Args:
            task_id: 任务 ID

        Returns:
            更新后的任务文档

        Raises:
            TaskNotFoundError: 任务不存在
            ValueError: 任务状态不允许取消
        """
        task = await self.get_task(task_id)

        if task.status not in (TaskStatus.PENDING, TaskStatus.RETRYING):
            raise ValueError(
                f"Only pending or retrying tasks can be cancelled. "
                f"Current status: {task.status}"
            )

        now = datetime.now(UTC)
        updated = await self._task_repo.update_status(
            task_id, TaskStatus.CANCELLED, completed_at=now
        )

        logger.info("Task cancelled: %s", task_id)
        return updated

    async def list_tasks(
        self,
        status: TaskStatus | None = None,
        task_type: str | None = None,
        priority: TaskPriority | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TaskDocument]:
        """查询任务列表。

        Args:
            status: 状态过滤
            task_type: 类型过滤
            priority: 优先级过滤
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            任务文档列表
        """
        return await self._task_repo.find_by_filters(
            status=status,
            task_type=task_type,
            priority=priority,
            skip=skip,
            limit=limit,
        )

    async def get_stats(self) -> dict[str, Any]:
        """获取任务统计信息。

        合并 Redis 实时数据和 MongoDB 持久统计。

        Returns:
            统计信息字典
        """
        # Redis 实时统计
        redis_stats = await self._redis_queue.get_stats()

        # MongoDB 各状态计数
        pending_count = await self._task_repo.count({"status": TaskStatus.PENDING})
        running_count = await self._task_repo.count({"status": TaskStatus.RUNNING})
        completed_count = await self._task_repo.count({"status": TaskStatus.COMPLETED})
        failed_count = await self._task_repo.count({"status": TaskStatus.FAILED})
        retrying_count = await self._task_repo.count({"status": TaskStatus.RETRYING})
        total_count = await self._task_repo.count()

        return {
            # MongoDB 持久统计
            "total_tasks": total_count,
            "pending": pending_count,
            "running": running_count,
            "completed": completed_count,
            "failed": failed_count,
            "retrying": retrying_count,
            # Redis 实时队列统计
            "queue_high": redis_stats["queue_high"],
            "queue_normal": redis_stats["queue_normal"],
            "queue_low": redis_stats["queue_low"],
            # Redis 累计统计
            "total_submitted": redis_stats["total_submitted"],
            "total_completed": redis_stats["total_completed"],
            "total_failed": redis_stats["total_failed"],
            "total_retried": redis_stats["total_retried"],
        }
