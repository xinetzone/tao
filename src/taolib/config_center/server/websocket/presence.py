"""用户在线状态追踪模块。

基于 Redis HASH 实现的分布式在线状态管理，支持多实例部署。
"""
import json
import logging
from datetime import UTC, datetime

import redis.asyncio as aioredis

from .models import ConnectionStatus, UserPresence

logger = logging.getLogger(__name__)


class RedisPresenceTracker:
    """基于 Redis HASH 的在线状态追踪实现。"""

    def __init__(
        self,
        redis_client: aioredis.Redis,
        *,
        presence_ttl: int = 120,
    ) -> None:
        self._redis = redis_client
        self._ttl = presence_ttl

    def _key(self, user_id: str) -> str:
        return f"push:presence:{user_id}"

    async def set_online(self, user_id: str, instance_id: str) -> None:
        """标记用户在线。"""
        key = self._key(user_id)
        now = datetime.now(UTC).isoformat()

        # 获取当前实例列表
        raw_instances = await self._redis.hget(key, "instance_ids")
        instances: list[str] = json.loads(raw_instances) if raw_instances else []
        if instance_id not in instances:
            instances.append(instance_id)

        pipe = self._redis.pipeline()
        pipe.hset(
            key,
            mapping={
                "status": ConnectionStatus.ONLINE.value,
                "last_seen": now,
                "instance_ids": json.dumps(instances),
            },
        )
        pipe.hincrby(key, "connection_count", 1)
        pipe.expire(key, self._ttl)
        await pipe.execute()

    async def set_offline(self, user_id: str, instance_id: str) -> None:
        """标记用户离线（若该实例上无更多连接）。"""
        key = self._key(user_id)
        now = datetime.now(UTC).isoformat()

        # 更新实例列表
        raw_instances = await self._redis.hget(key, "instance_ids")
        instances: list[str] = json.loads(raw_instances) if raw_instances else []
        if instance_id in instances:
            instances.remove(instance_id)

        count = await self._redis.hincrby(key, "connection_count", -1)
        new_status = ConnectionStatus.ONLINE if count > 0 else ConnectionStatus.OFFLINE

        pipe = self._redis.pipeline()
        pipe.hset(
            key,
            mapping={
                "status": new_status.value,
                "last_seen": now,
                "instance_ids": json.dumps(instances),
            },
        )
        if count <= 0:
            # 离线后保留记录一段时间（用于查询 last_seen）
            pipe.expire(key, self._ttl * 5)
        else:
            pipe.expire(key, self._ttl)
        await pipe.execute()

    async def get_status(self, user_id: str) -> UserPresence | None:
        """获取用户在线状态。"""
        key = self._key(user_id)
        data = await self._redis.hgetall(key)
        if not data:
            return None
        return UserPresence(
            user_id=user_id,
            status=ConnectionStatus(data.get("status", "offline")),
            last_seen=datetime.fromisoformat(data["last_seen"])
            if "last_seen" in data
            else datetime.now(UTC),
            connection_count=int(data.get("connection_count", 0)),
            active_channels=json.loads(data["channels"]) if "channels" in data else [],
        )

    async def get_all_online(self) -> list[UserPresence]:
        """获取所有在线用户（通过 SCAN 避免阻塞）。"""
        result: list[UserPresence] = []
        cursor: int | bytes = 0
        while True:
            cursor, keys = await self._redis.scan(
                cursor, match="push:presence:*", count=100
            )
            for key in keys:
                data = await self._redis.hgetall(key)
                if data and data.get("status") == ConnectionStatus.ONLINE.value:
                    # 从 key 提取 user_id
                    user_id = str(key).split("push:presence:", 1)[-1]
                    result.append(
                        UserPresence(
                            user_id=user_id,
                            status=ConnectionStatus.ONLINE,
                            last_seen=datetime.fromisoformat(data["last_seen"])
                            if "last_seen" in data
                            else datetime.now(UTC),
                            connection_count=int(data.get("connection_count", 0)),
                            active_channels=json.loads(data["channels"])
                            if "channels" in data
                            else [],
                        )
                    )
            if cursor == 0:
                break
        return result

    async def refresh(self, user_id: str) -> None:
        """刷新在线状态 TTL（心跳时调用）。"""
        key = self._key(user_id)
        pipe = self._redis.pipeline()
        pipe.hset(key, "last_seen", datetime.now(UTC).isoformat())
        pipe.expire(key, self._ttl)
        await pipe.execute()


class InMemoryPresenceTracker:
    """内存在线状态追踪实现（用于测试）。"""

    def __init__(self) -> None:
        self._state: dict[str, UserPresence] = {}
        self._instances: dict[str, set[str]] = {}  # user_id -> instance_ids

    async def set_online(self, user_id: str, instance_id: str) -> None:
        if user_id not in self._instances:
            self._instances[user_id] = set()
        self._instances[user_id].add(instance_id)

        if user_id in self._state:
            self._state[user_id].status = ConnectionStatus.ONLINE
            self._state[user_id].connection_count += 1
            self._state[user_id].last_seen = datetime.now(UTC)
        else:
            self._state[user_id] = UserPresence(
                user_id=user_id,
                status=ConnectionStatus.ONLINE,
                connection_count=1,
            )

    async def set_offline(self, user_id: str, instance_id: str) -> None:
        if user_id in self._instances:
            self._instances[user_id].discard(instance_id)

        if user_id in self._state:
            self._state[user_id].connection_count -= 1
            self._state[user_id].last_seen = datetime.now(UTC)
            if self._state[user_id].connection_count <= 0:
                self._state[user_id].status = ConnectionStatus.OFFLINE
                self._state[user_id].connection_count = 0

    async def get_status(self, user_id: str) -> UserPresence | None:
        return self._state.get(user_id)

    async def get_all_online(self) -> list[UserPresence]:
        return [p for p in self._state.values() if p.status == ConnectionStatus.ONLINE]

    async def refresh(self, user_id: str) -> None:
        if user_id in self._state:
            self._state[user_id].last_seen = datetime.now(UTC)
