"""OAuth 连接 Repository 模块。

提供 OAuth 连接的数据访问操作。
"""

from taolib._base.repository import AsyncRepository

from ..models.connection import OAuthConnectionDocument
from ..models.enums import OAuthProvider


class OAuthConnectionRepository(AsyncRepository[OAuthConnectionDocument]):
    """OAuth 连接数据访问层。"""

    def __init__(self, collection) -> None:
        """初始化 Repository。

        Args:
            collection: MongoDB 集合对象
        """
        super().__init__(collection, OAuthConnectionDocument)

    async def find_by_user_and_provider(
        self, user_id: str, provider: OAuthProvider | str
    ) -> OAuthConnectionDocument | None:
        """按用户 ID 和提供商查找连接。

        Args:
            user_id: 本地用户 ID
            provider: OAuth 提供商

        Returns:
            连接文档，不存在则返回 None
        """
        doc = await self._collection.find_one(
            {"user_id": user_id, "provider": str(provider)}
        )
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return OAuthConnectionDocument(**doc)

    async def find_by_provider_user_id(
        self, provider: OAuthProvider | str, provider_user_id: str
    ) -> OAuthConnectionDocument | None:
        """按提供商和提供商侧用户 ID 查找连接。

        Args:
            provider: OAuth 提供商
            provider_user_id: 提供商侧用户 ID

        Returns:
            连接文档，不存在则返回 None
        """
        doc = await self._collection.find_one(
            {"provider": str(provider), "provider_user_id": provider_user_id}
        )
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return OAuthConnectionDocument(**doc)

    async def find_all_for_user(self, user_id: str) -> list[OAuthConnectionDocument]:
        """获取指定用户的所有 OAuth 连接。

        Args:
            user_id: 本地用户 ID

        Returns:
            连接文档列表
        """
        cursor = self._collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=100)
        results = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            results.append(OAuthConnectionDocument(**doc))
        return results

    async def count_active_for_user(self, user_id: str) -> int:
        """统计用户的活跃连接数。

        Args:
            user_id: 本地用户 ID

        Returns:
            活跃连接数量
        """
        return await self._collection.count_documents(
            {"user_id": user_id, "status": "active"}
        )

    async def create_indexes(self) -> None:
        """创建 MongoDB 索引。"""
        await self._collection.create_index(
            [("user_id", 1), ("provider", 1)], unique=True
        )
        await self._collection.create_index(
            [("provider", 1), ("provider_user_id", 1)], unique=True
        )
        await self._collection.create_index("user_id")
        await self._collection.create_index("status")
