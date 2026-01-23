"""连接抽象与工厂函数（默认按需导入 fabric）。"""
from collections.abc import Callable
from functools import lru_cache
from typing import Any, ContextManager, Protocol

from .errors import RemoteDependencyError


class RunResult(Protocol):
    stdout: str
    ok: bool


class ConnectionLike(Protocol):
    def __enter__(self) -> "ConnectionLike": ...
    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool | None: ...
    def prefix(self, command: str) -> ContextManager[None]: ...
    def run(self, command: str, **kwargs: Any) -> RunResult: ...


ConnectionFactory = Callable[..., ConnectionLike]


@lru_cache(maxsize=1)
def fabric_connection_factory() -> ConnectionFactory:
    """获取 Fabric Connection 工厂。"""
    try:
        from fabric import Connection
    except ImportError as exc:
        raise RemoteDependencyError("缺少依赖：fabric。请先安装 fabric 后再使用该接口。") from exc
    return Connection
