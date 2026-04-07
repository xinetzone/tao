"""Violation tracker for recording rate limit violations to MongoDB."""
from typing import Any

from .models import ViolationDocument


class ViolationTracker:
    """违规记录追踪器。

    将超出限流阈值的请求记录到 MongoDB，用于后续分析和监控。

    Args:
        mongo_collection: MongoDB 集合对象（motor 异步集合）
        ttl_days: 违规记录保留天数
    """

    def __init__(
        self,
        mongo_collection: Any,
        ttl_days: int = 90,
    ) -> None:
        self._collection = mongo_collection
        self._ttl_days = ttl_days

    async def record_violation(
        self,
        identifier: str,
        ip_address: str,
        path: str,
        method: str,
        request_count: int,
        limit: int,
        window_seconds: int,
        retry_after: int,
        user_id: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """记录违规请求。

        Args:
            identifier: 用户标识符
            ip_address: IP 地址
            path: 请求路径
            method: HTTP 方法
            request_count: 窗口内请求数
            limit: 限流阈值
            window_seconds: 窗口大小
            retry_after: 建议重试秒数
            user_id: 用户 ID（如果已登录）
            user_agent: User-Agent 头
        """
        from .keys import parse_identifier_type

        violation = ViolationDocument(
            identifier=identifier,
            identifier_type=parse_identifier_type(identifier),
            user_id=user_id,
            ip_address=ip_address,
            path=path,
            method=method,
            request_count=request_count,
            limit=limit,
            window_seconds=window_seconds,
            retry_after=retry_after,
            user_agent=user_agent,
        )

        await self._collection.insert_one(violation.to_mongo_dict())

    async def ensure_indexes(self) -> None:
        """确保 MongoDB 索引存在。"""
        # TTL index on timestamp
        await self._collection.create_index(
            "timestamp", expireAfterSeconds=self._ttl_days * 86400
        )
        # Compound index for querying by identifier
        await self._collection.create_index([("identifier", 1), ("timestamp", 1)])
        # Index for aggregation by type
        await self._collection.create_index([("identifier_type", 1), ("timestamp", 1)])
