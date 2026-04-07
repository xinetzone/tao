"""异步调度器。

提供简单的 cron-like 定时调度功能。
"""

import asyncio
import logging
from datetime import UTC, datetime

try:
    from croniter import croniter
except ImportError:
    croniter = None

from taolib.data_sync.repository.job_repo import SyncJobRepository
from taolib.data_sync.services.orchestrator import SyncOrchestrator

logger = logging.getLogger(__name__)


class AsyncScheduler:
    """异步调度器。

    根据作业的 schedule_cron 配置定时运行同步作业。
    """

    def __init__(
        self,
        orchestrator: SyncOrchestrator,
        job_repo: SyncJobRepository,
        check_interval: int = 60,
    ) -> None:
        """初始化。

        Args:
            orchestrator: 同步管道编排器
            job_repo: 作业 Repository
            check_interval: 检查间隔（秒），默认 60 秒
        """
        self._orchestrator = orchestrator
        self._job_repo = job_repo
        self._check_interval = check_interval
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """启动调度器。"""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """停止调度器。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run_loop(self) -> None:
        """运行循环。"""
        while self._running:
            try:
                await self._check_and_run()
            except Exception:
                logger.exception("调度器检查周期出错")
            await asyncio.sleep(self._check_interval)

    async def _check_and_run(self) -> None:
        """检查并运行到期的作业。"""
        if croniter is None:
            return  # croniter 未安装

        jobs = await self._job_repo.find_by_schedule()
        now = datetime.now(UTC)

        for job in jobs:
            if not job.schedule_cron or not job.enabled:
                continue

            # 检查是否到期
            if self._is_due(job.schedule_cron, now):
                # 运行作业（不等待结果）
                asyncio.create_task(self._run_job(job.id))

    def _is_due(self, cron_expr: str, now: datetime) -> bool:
        """检查是否到期。

        简化实现：每分钟检查一次，如果 cron 表达式匹配当前分钟则运行。
        """
        try:
            cron = croniter(cron_expr, now)
            prev = cron.get_prev(datetime)
            diff = (now - prev).total_seconds()
            return diff < self._check_interval
        except Exception:
            return False

    async def _run_job(self, job_id: str) -> None:
        """运行单个作业。"""
        try:
            await self._orchestrator.run_job(job_id)
        except Exception:
            logger.error("作业 %s 执行失败", job_id, exc_info=True)
