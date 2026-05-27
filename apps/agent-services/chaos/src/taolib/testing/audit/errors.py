"""审计日志异常层次结构。

定义所有审计日志相关的异常类型。
"""


class AuditError(Exception):
    """所有审计日志错误的基类。"""

    def __init__(self, message: str = "审计日志错误") -> None:
        self.message = message
        super().__init__(message)


class AuditStorageError(AuditError):
    """审计日志存储错误。"""

    def __init__(self, message: str = "审计日志存储失败") -> None:
        super().__init__(message)


class AuditConfigError(AuditError):
    """审计日志配置错误。"""

    def __init__(self, message: str = "审计日志配置错误") -> None:
        super().__init__(message)
