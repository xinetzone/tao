"""退信处理服务。

处理硬退信和软退信，自动管理订阅状态。
"""

import logging

from taolib.email_service.models.enums import BounceType, TrackingEventType
from taolib.email_service.repository.email_repo import EmailRepository
from taolib.email_service.services.subscription_service import SubscriptionService
from taolib.email_service.services.tracking_service import TrackingService

logger = logging.getLogger(__name__)


class BounceHandler:
    """退信处理器。"""

    def __init__(
        self,
        tracking_service: TrackingService,
        subscription_service: SubscriptionService,
        email_repo: EmailRepository,
        hard_bounce_threshold: int = 1,
    ) -> None:
        """初始化。

        Args:
            tracking_service: 追踪服务
            subscription_service: 订阅服务
            email_repo: 邮件 Repository
            hard_bounce_threshold: 硬退信自动退订阈值
        """
        self._tracking = tracking_service
        self._subscription = subscription_service
        self._email_repo = email_repo
        self._hard_bounce_threshold = hard_bounce_threshold

    async def handle_bounce(
        self,
        email_id: str,
        bounce_type: BounceType,
        reason: str,
        recipient: str,
        provider: str | None = None,
        raw_payload: dict | None = None,
    ) -> None:
        """处理退信事件。

        Args:
            email_id: 邮件 ID
            bounce_type: 退信类型
            reason: 退信原因
            recipient: 收件人
            provider: 提供商名称
            raw_payload: 原始 Webhook 数据
        """
        # 记录追踪事件
        await self._tracking.record_event(
            email_id=email_id,
            event_type=TrackingEventType.BOUNCED,
            recipient=recipient,
            provider=provider,
            bounce_type=str(bounce_type),
            bounce_reason=reason,
            raw_payload=raw_payload,
        )

        # 硬退信：自动退订
        if bounce_type == BounceType.HARD:
            logger.info("Hard bounce for %s, auto-unsubscribing", recipient)
            await self._subscription.unsubscribe_by_email(
                recipient, reason=f"Hard bounce: {reason}"
            )

    async def handle_complaint(
        self,
        email_id: str,
        recipient: str,
        provider: str | None = None,
        raw_payload: dict | None = None,
    ) -> None:
        """处理投诉事件。

        投诉视为退订请求。

        Args:
            email_id: 邮件 ID
            recipient: 收件人
            provider: 提供商名称
            raw_payload: 原始 Webhook 数据
        """
        await self._tracking.record_event(
            email_id=email_id,
            event_type=TrackingEventType.COMPLAINED,
            recipient=recipient,
            provider=provider,
            raw_payload=raw_payload,
        )

        logger.info("Complaint received for %s, auto-unsubscribing", recipient)
        await self._subscription.unsubscribe_by_email(
            recipient, reason="Spam complaint"
        )
