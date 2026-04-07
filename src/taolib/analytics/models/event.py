"""事件数据模型。

定义 Event 的 4-tier Pydantic 模型：
Base → Create/BatchCreate → Response → Document

以及 SessionDocument 聚合会话模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.analytics.models.enums import DeviceType, EventType


class EventBase(BaseModel):
    """事件基础字段。"""

    event_type: EventType = Field(..., description="事件类型")
    app_id: str = Field(..., description="应用标识", min_length=1, max_length=100)
    session_id: str = Field(..., description="会话 ID", min_length=1)
    user_id: str | None = Field(None, description="用户 ID（可选）")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="事件时间戳"
    )
    page_url: str = Field(..., description="页面 URL")
    page_title: str = Field("", description="页面标题")
    referrer: str | None = Field(None, description="引用页")
    device_type: DeviceType = Field(default=DeviceType.UNKNOWN, description="设备类型")
    user_agent: str | None = Field(None, description="User-Agent")
    screen_width: int | None = Field(None, description="屏幕宽度")
    screen_height: int | None = Field(None, description="屏幕高度")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="事件类型相关的扩展数据"
    )


class EventCreate(EventBase):
    """创建事件的输入模型。"""


class EventBatchCreate(BaseModel):
    """批量创建事件的输入模型。"""

    events: list[EventCreate] = Field(
        ..., description="事件列表", min_length=1, max_length=1000
    )


class EventResponse(EventBase):
    """事件的 API 响应模型。"""

    id: str = Field(alias="_id")

    model_config = {"from_attributes": True}


class EventDocument(EventBase):
    """事件的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}

    def to_response(self) -> EventResponse:
        """转换为 API 响应。"""
        return EventResponse(
            _id=self.id,
            event_type=self.event_type,
            app_id=self.app_id,
            session_id=self.session_id,
            user_id=self.user_id,
            timestamp=self.timestamp,
            page_url=self.page_url,
            page_title=self.page_title,
            referrer=self.referrer,
            device_type=self.device_type,
            user_agent=self.user_agent,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            metadata=self.metadata,
        )


class SessionDocument(BaseModel):
    """聚合会话的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    app_id: str = Field(..., description="应用标识")
    user_id: str | None = Field(None, description="用户 ID")
    device_type: DeviceType = Field(default=DeviceType.UNKNOWN, description="设备类型")
    started_at: datetime = Field(..., description="会话开始时间")
    ended_at: datetime | None = Field(None, description="会话结束时间")
    duration_seconds: float | None = Field(None, description="会话时长（秒）")
    page_count: int = Field(0, description="浏览页面数")
    event_count: int = Field(0, description="事件总数")
    entry_page: str = Field(..., description="入口页面")
    exit_page: str | None = Field(None, description="退出页面")
    pages_visited: list[str] = Field(default_factory=list, description="浏览过的页面")

    model_config = {"populate_by_name": True}
