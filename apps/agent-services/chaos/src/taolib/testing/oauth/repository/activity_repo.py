"""OAuth 活动日志 Repository 模块。

提供 OAuth 活动日志的数据访问操作。
"""

from datetime import datetime
from typing import Any

from taolib.testing._base.repository import AsyncRepository

from ..models.activity import OAuthActivityLogDocument
from ..models.enums import OAuthActivityAction, OAuthActivityStatus, OAuthProvider


class OAuthActivityLogRepository(AsyncRepository[OAuthActivityLogDocument]):
    """OAuth 活动日志数据访问层。"""

    def __init__(self, collection) -> None:
        """初始化 Repository。

        Args:
            collection: MongoDB 集合对象
        """
        super().__init__(collection, OAuthActivityLogDocument)

    async def log_activity(
        self,
        *,
        action: OAuthActivityAction,
        status: OAuthActivityStatus,
        provider: OAuthProvider | None = None,
        user_id: str | None = None,
        connection_id: str | None = None,
        ip_address: str = "",
        user_agent: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> OAuthActivityLogDocument:
        """记录一条活动日志。

        Args:
            action: 操作类型
            status: 操作状态
            provider: OAuth 提供商
            user_id: 用户 ID
            connection_id: 连接 ID
            ip_address: 客户端 IP
            user_agent: 客户端 User-Agent
            metadata: 额外上下文

        Returns:
            活动日志文档
        """
        doc_data: dict[str, Any] = {
            "action": str(action),
            "status": str(status),
            "provider": str(provider) if provider else None,
            "user_id": user_id,
            "connection_id": connection_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "metadata": metadata or {},
        }
        return await self.create(doc_data)

    async def query_logs(
        self,
        *,
        user_id: str | None = None,
        provider: str | None = None,
        action: str | None = None,
        status: str | None = None,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[OAuthActivityLogDocument]:
        """查询活动日志。

        Args:
            user_id: 按用户 ID 过滤
            provider: 按提供商过滤
            action: 按操作类型过滤
            status: 按状态过滤
            time_from: 起始时间
            time_to: 结束时间
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            活动日志列表
        """
        filters: dict[str, Any] = {}
        if user_id:
            filters["user_id"] = user_id
        if provider:
            filters["provider"] = provider
        if action:
            filters["action"] = action
        if status:
            filters["status"] = status
        if time_from or time_to:
            time_filter: dict[str, Any] = {}
            if time_from:
                time_filter["$gte"] = time_from
            if time_to:
                time_filter["$lte"] = time_to
            filters["timestamp"] = time_filter

        return await self.list(
            filters=filters,
            skip=skip,
            limit=limit,
            sort=[("timestamp", -1)],
        )

    async def get_stats(self) -> dict[str, Any]:
        """获取活动统计摘要。

        Returns:
            统计数据字典
        """
        total = await self.count()
        success_count = await self.count({"status": "success"})
        failed_count = await self.count({"status": "failed"})
        login_count = await self.count({"action": "oauth.login"})

        return {
            "total_events": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "login_count": login_count,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
        }

    async def create_indexes(self) -> None:
        """创建 MongoDB 索引。"""
        await self._collection.create_index([("user_id", 1), ("timestamp", -1)])
        await self._collection.create_index([("provider", 1), ("timestamp", -1)])
        await self._collection.create_index([("action", 1), ("timestamp", -1)])
        await self._collection.create_index(
            "timestamp", expireAfterSeconds=90 * 24 * 60 * 60
        )


