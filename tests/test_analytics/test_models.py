"""分析模块模型测试。"""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from taolib.analytics.models.enums import DeviceType, EventType
from taolib.analytics.models.event import (
    EventBatchCreate,
    EventCreate,
    EventDocument,
    EventResponse,
    SessionDocument,
)


class TestEventTypeEnum:
    """测试 EventType 枚举。"""

    def test_all_values(self) -> None:
        assert EventType.PAGE_VIEW == "page_view"
        assert EventType.CLICK == "click"
        assert EventType.FEATURE_USE == "feature_use"
        assert EventType.SESSION_START == "session_start"
        assert EventType.SESSION_END == "session_end"
        assert EventType.NAVIGATION == "navigation"
        assert EventType.TIME_ON_SECTION == "time_on_section"
        assert EventType.CUSTOM == "custom"

    def test_member_count(self) -> None:
        assert len(EventType) == 8


class TestDeviceTypeEnum:
    """测试 DeviceType 枚举。"""

    def test_all_values(self) -> None:
        assert DeviceType.DESKTOP == "desktop"
        assert DeviceType.MOBILE == "mobile"
        assert DeviceType.TABLET == "tablet"
        assert DeviceType.UNKNOWN == "unknown"

    def test_member_count(self) -> None:
        assert len(DeviceType) == 4


class TestEventCreate:
    """测试 EventCreate 模型。"""

    def test_valid_creation(self, sample_page_view: dict[str, Any]) -> None:
        event = EventCreate(**sample_page_view)
        assert event.event_type == EventType.PAGE_VIEW
        assert event.app_id == "test-app"
        assert event.session_id == "sess-001"
        assert event.page_url == "/home"
        assert event.device_type == DeviceType.DESKTOP

    def test_valid_with_metadata(self, sample_click_event: dict[str, Any]) -> None:
        event = EventCreate(**sample_click_event)
        assert event.metadata["element_selector"] == "#signup-btn"
        assert event.metadata["element_text"] == "Sign Up"
        assert event.user_id == "user-123"

    def test_missing_app_id(self, sample_page_view: dict[str, Any]) -> None:
        del sample_page_view["app_id"]
        with pytest.raises(ValidationError):
            EventCreate(**sample_page_view)

    def test_missing_session_id(self, sample_page_view: dict[str, Any]) -> None:
        del sample_page_view["session_id"]
        with pytest.raises(ValidationError):
            EventCreate(**sample_page_view)

    def test_empty_app_id(self, sample_page_view: dict[str, Any]) -> None:
        sample_page_view["app_id"] = ""
        with pytest.raises(ValidationError):
            EventCreate(**sample_page_view)

    def test_default_device_type(self) -> None:
        event = EventCreate(
            event_type="page_view",
            app_id="app",
            session_id="sess",
            page_url="/",
        )
        assert event.device_type == DeviceType.UNKNOWN

    def test_default_metadata(self) -> None:
        event = EventCreate(
            event_type="page_view",
            app_id="app",
            session_id="sess",
            page_url="/",
        )
        assert event.metadata == {}

    def test_default_timestamp(self) -> None:
        event = EventCreate(
            event_type="page_view",
            app_id="app",
            session_id="sess",
            page_url="/",
        )
        assert event.timestamp is not None
        assert event.timestamp.tzinfo is not None


class TestEventBatchCreate:
    """测试 EventBatchCreate 模型。"""

    def test_valid_batch(self, sample_event_batch: list[dict[str, Any]]) -> None:
        batch = EventBatchCreate(events=sample_event_batch)
        assert len(batch.events) == 5

    def test_empty_batch(self) -> None:
        with pytest.raises(ValidationError):
            EventBatchCreate(events=[])

    def test_single_event_batch(self, sample_page_view: dict[str, Any]) -> None:
        batch = EventBatchCreate(events=[sample_page_view])
        assert len(batch.events) == 1


class TestEventDocument:
    """测试 EventDocument 模型。"""

    def test_creation_with_id(self, sample_page_view: dict[str, Any]) -> None:
        sample_page_view["_id"] = "evt-001"
        doc = EventDocument(**sample_page_view)
        assert doc.id == "evt-001"
        assert doc.app_id == "test-app"

    def test_to_response(self, sample_page_view: dict[str, Any]) -> None:
        sample_page_view["_id"] = "evt-001"
        doc = EventDocument(**sample_page_view)
        response = doc.to_response()
        assert isinstance(response, EventResponse)
        assert response.id == "evt-001"
        assert response.event_type == EventType.PAGE_VIEW
        assert response.app_id == doc.app_id
        assert response.session_id == doc.session_id

    def test_populate_by_name(self, sample_page_view: dict[str, Any]) -> None:
        sample_page_view["_id"] = "evt-002"
        doc = EventDocument(**sample_page_view)
        assert doc.id == "evt-002"


class TestSessionDocument:
    """测试 SessionDocument 模型。"""

    def test_creation(self) -> None:
        session = SessionDocument(
            _id="sess-001",
            app_id="test-app",
            started_at=datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
            entry_page="/home",
        )
        assert session.id == "sess-001"
        assert session.app_id == "test-app"
        assert session.page_count == 0
        assert session.event_count == 0
        assert session.pages_visited == []
        assert session.ended_at is None
        assert session.duration_seconds is None

    def test_full_session(self) -> None:
        session = SessionDocument(
            _id="sess-002",
            app_id="test-app",
            user_id="user-123",
            device_type=DeviceType.MOBILE,
            started_at=datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
            ended_at=datetime(2026, 4, 6, 10, 5, 0, tzinfo=UTC),
            duration_seconds=300.0,
            page_count=5,
            event_count=12,
            entry_page="/home",
            exit_page="/checkout",
            pages_visited=["/home", "/products", "/cart", "/checkout"],
        )
        assert session.user_id == "user-123"
        assert session.duration_seconds == 300.0
        assert session.page_count == 5
        assert len(session.pages_visited) == 4
