"""Redis PubSub 桥接模块。

桥接 Redis PubSub 与 WebSocket Manager，实现多实例部署时的消息广播。
支持模式订阅、健康监控和自动指数退避重连。
"""
import asyncio
import json
import logging
import uuid

import redis.asyncio as aioredis

from .models import PushMessage
from .protocols import ConnectionManagerProtocol

logger = logging.getLogger(__name__)


class PubSubBridge:
    """Redis PubSub 桥接器。

    通过 PSUBSCRIBE 模式订阅所有推送频道，
    将接收到的消息路由到本地 WebSocket 连接管理器。
    """

    BROADCAST_PATTERN = "push:broadcast:*"
    INSTANCE_KEY_PREFIX = "push:instance:"

    def __init__(
        self,
        redis_client: aioredis.Redis,
        websocket_manager: ConnectionManagerProtocol,
        *,
        instance_id: str = "",
        health_check_interval: int = 15,
        max_reconnect_delay: int = 30,
    ) -> None:
        self._redis = redis_client
        self._manager = websocket_manager
        self._instance_id = instance_id or uuid.uuid4().hex[:8]
        self._health_interval = health_check_interval
        self._max_reconnect_delay = max_reconnect_delay

        self._pubsub: aioredis.client.PubSub | None = None
        self._listen_task: asyncio.Task[None] | None = None
        self._health_task: asyncio.Task[None] | None = None
        self._healthy = False
        self._reconnect_attempts = 0

    @property
    def healthy(self) -> bool:
        """PubSub 连接是否健康。"""
        return self._healthy

    @property
    def instance_id(self) -> str:
        return self._instance_id

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """启动 PubSub 订阅和健康检查。"""
        await self._setup_pubsub()
        self._listen_task = asyncio.create_task(self._listen_loop())
        self._health_task = asyncio.create_task(self._health_check_loop())
        self._healthy = True
        logger.info(
            "PubSub 桥接器已启动 (instance=%s, pattern=%s)",
            self._instance_id,
            self.BROADCAST_PATTERN,
        )

    async def stop(self) -> None:
        """停止 PubSub 订阅和清理资源。"""
        self._healthy = False

        for task in (self._listen_task, self._health_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._listen_task = None
        self._health_task = None

        if self._pubsub:
            try:
                await self._pubsub.punsubscribe(self.BROADCAST_PATTERN)
                await self._pubsub.aclose()
            except Exception:
                pass
            self._pubsub = None

        logger.info("PubSub 桥接器已停止 (instance=%s)", self._instance_id)

    async def _setup_pubsub(self) -> None:
        """创建并配置 PubSub 订阅。"""
        self._pubsub = self._redis.pubsub()
        await self._pubsub.psubscribe(self.BROADCAST_PATTERN)

    # ------------------------------------------------------------------
    # 消息监听
    # ------------------------------------------------------------------

    async def _listen_loop(self) -> None:
        """监听 Redis PubSub 消息并转发到 WebSocket。"""
        while True:
            try:
                await self._listen_messages()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("PubSub 监听循环异常，尝试重连")
                self._healthy = False
                await self._reconnect()

    async def _listen_messages(self) -> None:
        """从 PubSub 读取消息并路由到管理器。"""
        if self._pubsub is None:
            return

        async for raw_message in self._pubsub.listen():
            msg_type = raw_message.get("type", "")

            # 模式订阅消息类型为 "pmessage"
            if msg_type != "pmessage":
                continue

            try:
                payload = json.loads(raw_message["data"])
                message = PushMessage.from_dict(payload)

                # 从 Redis 频道名提取实际频道
                # "push:broadcast:config:dev:auth-svc" → "config:dev:auth-svc"
                redis_channel = raw_message.get("channel", "")
                if isinstance(redis_channel, bytes):
                    redis_channel = redis_channel.decode("utf-8")
                actual_channel = redis_channel.removeprefix("push:broadcast:")

                await self._manager.broadcast(actual_channel, message)

            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("PubSub 消息解析失败: %s", exc)
                continue

    # ------------------------------------------------------------------
    # 发布（便捷方法）
    # ------------------------------------------------------------------

    async def publish(self, message: PushMessage) -> None:
        """发布消息到 Redis PubSub。

        Args:
            message: 推送消息
        """
        redis_channel = f"push:broadcast:{message.channel}"
        payload = json.dumps(message.to_dict(), ensure_ascii=False)
        await self._redis.publish(redis_channel, payload)

    # ------------------------------------------------------------------
    # 健康检查和重连
    # ------------------------------------------------------------------

    async def _health_check_loop(self) -> None:
        """定期检查 Redis 连接健康状态并注册实例心跳。"""
        while True:
            await asyncio.sleep(self._health_interval)
            try:
                # Redis ping
                await self._redis.ping()
                self._healthy = True
                self._reconnect_attempts = 0

                # 注册实例心跳
                instance_key = f"{self.INSTANCE_KEY_PREFIX}{self._instance_id}"
                await self._redis.set(instance_key, "alive", ex=60)

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.warning("Redis 健康检查失败 (instance=%s)", self._instance_id)
                self._healthy = False

    async def _reconnect(self) -> None:
        """指数退避重连。"""
        while True:
            self._reconnect_attempts += 1
            delay = min(2**self._reconnect_attempts, self._max_reconnect_delay)
            logger.info(
                "PubSub 重连尝试 #%d，%ds 后重试",
                self._reconnect_attempts,
                delay,
            )
            await asyncio.sleep(delay)

            try:
                # 清理旧连接
                if self._pubsub:
                    try:
                        await self._pubsub.aclose()
                    except Exception:
                        pass

                # 重新建立订阅
                await self._setup_pubsub()
                self._healthy = True
                self._reconnect_attempts = 0
                logger.info("PubSub 重连成功 (instance=%s)", self._instance_id)
                return

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("PubSub 重连失败")
                continue


