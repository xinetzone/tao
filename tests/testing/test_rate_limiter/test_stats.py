"""Tests for rate limiter statistics service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.rate_limiter.stats import RateLimitStatsService


class TestRateLimitStatsService:
    """Test statistics aggregation service."""

    @pytest.mark.asyncio
    async def test_get_top_users(self):
        """Test top users statistics."""
        mock_store = AsyncMock()
        mock_store.get_top_users.return_value = [
            ("user:123", 150),
            ("ip:1.2.3.4", 80),
        ]

        service = RateLimitStatsService(store=mock_store)
        users = await service.get_top_users(limit=10)

        assert len(users) == 2
        assert users[0].identifier == "user:123"
        assert users[0].request_count == 150
        assert users[0].identifier_type == "user"

    @pytest.mark.asyncio
    async def test_get_top_users_empty(self):
        """Test top users with no data."""
        mock_store = AsyncMock()
        mock_store.get_top_users.return_value = []

        service = RateLimitStatsService(store=mock_store)
        users = await service.get_top_users()

        assert users == []

    @pytest.mark.asyncio
    async def test_get_violation_stats_no_mongo(self):
        """Test violation stats without MongoDB."""
        mock_store = AsyncMock()
        service = RateLimitStatsService(store=mock_store, mongo_collection=None)

        violations = await service.get_violation_stats()
        assert violations == []

    @pytest.mark.asyncio
    async def test_get_violation_stats_with_mongo(self):
        """Test violation stats with MongoDB."""
        mock_store = AsyncMock()
        mock_collection = MagicMock()

        # Mock MongoDB aggregation result - need to return an async iterator
        mock_doc = {
            "_id": "user:123",
            "count": 15,
            "identifier_type": "user",
            "last_violation": datetime.now(UTC),
        }

        # Create an async iterable that returns the mock document
        async def async_gen():
            for item in [mock_doc]:
                yield item

        mock_collection.aggregate.return_value = async_gen()

        service = RateLimitStatsService(
            store=mock_store, mongo_collection=mock_collection
        )

        violations = await service.get_violation_stats(period_hours=24)
        assert len(violations) == 1
        assert violations[0].identifier == "user:123"
        assert violations[0].count == 15

    @pytest.mark.asyncio
    async def test_get_realtime_stats(self):
        """Test realtime statistics."""
        mock_store = AsyncMock()
        mock_store.get_realtime_requests.return_value = {
            "active_requests": 42,
            "requests_per_second": 0.7,
            "top_paths": [
                {"path": "/api/test", "count": 30},
                {"path": "/api/heavy", "count": 12},
            ],
        }

        service = RateLimitStatsService(store=mock_store)
        stats = await service.get_realtime(window_seconds=60)

        assert stats.active_requests == 42
        assert stats.requests_per_second == 0.7
        assert len(stats.top_paths) == 2


class TestRateLimitStatsEdgeCases:
    """统计服务边缘场景测试。"""

    @pytest.mark.asyncio
    async def test_get_violation_stats_multiple_docs(self):
        """多个违规统计文档正确聚合。"""
        mock_store = AsyncMock()
        mock_collection = MagicMock()

        docs = [
            {
                "_id": "user:a",
                "count": 20,
                "identifier_type": "user",
                "last_violation": datetime.now(UTC),
            },
            {
                "_id": "ip:1.2.3.4",
                "count": 15,
                "identifier_type": "ip",
                "last_violation": datetime.now(UTC),
            },
            {
                "_id": "user:b",
                "count": 5,
                "identifier_type": "user",
                "last_violation": None,
            },
        ]

        async def async_gen():
            for item in docs:
                yield item

        mock_collection.aggregate.return_value = async_gen()

        service = RateLimitStatsService(
            store=mock_store, mongo_collection=mock_collection
        )

        violations = await service.get_violation_stats(period_hours=48)
        assert len(violations) == 3
        assert violations[0].identifier == "user:a"
        assert violations[0].count == 20
        assert violations[1].identifier_type == "ip"
        assert violations[2].last_violation is None

    @pytest.mark.asyncio
    async def test_get_violation_stats_empty_result(self):
        """聚合结果为空。"""
        mock_store = AsyncMock()
        mock_collection = MagicMock()

        async def async_gen():
            return
            yield  # noqa: unreachable code to make this a generator

        mock_collection.aggregate.return_value = async_gen()

        service = RateLimitStatsService(
            store=mock_store, mongo_collection=mock_collection
        )

        violations = await service.get_violation_stats()
        assert violations == []

    @pytest.mark.asyncio
    async def test_get_top_users_passes_limit(self):
        """limit 参数正确传递给 store。"""
        mock_store = AsyncMock()
        mock_store.get_top_users.return_value = []

        service = RateLimitStatsService(store=mock_store)
        await service.get_top_users(limit=5)

        mock_store.get_top_users.assert_awaited_once_with(5)

    @pytest.mark.asyncio
    async def test_get_top_users_identifier_type_parsing(self):
        """identifier_type 正确解析。"""
        mock_store = AsyncMock()
        mock_store.get_top_users.return_value = [
            ("user:admin", 100),
            ("ip:10.0.0.1", 50),
            ("plain-id", 10),
        ]

        service = RateLimitStatsService(store=mock_store)
        users = await service.get_top_users()

        assert users[0].identifier_type == "user"
        assert users[1].identifier_type == "ip"
        assert users[2].identifier_type == "unknown"

    @pytest.mark.asyncio
    async def test_get_realtime_custom_window(self):
        """自定义窗口参数传递。"""
        mock_store = AsyncMock()
        mock_store.get_realtime_requests.return_value = {
            "active_requests": 0,
            "requests_per_second": 0.0,
            "top_paths": [],
        }

        service = RateLimitStatsService(store=mock_store)
        await service.get_realtime(window_seconds=300)

        mock_store.get_realtime_requests.assert_awaited_once_with(300)

    @pytest.mark.asyncio
    async def test_get_violation_stats_custom_period(self):
        """自定义统计周期。"""
        mock_store = AsyncMock()
        mock_collection = MagicMock()

        async def async_gen():
            return
            yield

        mock_collection.aggregate.return_value = async_gen()

        service = RateLimitStatsService(
            store=mock_store, mongo_collection=mock_collection
        )

        await service.get_violation_stats(period_hours=168)

        # 验证 pipeline 的 $match 使用了正确的时间范围
        call_args = mock_collection.aggregate.call_args[0][0]
        match_stage = call_args[0]
        assert "$match" in match_stage



