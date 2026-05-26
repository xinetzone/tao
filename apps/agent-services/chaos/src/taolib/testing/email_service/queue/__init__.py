"""邮件队列层。"""

from .memory_queue import InMemoryEmailQueue
from .protocol import EmailQueueProtocol
from .redis_queue import RedisEmailQueue

__all__ = [
    "EmailQueueProtocol",
    "InMemoryEmailQueue",
    "RedisEmailQueue",
]


