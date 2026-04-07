"""分析模块数据模型。

导出所有 Pydantic 模型和枚举。
"""

from taolib.analytics.models.enums import DeviceType, EventType
from taolib.analytics.models.event import (
    EventBase,
    EventBatchCreate,
    EventCreate,
    EventDocument,
    EventResponse,
    SessionDocument,
)

__all__ = [
    # Enums
    "EventType",
    "DeviceType",
    # Event models
    "EventBase",
    "EventCreate",
    "EventBatchCreate",
    "EventResponse",
    "EventDocument",
    # Session models
    "SessionDocument",
]
