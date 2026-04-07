"""OAuth 会话 Repository 模块。

提供 OAuth 会话的数据访问操作。
"""

from datetime import UTC, datetime

from taolib._base.repository import AsyncRepository

from ..models.session import OAuthSessionDocument


class OAuthSessionRepository(AsyncRepository[OAuthSessionDocument]):
    """OAuth 会话数据访问层。"""

    def __init__(self, collection) -> None:
        """初始化 Repository。

        Args:
            collection: MongoDB 集合对象
        """
        super().__init__(collection, OAuthSessionDocument)

    async def find_active_sessions(self, user_id: str) -> list[OAuthSessionDocument]:
        """获取用户的所有活跃会话。

        Args:
            user_id: 用户 ID

        Returns:
            活跃会话列表
        """
        now = datetime.now(UTC)
        cursor = self._collection.find(
            {"user_id": user_id, "is_active": True, "expires_at": {"$gt": now}}
        )
        docs = await cursor.to_list(length=100)
        results = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            results.append(OAuthSessionDocument(**doc))
        return results

    async def deactivate_session(self, session_id: str) -> bool:
        """停用指定会话。

        Args:
            session_id: 会话 ID

        Returns:
            是否成功停用
        """
        result = await self._collection.update_one(
            {"_id": session_id},
            {"$set": {"is_active": False}},
        )
        return result.modified_count > 0

    async def deactivate_all_for_user(self, user_id: str) -> int:
        """停用用户的所有会话。

        Args:
            user_id: 用户 ID

        Returns:
            停用的会话数量
        """
        result = await self._collection.update_many(
            {"user_id": user_id, "is_active": True},
            {"$set": {"is_active": False}},
        )
        return result.modified_count

    async def touch_session(self, session_id: str) -> None:
        """更新会话的最后活跃时间。

        Args:
            session_id: 会话 ID
        """
        await self._collection.update_one(
            {"_id": session_id},
            {"$set": {"last_activity_at": datetime.now(UTC)}},
        )

    async def create_indexes(self) -> None:
        """创建 MongoDB 索引。"""
        await self._collection.create_index("user_id")
        await self._collection.create_index("expires_at", expireAfterSeconds=0)
        await self._collection.create_index([("is_active", 1), ("user_id", 1)])
