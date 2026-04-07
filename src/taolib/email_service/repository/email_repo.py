"""邮件 Repository。

提供邮件文档的数据访问操作。
"""

from datetime import UTC, datetime
from typing import Any

from taolib._base.repository import AsyncRepository
from taolib.email_service.models.email import EmailDocument
from taolib.email_service.models.enums import EmailStatus


class EmailRepository(AsyncRepository[EmailDocument]):
    """邮件 Repository。"""

    def __init__(self, collection) -> None:
        """初始化。"""
        super().__init__(collection, EmailDocument)

    async def find_by_status(
        self, status: EmailStatus, skip: int = 0, limit: int = 100
    ) -> list[EmailDocument]:
        """按状态查询邮件。"""
        return await self.list(
            filters={"status": str(status)},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_by_recipient(
        self, email: str, skip: int = 0, limit: int = 100
    ) -> list[EmailDocument]:
        """按收件人查询邮件。"""
        return await self.list(
            filters={"recipients.email": email},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_queued_emails(self, limit: int = 100) -> list[EmailDocument]:
        """查找待发送的队列邮件。"""
        now = datetime.now(UTC)
        return await self.list(
            filters={
                "status": str(EmailStatus.QUEUED),
                "$or": [
                    {"schedule_at": None},
                    {"schedule_at": {"$lte": now}},
                ],
            },
            limit=limit,
            sort=[("priority", 1), ("created_at", 1)],
        )

    async def find_scheduled_ready(self, limit: int = 50) -> list[EmailDocument]:
        """查找到期的计划邮件。"""
        now = datetime.now(UTC)
        return await self.list(
            filters={
                "status": str(EmailStatus.QUEUED),
                "schedule_at": {"$lte": now},
            },
            limit=limit,
        )

    async def update_status(
        self, email_id: str, status: EmailStatus, **extra_fields: Any
    ) -> EmailDocument | None:
        """更新邮件状态。"""
        updates: dict[str, Any] = {
            "status": str(status),
            "updated_at": datetime.now(UTC),
            **extra_fields,
        }
        return await self.update(email_id, updates)

    async def increment_retry(self, email_id: str) -> EmailDocument | None:
        """递增重试计数。"""
        result = await self._collection.find_one_and_update(
            {"_id": email_id},
            {
                "$inc": {"retry_count": 1},
                "$set": {"updated_at": datetime.now(UTC)},
            },
            return_document=True,
        )
        if result is None:
            return None
        result["_id"] = str(result["_id"])
        return EmailDocument(**result)

    async def get_stats(self, start: datetime, end: datetime) -> dict[str, int]:
        """获取指定时间范围内的邮件统计。"""
        pipeline = [
            {"$match": {"created_at": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        results: dict[str, int] = {}
        async for doc in self._collection.aggregate(pipeline):
            results[doc["_id"]] = doc["count"]
        return results

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("status")
        await self._collection.create_index("email_type")
        await self._collection.create_index([("created_at", -1)])
        await self._collection.create_index("schedule_at")
        await self._collection.create_index("recipients.email")
        await self._collection.create_index("tags")
