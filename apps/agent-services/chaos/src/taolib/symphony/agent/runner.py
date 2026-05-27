"""智能体运行器。

编排单个 Issue 的完整运行流程：
工作区创建 → before_run 钩子 → 启动 app-server →
轮次循环 → 停止 → after_run 钩子。
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .appserver import AppServerClient, AppServerError
from .events import AppServerEvent, TurnResult
from .transport import AgentTransport

__all__ = ["AgentRunner", "IssueInfo", "RunnerConfig"]

logger = logging.getLogger(__name__)


class IssueInfo(Protocol):
    """Issue 信息的协议接口。"""

    @property
    def identifier(self) -> str: ...

    @property
    def title(self) -> str: ...

    @property
    def status(self) -> str: ...

    def model_dump(self) -> dict[str, Any]: ...


@dataclass
class RunnerConfig:
    """运行器配置。"""

    command: str = "codex"
    """启动 app-server 的命令。"""

    max_turns: int = 10
    """单次运行最大轮次数。"""

    approval_policy: str = "never"
    """审批策略。"""

    stall_timeout_ms: int = 300_000
    """停滞检测超时（毫秒）。"""

    before_run: str | None = None
    """运行前钩子脚本。"""

    after_run: str | None = None
    """运行后钩子脚本。"""

    hook_timeout_ms: int = 30_000
    """钩子超时（毫秒）。"""


class AgentRunner:
    """智能体运行器。

    编排单个 Issue 的完整运行生命周期：
    创建工作区 → 执行 before_run 钩子 → 启动 app-server →
    轮次循环 → 停止 app-server → 执行 after_run 钩子。
    """

    def __init__(
        self,
        transport: AgentTransport,
        config: RunnerConfig | None = None,
    ) -> None:
        self._transport = transport
        self._config = config or RunnerConfig()
        self._client = AppServerClient(transport)

    @property
    def client(self) -> AppServerClient:
        """底层 AppServer 客户端。"""
        return self._client

    async def run_attempt(
        self,
        issue: IssueInfo,
        attempt: int,
        workspace_path: str,
        *,
        build_prompt: Callable[[IssueInfo, int, int], str],
        check_issue_status: Callable[
            [IssueInfo], asyncio.Coroutine[Any, Any, str | None]
        ]
        | None = None,
        on_event: Callable[[AppServerEvent], None] | None = None,
    ) -> TurnResult:
        """执行一次完整的运行尝试。

        流程：
        1. 执行 before_run 钩子
        2. 启动 app-server 进程
        3. 初始化会话
        4. 轮次循环（构建提示词 → 运行轮次 → 检查状态）
        5. 停止 app-server
        6. 执行 after_run 钩子

        Args:
            issue: Issue 信息。
            attempt: 尝试序号（从 0 开始）。
            workspace_path: 工作区路径。
            build_prompt: 提示词构建回调。
            check_issue_status: Issue 状态检查回调（可选）。
            on_event: 事件回调（可选）。

        Returns:
            最终轮次结果。
        """
        session_id: str | None = None
        last_result: TurnResult = TurnResult(success=False, error="未执行任何轮次")

        try:
            # 1. before_run 钩子
            if self._config.before_run:
                await self._transport.run_hook(
                    self._config.before_run,
                    workspace_path,
                    self._config.hook_timeout_ms,
                )

            # 2. 启动 app-server
            await self._client.start(
                self._config.command,
                workspace_path,
                approval_policy=self._config.approval_policy,
            )

            # 3. 初始化会话
            session_id = await self._client.initialize_session()

            # 4. 轮次循环
            for turn in range(self._config.max_turns):
                prompt = build_prompt(issue, turn + 1, attempt)
                logger.info(
                    "Issue %s: 轮次 %d/%d",
                    issue.identifier,
                    turn + 1,
                    self._config.max_turns,
                )

                last_result = await self._client.run_turn(
                    session_id, prompt, on_event=on_event
                )

                if not last_result.success:
                    logger.warning(
                        "Issue %s: 轮次 %d 失败: %s",
                        issue.identifier,
                        turn + 1,
                        last_result.error,
                    )
                    break

                # 检查 Issue 状态是否已变为终态
                if check_issue_status is not None:
                    terminal_status = await check_issue_status(issue)
                    if terminal_status is not None:
                        logger.info(
                            "Issue %s: 状态变为 %s，停止运行",
                            issue.identifier,
                            terminal_status,
                        )
                        last_result = TurnResult(success=True)
                        break

        except AppServerError as e:
            logger.error("Issue %s: AppServer 错误: %s", issue.identifier, e)
            last_result = TurnResult(success=False, error=str(e))
        except TimeoutError:
            logger.error("Issue %s: 运行超时", issue.identifier)
            last_result = TurnResult(success=False, error="运行超时")
        except Exception as e:
            logger.error("Issue %s: 未预期的错误: %s", issue.identifier, e)
            last_result = TurnResult(success=False, error=str(e))
        finally:
            # 5. 停止 app-server
            if session_id is not None:
                await self._client.stop(session_id)

            # 6. after_run 钩子
            if self._config.after_run:
                try:
                    await self._transport.run_hook(
                        self._config.after_run,
                        workspace_path,
                        self._config.hook_timeout_ms,
                    )
                except Exception as e:
                    logger.warning("after_run 钩子失败: %s", e)

        return last_result
