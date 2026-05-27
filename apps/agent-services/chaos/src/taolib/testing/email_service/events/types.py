"""邮件生命周期事件数据类。

定义邮件系统中各种事件的数据结构，用于事件发布和日志记录。
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class EmailQueuedEvent:
    """邮件入队事件。"""

    email_id: str
    recipient_count: int
    priority: str
    email_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.queued",
            "email_id": self.email_id,
            "recipient_count": self.recipient_count,
            "priority": self.priority,
            "email_type": self.email_type,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmailSentEvent:
    """邮件已发送事件。"""

    email_id: str
    provider: str
    provider_message_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.sent",
            "email_id": self.email_id,
            "provider": self.provider,
            "provider_message_id": self.provider_message_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmailDeliveredEvent:
    """邮件已投递事件。"""

    email_id: str
    recipient: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.delivered",
            "email_id": self.email_id,
            "recipient": self.recipient,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmailOpenedEvent:
    """邮件已打开事件。"""

    email_id: str
    recipient: str
    ip_address: str | None = None
    user_agent: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.opened",
            "email_id": self.email_id,
            "recipient": self.recipient,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmailClickedEvent:
    """邮件链接被点击事件。"""

    email_id: str
    recipient: str
    url: str
    ip_address: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.clicked",
            "email_id": self.email_id,
            "recipient": self.recipient,
            "url": self.url,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmailBouncedEvent:
    """邮件退信事件。"""

    email_id: str
    recipient: str
    bounce_type: str
    reason: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.bounced",
            "email_id": self.email_id,
            "recipient": self.recipient,
            "bounce_type": self.bounce_type,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmailFailedEvent:
    """邮件发送失败事件。"""

    email_id: str
    error_message: str
    retry_count: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "event": "email.failed",
            "email_id": self.email_id,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp.isoformat(),
        }
