"""分析模块测试 fixtures。"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest


class MockCursor:
    """模拟 MongoDB 游标。"""

    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self._documents = documents

    def sort(self, *args, **kwargs):
        return self

    def skip(self, n):
        self._documents = self._documents[n:]
        return self

    def limit(self, n):
        self._documents = self._documents[:n]
        return self

    async def to_list(self, length=None):
        if length is not None:
            return self._documents[:length]
        return self._documents


class MockMongoCollection:
    """模拟 MongoDB 集合。"""

    def __init__(self, name: str = "test_collection") -> None:
        self._documents: dict[str, dict[str, Any]] = {}
        self._next_id = 1
        self.indexes: list[dict[str, Any]] = []
        self.name = name

    async def insert_one(self, document: dict[str, Any]) -> Any:
        if "_id" not in document:
            document["_id"] = f"auto_{self._next_id}"
            self._next_id += 1
        doc_id = document["_id"]
        self._documents[doc_id] = dict(document)
        result = MagicMock()
        result.inserted_id = doc_id
        return result

    async def insert_many(self, documents: list[dict[str, Any]]) -> Any:
        ids = []
        for doc in documents:
            result = await self.insert_one(doc)
            ids.append(result.inserted_id)
        result = MagicMock()
        result.inserted_ids = ids
        return result

    async def find_one(self, filter_dict: dict[str, Any]) -> dict[str, Any] | None:
        for doc in self._documents.values():
            if self._matches_filter(doc, filter_dict):
                return dict(doc)
        return None

    def find(self, filter_dict: dict[str, Any] | None = None, **kwargs) -> MockCursor:
        if filter_dict is None:
            return MockCursor(list(self._documents.values()))
        matched = [
            dict(doc)
            for doc in self._documents.values()
            if self._matches_filter(doc, filter_dict)
        ]
        return MockCursor(matched)

    async def find_one_and_update(
        self,
        filter_dict: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
        return_document: bool = False,
    ) -> dict[str, Any] | None:
        doc = None
        for d in self._documents.values():
            if self._matches_filter(d, filter_dict):
                doc = d
                break

        if doc is None and upsert:
            doc_id = filter_dict.get("_id", f"auto_{self._next_id}")
            self._next_id += 1
            doc = {"_id": doc_id}
            self._documents[doc_id] = doc

        if doc is None:
            return None

        # Apply $set
        if "$set" in update:
            doc.update(update["$set"])
        # Apply $setOnInsert (only on new docs)
        if "$setOnInsert" in update and upsert:
            for k, v in update["$setOnInsert"].items():
                if k not in doc:
                    doc[k] = v
        # Apply $inc
        if "$inc" in update:
            for k, v in update["$inc"].items():
                doc[k] = doc.get(k, 0) + v
        # Apply $addToSet
        if "$addToSet" in update:
            for k, v in update["$addToSet"].items():
                if k not in doc:
                    doc[k] = []
                if isinstance(v, dict) and "$each" in v:
                    for item in v["$each"]:
                        if item not in doc[k]:
                            doc[k].append(item)
                elif v not in doc[k]:
                    doc[k].append(v)

        return dict(doc)

    async def delete_one(self, filter_dict: dict[str, Any]) -> Any:
        for doc_id, doc in list(self._documents.items()):
            if self._matches_filter(doc, filter_dict):
                del self._documents[doc_id]
                result = MagicMock()
                result.deleted_count = 1
                return result
        result = MagicMock()
        result.deleted_count = 0
        return result

    async def count_documents(self, filter_dict: dict[str, Any] | None = None) -> int:
        if not filter_dict:
            return len(self._documents)
        return sum(
            1
            for doc in self._documents.values()
            if self._matches_filter(doc, filter_dict)
        )

    async def create_index(self, keys, **kwargs) -> str:
        self.indexes.append({"keys": keys, **kwargs})
        return f"index_{len(self.indexes)}"

    def aggregate(self, pipeline: list[dict]) -> MockCursor:
        # 简化的聚合模拟 - 返回空结果
        return MockCursor([])

    def _matches_filter(self, doc: dict, filter_dict: dict) -> bool:
        for key, value in filter_dict.items():
            if key == "$or":
                if not any(self._matches_filter(doc, sub) for sub in value):
                    return False
                continue
            if key == "$and":
                if not all(self._matches_filter(doc, sub) for sub in value):
                    return False
                continue

            # 嵌套字段处理
            doc_value = doc
            for part in key.split("."):
                if isinstance(doc_value, dict):
                    doc_value = doc_value.get(part)
                else:
                    doc_value = None
                    break

            if isinstance(value, dict):
                for op, op_val in value.items():
                    if op == "$gte" and (doc_value is None or doc_value < op_val):
                        return False
                    if op == "$lte" and (doc_value is None or doc_value > op_val):
                        return False
                    if op == "$in" and doc_value not in op_val:
                        return False
            elif doc_value != value:
                return False
        return True


@pytest.fixture
def mock_events_collection() -> MockMongoCollection:
    """事件集合 mock。"""
    return MockMongoCollection("analytics_events")


@pytest.fixture
def mock_sessions_collection() -> MockMongoCollection:
    """会话集合 mock。"""
    return MockMongoCollection("analytics_sessions")


@pytest.fixture
def mock_mongo_db(
    mock_events_collection: MockMongoCollection,
    mock_sessions_collection: MockMongoCollection,
) -> MagicMock:
    """模拟 MongoDB 数据库。"""
    db = MagicMock()
    db.analytics_events = mock_events_collection
    db.analytics_sessions = mock_sessions_collection
    return db


@pytest.fixture
def sample_page_view() -> dict[str, Any]:
    """示例页面浏览事件。"""
    return {
        "event_type": "page_view",
        "app_id": "test-app",
        "session_id": "sess-001",
        "user_id": None,
        "timestamp": datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC),
        "page_url": "/home",
        "page_title": "Home",
        "referrer": None,
        "device_type": "desktop",
        "user_agent": "TestAgent/1.0",
        "screen_width": 1920,
        "screen_height": 1080,
        "metadata": {},
    }


@pytest.fixture
def sample_click_event() -> dict[str, Any]:
    """示例点击事件。"""
    return {
        "event_type": "click",
        "app_id": "test-app",
        "session_id": "sess-001",
        "user_id": "user-123",
        "timestamp": datetime(2026, 4, 6, 10, 1, 0, tzinfo=UTC),
        "page_url": "/home",
        "page_title": "Home",
        "referrer": None,
        "device_type": "desktop",
        "user_agent": "TestAgent/1.0",
        "screen_width": 1920,
        "screen_height": 1080,
        "metadata": {
            "element_selector": "#signup-btn",
            "element_text": "Sign Up",
            "element_id": "signup-btn",
            "click_x": 500,
            "click_y": 300,
        },
    }


@pytest.fixture
def sample_feature_event() -> dict[str, Any]:
    """示例功能使用事件。"""
    return {
        "event_type": "feature_use",
        "app_id": "test-app",
        "session_id": "sess-001",
        "user_id": "user-123",
        "timestamp": datetime(2026, 4, 6, 10, 2, 0, tzinfo=UTC),
        "page_url": "/settings",
        "page_title": "Settings",
        "referrer": "/home",
        "device_type": "desktop",
        "user_agent": "TestAgent/1.0",
        "screen_width": 1920,
        "screen_height": 1080,
        "metadata": {
            "feature_name": "dark-mode",
            "feature_category": "settings",
        },
    }


@pytest.fixture
def sample_event_batch() -> list[dict[str, Any]]:
    """示例批量事件（模拟完整用户会话）。"""
    base_ts = datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC)
    return [
        {
            "event_type": "session_start",
            "app_id": "test-app",
            "session_id": "sess-batch-001",
            "user_id": None,
            "timestamp": base_ts,
            "page_url": "/",
            "page_title": "Landing",
            "referrer": None,
            "device_type": "desktop",
            "user_agent": "TestAgent/1.0",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {},
        },
        {
            "event_type": "page_view",
            "app_id": "test-app",
            "session_id": "sess-batch-001",
            "user_id": None,
            "timestamp": base_ts,
            "page_url": "/",
            "page_title": "Landing",
            "referrer": None,
            "device_type": "desktop",
            "user_agent": "TestAgent/1.0",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {},
        },
        {
            "event_type": "click",
            "app_id": "test-app",
            "session_id": "sess-batch-001",
            "user_id": None,
            "timestamp": datetime(2026, 4, 6, 10, 0, 15, tzinfo=UTC),
            "page_url": "/",
            "page_title": "Landing",
            "referrer": None,
            "device_type": "desktop",
            "user_agent": "TestAgent/1.0",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {"element_selector": "a.cta", "element_text": "Get Started"},
        },
        {
            "event_type": "page_view",
            "app_id": "test-app",
            "session_id": "sess-batch-001",
            "user_id": None,
            "timestamp": datetime(2026, 4, 6, 10, 0, 16, tzinfo=UTC),
            "page_url": "/signup",
            "page_title": "Sign Up",
            "referrer": "/",
            "device_type": "desktop",
            "user_agent": "TestAgent/1.0",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {},
        },
        {
            "event_type": "feature_use",
            "app_id": "test-app",
            "session_id": "sess-batch-001",
            "user_id": "user-new",
            "timestamp": datetime(2026, 4, 6, 10, 1, 0, tzinfo=UTC),
            "page_url": "/signup",
            "page_title": "Sign Up",
            "referrer": "/",
            "device_type": "desktop",
            "user_agent": "TestAgent/1.0",
            "screen_width": 1920,
            "screen_height": 1080,
            "metadata": {"feature_name": "social-login", "feature_category": "auth"},
        },
    ]
