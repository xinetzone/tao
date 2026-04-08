"""分析模块 Service 测试。"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.analytics.models.event import EventCreate
from taolib.testing.analytics.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """测试 AnalyticsService。"""

    @pytest.fixture
    def mock_event_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.bulk_create = AsyncMock(return_value=5)
        repo.get_overview_stats = AsyncMock(
            return_value={
                "total_events": 100,
                "unique_sessions": 20,
                "unique_users": 15,
                "top_pages": [{"page": "/home", "count": 50}],
                "event_types": [{"type": "page_view", "count": 60}],
            }
        )
        repo.aggregate_funnel = AsyncMock(
            return_value=[
                {"name": "/home", "count": 100},
                {"name": "/signup", "count": 60},
                {"name": "/dashboard", "count": 30},
            ]
        )
        repo.aggregate_feature_usage = AsyncMock(
            return_value=[
                {
                    "name": "dark-mode",
                    "category": "settings",
                    "count": 50,
                    "unique_users": 30,
                },
                {
                    "name": "export",
                    "category": "tools",
                    "count": 25,
                    "unique_users": 15,
                },
            ]
        )
        repo.aggregate_navigation_paths = AsyncMock(
            return_value=[
                {"source": "/home", "target": "/products", "value": 40},
                {"source": "/products", "target": "/cart", "value": 20},
            ]
        )
        repo.aggregate_time_on_section = AsyncMock(
            return_value=[
                {"section_id": "hero", "avg_duration_ms": 5000, "total_views": 100},
            ]
        )
        repo.aggregate_drop_off = AsyncMock(
            return_value=[
                {
                    "name": "/cart",
                    "entered": 100,
                    "completed": 100,
                    "drop_off_rate": 0.0,
                },
                {
                    "name": "/checkout",
                    "entered": 100,
                    "completed": 60,
                    "drop_off_rate": 0.4,
                },
                {
                    "name": "/payment",
                    "entered": 60,
                    "completed": 45,
                    "drop_off_rate": 0.25,
                },
            ]
        )
        return repo

    @pytest.fixture
    def mock_session_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.upsert_session = AsyncMock()
        repo.get_session_stats = AsyncMock(
            return_value={
                "total_sessions": 20,
                "avg_duration_seconds": 120.5,
                "avg_page_count": 3.2,
                "bounce_rate": 0.35,
            }
        )
        return repo

    @pytest.fixture
    def service(
        self, mock_event_repo: MagicMock, mock_session_repo: MagicMock
    ) -> AnalyticsService:
        return AnalyticsService(mock_event_repo, mock_session_repo)

    @pytest.mark.asyncio
    async def test_ingest_events(
        self,
        service: AnalyticsService,
        mock_event_repo: MagicMock,
        mock_session_repo: MagicMock,
        sample_event_batch: list[dict[str, Any]],
    ) -> None:
        events = [EventCreate(**e) for e in sample_event_batch]
        result = await service.ingest_events(events)

        assert result["accepted"] == 5
        assert result["rejected"] == 0
        mock_event_repo.bulk_create.assert_called_once()
        # 所有事件同一 session，所以只 upsert 一次
        mock_session_repo.upsert_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_ingest_empty_events(self, service: AnalyticsService) -> None:
        result = await service.ingest_events([])
        assert result["accepted"] == 0
        assert result["rejected"] == 0

    @pytest.mark.asyncio
    async def test_get_overview(
        self,
        service: AnalyticsService,
        mock_event_repo: MagicMock,
    ) -> None:
        start = datetime(2026, 4, 1, tzinfo=UTC)
        end = datetime(2026, 4, 7, tzinfo=UTC)
        result = await service.get_overview("test-app", start, end)

        assert result["total_events"] == 100
        assert result["unique_sessions"] == 20
        assert result["unique_users"] == 15
        assert result["total_sessions"] == 20
        assert result["avg_duration_seconds"] == 120.5
        mock_event_repo.get_overview_stats.assert_called_once_with(
            "test-app", start, end
        )

    @pytest.mark.asyncio
    async def test_get_funnel(
        self,
        service: AnalyticsService,
        mock_event_repo: MagicMock,
    ) -> None:
        start = datetime(2026, 4, 1, tzinfo=UTC)
        end = datetime(2026, 4, 7, tzinfo=UTC)
        steps = ["/home", "/signup", "/dashboard"]
        result = await service.get_funnel("test-app", steps, start, end)

        assert "steps" in result
        assert len(result["steps"]) == 3
        assert result["steps"][0]["name"] == "/home"
        assert result["steps"][0]["count"] == 100
        assert result["overall_conversion"] == 0.3  # 30/100

    @pytest.mark.asyncio
    async def test_get_feature_ranking(
        self,
        service: AnalyticsService,
        mock_event_repo: MagicMock,
    ) -> None:
        start = datetime(2026, 4, 1, tzinfo=UTC)
        end = datetime(2026, 4, 7, tzinfo=UTC)
        result = await service.get_feature_ranking("test-app", start, end)

        assert "features" in result
        assert len(result["features"]) == 2
        assert result["features"][0]["name"] == "dark-mode"

    @pytest.mark.asyncio
    async def test_get_navigation_paths(
        self,
        service: AnalyticsService,
        mock_event_repo: MagicMock,
    ) -> None:
        start = datetime(2026, 4, 1, tzinfo=UTC)
        end = datetime(2026, 4, 7, tzinfo=UTC)
        result = await service.get_navigation_paths("test-app", start, end)

        assert "paths" in result
        assert len(result["paths"]) == 2
        assert result["paths"][0]["source"] == "/home"
        assert result["paths"][0]["target"] == "/products"

    @pytest.mark.asyncio
    async def test_get_retention(
        self,
        service: AnalyticsService,
    ) -> None:
        start = datetime(2026, 4, 1, tzinfo=UTC)
        end = datetime(2026, 4, 7, tzinfo=UTC)
        result = await service.get_retention("test-app", start, end)

        assert "sections" in result
        assert len(result["sections"]) == 1
        assert result["sections"][0]["section_id"] == "hero"

    @pytest.mark.asyncio
    async def test_get_drop_off(
        self,
        service: AnalyticsService,
    ) -> None:
        start = datetime(2026, 4, 1, tzinfo=UTC)
        end = datetime(2026, 4, 7, tzinfo=UTC)
        steps = ["/cart", "/checkout", "/payment"]
        result = await service.get_drop_off("test-app", steps, start, end)

        assert "steps" in result
        assert len(result["steps"]) == 3
        assert result["steps"][1]["drop_off_rate"] == 0.4

    @pytest.mark.asyncio
    async def test_default_time_range(self) -> None:
        start, end = AnalyticsService.default_time_range()
        assert start < end
        diff = (end - start).total_seconds()
        # 大约 7 天
        assert 6 * 86400 < diff < 8 * 86400



