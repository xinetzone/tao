"""邮件生命周期事件类型。"""

from .types import (
    EmailBouncedEvent,
    EmailClickedEvent,
    EmailDeliveredEvent,
    EmailFailedEvent,
    EmailOpenedEvent,
    EmailQueuedEvent,
    EmailSentEvent,
)

__all__ = [
    "EmailBouncedEvent",
    "EmailClickedEvent",
    "EmailDeliveredEvent",
    "EmailFailedEvent",
    "EmailOpenedEvent",
    "EmailQueuedEvent",
    "EmailSentEvent",
]
