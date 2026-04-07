"""分析模块 Repository 测试。"""

from datetime import UTC, datetime
from typing import Any

import pytest

from taolib.analytics.models.enums import EventType
from taolib.analytics.models.event import EventDocument
from taolib.analytics.repository.event_repo import EventRepository
from taolib.analytics.repository.session_repo import SessionRepository

from .conftest import MockMongoCollection


class TestEventRepository:
    """测试 EventRepository。"""

    @pytest.fixture
    def repo(self, mock_events_collection: MockMongoCollection) -> EventRepository:
        return EventRepository(mock_events_collection)

    @pytest.mark.asyncio
    async def test_bulk_create_empty(self, repo: EventRepository) -> None:
        count = await repo.bulk_create([])
        assert count == 0

    @pytest.mark.asyncio
    async def test_bulk_create_with_data(
        self, repo: EventRepository, sample_page_view: dict[str, Any]
    ) -> None:
        sample_page_view["_id"] = "evt-001"
        count = await repo.bulk_create([sample_page_view])
        assert count == 1

    @pytest.mark.asyncio
    async def test_bulk_create_multiple(self, repo: EventRepository) -> None:
        events = [
            {
                "_id": f"evt-{i}",
                "event_type": "page_view",
                "app_id": "test-app",
                "session_id": "sess-001",
                "timestamp": datetime(2026, 4, 6, 10, 0, i, tzinfo=UTC),
                "page_url": f"/page-{i}",
                "page_title": f"Page {i}",
                "device_type": "desktop",
                "metadata": {},
            }
            for i in range(5)
        ]
        count = await repo.bulk_create(events)
        assert count == 5

    @pytest.mark.asyncio
    async def test_find_by_session(
        self,
        repo: EventRepository,
        mock_events_collection: MockMongoCollection,
    ) -> None:
        # 插入测试数据
        for i in range(3):
            await mock_events_collection.insert_one(
                {
                    "_id": f"evt-{i}",
                    "event_type": "page_view",
                    "app_id": "test-app",
                    "session_id": "sess-001",
                    "timestamp": datetime(2026, 4, 6, 10, 0, i, tzinfo=UTC),
                    "page_url": f"/page-{i}",
                    "page_title": f"Page {i}",
                    "device_type": "desktop",
                    "metadata": {},
                }
            )
        # 另一个 session 的事件
        await mock_events_collection.insert_one(
            {
                "_id": "evt-other",
                "event_type": "page_view",
                "app_id": "test-app",
                "session_id": "sess-002",
                "timestamp": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "page_url": "/other",
                "page_title": "Other",
                "device_type": "desktop",
                "metadata": {},
            }
        )

        results = await repo.find_by_session("sess-001")
        assert len(results) == 3
        assert all(isinstance(r, EventDocument) for r in results)
        assert all(r.session_id == "sess-001" for r in results)

    @pytest.mark.asyncio
    async def test_find_by_app(
        self,
        repo: EventRepository,
        mock_events_collection: MockMongoCollection,
    ) -> None:
        await mock_events_collection.insert_one(
            {
                "_id": "evt-1",
                "event_type": "page_view",
                "app_id": "test-app",
                "session_id": "sess-001",
                "timestamp": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "page_url": "/home",
                "page_title": "Home",
                "device_type": "desktop",
                "metadata": {},
            }
        )
        await mock_events_collection.insert_one(
            {
                "_id": "evt-2",
                "event_type": "click",
                "app_id": "other-app",
                "session_id": "sess-002",
                "timestamp": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "page_url": "/other",
                "page_title": "Other",
                "device_type": "desktop",
                "metadata": {},
            }
        )

        results = await repo.find_by_app(
            "test-app",
            start=datetime(2026, 4, 6, 0, 0, 0, tzinfo=UTC),
            end=datetime(2026, 4, 7, 0, 0, 0, tzinfo=UTC),
        )
        assert len(results) == 1
        assert results[0].app_id == "test-app"

    @pytest.mark.asyncio
    async def test_find_by_app_with_type_filter(
        self,
        repo: EventRepository,
        mock_events_collection: MockMongoCollection,
    ) -> None:
        await mock_events_collection.insert_one(
            {
                "_id": "evt-pv",
                "event_type": "page_view",
                "app_id": "test-app",
                "session_id": "sess-001",
                "timestamp": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "page_url": "/home",
                "page_title": "Home",
                "device_type": "desktop",
                "metadata": {},
            }
        )
        await mock_events_collection.insert_one(
            {
                "_id": "evt-cl",
                "event_type": "click",
                "app_id": "test-app",
                "session_id": "sess-001",
                "timestamp": datetime(2026, 4, 6, 10, 1, 0, tzinfo=UTC),
                "page_url": "/home",
                "page_title": "Home",
                "device_type": "desktop",
                "metadata": {},
            }
        )

        results = await repo.find_by_app(
            "test-app",
            start=datetime(2026, 4, 6, 0, 0, 0, tzinfo=UTC),
            end=datetime(2026, 4, 7, 0, 0, 0, tzinfo=UTC),
            event_type=EventType.CLICK,
        )
        assert len(results) == 1
        assert results[0].event_type == EventType.CLICK

    @pytest.mark.asyncio
    async def test_create_indexes(
        self,
        repo: EventRepository,
        mock_events_collection: MockMongoCollection,
    ) -> None:
        await repo.create_indexes()
        assert len(mock_events_collection.indexes) == 5


class TestSessionRepository:
    """测试 SessionRepository。"""

    @pytest.fixture
    def repo(self, mock_sessions_collection: MockMongoCollection) -> SessionRepository:
        return SessionRepository(mock_sessions_collection)

    @pytest.mark.asyncio
    async def test_upsert_session_create(self, repo: SessionRepository) -> None:
        session = await repo.upsert_session(
            {
                "_id": "sess-001",
                "app_id": "test-app",
                "user_id": None,
                "device_type": "desktop",
                "started_at": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "ended_at": datetime(2026, 4, 6, 10, 5, 0, tzinfo=UTC),
                "entry_page": "/home",
                "exit_page": "/settings",
                "event_count": 3,
                "pages_visited": ["/home", "/settings"],
            }
        )
        assert session.id == "sess-001"
        assert session.app_id == "test-app"

    @pytest.mark.asyncio
    async def test_upsert_session_update(self, repo: SessionRepository) -> None:
        # 第一次创建
        await repo.upsert_session(
            {
                "_id": "sess-001",
                "app_id": "test-app",
                "started_at": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "ended_at": datetime(2026, 4, 6, 10, 1, 0, tzinfo=UTC),
                "entry_page": "/home",
                "exit_page": "/home",
                "event_count": 1,
                "pages_visited": ["/home"],
            }
        )
        # 第二次更新
        session = await repo.upsert_session(
            {
                "_id": "sess-001",
                "app_id": "test-app",
                "started_at": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
                "ended_at": datetime(2026, 4, 6, 10, 5, 0, tzinfo=UTC),
                "entry_page": "/home",
                "exit_page": "/checkout",
                "event_count": 2,
                "pages_visited": ["/checkout"],
            }
        )
        assert session.exit_page == "/checkout"
        assert session.event_count == 3  # 1 + 2 (incremented)

    @pytest.mark.asyncio
    async def test_create_indexes(
        self,
        repo: SessionRepository,
        mock_sessions_collection: MockMongoCollection,
    ) -> None:
        await repo.create_indexes()
        assert len(mock_sessions_collection.indexes) == 3
