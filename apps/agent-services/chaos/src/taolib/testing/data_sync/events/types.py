"""数据同步事件类型。

定义同步过程中发布的事件。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SyncStartedEvent:
    """同步开始事件。"""

    job_id: str
    job_name: str
    mode: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "mode": self.mode,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class SyncCompletedEvent:
    """同步完成事件。"""

    job_id: str
    job_name: str
    log_id: str
    status: str
    metrics: dict[str, Any]
    duration_seconds: float
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "log_id": self.log_id,
            "status": self.status,
            "metrics": self.metrics,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class SyncFailedEvent:
    """同步失败事件。"""

    job_id: str
    job_name: str
    log_id: str
    error_message: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "log_id": self.log_id,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }
