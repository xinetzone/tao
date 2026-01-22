"""远端执行相关异常定义。"""
class RemoteError(RuntimeError):
    """远端执行相关错误基类。"""


class RemoteDependencyError(RemoteError):
    """依赖缺失或版本不兼容导致的错误。"""


class RemoteConfigError(RemoteError):
    """配置不合法或缺失导致的错误。"""


class RemoteExecutionError(RemoteError):
    """远端命令执行失败导致的错误。"""

    def __init__(self, message: str, *, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command

