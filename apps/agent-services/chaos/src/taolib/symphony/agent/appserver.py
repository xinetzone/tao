"""Codex app-server stdio 客户端。

通过 JSON 行协议与 Codex app-server 子进程通信，
支持会话初始化、轮次运行、流式事件处理和会话停止。
"""

import json
import logging
from collections.abc import Callable
from typing import Any

from ..errors import AgentError
from .events import AppServerEvent, TokenAccounting, TurnResult, parse_event
from .transport import AgentProcess, AgentTransport

__all__ = ["AppServerClient", "AppServerError"]

logger = logging.getLogger(__name__)


class AppServerError(AgentError):
    """AppServer 通信错误。"""


class AppServerClient:
    """Codex app-server stdio 客户端。

    通过 stdin/stdout JSON 行协议与 Codex app-server 子进程通信，
    实现会话初始化、轮次运行、流式事件解析等核心交互。
    """

    def __init__(self, transport: AgentTransport) -> None:
        self._transport = transport
        self._process: AgentProcess | None = None
        self._token_accounting = TokenAccounting()
        self._session_id: str | None = None

    @property
    def token_accounting(self) -> TokenAccounting:
        """令牌使用追踪器。"""
        return self._token_accounting

    @property
    def session_id(self) -> str | None:
        """当前会话 ID。"""
        return self._session_id

    async def start(
        self,
        command: str,
        workspace_path: str,
        *,
        approval_policy: str = "never",
        sandbox_policy: dict | None = None,
    ) -> None:
        """启动 app-server 进程。

        Args:
            command: 启动 app-server 的命令。
            workspace_path: 工作区路径（作为 cwd）。
            approval_policy: 审批策略（默认 never）。
            sandbox_policy: 沙箱策略配置。
        """
        self._process = await self._transport.start_process(command, workspace_path)
        logger.info("AppServer 进程已启动: cwd=%s", workspace_path)

    async def initialize_session(self, config: dict[str, Any] | None = None) -> str:
        """发送 initialize 消息，返回 session_id。

        Args:
            config: 初始化配置（工具定义、审批策略等）。

        Returns:
            会话 ID 字符串。

        Raises:
            AppServerError: 初始化失败或通信错误。
        """
        msg: dict[str, Any] = {"type": "initialize"}
        if config:
            msg.update(config)
        await self._send(msg)

        resp = await self._recv()
        if resp.get("type") != "session_started":
            raise AppServerError(
                f"初始化失败: 期望 session_started，收到 {resp.get('type')}"
            )

        self._session_id = resp["session_id"]
        logger.info("AppServer 会话已初始化: %s", self._session_id)
        return self._session_id

    async def run_turn(
        self,
        session_id: str,
        prompt: str,
        on_event: Callable[[AppServerEvent], None] | None = None,
    ) -> TurnResult:
        """运行一个轮次，流式处理事件。

        Args:
            session_id: 会话 ID。
            prompt: 轮次提示词。
            on_event: 事件回调函数。

        Returns:
            轮次执行结果。

        Raises:
            AppServerError: 通信错误。
        """
        await self._send({
            "type": "start_turn",
            "session_id": session_id,
            "prompt": prompt,
        })

        turn_tokens = 0
        async for event in self._stream_events():
            if on_event is not None:
                on_event(event)

            # 跟踪令牌使用
            if event.type == "token_usage":
                turn_tokens = event.data.get("total_tokens", turn_tokens)

            if event.type == "turn_complete":
                self._token_accounting.record(turn_tokens)
                return TurnResult(success=True, token_usage=turn_tokens)

            if event.type == "error":
                error_msg = event.data.get("message", "未知错误")
                self._token_accounting.record(turn_tokens)
                return TurnResult(success=False, token_usage=turn_tokens, error=error_msg)

        # 流意外结束
        self._token_accounting.record(turn_tokens)
        return TurnResult(success=False, token_usage=turn_tokens, error="事件流意外结束")

    async def stop(self, session_id: str) -> None:
        """停止会话并关闭进程。

        Args:
            session_id: 会话 ID。
        """
        if self._session_id is not None:
            try:
                await self._send({"type": "stop_session", "session_id": session_id})
            except Exception:
                logger.warning("发送 stop_session 失败，强制关闭")
            self._session_id = None

        if self._process is not None:
            try:
                self._process.stdin.close()
                await self._process.stdin.wait_closed()
            except Exception:
                pass
            self._process = None
            logger.info("AppServer 进程已关闭")

    async def _send(self, msg: dict) -> None:
        """发送 JSON 行。"""
        if self._process is None:
            raise AppServerError("进程未启动")
        line = json.dumps(msg, ensure_ascii=False) + "\n"
        self._process.stdin.write(line.encode("utf-8"))
        await self._process.stdin.drain()

    async def _recv(self) -> dict:
        """接收一行 JSON。"""
        if self._process is None:
            raise AppServerError("进程未启动")
        line_bytes = await self._process.stdout.readline()
        if not line_bytes:
            raise AppServerError("进程已关闭连接")
        line = line_bytes.decode("utf-8").strip()
        if not line:
            raise AppServerError("收到空行")
        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            raise AppServerError(f"JSON 解析失败: {e}") from e

    async def _stream_events(self):
        """异步迭代接收事件。"""
        while True:
            try:
                raw = await self._recv()
            except AppServerError:
                return
            event = parse_event(raw)
            yield event
            if event.type in ("turn_complete", "error", "session_ended"):
                return
