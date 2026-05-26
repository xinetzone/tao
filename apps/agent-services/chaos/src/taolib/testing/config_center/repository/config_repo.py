"""配置 Repository 模块。

提供配置文档的 MongoDB 操作实现。
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from ..models.config import ConfigDocument
from ..models.enums import ConfigStatus, Environment
from .base import AsyncRepository


class ConfigRepository(AsyncRepository[ConfigDocument]):
    """配置 Repository 实现。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化配置 Repository。

        Args:
            collection: MongoDB configs 集合对象
        """
        super().__init__(collection, ConfigDocument)

    async def find_by_key_env_service(
        self,
        key: str,
        environment: Environment,
        service: str,
    ) -> ConfigDocument | None:
        """根据 key、环境和服务查找配置。

        Args:
            key: 配置键
            environment: 环境类型
            service: 服务名称

        Returns:
            配置文档实例，如果不存在则返回 None
        """
        document = await self._collection.find_one(
            {
                "key": key,
                "environment": environment,
                "service": service,
            }
        )
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return ConfigDocument(**document)

    async def find_by_tags(
        self,
        tags: list[str],
        environment: Environment | None = None,
        service: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConfigDocument]:
        """根据标签查找配置。

        Args:
            tags: 标签列表
            environment: 环境过滤
            service: 服务过滤
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            配置文档列表
        """
        filters: dict[str, Any] = {"tags": {"$in": tags}}
        if environment:
            filters["environment"] = environment
        if service:
            filters["service"] = service

        return await self.list(filters=filters, skip=skip, limit=limit)

    async def find_by_status(
        self,
        status: ConfigStatus,
        environment: Environment | None = None,
        service: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConfigDocument]:
        """根据状态查找配置。

        Args:
            status: 配置状态
            environment: 环境过滤
            service: 服务过滤
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            配置文档列表
        """
        filters: dict[str, Any] = {"status": status}
        if environment:
            filters["environment"] = environment
        if service:
            filters["service"] = service

        return await self.list(filters=filters, skip=skip, limit=limit)

    async def find_by_environment_and_service(
        self,
        environment: Environment,
        service: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConfigDocument]:
        """根据环境和服务查找所有配置。

        Args:
            environment: 环境类型
            service: 服务名称
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            配置文档列表
        """
        return await self.list(
            filters={"environment": environment, "service": service},
            skip=skip,
            limit=limit,
        )

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index(
            [("key", 1), ("environment", 1), ("service", 1)],
            unique=True,
        )
        await self._collection.create_index([("status", 1)])
        await self._collection.create_index([("tags", 1)])
        await self._collection.create_index([("environment", 1), ("service", 1)])


