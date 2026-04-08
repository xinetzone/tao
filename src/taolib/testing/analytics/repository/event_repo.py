"""事件 Repository 模块。

提供事件的数据访问和 MongoDB 聚合管道。
"""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing.analytics.models.enums import EventType
from taolib.testing.analytics.models.event import EventDocument
from taolib.testing._base.repository import AsyncRepository


class EventRepository(AsyncRepository[EventDocument]):
    """事件数据访问层。"""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """初始化事件 Repository。"""
        super().__init__(collection, EventDocument)

    async def bulk_create(self, events: list[dict[str, Any]]) -> int:
        """批量创建事件。

        Args:
            events: 事件数据字典列表

        Returns:
            成功插入的事件数量
        """
        if not events:
            return 0
        result = await self._collection.insert_many(events)
        return len(result.inserted_ids)

    async def find_by_session(self, session_id: str) -> list[EventDocument]:
        """根据会话 ID 查询事件（按时间排序）。

        Args:
            session_id: 会话 ID

        Returns:
            事件文档列表
        """
        cursor = self._collection.find({"session_id": session_id}).sort("timestamp", 1)
        documents = await cursor.to_list(length=10000)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(EventDocument(**doc))
        return results

    async def find_by_app(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
        event_type: EventType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EventDocument]:
        """按应用和时间范围查询事件。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间
            event_type: 事件类型（可选）
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            事件文档列表
        """
        query: dict[str, Any] = {
            "app_id": app_id,
            "timestamp": {"$gte": start, "$lte": end},
        }
        if event_type is not None:
            query["event_type"] = event_type

        cursor = (
            self._collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(EventDocument(**doc))
        return results

    async def aggregate_funnel(
        self,
        app_id: str,
        steps: list[str],
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """转化漏斗聚合分析。

        统计每个步骤的完成人数（基于 session_id 去重）。

        Args:
            app_id: 应用标识
            steps: 漏斗步骤名称列表（对应 page_url 或 metadata.feature_name）
            start: 开始时间
            end: 结束时间

        Returns:
            每个步骤的统计数据列表
        """
        results = []
        for step in steps:
            pipeline = [
                {
                    "$match": {
                        "app_id": app_id,
                        "timestamp": {"$gte": start, "$lte": end},
                        "$or": [
                            {"page_url": step},
                            {"metadata.feature_name": step},
                        ],
                    }
                },
                {"$group": {"_id": None, "count": {"$addToSet": "$session_id"}}},
                {"$project": {"_id": 0, "count": {"$size": "$count"}}},
            ]
            cursor = self._collection.aggregate(pipeline)
            docs = await cursor.to_list(length=1)
            count = docs[0]["count"] if docs else 0
            results.append({"name": step, "count": count})

        return results

    async def aggregate_feature_usage(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """功能使用排名聚合。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间
            limit: 返回数量限制

        Returns:
            功能使用排名列表
        """
        pipeline = [
            {
                "$match": {
                    "app_id": app_id,
                    "event_type": EventType.FEATURE_USE,
                    "timestamp": {"$gte": start, "$lte": end},
                }
            },
            {
                "$group": {
                    "_id": {
                        "name": "$metadata.feature_name",
                        "category": "$metadata.feature_category",
                    },
                    "count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$session_id"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.name",
                    "category": "$_id.category",
                    "count": 1,
                    "unique_users": {"$size": "$unique_users"},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def aggregate_navigation_paths(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """用户导航路径聚合（页面流向）。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间
            limit: 返回数量限制

        Returns:
            页面导航路径列表 [{source, target, value}]
        """
        pipeline = [
            {
                "$match": {
                    "app_id": app_id,
                    "event_type": EventType.PAGE_VIEW,
                    "timestamp": {"$gte": start, "$lte": end},
                }
            },
            {"$sort": {"session_id": 1, "timestamp": 1}},
            {
                "$group": {
                    "_id": "$session_id",
                    "pages": {"$push": "$page_url"},
                }
            },
            {
                "$project": {
                    "pairs": {
                        "$zip": {
                            "inputs": [
                                "$pages",
                                {"$slice": ["$pages", 1, {"$size": "$pages"}]},
                            ]
                        }
                    }
                }
            },
            {"$unwind": "$pairs"},
            {
                "$group": {
                    "_id": {
                        "source": {"$arrayElemAt": ["$pairs", 0]},
                        "target": {"$arrayElemAt": ["$pairs", 1]},
                    },
                    "value": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "source": "$_id.source",
                    "target": "$_id.target",
                    "value": 1,
                }
            },
            {"$sort": {"value": -1}},
            {"$limit": limit},
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def aggregate_time_on_section(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """区域停留时间聚合。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间

        Returns:
            每个区域的平均停留时间
        """
        pipeline = [
            {
                "$match": {
                    "app_id": app_id,
                    "event_type": EventType.TIME_ON_SECTION,
                    "timestamp": {"$gte": start, "$lte": end},
                }
            },
            {
                "$group": {
                    "_id": "$metadata.section_id",
                    "avg_duration_ms": {"$avg": "$metadata.duration_ms"},
                    "total_views": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "section_id": "$_id",
                    "avg_duration_ms": {"$round": ["$avg_duration_ms", 0]},
                    "total_views": 1,
                }
            },
            {"$sort": {"total_views": -1}},
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=100)

    async def aggregate_drop_off(
        self,
        app_id: str,
        flow_steps: list[str],
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """流失点聚合分析。

        计算多步流程中每一步的完成人数和流失率。

        Args:
            app_id: 应用标识
            flow_steps: 流程步骤列表
            start: 开始时间
            end: 结束时间

        Returns:
            每步的进入/完成/流失数据
        """
        results = []
        prev_count = None

        for step in flow_steps:
            pipeline = [
                {
                    "$match": {
                        "app_id": app_id,
                        "timestamp": {"$gte": start, "$lte": end},
                        "$or": [
                            {"page_url": step},
                            {"metadata.feature_name": step},
                        ],
                    }
                },
                {"$group": {"_id": None, "sessions": {"$addToSet": "$session_id"}}},
                {"$project": {"_id": 0, "count": {"$size": "$sessions"}}},
            ]
            cursor = self._collection.aggregate(pipeline)
            docs = await cursor.to_list(length=1)
            count = docs[0]["count"] if docs else 0

            if prev_count is None:
                drop_off_rate = 0.0
            elif prev_count > 0:
                drop_off_rate = round(1 - count / prev_count, 4)
            else:
                drop_off_rate = 0.0

            results.append(
                {
                    "name": step,
                    "entered": prev_count if prev_count is not None else count,
                    "completed": count,
                    "drop_off_rate": drop_off_rate,
                }
            )
            prev_count = count

        return results

    async def get_overview_stats(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        """获取概览统计数据。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间

        Returns:
            概览统计字典
        """
        base_match = {
            "app_id": app_id,
            "timestamp": {"$gte": start, "$lte": end},
        }

        # 总事件数
        total_events = await self._collection.count_documents(base_match)

        # 唯一会话和用户
        pipeline = [
            {"$match": base_match},
            {
                "$group": {
                    "_id": None,
                    "unique_sessions": {"$addToSet": "$session_id"},
                    "unique_users": {"$addToSet": "$user_id"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "unique_sessions": {"$size": "$unique_sessions"},
                    "unique_users": {
                        "$size": {
                            "$filter": {
                                "input": "$unique_users",
                                "cond": {"$ne": ["$$this", None]},
                            }
                        }
                    },
                }
            },
        ]
        cursor = self._collection.aggregate(pipeline)
        docs = await cursor.to_list(length=1)
        stats = docs[0] if docs else {"unique_sessions": 0, "unique_users": 0}

        # 热门页面
        top_pages_pipeline = [
            {"$match": {**base_match, "event_type": EventType.PAGE_VIEW}},
            {"$group": {"_id": "$page_url", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
            {"$project": {"_id": 0, "page": "$_id", "count": 1}},
        ]
        cursor = self._collection.aggregate(top_pages_pipeline)
        top_pages = await cursor.to_list(length=10)

        # 事件类型分布
        type_pipeline = [
            {"$match": base_match},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "type": "$_id", "count": 1}},
            {"$sort": {"count": -1}},
        ]
        cursor = self._collection.aggregate(type_pipeline)
        event_types = await cursor.to_list(length=20)

        return {
            "total_events": total_events,
            "unique_sessions": stats["unique_sessions"],
            "unique_users": stats["unique_users"],
            "top_pages": top_pages,
            "event_types": event_types,
        }

    async def create_indexes(self) -> None:
        """创建所有必要的索引。"""
        # 应用 + 时间范围查询
        await self._collection.create_index(
            [("app_id", 1), ("timestamp", -1)],
        )
        # 应用 + 事件类型
        await self._collection.create_index(
            [("app_id", 1), ("event_type", 1)],
        )
        # 会话重建
        await self._collection.create_index(
            [("session_id", 1), ("timestamp", 1)],
        )
        # 功能使用聚合
        await self._collection.create_index(
            [("app_id", 1), ("event_type", 1), ("metadata.feature_name", 1)],
            sparse=True,
        )
        # TTL 自动清理（默认 90 天）
        await self._collection.create_index(
            "timestamp",
            expireAfterSeconds=90 * 24 * 3600,
        )


