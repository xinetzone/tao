"""分析模块事件层。

导出所有内部事件类型。
"""

from taolib.analytics.events.types import AnalyticsQueryEvent, EventsReceivedEvent

__all__ = [
    "EventsReceivedEvent",
    "AnalyticsQueryEvent",
]
