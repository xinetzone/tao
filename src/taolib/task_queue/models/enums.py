"""任务队列枚举类型。

定义任务队列中使用的各种枚举。
"""

from enum import StrEnum


class TaskStatus(StrEnum):
    """任务状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    """任务优先级。"""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
