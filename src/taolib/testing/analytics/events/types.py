"""分析模块内部事件类型。

定义分析系统内部使用的事件数据类。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class EventsReceivedEvent:
    """事件接收事件（元事件）。"""

    app_id: str
    event_count: int
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "app_id": self.app_id,
            "event_count": self.event_count,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class AnalyticsQueryEvent:
    """分析查询事件（元事件）。"""

    app_id: str
    query_type: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "app_id": self.app_id,
            "query_type": self.query_type,
            "timestamp": self.timestamp.isoformat(),
        }


