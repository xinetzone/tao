"""任务工作协程。

单个 Worker 的实现，从 Redis 队列中拉取任务并执行。
"""

import asyncio
import logging
import traceback
from datetime import UTC, datetime, timedelta
from typing import Any

from taolib.task_queue.models.enums import TaskStatus
from taolib.task_queue.models.task import TaskDocument
from taolib.task_queue.queue.redis_queue import RedisTaskQueue
from taolib.task_queue.repository.task_repo import TaskRepository
from taolib.task_queue.worker.registry import TaskHandlerRegistry

logger = logging.getLogger(__name__)


class TaskWorker:
    """任务工作协程。

    从 Redis 队列中拉取任务、查找处理器并执行，
    处理成功/失败结果和重试逻辑。
    """

    def __init__(
        self,
        worker_id: str,
        redis_queue: RedisTaskQueue,
        task_repo: TaskRepository,
        registry: TaskHandlerRegistry,
    ) -> None:
        """初始化。

        Args:
            worker_id: 工作者标识
            redis_queue: Redis 任务队列
            task_repo: 任务 Repository
            registry: 任务处理器注册表
        """
        self._worker_id = worker_id
        self._redis_queue = redis_queue
        self._task_repo = task_repo
        self._registry = registry
        self._running = False
        self._current_task_id: str | None = None

    @property
    def worker_id(self) -> str:
        """工作者标识。"""
        return self._worker_id

    @property
    def is_running(self) -> bool:
        """是否正在运行。"""
        return self._running

    @property
    def current_task_id(self) -> str | None:
        """当前正在执行的任务 ID。"""
        return self._current_task_id

    async def start(self) -> None:
        """启动工作协程。"""
        self._running = True
        logger.info("Worker %s started.", self._worker_id)
        try:
            await self._run_loop()
        finally:
            self._running = False
            logger.info("Worker %s stopped.", self._worker_id)

    def stop(self) -> None:
        """请求停止工作协程（完成当前任务后退出）。"""
        self._running = False

    async def _run_loop(self) -> None:
        """主工作循环。"""
        while self._running:
            try:
                task_id = await self._redis_queue.dequeue(timeout=5.0)
                if task_id is None:
                    continue

                self._current_task_id = task_id
                try:
                    await self._process_task(task_id)
                finally:
                    self._current_task_id = None

            except asyncio.CancelledError:
                logger.info("Worker %s cancelled.", self._worker_id)
                break
            except Exception:
                logger.exception(
                    "Worker %s encountered unexpected error.", self._worker_id
                )
                await asyncio.sleep(1)

    async def _process_task(self, task_id: str) -> None:
        """处理单个任务。

        Args:
            task_id: 任务 ID
        """
        # 从 MongoDB 获取完整任务数据
        task = await self._task_repo.get_by_id(task_id)
        if task is None:
            logger.warning(
                "Worker %s: task %s not found in MongoDB, acking.",
                self._worker_id,
                task_id,
            )
            await self._redis_queue.ack(task_id)
            return

        # 检查任务是否已被取消
        if task.status == TaskStatus.CANCELLED:
            logger.info(
                "Worker %s: task %s was cancelled, acking.",
                self._worker_id,
                task_id,
            )
            await self._redis_queue.ack(task_id)
            return

        # 查找处理器
        handler = self._registry.get(task.task_type)
        if handler is None:
            logger.error(
                "Worker %s: no handler for task type '%s'.",
                self._worker_id,
                task.task_type,
            )
            await self._handle_failure(
                task,
                Exception(f"No handler registered for task type: {task.task_type}"),
            )
            return

        # 更新状态为 RUNNING
        now = datetime.now(UTC)
        await self._task_repo.update_status(task_id, TaskStatus.RUNNING, started_at=now)

        # 执行处理器
        try:
            result = await self._execute_handler(handler, task)
            await self._handle_success(task, result)
        except Exception as e:
            await self._handle_failure(task, e)

    async def _execute_handler(
        self,
        handler: Any,
        task: TaskDocument,
    ) -> dict[str, Any]:
        """执行任务处理器。

        Args:
            handler: 处理器函数
            task: 任务文档

        Returns:
            处理结果字典
        """
        if TaskHandlerRegistry.is_async_handler(handler):
            result = await handler(task.params)
        else:
            result = await asyncio.to_thread(handler, task.params)

        if result is None:
            result = {}
        if not isinstance(result, dict):
            result = {"result": result}
        return result

    async def _handle_success(
        self,
        task: TaskDocument,
        result: dict[str, Any],
    ) -> None:
        """处理任务成功完成。

        Args:
            task: 任务文档
            result: 执行结果
        """
        now = datetime.now(UTC)
        await self._task_repo.update_status(
            task.id,
            TaskStatus.COMPLETED,
            result=result,
            completed_at=now,
            error_message=None,
            error_traceback=None,
        )
        await self._redis_queue.ack(task.id)
        logger.info(
            "Worker %s: task %s completed successfully.",
            self._worker_id,
            task.id,
        )

    async def _handle_failure(
        self,
        task: TaskDocument,
        error: Exception,
    ) -> None:
        """处理任务执行失败。

        Args:
            task: 任务文档
            error: 异常对象
        """
        now = datetime.now(UTC)
        error_msg = str(error)
        error_tb = traceback.format_exc()
        new_retry_count = task.retry_count + 1

        if new_retry_count < task.max_retries:
            # 调度重试
            delay_index = min(task.retry_count, len(task.retry_delays) - 1)
            delay_seconds = task.retry_delays[delay_index]
            next_retry_at = now + timedelta(seconds=delay_seconds)

            await self._task_repo.update_status(
                task.id,
                TaskStatus.RETRYING,
                retry_count=new_retry_count,
                error_message=error_msg,
                error_traceback=error_tb,
                next_retry_at=next_retry_at,
            )
            await self._redis_queue.nack(
                task.id,
                schedule_retry=True,
                retry_at=next_retry_at.timestamp(),
            )
            logger.warning(
                "Worker %s: task %s failed (attempt %d/%d), "
                "retry scheduled at %s. Error: %s",
                self._worker_id,
                task.id,
                new_retry_count,
                task.max_retries,
                next_retry_at.isoformat(),
                error_msg,
            )
        else:
            # 最终失败
            await self._task_repo.update_status(
                task.id,
                TaskStatus.FAILED,
                retry_count=new_retry_count,
                error_message=error_msg,
                error_traceback=error_tb,
                completed_at=now,
                next_retry_at=None,
            )
            await self._redis_queue.nack(
                task.id,
                schedule_retry=False,
            )
            logger.error(
                "Worker %s: task %s failed permanently after %d attempts. Error: %s",
                self._worker_id,
                task.id,
                new_retry_count,
                error_msg,
            )
