"""订阅 Repository。

提供订阅/退订的数据访问操作。
"""

from taolib._base.repository import AsyncRepository
from taolib.email_service.models.enums import SubscriptionStatus
from taolib.email_service.models.subscription import SubscriptionDocument


class SubscriptionRepository(AsyncRepository[SubscriptionDocument]):
    """订阅 Repository。"""

    def __init__(self, collection) -> None:
        """初始化。"""
        super().__init__(collection, SubscriptionDocument)

    async def find_by_email(self, email: str) -> SubscriptionDocument | None:
        """按邮箱查找订阅记录。"""
        doc = await self._collection.find_one({"email": email})
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return SubscriptionDocument(**doc)

    async def find_by_token(self, token: str) -> SubscriptionDocument | None:
        """按退订令牌查找订阅记录。"""
        doc = await self._collection.find_one({"unsubscribe_token": token})
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return SubscriptionDocument(**doc)

    async def is_subscribed(self, email: str) -> bool:
        """检查邮箱是否处于订阅状态。

        如果没有记录，默认视为已订阅。
        """
        doc = await self.find_by_email(email)
        if doc is None:
            return True  # 无记录视为已订阅
        return doc.status == SubscriptionStatus.ACTIVE

    async def find_unsubscribed(
        self, skip: int = 0, limit: int = 100
    ) -> list[SubscriptionDocument]:
        """查找所有已退订的记录。"""
        return await self.list(
            filters={"status": str(SubscriptionStatus.UNSUBSCRIBED)},
            skip=skip,
            limit=limit,
            sort=[("unsubscribed_at", -1)],
        )

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("email", unique=True)
        await self._collection.create_index("unsubscribe_token", unique=True)
        await self._collection.create_index("status")
