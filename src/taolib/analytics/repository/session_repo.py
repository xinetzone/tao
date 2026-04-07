"""会话 Repository 模块。

提供会话数据的访问和聚合查询。
"""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.analytics.models.event import SessionDocument
from taolib._base.repository import AsyncRepository


class SessionRepository(AsyncRepository[SessionDocument]):
    """会话数据访问层。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化会话 Repository。"""
        super().__init__(collection, SessionDocument)

    async def upsert_session(self, session_data: dict[str, Any]) -> SessionDocument:
        """更新或创建会话记录。

        Args:
            session_data: 会话数据字典，必须包含 _id (session_id)

        Returns:
            更新后的会话文档
        """
        session_id = session_data["_id"]
        update_ops: dict[str, Any] = {
            "$set": {
                "app_id": session_data["app_id"],
                "ended_at": session_data.get("ended_at"),
                "exit_page": session_data.get("exit_page"),
            },
            "$setOnInsert": {
                "started_at": session_data["started_at"],
                "entry_page": session_data["entry_page"],
                "device_type": session_data.get("device_type", "unknown"),
            },
            "$inc": {
                "event_count": session_data.get("event_count", 1),
            },
        }

        if session_data.get("user_id") is not None:
            update_ops["$set"]["user_id"] = session_data["user_id"]

        if session_data.get("pages_visited"):
            update_ops["$addToSet"] = {
                "pages_visited": {"$each": session_data["pages_visited"]}
            }

        result = await self._collection.find_one_and_update(
            {"_id": session_id},
            update_ops,
            upsert=True,
            return_document=True,
        )

        # 计算 page_count 和 duration
        if result:
            updates: dict[str, Any] = {}
            if result.get("pages_visited"):
                updates["page_count"] = len(result["pages_visited"])
            if result.get("started_at") and result.get("ended_at"):
                duration = (result["ended_at"] - result["started_at"]).total_seconds()
                updates["duration_seconds"] = duration
            if updates:
                result = await self._collection.find_one_and_update(
                    {"_id": session_id},
                    {"$set": updates},
                    return_document=True,
                )

        result["_id"] = str(result["_id"])
        return SessionDocument(**result)

    async def find_by_app(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SessionDocument]:
        """按应用和时间范围查询会话。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            会话文档列表
        """
        cursor = (
            self._collection.find(
                {
                    "app_id": app_id,
                    "started_at": {"$gte": start, "$lte": end},
                }
            )
            .sort("started_at", -1)
            .skip(skip)
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(SessionDocument(**doc))
        return results

    async def get_session_stats(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        """获取会话统计数据。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间

        Returns:
            会话统计字典（平均时长、平均页面数、跳出率）
        """
        pipeline = [
            {
                "$match": {
                    "app_id": app_id,
                    "started_at": {"$gte": start, "$lte": end},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "avg_duration": {"$avg": "$duration_seconds"},
                    "avg_page_count": {"$avg": "$page_count"},
                    "bounce_count": {
                        "$sum": {"$cond": [{"$lte": ["$page_count", 1]}, 1, 0]}
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total_sessions": 1,
                    "avg_duration_seconds": {"$round": ["$avg_duration", 1]},
                    "avg_page_count": {"$round": ["$avg_page_count", 1]},
                    "bounce_rate": {
                        "$round": [
                            {"$divide": ["$bounce_count", "$total_sessions"]},
                            4,
                        ]
                    },
                }
            },
        ]
        cursor = self._collection.aggregate(pipeline)
        docs = await cursor.to_list(length=1)
        if docs:
            return docs[0]
        return {
            "total_sessions": 0,
            "avg_duration_seconds": 0,
            "avg_page_count": 0,
            "bounce_rate": 0,
        }

    async def create_indexes(self) -> None:
        """创建所有必要的索引。"""
        # 应用 + 时间查询
        await self._collection.create_index(
            [("app_id", 1), ("started_at", -1)],
        )
        # 用户查找
        await self._collection.create_index(
            [("app_id", 1), ("user_id", 1)],
            sparse=True,
        )
        # TTL 自动清理（默认 180 天）
        await self._collection.create_index(
            "started_at",
            expireAfterSeconds=180 * 24 * 3600,
        )
