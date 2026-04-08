"""WebSocket 连接管理器模块。

管理所有 WebSocket 连接、频道订阅、消息投递、心跳检测和 ACK 重传。
支持数万级并发连接和分布式多实例部署。
"""
import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket

from .heartbeat import HeartbeatMonitor
from .models import (
    ConnectionInfo,
    ConnectionStats,
    ConnectionStatus,
    MessageType,
    PushMessage,
    UserPresence,
)
from .protocols import MessageBufferProtocol, PresenceTrackerProtocol

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """高性能 WebSocket 连接管理器。

    核心职责：
    - 连接池管理：accept / disconnect / 多设备支持
    - 频道订阅：subscribe / unsubscribe / broadcast
    - 消息投递：优先级排序、ACK 追踪、超时重传
    - 心跳检测：通过 HeartbeatMonitor 检测僵尸连接
    - 在线状态：通过 PresenceTracker 跨实例同步
    - 离线缓冲：通过 MessageBuffer 保证 at-least-once 投递
    - 统计监控：连接数 / 消息数 / ACK 统计
    """

    def __init__(
        self,
        presence_tracker: PresenceTrackerProtocol | None = None,
        message_buffer: MessageBufferProtocol | None = None,
        *,
        instance_id: str = "",
        heartbeat_interval: int = 30,
        heartbeat_timeout: int = 70,
        ack_timeout: int = 10,
        max_retries: int = 3,
    ) -> None:
        # 连接状态
        self._connections: dict[WebSocket, ConnectionInfo] = {}
        self._subscriptions: dict[str, set[WebSocket]] = {}
        self._user_connections: dict[str, set[WebSocket]] = {}

        # 依赖
        self._presence = presence_tracker
        self._buffer = message_buffer
        self._instance_id = instance_id

        # 配置
        self._ack_timeout = ack_timeout
        self._max_retries = max_retries

        # 统计
        self._stats = ConnectionStats()
        self._started_at = datetime.now(UTC)

        # 后台任务
        self._heartbeat = HeartbeatMonitor(
            interval=heartbeat_interval,
            timeout=heartbeat_timeout,
            on_stale=self._handle_stale_connection,
        )
        self._ack_task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """启动心跳检测和 ACK 清理后台任务。"""
        await self._heartbeat.start(lambda: self._connections)
        self._ack_task = asyncio.create_task(self._run_ack_cleanup_loop())
        logger.info("WebSocket 连接管理器已启动 (instance=%s)", self._instance_id)

    async def stop(self) -> None:
        """优雅关闭：停止后台任务，断开所有连接。"""
        await self._heartbeat.stop()
        if self._ack_task:
            self._ack_task.cancel()
            try:
                await self._ack_task
            except asyncio.CancelledError:
                pass
            self._ack_task = None

        # 关闭所有连接
        for ws in list(self._connections):
            try:
                await ws.close(code=1001, reason="服务器关闭")
            except Exception:
                pass
            self.disconnect(ws)

        logger.info("WebSocket 连接管理器已关闭")

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        environments: list[str] | None = None,
        services: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """接受 WebSocket 连接并初始化。

        Args:
            websocket: WebSocket 连接
            user_id: 用户 ID
            environments: 订阅的环境列表
            services: 订阅的服务列表
            metadata: 额外上下文信息
        """
        await websocket.accept()

        info = ConnectionInfo(
            user_id=user_id,
            metadata=metadata or {},
        )

        async with self._lock:
            self._connections[websocket] = info
            # 多设备：同一用户可有多个连接
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(websocket)

        # 自动订阅匹配的频道
        environments = environments or []
        services = services or []
        for env in environments:
            for svc in services:
                channel = f"config:{env}:{svc}"
                await self.subscribe(websocket, channel)

        # 更新在线状态
        if self._presence:
            await self._presence.set_online(user_id, self._instance_id)

        # 投递离线消息
        if self._buffer:
            offline_msgs = await self._buffer.flush(user_id)
            for msg in offline_msgs:
                await self._deliver_message(websocket, info, msg)

        # 更新统计
        self._stats.total_connections += 1
        self._stats.active_connections = len(self._connections)

        logger.info(
            "WebSocket 连接建立: user_id=%s, channels=%d",
            user_id,
            len(info.channels),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """断开 WebSocket 连接并清理所有关联状态。"""
        info = self._connections.pop(websocket, None)
        if info is None:
            return

        # 清理频道订阅
        for channel in list(info.channels):
            if channel in self._subscriptions:
                self._subscriptions[channel].discard(websocket)
                if not self._subscriptions[channel]:
                    del self._subscriptions[channel]

        # 清理用户连接映射
        user_id = info.user_id
        if user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        # 将 pending ACK 消息转入离线缓冲
        if self._buffer and info.pending_acks:
            for msg in info.pending_acks.values():
                asyncio.create_task(self._buffer.push(user_id, msg))

        # 更新在线状态（仅当该用户无更多连接时）
        if user_id not in self._user_connections and self._presence:
            asyncio.create_task(self._presence.set_offline(user_id, self._instance_id))

        # 更新统计
        self._stats.active_connections = len(self._connections)

        logger.info("WebSocket 连接断开: user_id=%s", user_id)

    # ------------------------------------------------------------------
    # 频道订阅
    # ------------------------------------------------------------------

    async def subscribe(self, websocket: WebSocket, channel: str) -> None:
        """订阅频道。"""
        info = self._connections.get(websocket)
        if info is None:
            return
        if channel not in self._subscriptions:
            self._subscriptions[channel] = set()
        self._subscriptions[channel].add(websocket)
        info.channels.add(channel)

    def unsubscribe(self, websocket: WebSocket, channel: str) -> None:
        """取消订阅频道。"""
        info = self._connections.get(websocket)
        if info:
            info.channels.discard(channel)
        if channel in self._subscriptions:
            self._subscriptions[channel].discard(websocket)
            if not self._subscriptions[channel]:
                del self._subscriptions[channel]

    # ------------------------------------------------------------------
    # 消息投递
    # ------------------------------------------------------------------

    async def broadcast(self, channel: str, message: PushMessage) -> int:
        """向频道所有订阅者广播消息。

        Returns:
            成功投递的连接数
        """
        subscribers = self._subscriptions.get(channel)
        if not subscribers:
            return 0

        # 对订阅者集合做快照，避免迭代时修改
        ws_list = list(subscribers)
        delivered = 0
        disconnected: list[WebSocket] = []

        for ws in ws_list:
            info = self._connections.get(ws)
            if info is None:
                disconnected.append(ws)
                continue
            success = await self._deliver_message(ws, info, message)
            if success:
                delivered += 1
            else:
                disconnected.append(ws)

        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws)

        return delivered

    async def send_to_user(self, user_id: str, message: PushMessage) -> int:
        """向特定用户的所有连接发送消息。

        若用户离线，消息存入离线缓冲。

        Returns:
            成功投递的连接数
        """
        ws_set = self._user_connections.get(user_id)
        if not ws_set:
            # 用户离线，缓冲消息
            if self._buffer:
                await self._buffer.push(user_id, message)
            return 0

        delivered = 0
        for ws in list(ws_set):
            info = self._connections.get(ws)
            if info and await self._deliver_message(ws, info, message):
                delivered += 1
        return delivered

    async def send_personal(
        self, websocket: WebSocket, message: dict[str, Any]
    ) -> None:
        """发送个人消息（向后兼容接口）。"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def _deliver_message(
        self,
        ws: WebSocket,
        info: ConnectionInfo,
        msg: PushMessage,
    ) -> bool:
        """原子消息投递：发送 + ACK 追踪。"""
        try:
            message_json = json.dumps(msg.to_dict(), ensure_ascii=False)
            await ws.send_text(message_json)
        except Exception:
            self._stats.total_messages_failed += 1
            return False

        self._stats.total_messages_sent += 1

        # ACK 追踪
        if msg.requires_ack:
            info.pending_acks[msg.id] = msg

        return True

    # ------------------------------------------------------------------
    # 客户端消息处理
    # ------------------------------------------------------------------

    async def handle_client_message(self, websocket: WebSocket, raw_data: str) -> None:
        """处理来自客户端的消息。

        支持的消息类型：ack, pong, subscribe, unsubscribe
        """
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            await self._send_error(websocket, "无效的 JSON 格式")
            return

        msg_type = data.get("type", "")

        if msg_type == MessageType.ACK:
            self._handle_ack(websocket, data.get("message_id", ""))
        elif msg_type == MessageType.PONG:
            info = self._connections.get(websocket)
            if info:
                info.last_heartbeat = datetime.now(UTC)
        elif msg_type == MessageType.SUBSCRIBE:
            channel = data.get("channel", "")
            if channel:
                await self.subscribe(websocket, channel)
        elif msg_type == MessageType.UNSUBSCRIBE:
            channel = data.get("channel", "")
            if channel:
                self.unsubscribe(websocket, channel)
        else:
            await self._send_error(websocket, f"未知消息类型: {msg_type}")

    def _handle_ack(self, websocket: WebSocket, message_id: str) -> None:
        """处理客户端消息确认。"""
        info = self._connections.get(websocket)
        if info and message_id in info.pending_acks:
            del info.pending_acks[message_id]
            self._stats.total_acks_received += 1

    @staticmethod
    async def _send_error(websocket: WebSocket, detail: str) -> None:
        """向客户端发送错误消息。"""
        try:
            await websocket.send_json({"type": "error", "detail": detail})
        except Exception:
            pass

    # ------------------------------------------------------------------
    # ACK 超时清理
    # ------------------------------------------------------------------

    async def _run_ack_cleanup_loop(self) -> None:
        """定期检查 ACK 超时，执行重传或离线缓冲。"""
        while True:
            await asyncio.sleep(5)
            try:
                await self._cleanup_pending_acks()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("ACK 清理循环异常")

    async def _cleanup_pending_acks(self) -> None:
        """扫描所有连接的 pending_acks，处理超时消息。"""
        now = datetime.now(UTC)

        for ws, info in list(self._connections.items()):
            expired: list[str] = []
            for msg_id, msg in info.pending_acks.items():
                elapsed = (now - msg.timestamp).total_seconds()
                if elapsed > self._ack_timeout:
                    expired.append(msg_id)

            for msg_id in expired:
                msg = info.pending_acks.pop(msg_id)
                if msg.retry_count < self._max_retries:
                    # 重传
                    msg.retry_count += 1
                    msg.timestamp = now  # 重置超时计时
                    await self._deliver_message(ws, info, msg)
                    logger.debug(
                        "消息重传: msg_id=%s, retry=%d/%d",
                        msg_id,
                        msg.retry_count,
                        msg.max_retries,
                    )
                else:
                    # 超过最大重试，转入离线缓冲
                    self._stats.total_acks_timeout += 1
                    if self._buffer:
                        await self._buffer.push(info.user_id, msg)
                    logger.warning(
                        "消息 ACK 超时放弃: msg_id=%s, user=%s",
                        msg_id,
                        info.user_id,
                    )

    # ------------------------------------------------------------------
    # 僵尸连接处理
    # ------------------------------------------------------------------

    async def _handle_stale_connection(self, websocket: WebSocket) -> None:
        """处理心跳超时的僵尸连接。"""
        try:
            await websocket.close(code=1001, reason="心跳超时")
        except Exception:
            pass
        self.disconnect(websocket)

    # ------------------------------------------------------------------
    # 统计和监控
    # ------------------------------------------------------------------

    def get_stats(self) -> ConnectionStats:
        """获取当前连接统计快照。"""
        self._stats.active_connections = len(self._connections)
        self._stats.total_channels = len(self._subscriptions)
        self._stats.uptime_seconds = (
            datetime.now(UTC) - self._started_at
        ).total_seconds()
        self._stats.online_users = len(self._user_connections)
        return self._stats

    def get_user_presence(self, user_id: str) -> UserPresence | None:
        """获取用户本地连接的在线状态。"""
        ws_set = self._user_connections.get(user_id)
        if not ws_set:
            return None
        channels: list[str] = []
        for ws in ws_set:
            info = self._connections.get(ws)
            if info:
                channels.extend(info.channels)
        return UserPresence(
            user_id=user_id,
            status=ConnectionStatus.ONLINE,
            connection_count=len(ws_set),
            active_channels=list(set(channels)),
        )


# 全局默认管理器实例（轻量级回退，生产环境使用 app.state.push_manager）
manager = WebSocketConnectionManager()


