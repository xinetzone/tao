"""邮件队列协议。

定义邮件队列的统一接口。
"""

from typing import Protocol

from taolib.email_service.models.enums import EmailPriority


class EmailQueueProtocol(Protocol):
    """邮件队列协议。

    所有队列实现必须符合此协议。
    """

    async def enqueue(
        self, email_id: str, priority: EmailPriority = EmailPriority.NORMAL
    ) -> None:
        """将邮件 ID 加入队列。

        Args:
            email_id: 邮件 ID
            priority: 优先级
        """
        ...

    async def enqueue_bulk(
        self, email_ids: list[str], priority: EmailPriority = EmailPriority.NORMAL
    ) -> None:
        """批量加入队列。

        Args:
            email_ids: 邮件 ID 列表
            priority: 优先级
        """
        ...

    async def dequeue(self, timeout: int = 5) -> str | None:
        """从队列取出一封邮件 ID。

        按优先级顺序（高→普通→低）取出。

        Args:
            timeout: 等待超时秒数

        Returns:
            邮件 ID，队列为空时返回 None
        """
        ...

    async def size(self) -> dict[str, int]:
        """获取各优先级队列的大小。

        Returns:
            {priority: count} 字典
        """
        ...
