"""任务队列事件类型。

定义任务处理过程中发布的事件。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class TaskSubmittedEvent:
    """任务提交事件。"""

    task_id: str
    task_type: str
    priority: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class TaskStartedEvent:
    """任务开始执行事件。"""

    task_id: str
    task_type: str
    worker_id: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "worker_id": self.worker_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class TaskCompletedEvent:
    """任务完成事件。"""

    task_id: str
    task_type: str
    duration_seconds: float
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class TaskFailedEvent:
    """任务失败事件。"""

    task_id: str
    task_type: str
    error_message: str
    retry_count: int
    will_retry: bool
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "will_retry": self.will_retry,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class TaskRetriedEvent:
    """任务重试事件。"""

    task_id: str
    task_type: str
    retry_count: int
    next_retry_at: datetime
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "retry_count": self.retry_count,
            "next_retry_at": self.next_retry_at.isoformat(),
            "timestamp": self.timestamp.isoformat(),
        }
