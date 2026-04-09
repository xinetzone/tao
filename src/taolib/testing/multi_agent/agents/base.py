"""智能体基类。

定义所有智能体必须实现的基础接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import UTC, datetime

from taolib.testing.multi_agent.errors import AgentError
from taolib.testing.multi_agent.models import (
    AgentDocument,
    AgentStatus,
    Message,
    MessageType,
    TaskDocument,
    TaskStatus,
)


class BaseAgent(ABC):
    """智能体基类。"""

    def __init__(self, document: AgentDocument):
        """初始化智能体。

        Args:
            document: 智能体文档
        """
        self._document = document
        self._status = document.status
        self._current_task: Optional[TaskDocument] = None
        self._message_queue: list[Message] = []

    @property
    def id(self) -> str:
        """获取智能体ID。"""
        return self._document.id

    @property
    def name(self) -> str:
        """获取智能体名称。"""
        return self._document.name

    @property
    def status(self) -> AgentStatus:
        """获取智能体状态。"""
        return self._status

    @property
    def document(self) -> AgentDocument:
        """获取智能体文档。"""
        return self._document

    @property
    def current_task(self) -> Optional[TaskDocument]:
        """获取当前任务。"""
        return self._current_task

    async def initialize(self) -> None:
        """初始化智能体。"""
        self._status = AgentStatus.IDLE
        self._document.status = AgentStatus.IDLE
        self._document.last_active_at = datetime.now(UTC)

    async def send_message(self, message: Message) -> None:
        """发送消息。

        Args:
            message: 要发送的消息
        """
        self._message_queue.append(message)
        await self._on_message_sent(message)

    async def receive_message(self, message: Message) -> None:
        """接收消息。

        Args:
            message: 接收到的消息
        """
        await self._handle_message(message)

    async def _on_message_sent(self, message: Message) -> None:
        """消息发送后的回调。

        Args:
            message: 发送的消息
        """
        pass

    @abstractmethod
    async def _handle_message(self, message: Message) -> None:
        """处理接收到的消息。

        Args:
            message: 接收到的消息
        """
        pass

    @abstractmethod
    async def execute_task(self, task: TaskDocument) -> None:
        """执行任务。

        Args:
            task: 要执行的任务
        """
        pass

    async def assign_task(self, task: TaskDocument) -> None:
        """分配任务给智能体。

        Args:
            task: 要分配的任务

        Raises:
            AgentError: 智能体忙碌
        """
        if self._status == AgentStatus.BUSY:
            raise AgentError(f"Agent {self.id} is busy")

        self._current_task = task
        self._status = AgentStatus.BUSY
        self._document.status = AgentStatus.BUSY
        self._document.current_task_id = task.id

        await self._on_task_assigned(task)

    async def _on_task_assigned(self, task: TaskDocument) -> None:
        """任务分配后的回调。

        Args:
            task: 分配的任务
        """
        pass

    async def complete_task(self, success: bool, result: Optional[Any] = None) -> None:
        """完成当前任务。

        Args:
            success: 是否成功
            result: 任务结果
        """
        if self._current_task is None:
            return

        task = self._current_task
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

        if success:
            self._document.completed_tasks += 1
        else:
            self._document.failed_tasks += 1

        await self._on_task_completed(task, success, result)

        self._current_task = None
        self._status = AgentStatus.IDLE
        self._document.status = AgentStatus.IDLE
        self._document.current_task_id = None
        self._document.last_active_at = datetime.now(UTC)

    async def _on_task_completed(
        self, task: TaskDocument, success: bool, result: Optional[Any]
    ) -> None:
        """任务完成后的回调。

        Args:
            task: 完成的任务
            success: 是否成功
            result: 任务结果
        """
        pass

    async def sleep(self) -> None:
        """使智能体休眠。"""
        if self._status == AgentStatus.BUSY:
            raise AgentError(f"Cannot sleep busy agent {self.id}")

        self._status = AgentStatus.SLEEPING
        self._document.status = AgentStatus.SLEEPING

    async def wake(self) -> None:
        """唤醒智能体。"""
        if self._status != AgentStatus.SLEEPING:
            return

        self._status = AgentStatus.IDLE
        self._document.status = AgentStatus.IDLE
        self._document.last_active_at = datetime.now(UTC)

    async def destroy(self) -> None:
        """销毁智能体。"""
        if self._current_task is not None:
            await self.complete_task(False, "Agent destroyed")

        self._status = AgentStatus.DESTROYED
        self._document.status = AgentStatus.DESTROYED

        await self._on_destroy()

    async def _on_destroy(self) -> None:
        """智能体销毁前的回调。"""
        pass
