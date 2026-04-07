"""内存邮件队列实现。

用于测试环境，无需 Redis 依赖。
"""

import asyncio

from taolib.email_service.models.enums import EmailPriority

_PRIORITY_MAP = {
    EmailPriority.HIGH: 0,
    EmailPriority.NORMAL: 1,
    EmailPriority.LOW: 2,
}


class InMemoryEmailQueue:
    """内存邮件队列。

    使用 asyncio.PriorityQueue 实现，仅用于测试。
    """

    def __init__(self) -> None:
        """初始化。"""
        self._queue: asyncio.PriorityQueue[tuple[int, str]] = asyncio.PriorityQueue()
        self._counts: dict[str, int] = {"high": 0, "normal": 0, "low": 0}

    async def enqueue(
        self, email_id: str, priority: EmailPriority = EmailPriority.NORMAL
    ) -> None:
        """将邮件 ID 加入队列。"""
        pri_num = _PRIORITY_MAP.get(priority, 1)
        await self._queue.put((pri_num, email_id))
        self._counts[priority] = self._counts.get(priority, 0) + 1

    async def enqueue_bulk(
        self, email_ids: list[str], priority: EmailPriority = EmailPriority.NORMAL
    ) -> None:
        """批量加入队列。"""
        for email_id in email_ids:
            await self.enqueue(email_id, priority)

    async def dequeue(self, timeout: int = 5) -> str | None:
        """从队列取出一封邮件 ID。"""
        try:
            _, email_id = await asyncio.wait_for(self._queue.get(), timeout=timeout)
            return email_id
        except TimeoutError:
            return None

    async def size(self) -> dict[str, int]:
        """获取队列大小（近似值）。"""
        total = self._queue.qsize()
        return {
            "high": 0,
            "normal": total,
            "low": 0,
            "total": total,
        }
