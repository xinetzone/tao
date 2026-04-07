"""推送服务数据模型模块。

定义消息、连接信息、在线状态等核心数据类型。
"""
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class MessagePriority(StrEnum):
    """消息优先级。"""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ConnectionStatus(StrEnum):
    """连接状态。"""

    ONLINE = "online"
    OFFLINE = "offline"
    RECONNECTING = "reconnecting"


class MessageType(StrEnum):
    """消息类型。"""

    PUSH = "push"
    ACK = "ack"
    HEARTBEAT = "heartbeat"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ERROR = "error"
    SYSTEM = "system"
    CONFIG_CHANGED = "config_changed"


@dataclass(slots=True)
class PushMessage:
    """推送消息。

    Attributes:
        id: 唯一消息 ID
        channel: 目标频道
        event_type: 事件类型
        data: 消息负载
        priority: 优先级
        timestamp: 创建时间戳
        requires_ack: 是否需要客户端确认
        retry_count: 当前重试次数
        max_retries: 最大重试次数
        sender_id: 发送者标识（服务实例 ID）
    """

    channel: str
    event_type: str
    data: dict[str, Any]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    requires_ack: bool = False
    retry_count: int = 0
    max_retries: int = 3
    sender_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """序列化为可发送的字典格式。"""
        return {
            "id": self.id,
            "type": self.event_type,
            "channel": self.channel,
            "data": self.data,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "requires_ack": self.requires_ack,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> PushMessage:
        """从字典反序列化。"""
        return cls(
            id=raw.get("id", uuid.uuid4().hex),
            channel=raw.get("channel", ""),
            event_type=raw.get("type", raw.get("event_type", "push")),
            data=raw.get("data", {}),
            priority=MessagePriority(raw.get("priority", "normal")),
            timestamp=datetime.fromisoformat(raw["timestamp"])
            if "timestamp" in raw
            else datetime.now(UTC),
            requires_ack=raw.get("requires_ack", False),
            retry_count=raw.get("retry_count", 0),
            max_retries=raw.get("max_retries", 3),
            sender_id=raw.get("sender_id", ""),
        )


@dataclass(slots=True)
class ConnectionInfo:
    """WebSocket 连接上下文信息。

    Attributes:
        user_id: 用户唯一标识
        connected_at: 连接建立时间
        last_heartbeat: 最后心跳时间
        status: 当前连接状态
        channels: 已订阅频道集合
        pending_acks: 等待确认的消息 (message_id -> PushMessage)
        message_buffer: 离线消息缓冲队列
        metadata: 额外上下文（环境、服务列表等）
    """

    user_id: str
    connected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: ConnectionStatus = ConnectionStatus.ONLINE
    channels: set[str] = field(default_factory=set)
    pending_acks: dict[str, PushMessage] = field(default_factory=dict)
    message_buffer: deque[PushMessage] = field(
        default_factory=lambda: deque(maxlen=1000)
    )
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConnectionStats:
    """连接统计信息。"""

    total_connections: int = 0
    active_connections: int = 0
    total_channels: int = 0
    total_messages_sent: int = 0
    total_messages_failed: int = 0
    total_acks_received: int = 0
    total_acks_timeout: int = 0
    uptime_seconds: float = 0.0
    online_users: int = 0
    reconnecting_users: int = 0

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "total_channels": self.total_channels,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_failed": self.total_messages_failed,
            "total_acks_received": self.total_acks_received,
            "total_acks_timeout": self.total_acks_timeout,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "online_users": self.online_users,
            "reconnecting_users": self.reconnecting_users,
        }


@dataclass(slots=True)
class UserPresence:
    """用户在线状态。"""

    user_id: str
    status: ConnectionStatus
    last_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    connection_count: int = 0
    active_channels: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "user_id": self.user_id,
            "status": self.status.value,
            "last_seen": self.last_seen.isoformat(),
            "connection_count": self.connection_count,
            "active_channels": self.active_channels,
        }
