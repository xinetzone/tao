"""订阅管理服务。

处理退订请求和订阅状态管理。
"""

import uuid
from datetime import UTC, datetime

from taolib.testing.email_service.errors import SubscriptionError
from taolib.testing.email_service.models.enums import SubscriptionStatus
from taolib.testing.email_service.models.subscription import (
    SubscriptionDocument,
    SubscriptionResponse,
)
from taolib.testing.email_service.repository.subscription_repo import SubscriptionRepository


class SubscriptionService:
    """订阅管理服务。"""

    def __init__(self, subscription_repo: SubscriptionRepository) -> None:
        """初始化。

        Args:
            subscription_repo: 订阅 Repository
        """
        self._repo = subscription_repo

    async def get_or_create_subscription(self, email: str) -> SubscriptionDocument:
        """获取或创建订阅记录。

        如果邮箱没有订阅记录，则创建一个新的激活状态记录。

        Args:
            email: 邮箱地址

        Returns:
            订阅文档
        """
        existing = await self._repo.find_by_email(email)
        if existing:
            return existing

        doc_dict = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "status": str(SubscriptionStatus.ACTIVE),
            "unsubscribe_token": str(uuid.uuid4()),
            "tags": [],
            "subscribed_at": datetime.now(UTC),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        return await self._repo.create(doc_dict)

    async def unsubscribe(
        self, token: str, reason: str | None = None
    ) -> SubscriptionResponse:
        """处理退订请求。

        Args:
            token: 退订令牌
            reason: 退订原因

        Returns:
            更新后的订阅响应

        Raises:
            SubscriptionError: 令牌无效或已退订
        """
        doc = await self._repo.find_by_token(token)
        if doc is None:
            raise SubscriptionError(f"Invalid unsubscribe token: {token}")

        if doc.status == SubscriptionStatus.UNSUBSCRIBED:
            return doc.to_response()

        now = datetime.now(UTC)
        updates: dict = {
            "status": str(SubscriptionStatus.UNSUBSCRIBED),
            "unsubscribed_at": now,
            "updated_at": now,
        }
        if reason:
            updates["unsubscribe_reason"] = reason

        updated = await self._repo.update(doc.id, updates)
        if updated is None:
            raise SubscriptionError("Failed to update subscription")
        return updated.to_response()

    async def unsubscribe_by_email(
        self, email: str, reason: str | None = None
    ) -> SubscriptionResponse | None:
        """按邮箱退订（用于硬退信自动退订）。"""
        doc = await self._repo.find_by_email(email)
        if doc is None:
            # 创建并立即退订
            doc = await self.get_or_create_subscription(email)

        if doc.status == SubscriptionStatus.UNSUBSCRIBED:
            return doc.to_response()

        return await self.unsubscribe(doc.unsubscribe_token, reason)

    async def resubscribe(self, email: str) -> SubscriptionResponse:
        """重新订阅。

        Args:
            email: 邮箱地址

        Returns:
            更新后的订阅响应

        Raises:
            SubscriptionError: 订阅记录不存在
        """
        doc = await self._repo.find_by_email(email)
        if doc is None:
            raise SubscriptionError(f"No subscription found for: {email}")

        now = datetime.now(UTC)
        updated = await self._repo.update(
            doc.id,
            {
                "status": str(SubscriptionStatus.ACTIVE),
                "unsubscribed_at": None,
                "unsubscribe_reason": None,
                "updated_at": now,
            },
        )
        if updated is None:
            raise SubscriptionError("Failed to update subscription")
        return updated.to_response()

    async def is_subscribed(self, email: str) -> bool:
        """检查是否订阅。"""
        return await self._repo.is_subscribed(email)

    async def get_unsubscribe_token(self, email: str) -> str:
        """获取退订令牌（自动创建订阅记录）。"""
        doc = await self.get_or_create_subscription(email)
        return doc.unsubscribe_token


