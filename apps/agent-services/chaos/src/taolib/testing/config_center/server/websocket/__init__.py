"""WebSocket 实时推送模块。

提供 WebSocket 连接管理、Redis PubSub 桥接、心跳检测、
离线消息缓冲和在线状态追踪等完整的实时推送基础设施。
"""

from .manager import WebSocketConnectionManager
from .models import (
    ConnectionInfo,
    ConnectionStats,
    ConnectionStatus,
    MessagePriority,
    MessageType,
    PushMessage,
    UserPresence,
)
from .protocols import (
    ConnectionManagerProtocol,
    MessageBufferProtocol,
    PresenceTrackerProtocol,
)
from .pubsub_bridge import PubSubBridge

__all__ = [
    "ConnectionInfo",
    "ConnectionManagerProtocol",
    "ConnectionStats",
    "ConnectionStatus",
    "MessageBufferProtocol",
    "MessagePriority",
    "MessageType",
    "PresenceTrackerProtocol",
    "PubSubBridge",
    "PushMessage",
    "UserPresence",
    "WebSocketConnectionManager",
]


