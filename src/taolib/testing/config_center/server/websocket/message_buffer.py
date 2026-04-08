"""离线消息缓冲模块。

基于 Redis LIST 实现的消息缓冲，支持用户离线消息暂存和频道消息轮询。
"""
import json
import logging
from collections import deque
from datetime import datetime

import redis.asyncio as aioredis

from .models import PushMessage

logger = logging.getLogger(__name__)


class RedisMessageBuffer:
    """基于 Redis LIST 的消息缓冲实现。"""

    def __init__(
        self,
        redis_client: aioredis.Redis,
        *,
        max_user_messages: int = 1000,
        max_channel_messages: int = 5000,
        user_buffer_ttl: int = 86400,
        channel_buffer_ttl: int = 3600,
    ) -> None:
        self._redis = redis_client
        self._max_user = max_user_messages
        self._max_channel = max_channel_messages
        self._user_ttl = user_buffer_ttl
        self._channel_ttl = channel_buffer_ttl

    def _user_key(self, user_id: str) -> str:
        return f"push:buffer:{user_id}"

    def _channel_key(self, channel: str) -> str:
        return f"push:channel_buf:{channel}"

    async def push(self, user_id: str, message: PushMessage) -> None:
        """缓冲一条用户离线消息。"""
        key = self._user_key(user_id)
        data = json.dumps(message.to_dict(), ensure_ascii=False)
        pipe = self._redis.pipeline()
        pipe.lpush(key, data)
        pipe.ltrim(key, 0, self._max_user - 1)
        pipe.expire(key, self._user_ttl)
        await pipe.execute()

    async def push_to_channel(self, channel: str, message: PushMessage) -> None:
        """缓冲一条频道消息（供 HTTP 轮询使用）。"""
        key = self._channel_key(channel)
        data = json.dumps(message.to_dict(), ensure_ascii=False)
        pipe = self._redis.pipeline()
        pipe.lpush(key, data)
        pipe.ltrim(key, 0, self._max_channel - 1)
        pipe.expire(key, self._channel_ttl)
        await pipe.execute()

    async def flush(self, user_id: str, limit: int = 100) -> list[PushMessage]:
        """取出并清除用户的离线消息。

        使用 LRANGE + LTRIM 保证原子性读取。
        返回消息按时间正序排列（最旧的在前）。
        """
        key = self._user_key(user_id)
        pipe = self._redis.pipeline()
        pipe.lrange(key, 0, limit - 1)
        pipe.ltrim(key, limit, -1)
        results = await pipe.execute()

        raw_messages: list[str] = results[0] or []
        messages: list[PushMessage] = []
        for raw in reversed(raw_messages):  # LPUSH 是头部插入，reversed 得到时间正序
            try:
                messages.append(PushMessage.from_dict(json.loads(raw)))
            except (json.JSONDecodeError, KeyError):
                logger.warning("跳过无法解析的离线消息: %s", raw[:100])
        return messages

    async def get_recent(
        self,
        channel: str,
        since: datetime,
        limit: int = 50,
    ) -> list[PushMessage]:
        """获取频道自指定时间以来的消息。"""
        key = self._channel_key(channel)
        raw_messages: list[str] = await self._redis.lrange(key, 0, limit * 2)

        messages: list[PushMessage] = []
        for raw in reversed(raw_messages):
            try:
                msg = PushMessage.from_dict(json.loads(raw))
                if msg.timestamp >= since:
                    messages.append(msg)
                    if len(messages) >= limit:
                        break
            except (json.JSONDecodeError, KeyError):
                continue
        return messages


class InMemoryMessageBuffer:
    """内存消息缓冲实现（用于测试）。"""

    def __init__(self, *, max_messages: int = 1000) -> None:
        self._user_buffers: dict[str, deque[PushMessage]] = {}
        self._channel_buffers: dict[str, deque[PushMessage]] = {}
        self._max = max_messages

    async def push(self, user_id: str, message: PushMessage) -> None:
        if user_id not in self._user_buffers:
            self._user_buffers[user_id] = deque(maxlen=self._max)
        self._user_buffers[user_id].append(message)

    async def push_to_channel(self, channel: str, message: PushMessage) -> None:
        if channel not in self._channel_buffers:
            self._channel_buffers[channel] = deque(maxlen=self._max)
        self._channel_buffers[channel].append(message)

    async def flush(self, user_id: str, limit: int = 100) -> list[PushMessage]:
        buf = self._user_buffers.get(user_id)
        if not buf:
            return []
        messages: list[PushMessage] = []
        while buf and len(messages) < limit:
            messages.append(buf.popleft())
        return messages

    async def get_recent(
        self,
        channel: str,
        since: datetime,
        limit: int = 50,
    ) -> list[PushMessage]:
        buf = self._channel_buffers.get(channel)
        if not buf:
            return []
        return [m for m in buf if m.timestamp >= since][:limit]


