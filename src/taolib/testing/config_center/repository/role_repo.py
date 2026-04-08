"""角色 Repository 模块。

提供角色文档的 MongoDB 操作实现。
"""

from ..models.user import RoleDocument
from .base import AsyncRepository


class RoleRepository(AsyncRepository[RoleDocument]):
    """角色 Repository 实现。"""

    def __init__(self, collection) -> None:
        """初始化角色 Repository。

        Args:
            collection: MongoDB roles 集合对象
        """
        super().__init__(collection, RoleDocument)

    async def find_by_name(self, name: str) -> RoleDocument | None:
        """根据角色名称查找角色。

        Args:
            name: 角色名称

        Returns:
            角色文档实例，如果不存在则返回 None
        """
        document = await self._collection.find_one({"name": name})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return RoleDocument(**document)

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index([("name", 1)], unique=True)


