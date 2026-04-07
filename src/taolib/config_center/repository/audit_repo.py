"""审计日志 Repository 模块。

提供审计日志文档的 MongoDB 操作实现。
"""

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from ..models.audit import AuditLogDocument
from .base import AsyncRepository


class AuditLogRepository(AsyncRepository[AuditLogDocument]):
    """审计日志 Repository 实现。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化审计日志 Repository。

        Args:
            collection: MongoDB audit_logs 集合对象
        """
        super().__init__(collection, AuditLogDocument)

    async def create_log(self, document: dict[str, Any]) -> AuditLogDocument:
        """创建审计日志。

        Args:
            document: 日志文档数据

        Returns:
            创建的审计日志实例
        """
        if "timestamp" not in document:
            document["timestamp"] = datetime.now(UTC)
        return await self.create(document)

    async def query_logs(
        self,
        resource_type: str | None = None,
        resource_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogDocument]:
        """查询审计日志。

        Args:
            resource_type: 资源类型过滤
            resource_id: 资源 ID 过滤
            actor_id: 操作人 ID 过滤
            action: 操作类型过滤
            time_from: 起始时间
            time_to: 结束时间
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            审计日志列表
        """
        filters: dict[str, Any] = {}
        if resource_type:
            filters["resource_type"] = resource_type
        if resource_id:
            filters["resource_id"] = resource_id
        if actor_id:
            filters["actor_id"] = actor_id
        if action:
            filters["action"] = action
        if time_from or time_to:
            time_range: dict[str, Any] = {}
            if time_from:
                time_range["$gte"] = time_from
            if time_to:
                time_range["$lte"] = time_to
            filters["timestamp"] = time_range

        return await self.list(
            filters=filters,
            skip=skip,
            limit=limit,
            sort=[("timestamp", -1)],
        )

    async def create_indexes(self) -> None:
        """创建索引（含 TTL）。"""
        await self._collection.create_index(
            [("resource_type", 1), ("resource_id", 1), ("timestamp", -1)]
        )
        await self._collection.create_index([("actor_id", 1), ("timestamp", -1)])
        await self._collection.create_index([("action", 1)])
        # TTL 索引：180 天后自动删除
        await self._collection.create_index(
            [("timestamp", 1)],
            expireAfterSeconds=180 * 24 * 60 * 60,
        )
