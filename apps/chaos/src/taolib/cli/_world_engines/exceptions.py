"""Session Engine 自定义异常。"""


class SessionError(Exception):
    """Session 操作基础异常。"""


class SessionNotFoundError(SessionError):
    """目标 session 目录或 manifest 不存在。"""


class LockHeldError(SessionError):
    """锁被其他端持有且租约有效。"""


class SessionArchivedError(SessionError):
    """Session 已归档，不可写入。"""
