"""Redis 邮件队列实现。

基于 Redis List 的优先级队列，使用 LPUSH/BRPOP 模式。
"""

from redis.asyncio import Redis

from taolib.testing.email_service.models.enums import EmailPriority

_QUEUE_KEYS = {
    EmailPriority.HIGH: "email:queue:high",
    EmailPriority.NORMAL: "email:queue:normal",
    EmailPriority.LOW: "email:queue:low",
}

_PRIORITY_ORDER = [
    _QUEUE_KEYS[EmailPriority.HIGH],
    _QUEUE_KEYS[EmailPriority.NORMAL],
    _QUEUE_KEYS[EmailPriority.LOW],
]


class RedisEmailQueue:
    """Redis 邮件队列。

    使用三个 Redis List 实现优先级队列：
    - email:queue:high   (高优先级)
    - email:queue:normal (普通优先级)
    - email:queue:low    (低优先级)

    BRPOP 按顺序检查三个列表，自然实现优先级。
    """

    def __init__(self, redis_client: Redis) -> None:
        """初始化。

        Args:
            redis_client: Redis 异步客户端
        """
        self._redis = redis_client

    async def enqueue(
        self, email_id: str, priority: EmailPriority = EmailPriority.NORMAL
    ) -> None:
        """将邮件 ID 加入队列。"""
        key = _QUEUE_KEYS.get(priority, _QUEUE_KEYS[EmailPriority.NORMAL])
        await self._redis.lpush(key, email_id)

    async def enqueue_bulk(
        self, email_ids: list[str], priority: EmailPriority = EmailPriority.NORMAL
    ) -> None:
        """批量加入队列。"""
        if not email_ids:
            return
        key = _QUEUE_KEYS.get(priority, _QUEUE_KEYS[EmailPriority.NORMAL])
        await self._redis.lpush(key, *email_ids)

    async def dequeue(self, timeout: int = 5) -> str | None:
        """从队列取出一封邮件 ID（按优先级）。

        使用 BRPOP 按 high → normal → low 顺序检查。
        """
        result = await self._redis.brpop(_PRIORITY_ORDER, timeout=timeout)
        if result is None:
            return None
        # BRPOP 返回 (key, value)
        _, email_id = result
        if isinstance(email_id, bytes):
            return email_id.decode("utf-8")
        return str(email_id)

    async def size(self) -> dict[str, int]:
        """获取各优先级队列大小。"""
        return {
            "high": await self._redis.llen(_QUEUE_KEYS[EmailPriority.HIGH]),
            "normal": await self._redis.llen(_QUEUE_KEYS[EmailPriority.NORMAL]),
            "low": await self._redis.llen(_QUEUE_KEYS[EmailPriority.LOW]),
        }


