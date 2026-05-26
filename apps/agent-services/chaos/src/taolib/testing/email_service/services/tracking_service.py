"""追踪和分析服务。

记录邮件追踪事件并提供分析数据。
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from taolib.testing.email_service.models.enums import EmailStatus, TrackingEventType
from taolib.testing.email_service.models.tracking import (
    TrackingEventResponse,
)
from taolib.testing.email_service.repository.email_repo import EmailRepository
from taolib.testing.email_service.repository.tracking_repo import TrackingRepository


class EmailAnalytics(BaseModel):
    """邮件分析数据。"""

    total_sent: int = Field(default=0, description="总发送数")
    total_delivered: int = Field(default=0, description="总投递数")
    total_opened: int = Field(default=0, description="总打开数")
    total_clicked: int = Field(default=0, description="总点击数")
    total_bounced: int = Field(default=0, description="总退信数")
    total_failed: int = Field(default=0, description="总失败数")
    delivery_rate: float = Field(default=0.0, description="投递率 (%)")
    open_rate: float = Field(default=0.0, description="打开率 (%)")
    click_rate: float = Field(default=0.0, description="点击率 (%)")
    bounce_rate: float = Field(default=0.0, description="退信率 (%)")


class TrackingService:
    """追踪和分析服务。"""

    def __init__(
        self,
        tracking_repo: TrackingRepository,
        email_repo: EmailRepository,
    ) -> None:
        """初始化。

        Args:
            tracking_repo: 追踪事件 Repository
            email_repo: 邮件 Repository
        """
        self._tracking_repo = tracking_repo
        self._email_repo = email_repo

    async def record_event(
        self,
        email_id: str,
        event_type: TrackingEventType,
        recipient: str,
        provider: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        click_url: str | None = None,
        bounce_type: str | None = None,
        bounce_reason: str | None = None,
        raw_payload: dict | None = None,
    ) -> TrackingEventResponse:
        """记录追踪事件。

        同时更新关联的 EmailDocument 状态。
        """
        now = datetime.now(UTC)
        doc_dict = {
            "_id": str(uuid.uuid4()),
            "email_id": email_id,
            "event_type": str(event_type),
            "recipient": recipient,
            "timestamp": now,
            "provider": provider,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "click_url": click_url,
            "bounce_type": bounce_type,
            "bounce_reason": bounce_reason,
            "raw_payload": raw_payload,
            "created_at": now,
        }
        doc = await self._tracking_repo.create(doc_dict)

        # 同步更新邮件文档状态
        await self._update_email_status(email_id, event_type, now)

        return doc.to_response()

    async def get_events_for_email(self, email_id: str) -> list[TrackingEventResponse]:
        """获取邮件的所有追踪事件。"""
        docs = await self._tracking_repo.find_by_email_id(email_id)
        return [d.to_response() for d in docs]

    async def get_analytics(self, start: datetime, end: datetime) -> EmailAnalytics:
        """获取时间范围内的分析数据。"""
        counts = await self._tracking_repo.get_event_counts(start, end)

        total_sent = counts.get(TrackingEventType.SENT, 0)
        total_delivered = counts.get(TrackingEventType.DELIVERED, 0)
        total_opened = counts.get(TrackingEventType.OPENED, 0)
        total_clicked = counts.get(TrackingEventType.CLICKED, 0)
        total_bounced = counts.get(TrackingEventType.BOUNCED, 0)

        return EmailAnalytics(
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_opened=total_opened,
            total_clicked=total_clicked,
            total_bounced=total_bounced,
            delivery_rate=(total_delivered / total_sent * 100) if total_sent else 0,
            open_rate=(total_opened / total_delivered * 100) if total_delivered else 0,
            click_rate=(total_clicked / total_delivered * 100)
            if total_delivered
            else 0,
            bounce_rate=(total_bounced / total_sent * 100) if total_sent else 0,
        )

    async def get_daily_stats(self, start: datetime, end: datetime) -> list[dict]:
        """获取按日统计数据。"""
        return await self._tracking_repo.get_daily_stats(start, end)

    async def _update_email_status(
        self, email_id: str, event_type: TrackingEventType, timestamp: datetime
    ) -> None:
        """根据追踪事件更新邮件状态。"""
        status_map = {
            TrackingEventType.DELIVERED: (
                EmailStatus.DELIVERED,
                {"delivered_at": timestamp},
            ),
            TrackingEventType.OPENED: (EmailStatus.OPENED, {"opened_at": timestamp}),
            TrackingEventType.CLICKED: (EmailStatus.CLICKED, {}),
            TrackingEventType.BOUNCED: (EmailStatus.BOUNCED, {}),
        }

        mapping = status_map.get(event_type)
        if mapping:
            status, extra = mapping
            await self._email_repo.update_status(email_id, status, **extra)


