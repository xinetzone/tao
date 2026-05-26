"""OAuth 应用凭证 Repository 模块。

提供 OAuth 应用凭证的数据访问操作。
"""

from taolib.testing._base.repository import AsyncRepository

from ..models.credential import OAuthAppCredentialDocument
from ..models.enums import OAuthProvider


class OAuthAppCredentialRepository(AsyncRepository[OAuthAppCredentialDocument]):
    """OAuth 应用凭证数据访问层。"""

    def __init__(self, collection) -> None:
        """初始化 Repository。

        Args:
            collection: MongoDB 集合对象
        """
        super().__init__(collection, OAuthAppCredentialDocument)

    async def find_by_provider(
        self, provider: OAuthProvider | str
    ) -> OAuthAppCredentialDocument | None:
        """按提供商查找已启用的凭证。

        Args:
            provider: OAuth 提供商

        Returns:
            凭证文档，不存在则返回 None
        """
        doc = await self._collection.find_one(
            {"provider": str(provider), "enabled": True}
        )
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return OAuthAppCredentialDocument(**doc)

    async def find_all(self) -> list[OAuthAppCredentialDocument]:
        """获取所有凭证（包含已禁用的）。

        Returns:
            凭证文档列表
        """
        cursor = self._collection.find({})
        docs = await cursor.to_list(length=100)
        results = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            results.append(OAuthAppCredentialDocument(**doc))
        return results

    async def create_indexes(self) -> None:
        """创建 MongoDB 索引。"""
        await self._collection.create_index("provider", unique=True)
        await self._collection.create_index("enabled")


