"""任务处理器注册表。

提供装饰器式的任务处理器注册和查找功能。
"""

import inspect
from collections.abc import Callable
from typing import Any


class TaskHandlerRegistry:
    """任务处理器注册表。

    管理 task_type → handler 的映射关系。
    支持同步和异步处理器。

    使用示例::

        registry = TaskHandlerRegistry()

        @registry.handler("send_email")
        async def handle_send_email(params: dict) -> dict:
            # 发送邮件逻辑
            return {"sent": True}
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(self, task_type: str, handler: Callable[..., Any]) -> None:
        """注册任务处理器。

        Args:
            task_type: 任务类型
            handler: 处理器函数（同步或异步）
        """
        self._handlers[task_type] = handler

    def get(self, task_type: str) -> Callable[..., Any] | None:
        """获取任务处理器。

        Args:
            task_type: 任务类型

        Returns:
            处理器函数，未注册返回 None
        """
        return self._handlers.get(task_type)

    def has(self, task_type: str) -> bool:
        """检查是否已注册指定类型的处理器。

        Args:
            task_type: 任务类型

        Returns:
            是否已注册
        """
        return task_type in self._handlers

    def list_types(self) -> list[str]:
        """列出所有已注册的任务类型。

        Returns:
            任务类型列表
        """
        return list(self._handlers.keys())

    def handler(self, task_type: str) -> Callable:
        """装饰器：注册任务处理器。

        Args:
            task_type: 任务类型

        Returns:
            装饰器函数

        使用示例::

            @registry.handler("generate_report")
            async def handle_report(params: dict) -> dict:
                ...
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register(task_type, func)
            return func

        return decorator

    @staticmethod
    def is_async_handler(handler: Callable[..., Any]) -> bool:
        """判断处理器是否为异步函数。

        Args:
            handler: 处理器函数

        Returns:
            是否为异步函数
        """
        return inspect.iscoroutinefunction(handler)


# 模块级默认注册表
_default_registry = TaskHandlerRegistry()


def task_handler(task_type: str) -> Callable:
    """装饰器：在默认注册表中注册任务处理器。

    Args:
        task_type: 任务类型

    Returns:
        装饰器函数

    使用示例::

        @task_handler("send_email")
        async def handle_send_email(params: dict) -> dict:
            await send_email(params["to"], params["subject"])
            return {"sent": True}
    """
    return _default_registry.handler(task_type)


def get_default_registry() -> TaskHandlerRegistry:
    """获取默认注册表。

    Returns:
        默认 TaskHandlerRegistry 实例
    """
    return _default_registry


