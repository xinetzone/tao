"""推送服务 Protocol 接口定义模块。

定义消息缓冲、在线状态追踪和连接管理的抽象接口，
遵循现有 ConfigCacheProtocol 模式实现依赖注入和测试解耦。
"""
from datetime import datetime
from typing import Protocol, runtime_checkable

from .models import ConnectionStats, PushMessage, UserPresence


@runtime_checkable
class MessageBufferProtocol(Protocol):
    """离线消息缓冲协议。"""

    async def push(self, user_id: str, message: PushMessage) -> None:
        """缓冲一条用户离线消息。"""
        ...

    async def push_to_channel(self, channel: str, message: PushMessage) -> None:
        """缓冲一条频道消息（供 HTTP 轮询使用）。"""
        ...

    async def flush(self, user_id: str, limit: int = 100) -> list[PushMessage]:
        """取出并清除用户的离线消息。"""
        ...

    async def get_recent(
        self,
        channel: str,
        since: datetime,
        limit: int = 50,
    ) -> list[PushMessage]:
        """获取频道自指定时间以来的消息（HTTP 轮询用）。"""
        ...


@runtime_checkable
class PresenceTrackerProtocol(Protocol):
    """用户在线状态追踪协议。"""

    async def set_online(self, user_id: str, instance_id: str) -> None:
        """标记用户在线。"""
        ...

    async def set_offline(self, user_id: str, instance_id: str) -> None:
        """标记用户离线。"""
        ...

    async def get_status(self, user_id: str) -> UserPresence | None:
        """获取用户在线状态。"""
        ...

    async def get_all_online(self) -> list[UserPresence]:
        """获取所有在线用户。"""
        ...


@runtime_checkable
class ConnectionManagerProtocol(Protocol):
    """WebSocket 连接管理器协议。"""

    async def broadcast(self, channel: str, message: PushMessage) -> int:
        """向频道广播消息，返回投递成功的连接数。"""
        ...

    async def send_to_user(self, user_id: str, message: PushMessage) -> int:
        """向特定用户发送消息，返回投递成功的连接数。"""
        ...

    def get_stats(self) -> ConnectionStats:
        """获取连接统计信息。"""
        ...
