"""模板 Repository。

提供邮件模板的数据访问操作。
"""

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.email_service.models.enums import EmailType
from taolib.testing.email_service.models.template import TemplateDocument


class TemplateRepository(AsyncRepository[TemplateDocument]):
    """模板 Repository。"""

    def __init__(self, collection) -> None:
        """初始化。"""
        super().__init__(collection, TemplateDocument)

    async def find_by_name(self, name: str) -> TemplateDocument | None:
        """按名称查找模板。"""
        doc = await self._collection.find_one({"name": name})
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return TemplateDocument(**doc)

    async def find_active(
        self, skip: int = 0, limit: int = 100
    ) -> list[TemplateDocument]:
        """查找所有激活的模板。"""
        return await self.list(
            filters={"is_active": True},
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)],
        )

    async def find_by_email_type(
        self, email_type: EmailType, skip: int = 0, limit: int = 100
    ) -> list[TemplateDocument]:
        """按邮件类型查找模板。"""
        return await self.list(
            filters={"email_type": str(email_type), "is_active": True},
            skip=skip,
            limit=limit,
        )

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("name", unique=True)
        await self._collection.create_index("is_active")
        await self._collection.create_index("email_type")
        await self._collection.create_index("tags")


