"""Tests for violation tracker."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from taolib.testing.rate_limiter.violation_tracker import ViolationTracker


@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.create_index = AsyncMock()
    return collection


@pytest.fixture
def tracker(mock_collection):
    """Create a ViolationTracker with mock collection."""
    return ViolationTracker(mongo_collection=mock_collection, ttl_days=90)


class TestViolationTracker:
    """Test violation tracker functionality."""

    @pytest.mark.asyncio
    async def test_record_violation_user(self, tracker, mock_collection):
        """Test recording a violation for a user."""
        await tracker.record_violation(
            identifier="user:123",
            ip_address="1.2.3.4",
            path="/api/test",
            method="GET",
            request_count=101,
            limit=100,
            window_seconds=60,
            retry_after=45,
            user_id="123",
            user_agent="test-agent",
        )

        mock_collection.insert_one.assert_called_once()
        doc = mock_collection.insert_one.call_args[0][0]

        assert doc["identifier"] == "user:123"
        assert doc["identifier_type"] == "user"
        assert doc["user_id"] == "123"
        assert doc["ip_address"] == "1.2.3.4"
        assert doc["path"] == "/api/test"
        assert doc["method"] == "GET"
        assert doc["request_count"] == 101
        assert doc["limit"] == 100
        assert doc["window_seconds"] == 60
        assert doc["retry_after"] == 45
        assert doc["user_agent"] == "test-agent"
        assert "timestamp" in doc

    @pytest.mark.asyncio
    async def test_record_violation_ip(self, tracker, mock_collection):
        """Test recording a violation for an IP."""
        await tracker.record_violation(
            identifier="ip:5.6.7.8",
            ip_address="5.6.7.8",
            path="/api/heavy",
            method="POST",
            request_count=11,
            limit=10,
            window_seconds=60,
            retry_after=30,
        )

        mock_collection.insert_one.assert_called_once()
        doc = mock_collection.insert_one.call_args[0][0]

        assert doc["identifier"] == "ip:5.6.7.8"
        assert doc["identifier_type"] == "ip"
        assert doc["user_id"] is None
        assert doc["ip_address"] == "5.6.7.8"

    @pytest.mark.asyncio
    async def test_record_violation_without_optional_fields(
        self, tracker, mock_collection
    ):
        """Test recording violation without user_id and user_agent."""
        await tracker.record_violation(
            identifier="ip:1.2.3.4",
            ip_address="1.2.3.4",
            path="/api/test",
            method="GET",
            request_count=50,
            limit=10,
            window_seconds=60,
            retry_after=10,
        )

        doc = mock_collection.insert_one.call_args[0][0]
        assert doc["user_id"] is None
        assert doc["user_agent"] is None

    @pytest.mark.asyncio
    async def test_ensure_indexes(self, tracker, mock_collection):
        """Test ensuring MongoDB indexes."""
        await tracker.ensure_indexes()

        assert mock_collection.create_index.call_count == 3

        # Check TTL index
        mock_collection.create_index.assert_any_call(
            "timestamp", expireAfterSeconds=90 * 86400
        )

        # Check compound index
        mock_collection.create_index.assert_any_call(
            [("identifier", 1), ("timestamp", 1)]
        )

        # Check identifier_type index
        mock_collection.create_index.assert_any_call(
            [("identifier_type", 1), ("timestamp", 1)]
        )

    @pytest.mark.asyncio
    async def test_ensure_indexes_custom_ttl(self, mock_collection):
        """Test ensure_indexes with custom TTL."""
        tracker = ViolationTracker(mongo_collection=mock_collection, ttl_days=30)
        await tracker.ensure_indexes()

        mock_collection.create_index.assert_any_call(
            "timestamp", expireAfterSeconds=30 * 86400
        )


class TestViolationTrackerEdgeCases:
    """违规追踪器边缘场景测试。"""

    @pytest.mark.asyncio
    async def test_unknown_identifier_type_raises_validation_error(
        self, mock_collection
    ):
        """无冒号的标识符导致 'unknown' 类型，ViolationDocument 只接受 'user'/'ip'。"""
        from pydantic import ValidationError

        tracker = ViolationTracker(mongo_collection=mock_collection)
        with pytest.raises(ValidationError):
            await tracker.record_violation(
                identifier="plain-identifier",
                ip_address="1.2.3.4",
                path="/api/test",
                method="GET",
                request_count=101,
                limit=100,
                window_seconds=60,
                retry_after=45,
            )

    @pytest.mark.asyncio
    async def test_violation_timestamp_is_recent(self, mock_collection):
        """记录的违规文档包含近期时间戳。"""
        tracker = ViolationTracker(mongo_collection=mock_collection)
        before = datetime.now(UTC)
        await tracker.record_violation(
            identifier="user:123",
            ip_address="1.2.3.4",
            path="/api",
            method="GET",
            request_count=11,
            limit=10,
            window_seconds=60,
            retry_after=30,
        )
        after = datetime.now(UTC)

        doc = mock_collection.insert_one.call_args[0][0]
        assert before <= doc["timestamp"] <= after

    @pytest.mark.asyncio
    async def test_violation_ipv6_address(self, mock_collection):
        """IPv6 地址记录正常。"""
        tracker = ViolationTracker(mongo_collection=mock_collection)
        await tracker.record_violation(
            identifier="ip:::1",
            ip_address="::1",
            path="/api",
            method="GET",
            request_count=11,
            limit=10,
            window_seconds=60,
            retry_after=30,
        )

        doc = mock_collection.insert_one.call_args[0][0]
        assert doc["ip_address"] == "::1"
        assert doc["identifier_type"] == "ip"

    @pytest.mark.asyncio
    async def test_record_violation_propagates_db_error(self, mock_collection):
        """MongoDB 写入失败时异常传播。"""
        mock_collection.insert_one.side_effect = RuntimeError("DB error")
        tracker = ViolationTracker(mongo_collection=mock_collection)

        with pytest.raises(RuntimeError, match="DB error"):
            await tracker.record_violation(
                identifier="user:123",
                ip_address="1.2.3.4",
                path="/api",
                method="GET",
                request_count=11,
                limit=10,
                window_seconds=60,
                retry_after=30,
            )

    @pytest.mark.asyncio
    async def test_record_multiple_violations(self, mock_collection):
        """连续记录多次违规。"""
        tracker = ViolationTracker(mongo_collection=mock_collection)
        for i in range(3):
            await tracker.record_violation(
                identifier=f"user:{i}",
                ip_address="1.2.3.4",
                path="/api",
                method="GET",
                request_count=11,
                limit=10,
                window_seconds=60,
                retry_after=30,
            )

        assert mock_collection.insert_one.call_count == 3

    @pytest.mark.asyncio
    async def test_default_ttl_days(self, mock_collection):
        """默认 ttl_days=90。"""
        tracker = ViolationTracker(mongo_collection=mock_collection)
        await tracker.ensure_indexes()

        mock_collection.create_index.assert_any_call(
            "timestamp", expireAfterSeconds=90 * 86400
        )

    @pytest.mark.asyncio
    async def test_violation_document_has_all_fields(self, mock_collection):
        """违规文档包含所有必要字段。"""
        tracker = ViolationTracker(mongo_collection=mock_collection)
        await tracker.record_violation(
            identifier="user:admin",
            ip_address="10.0.0.1",
            path="/api/heavy",
            method="POST",
            request_count=200,
            limit=100,
            window_seconds=120,
            retry_after=60,
            user_id="admin",
            user_agent="Mozilla/5.0",
        )

        doc = mock_collection.insert_one.call_args[0][0]
        expected_keys = {
            "identifier",
            "identifier_type",
            "user_id",
            "ip_address",
            "path",
            "method",
            "request_count",
            "limit",
            "window_seconds",
            "retry_after",
            "user_agent",
            "timestamp",
            "_id",
        }
        assert expected_keys.issubset(set(doc.keys()))



