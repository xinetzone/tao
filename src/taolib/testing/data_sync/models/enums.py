"""数据同步枚举类型。

定义同步管道中使用的各种枚举。
"""

from enum import StrEnum


class SyncStatus(StrEnum):
    """同步状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncScope(StrEnum):
    """同步范围。"""

    CONFIG_CENTER = "config_center"
    DATABASE = "database"
    FULL = "full"


class SyncMode(StrEnum):
    """同步模式。"""

    FULL = "full"
    INCREMENTAL = "incremental"


class FailureAction(StrEnum):
    """失败处理动作。"""

    SKIP = "skip"
    RETRY = "retry"
    ABORT = "abort"


