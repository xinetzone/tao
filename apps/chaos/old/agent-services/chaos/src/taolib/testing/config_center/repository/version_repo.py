"""配置版本 Repository 模块。

提供配置版本文档的 MongoDB 操作实现。
"""

from motor.motor_asyncio import AsyncIOMotorCollection

from ..models.version import ConfigVersionDocument
from .base import AsyncRepository


class VersionRepository(AsyncRepository[ConfigVersionDocument]):
    """配置版本 Repository 实现。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化版本 Repository。

        Args:
            collection: MongoDB config_versions 集合对象
        """
        super().__init__(collection, ConfigVersionDocument)

    async def get_versions_by_config(
        self,
        config_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConfigVersionDocument]:
        """获取配置的所有版本历史。

        Args:
            config_id: 配置 ID
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            版本文档列表，按版本号降序排列
        """
        return await self.list(
            filters={"config_id": config_id},
            skip=skip,
            limit=limit,
            sort=[("version", -1)],
        )

    async def get_version(
        self,
        config_id: str,
        version_num: int,
    ) -> ConfigVersionDocument | None:
        """获取配置的指定版本。

        Args:
            config_id: 配置 ID
            version_num: 版本号

        Returns:
            版本文档实例，如果不存在则返回 None
        """
        document = await self._collection.find_one(
            {
                "config_id": config_id,
                "version": version_num,
            }
        )
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return ConfigVersionDocument(**document)

    async def get_latest_version(self, config_id: str) -> int:
        """获取配置的最新版本号。

        Args:
            config_id: 配置 ID

        Returns:
            最新版本号，如果没有版本则返回 0
        """
        document = await self._collection.find_one(
            {"config_id": config_id},
            sort=[("version", -1)],
        )
        if document is None:
            return 0
        return document.get("version", 0)

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index([("config_id", 1), ("version", 1)])
        await self._collection.create_index([("config_id", 1)])
