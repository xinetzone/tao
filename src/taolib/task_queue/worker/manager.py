"""工作者管理器。

编排多个 TaskWorker 协程，管理重试轮询和崩溃恢复。
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from taolib.task_queue.models.enums import TaskStatus
from taolib.task_queue.queue.redis_queue import RedisTaskQueue
from taolib.task_queue.repository.task_repo import TaskRepository
from taolib.task_queue.worker.registry import TaskHandlerRegistry
from taolib.task_queue.worker.worker import TaskWorker

logger = logging.getLogger(__name__)

# 重试轮询间隔（秒）
RETRY_POLL_INTERVAL = 30

# 崩溃恢复：超过此时间的 RUNNING 任务视为孤儿（秒）
STALE_TASK_TIMEOUT = 1800  # 30 minutes


class WorkerManager:
    """工作者管理器。

    管理多个 TaskWorker 的生命周期，包括：
    - 启动/停止工作者
    - 重试任务轮询
    - 崩溃恢复
    """

    def __init__(
        self,
        redis_queue: RedisTaskQueue,
        task_repo: TaskRepository,
        registry: TaskHandlerRegistry,
        num_workers: int = 3,
    ) -> None:
        """初始化。

        Args:
            redis_queue: Redis 任务队列
            task_repo: 任务 Repository
            registry: 任务处理器注册表
            num_workers: 工作者数量
        """
        self._redis_queue = redis_queue
        self._task_repo = task_repo
        self._registry = registry
        self._num_workers = num_workers
        self._workers: list[TaskWorker] = []
        self._worker_tasks: list[asyncio.Task] = []
        self._retry_poller_task: asyncio.Task | None = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """管理器是否正在运行。"""
        return self._running

    @property
    def num_workers(self) -> int:
        """工作者数量。"""
        return self._num_workers

    @property
    def workers(self) -> list[TaskWorker]:
        """工作者列表。"""
        return list(self._workers)

    async def start(self) -> None:
        """启动所有工作者和重试轮询。"""
        if self._running:
            logger.warning("WorkerManager is already running.")
            return

        self._running = True
        logger.info("Starting WorkerManager with %d workers...", self._num_workers)

        # 崩溃恢复
        await self._recover_running_tasks()

        # 启动工作者
        for i in range(self._num_workers):
            worker = TaskWorker(
                worker_id=f"worker-{i}",
                redis_queue=self._redis_queue,
                task_repo=self._task_repo,
                registry=self._registry,
            )
            self._workers.append(worker)
            task = asyncio.create_task(worker.start(), name=f"task-worker-{i}")
            self._worker_tasks.append(task)

        # 启动重试轮询
        self._retry_poller_task = asyncio.create_task(
            self._retry_poll_loop(), name="retry-poller"
        )

        logger.info("WorkerManager started with %d workers.", self._num_workers)

    async def stop(self) -> None:
        """优雅停止所有工作者。

        等待每个工作者完成当前任务后退出。
        """
        if not self._running:
            return

        self._running = False
        logger.info("Stopping WorkerManager...")

        # 通知所有工作者停止
        for worker in self._workers:
            worker.stop()

        # 等待所有工作者完成
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        # 停止重试轮询
        if self._retry_poller_task is not None:
            self._retry_poller_task.cancel()
            try:
                await self._retry_poller_task
            except asyncio.CancelledError:
                pass
            self._retry_poller_task = None

        # 清理
        self._workers.clear()
        self._worker_tasks.clear()

        logger.info("WorkerManager stopped.")

    async def _retry_poll_loop(self) -> None:
        """重试任务轮询循环。

        每 30 秒检查到期的重试任务，将其重新入队。
        """
        logger.info("Retry poller started (interval: %ds).", RETRY_POLL_INTERVAL)
        while self._running:
            try:
                await asyncio.sleep(RETRY_POLL_INTERVAL)
                if not self._running:
                    break

                re_enqueued = await self._redis_queue.poll_retries()
                if re_enqueued:
                    # 更新 MongoDB 状态
                    for task_id in re_enqueued:
                        await self._task_repo.update_status(
                            task_id,
                            TaskStatus.PENDING,
                            next_retry_at=None,
                        )
                    logger.info(
                        "Re-enqueued %d retry tasks: %s",
                        len(re_enqueued),
                        re_enqueued,
                    )
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in retry poller.")

    async def _recover_running_tasks(self) -> None:
        """崩溃恢复：检查 Redis 中的孤儿任务并重新入队。

        启动时调用，处理因进程崩溃而停留在 running 状态的任务。
        """
        try:
            running_ids = await self._redis_queue.get_running_task_ids()
            if not running_ids:
                return

            logger.info(
                "Crash recovery: found %d tasks in running state.",
                len(running_ids),
            )
            now = datetime.now(UTC)
            stale_threshold = now - timedelta(seconds=STALE_TASK_TIMEOUT)
            recovered = 0

            for task_id in running_ids:
                task = await self._task_repo.get_by_id(task_id)
                if task is None:
                    # 孤儿任务，直接清理 Redis
                    await self._redis_queue.remove_from_running(task_id)
                    continue

                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    # MongoDB 已更新但 Redis 未清理
                    await self._redis_queue.remove_from_running(task_id)
                    continue

                if task.started_at and task.started_at < stale_threshold:
                    # 超时任务，重新入队
                    await self._redis_queue.remove_from_running(task_id)
                    await self._task_repo.update_status(task_id, TaskStatus.PENDING)
                    await self._redis_queue.enqueue(
                        task_id,
                        task.priority,
                        {
                            "task_type": task.task_type,
                            "priority": task.priority,
                        },
                    )
                    recovered += 1
                    logger.info(
                        "Recovered stale task: %s (started_at: %s)",
                        task_id,
                        task.started_at,
                    )

            if recovered:
                logger.info("Crash recovery: re-enqueued %d stale tasks.", recovered)

        except Exception:
            logger.exception("Error during crash recovery.")
