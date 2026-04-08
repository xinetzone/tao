"""后台队列处理器。

从队列中取出邮件并通过提供商发送，支持重试和指数退避。
"""

import asyncio
import logging

from taolib.testing.email_service.models.enums import EmailStatus
from taolib.testing.email_service.queue.protocol import EmailQueueProtocol
from taolib.testing.email_service.repository.email_repo import EmailRepository

logger = logging.getLogger(__name__)


class QueueProcessor:
    """邮件队列处理器。

    作为后台 asyncio.Task 运行，持续从队列取出邮件并发送。
    参考 data_sync.services.scheduler.AsyncScheduler 模式。
    """

    def __init__(
        self,
        queue: EmailQueueProtocol,
        email_repo: EmailRepository,
        send_callback,
        poll_interval: float = 1.0,
        batch_size: int = 10,
    ) -> None:
        """初始化。

        Args:
            queue: 邮件队列
            email_repo: 邮件 Repository
            send_callback: 发送回调函数 (async def send(EmailDocument) -> EmailDocument)
            poll_interval: 轮询间隔（秒）
            batch_size: 每批处理数量
        """
        self._queue = queue
        self._email_repo = email_repo
        self._send_callback = send_callback
        self._poll_interval = poll_interval
        self._batch_size = batch_size
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """启动处理器。"""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Queue processor started")

    async def stop(self) -> None:
        """停止处理器。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Queue processor stopped")

    async def _run_loop(self) -> None:
        """主处理循环。"""
        while self._running:
            try:
                await self._process_batch()
            except Exception:
                logger.exception("Queue processor error")
            await asyncio.sleep(self._poll_interval)

    async def _process_batch(self) -> None:
        """处理一批邮件。"""
        processed = 0
        while processed < self._batch_size:
            email_id = await self._queue.dequeue(timeout=1)
            if email_id is None:
                break  # 队列为空

            await self._process_single(email_id)
            processed += 1

    async def _process_single(self, email_id: str) -> None:
        """处理单封邮件。"""
        try:
            doc = await self._email_repo.get_by_id(email_id)
            if doc is None:
                logger.warning("Email %s not found, skipping", email_id)
                return

            if doc.status != EmailStatus.QUEUED:
                logger.debug("Email %s status is %s, skipping", email_id, doc.status)
                return

            await self._send_callback(doc)
        except Exception:
            logger.exception("Failed to process email %s", email_id)

    async def process_scheduled(self) -> None:
        """处理到期的计划邮件。"""
        ready = await self._email_repo.find_scheduled_ready()
        for doc in ready:
            await self._queue.enqueue(doc.id, doc.priority)
            logger.debug("Scheduled email %s enqueued", doc.id)


