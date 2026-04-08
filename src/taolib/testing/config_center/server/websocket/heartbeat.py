"""WebSocket 心跳检测模块。

独立的心跳监控器，定期向所有连接发送 ping 并检测僵尸连接。
"""
import asyncio
import json
import logging
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any

from .models import ConnectionInfo

logger = logging.getLogger(__name__)

# 回调类型：接收 websocket 对象，异步执行清理
OnStaleCallback = Callable[[Any], Coroutine[Any, Any, None]]


class HeartbeatMonitor:
    """心跳监控器。

    定期向所有 WebSocket 连接发送 ping 消息，
    检测并回调清理超过阈值未响应的僵尸连接。
    """

    def __init__(
        self,
        *,
        interval: int = 30,
        timeout: int = 70,
        on_stale: OnStaleCallback | None = None,
    ) -> None:
        """初始化心跳监控器。

        Args:
            interval: 心跳间隔（秒）
            timeout: 超过此时间无 pong 视为僵尸连接（秒）
            on_stale: 僵尸连接回调函数
        """
        self._interval = interval
        self._timeout = timeout
        self._on_stale = on_stale
        self._task: asyncio.Task[None] | None = None

    async def start(
        self,
        get_connections: Callable[[], dict[Any, ConnectionInfo]],
    ) -> None:
        """启动心跳循环。

        Args:
            get_connections: 获取当前连接字典的回调
        """
        self._get_connections = get_connections
        self._task = asyncio.create_task(self._run(get_connections))

    async def stop(self) -> None:
        """停止心跳循环。"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(
        self,
        get_connections: Callable[[], dict[Any, ConnectionInfo]],
    ) -> None:
        """心跳主循环。"""
        while True:
            await asyncio.sleep(self._interval)
            try:
                await self._check_all(get_connections())
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("心跳检测循环异常")

    async def _check_all(self, connections: dict[Any, ConnectionInfo]) -> None:
        """检查所有连接并发送 ping / 清理僵尸。"""
        now = datetime.now(UTC)
        stale: list[Any] = []
        ping_tasks: list[Coroutine[Any, Any, None]] = []

        for ws, info in list(connections.items()):
            elapsed = (now - info.last_heartbeat).total_seconds()
            if elapsed > self._timeout:
                stale.append(ws)
            else:
                ping_tasks.append(self._send_ping(ws, now))

        # 批量发送 ping（限制并发防止事件循环饱和）
        if ping_tasks:
            await asyncio.gather(*ping_tasks, return_exceptions=True)

        # 清理僵尸连接
        for ws in stale:
            info = connections.get(ws)
            user_id = info.user_id if info else "unknown"
            logger.warning("僵尸连接检测: user_id=%s, 将断开连接", user_id)
            if self._on_stale:
                try:
                    await self._on_stale(ws)
                except Exception:
                    logger.exception("僵尸连接清理回调失败: user_id=%s", user_id)

    @staticmethod
    async def _send_ping(ws: Any, now: datetime) -> None:
        """向单个连接发送 ping 消息。"""
        try:
            ping_msg = json.dumps(
                {
                    "type": "ping",
                    "timestamp": now.isoformat(),
                }
            )
            await ws.send_text(ping_msg)
        except Exception:
            pass  # 发送失败将在下次检查时被检测为僵尸


