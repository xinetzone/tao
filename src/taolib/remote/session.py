"""远端 shell 上下文管理工具。"""
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from typing import ContextManager, Protocol


class SupportsPrefix(Protocol):
    def prefix(self, command: str) -> ContextManager[None]: ...


@contextmanager
def remote_prefixes(connection: SupportsPrefix, *prefix_cmds: str) -> Iterator[None]:
    """在同一个命令执行上下文中叠加多个 prefix。"""
    with ExitStack() as stack:
        for cmd in prefix_cmds:
            normalized = cmd.strip()
            if normalized:
                stack.enter_context(connection.prefix(normalized))
        yield

