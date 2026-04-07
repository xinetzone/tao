"""事件发布器模块。

实现消息的发布功能，支持优先级、批量发布和离线消息缓冲，
确保 at-least-once 投递保证。
"""
import json
import logging
import uuid
from typing import Any

import redis.asyncio as aioredis

from ..server.websocket.models import MessagePriority, MessageType, PushMessage
from ..server.websocket.protocols import MessageBufferProtocol
from .types import ConfigChangedEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """事件发布器。

    职责：
    - 构建带唯一 ID 的 PushMessage
    - 发布到 Redis Pub/Sub 供跨实例广播
    - 写入 MessageBuffer 保证离线用户可达
    - 支持批量发布和消息优先级
    """

    BROADCAST_PREFIX = "push:broadcast:"

    def __init__(
        self,
        redis_client: aioredis.Redis,
        message_buffer: MessageBufferProtocol | None = None,
        instance_id: str = "",
    ) -> None:
        self._redis = redis_client
        self._buffer = message_buffer
        self._instance_id = instance_id or uuid.uuid4().hex[:8]

    # ------------------------------------------------------------------
    # 配置变更发布
    # ------------------------------------------------------------------

    async def publish_config_changed(self, event: ConfigChangedEvent) -> str:
        """发布配置变更事件。

        构建 HIGH 优先级、需要 ACK 确认的消息。

        Args:
            event: 配置变更事件

        Returns:
            消息 ID
        """
        channel = f"config:{event.environment}:{event.service}"
        message = PushMessage(
            channel=channel,
            event_type=MessageType.CONFIG_CHANGED,
            data=event.to_dict(),
            priority=MessagePriority.HIGH,
            requires_ack=True,
            sender_id=self._instance_id,
        )
        await self._publish(message)
        return message.id

    # ------------------------------------------------------------------
    # 通用发布
    # ------------------------------------------------------------------

    async def publish(
        self,
        channel: str,
        event_type: str,
        data: dict[str, Any],
        *,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_ack: bool = False,
    ) -> str:
        """发布通用事件。

        Args:
            channel: 目标频道
            event_type: 事件类型
            data: 消息负载
            priority: 消息优先级
            requires_ack: 是否需要客户端确认

        Returns:
            消息 ID
        """
        message = PushMessage(
            channel=channel,
            event_type=event_type,
            data=data,
            priority=priority,
            requires_ack=requires_ack,
            sender_id=self._instance_id,
        )
        await self._publish(message)
        return message.id

    async def publish_batch(self, messages: list[PushMessage]) -> list[str]:
        """批量发布消息（使用 Redis pipeline 优化）。

        Args:
            messages: 消息列表

        Returns:
            消息 ID 列表
        """
        if not messages:
            return []

        pipe = self._redis.pipeline()
        for msg in messages:
            msg.sender_id = self._instance_id
            redis_channel = f"{self.BROADCAST_PREFIX}{msg.channel}"
            payload = json.dumps(msg.to_dict(), ensure_ascii=False)
            pipe.publish(redis_channel, payload)
        await pipe.execute()

        # 写入消息缓冲
        if self._buffer:
            for msg in messages:
                await self._buffer.push_to_channel(msg.channel, msg)

        ids = [msg.id for msg in messages]
        logger.info("批量发布 %d 条消息", len(ids))
        return ids

    # ------------------------------------------------------------------
    # 用户直达 / 系统告警 便捷方法
    # ------------------------------------------------------------------

    async def publish_to_user(
        self,
        user_id: str,
        event_type: str,
        data: dict[str, Any],
        *,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_ack: bool = False,
    ) -> str:
        """发布用户直达消息。"""
        channel = f"user:{user_id}"
        return await self.publish(
            channel,
            event_type,
            data,
            priority=priority,
            requires_ack=requires_ack,
        )

    async def publish_system_alert(
        self,
        data: dict[str, Any],
        *,
        priority: MessagePriority = MessagePriority.HIGH,
    ) -> str:
        """发布系统告警。"""
        return await self.publish(
            "system",
            "system_alert",
            data,
            priority=priority,
            requires_ack=True,
        )

    # ------------------------------------------------------------------
    # 内部发布逻辑
    # ------------------------------------------------------------------

    async def _publish(self, message: PushMessage) -> None:
        """核心发布动作：Redis PUBLISH + 消息缓冲。"""
        redis_channel = f"{self.BROADCAST_PREFIX}{message.channel}"
        payload = json.dumps(message.to_dict(), ensure_ascii=False)

        try:
            await self._redis.publish(redis_channel, payload)
        except Exception:
            logger.exception("Redis PUBLISH 失败: channel=%s", redis_channel)

        # 写入频道缓冲（供 HTTP 轮询和离线投递）
        if self._buffer:
            try:
                await self._buffer.push_to_channel(message.channel, message)
            except Exception:
                logger.exception("消息缓冲写入失败: channel=%s", message.channel)
