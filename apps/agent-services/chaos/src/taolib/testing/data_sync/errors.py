"""数据同步自定义异常。

定义同步管道中使用的异常层次结构。
"""


class SyncError(Exception):
    """所有同步错误的基类。"""

    pass


class SyncJobNotFoundError(SyncError):
    """同步作业不存在或已禁用。"""

    pass


class SyncConnectionError(SyncError):
    """无法连接到源/目标 MongoDB。"""

    pass


class SyncTransformError(SyncError):
    """用户转换函数抛出不可恢复的错误。"""

    pass


class SyncCheckpointError(SyncError):
    """检查点损坏或更新失败。"""

    pass


class SyncAbortError(SyncError):
    """当 failure_action == abort 时达到阈值触发。"""

    pass


