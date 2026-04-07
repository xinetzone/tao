"""分析业务逻辑服务。

提供事件摄入和分析查询的业务逻辑。
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from taolib.analytics.models.enums import EventType
from taolib.analytics.models.event import EventCreate
from taolib.analytics.repository.event_repo import EventRepository
from taolib.analytics.repository.session_repo import SessionRepository


class AnalyticsService:
    """分析服务。"""

    def __init__(
        self,
        event_repo: EventRepository,
        session_repo: SessionRepository,
    ) -> None:
        """初始化分析服务。

        Args:
            event_repo: 事件 Repository
            session_repo: 会话 Repository
        """
        self._event_repo = event_repo
        self._session_repo = session_repo

    async def ingest_events(
        self,
        events: list[EventCreate],
    ) -> dict[str, Any]:
        """摄入事件数据。

        Args:
            events: 事件列表

        Returns:
            摄入结果 {"accepted": int, "rejected": int}
        """
        if not events:
            return {"accepted": 0, "rejected": 0}

        accepted = 0
        rejected = 0
        event_dicts: list[dict[str, Any]] = []
        session_updates: dict[str, dict[str, Any]] = {}

        for event in events:
            try:
                event_dict = event.model_dump()
                event_dict["_id"] = str(uuid.uuid4())
                event_dicts.append(event_dict)

                # 收集会话更新数据
                sid = event.session_id
                if sid not in session_updates:
                    session_updates[sid] = {
                        "_id": sid,
                        "app_id": event.app_id,
                        "user_id": event.user_id,
                        "device_type": event.device_type,
                        "started_at": event.timestamp,
                        "ended_at": event.timestamp,
                        "entry_page": event.page_url,
                        "exit_page": event.page_url,
                        "event_count": 1,
                        "pages_visited": (
                            [event.page_url]
                            if event.event_type == EventType.PAGE_VIEW
                            else []
                        ),
                    }
                else:
                    s = session_updates[sid]
                    s["ended_at"] = max(s["ended_at"], event.timestamp)
                    s["exit_page"] = event.page_url
                    s["event_count"] += 1
                    if event.user_id:
                        s["user_id"] = event.user_id
                    if event.event_type == EventType.PAGE_VIEW:
                        if event.page_url not in s["pages_visited"]:
                            s["pages_visited"].append(event.page_url)

                accepted += 1
            except Exception:
                rejected += 1

        # 批量写入事件
        if event_dicts:
            await self._event_repo.bulk_create(event_dicts)

        # 更新会话
        for session_data in session_updates.values():
            await self._session_repo.upsert_session(session_data)

        return {"accepted": accepted, "rejected": rejected}

    async def get_overview(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        """获取概览统计。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间

        Returns:
            概览统计数据
        """
        event_stats = await self._event_repo.get_overview_stats(app_id, start, end)
        session_stats = await self._session_repo.get_session_stats(app_id, start, end)
        return {**event_stats, **session_stats}

    async def get_funnel(
        self,
        app_id: str,
        steps: list[str],
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        """获取转化漏斗分析。

        Args:
            app_id: 应用标识
            steps: 漏斗步骤列表
            start: 开始时间
            end: 结束时间

        Returns:
            漏斗分析数据
        """
        raw_steps = await self._event_repo.aggregate_funnel(app_id, steps, start, end)

        # 计算转化率
        result_steps = []
        first_count = raw_steps[0]["count"] if raw_steps else 0
        for i, step in enumerate(raw_steps):
            prev_count = raw_steps[i - 1]["count"] if i > 0 else step["count"]
            conversion_rate = (
                round(step["count"] / prev_count, 4) if prev_count > 0 else 0.0
            )
            result_steps.append(
                {
                    "name": step["name"],
                    "count": step["count"],
                    "conversion_rate": conversion_rate,
                }
            )

        overall = (
            round(raw_steps[-1]["count"] / first_count, 4)
            if raw_steps and first_count > 0
            else 0.0
        )

        return {"steps": result_steps, "overall_conversion": overall}

    async def get_feature_ranking(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
        limit: int = 20,
    ) -> dict[str, Any]:
        """获取功能使用排名。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间
            limit: 返回数量限制

        Returns:
            功能排名数据
        """
        features = await self._event_repo.aggregate_feature_usage(
            app_id, start, end, limit
        )
        return {"features": features}

    async def get_navigation_paths(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
        limit: int = 50,
    ) -> dict[str, Any]:
        """获取用户导航路径。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间
            limit: 返回数量限制

        Returns:
            导航路径数据 (Sankey 格式)
        """
        paths = await self._event_repo.aggregate_navigation_paths(
            app_id, start, end, limit
        )
        return {"paths": paths}

    async def get_retention(
        self,
        app_id: str,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        """获取区域停留时间分析。

        Args:
            app_id: 应用标识
            start: 开始时间
            end: 结束时间

        Returns:
            区域停留时间数据
        """
        sections = await self._event_repo.aggregate_time_on_section(app_id, start, end)
        return {"sections": sections}

    async def get_drop_off(
        self,
        app_id: str,
        flow_steps: list[str],
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        """获取流失点分析。

        Args:
            app_id: 应用标识
            flow_steps: 流程步骤列表
            start: 开始时间
            end: 结束时间

        Returns:
            流失分析数据
        """
        steps = await self._event_repo.aggregate_drop_off(
            app_id, flow_steps, start, end
        )
        return {"steps": steps}

    @staticmethod
    def default_time_range() -> tuple[datetime, datetime]:
        """获取默认时间范围（最近 7 天）。"""
        end = datetime.now(UTC)
        start = datetime(end.year, end.month, end.day, tzinfo=UTC).__class__(
            end.year,
            end.month,
            end.day,
            tzinfo=UTC,
        )
        from datetime import timedelta

        start = end - timedelta(days=7)
        return start, end
