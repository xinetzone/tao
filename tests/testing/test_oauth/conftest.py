"""OAuth 模块测试 fixtures 和工具。

提供 Mock 数据库连接、测试数据工厂和通用 fixtures。
"""

import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ---------------------------------------------------------------------------
# Mock MongoDB
# ---------------------------------------------------------------------------


class MockCursor:
    """Mock Motor cursor."""

    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self._documents = list(documents)
        self._skip = 0
        self._limit: int | None = None
        self._sort_fields: list[tuple[str, int]] | None = None

    def skip(self, n: int):
        self._skip = n
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def sort(self, key_or_list, direction: int | None = None):
        if isinstance(key_or_list, list):
            self._sort_fields = key_or_list
        else:
            self._sort_fields = [(key_or_list, direction or 1)]
        return self

    async def to_list(self, length: int | None = None) -> list[dict[str, Any]]:
        results = list(self._documents)
        if self._sort_fields:
            for field, order in reversed(self._sort_fields):
                results.sort(key=lambda x: x.get(field, ""), reverse=(order == -1))
        results = results[self._skip :]
        effective_limit = self._limit or length
        if effective_limit:
            results = results[:effective_limit]
        return results


class MockMongoCollection:
    """Mock MongoDB collection for testing."""

    def __init__(self, name: str = "test_collection") -> None:
        self.name = name
        self._documents: dict[str, dict[str, Any]] = {}
        self._next_id = 1
        self.indexes: list[dict[str, Any]] = []

    async def insert_one(self, document: dict[str, Any]) -> Any:
        if document.get("_id"):
            doc_id = str(document["_id"])
        else:
            doc_id = str(self._next_id)
            self._next_id += 1
        document["_id"] = doc_id
        self._documents[doc_id] = document.copy()
        mock_result = MagicMock()
        mock_result.inserted_id = doc_id
        return mock_result

    async def find_one(
        self, filter: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any] | None:
        results = []
        for doc in self._documents.values():
            if self._matches_filter(doc, filter):
                results.append(doc.copy())
        if not results:
            return None
        sort_fields = kwargs.get("sort")
        if sort_fields and isinstance(sort_fields, list):
            for field, order in reversed(sort_fields):
                results.sort(key=lambda x: x.get(field, ""), reverse=(order == -1))
        return results[0]

    def find(self, filter: dict[str, Any] = None, **kwargs: Any) -> MockCursor:
        filter = filter or {}
        results = []
        for doc in self._documents.values():
            if self._matches_filter(doc, filter):
                results.append(doc.copy())
        return MockCursor(results)

    async def find_one_and_update(
        self,
        filter: dict[str, Any],
        update: dict[str, Any],
        return_document: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        for doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                return doc.copy() if return_document else doc.copy()
        return None

    async def update_one(
        self,
        filter: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ) -> Any:
        mock_result = MagicMock()
        mock_result.modified_count = 0
        mock_result.upserted_id = None

        for doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                mock_result.modified_count = 1
                return mock_result

        if upsert:
            new_doc = filter.copy()
            if "$set" in update:
                new_doc.update(update["$set"])
            await self.insert_one(new_doc)
            mock_result.upserted_id = str(self._next_id - 1)

        return mock_result

    async def update_many(
        self,
        filter: dict[str, Any],
        update: dict[str, Any],
    ) -> Any:
        mock_result = MagicMock()
        count = 0
        for doc in self._documents.values():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                count += 1
        mock_result.modified_count = count
        return mock_result

    async def delete_one(self, filter: dict[str, Any]) -> Any:
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        for doc_id, doc in list(self._documents.items()):
            if self._matches_filter(doc, filter):
                del self._documents[doc_id]
                mock_result.deleted_count = 1
                break
        return mock_result

    async def create_index(self, keys, unique: bool = False, **kwargs: Any) -> str:
        if isinstance(keys, str):
            index_name = f"{keys}_1"
            keys = [(keys, 1)]
        else:
            index_name = "_".join(f"{field}_{order}" for field, order in keys)
        self.indexes.append({"keys": keys, "unique": unique, "name": index_name})
        return index_name

    async def count_documents(self, filter: dict[str, Any]) -> int:
        count = 0
        for doc in self._documents.values():
            if self._matches_filter(doc, filter):
                count += 1
        return count

    def _matches_filter(self, document: dict[str, Any], filter: dict[str, Any]) -> bool:
        if not filter:
            return True
        for key, value in filter.items():
            if key == "$and":
                if not all(self._matches_filter(document, cond) for cond in value):
                    return False
            elif key == "$or":
                if not any(self._matches_filter(document, cond) for cond in value):
                    return False
            elif isinstance(value, dict):
                doc_val = document.get(key)
                for op, op_val in value.items():
                    if (
                        (op == "$gte" and (doc_val is None or doc_val < op_val))
                        or (op == "$lte" and (doc_val is None or doc_val > op_val))
                        or (op == "$in" and doc_val not in op_val)
                    ):
                        return False
            else:
                if document.get(key) != value:
                    return False
        return True


# ---------------------------------------------------------------------------
# Mock Redis
# ---------------------------------------------------------------------------


class MockRedis:
    """Mock Redis client for testing."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._ttl: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: int = None) -> bool:
        self._data[key] = value
        if ex:
            self._ttl[key] = ex
        return True

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count

    async def ping(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_redis() -> MockRedis:
    """Create a mock Redis client."""
    return MockRedis()


@pytest.fixture
def mock_connection_collection() -> MockMongoCollection:
    return MockMongoCollection("oauth_connections")


@pytest.fixture
def mock_credential_collection() -> MockMongoCollection:
    return MockMongoCollection("oauth_credentials")


@pytest.fixture
def mock_session_collection() -> MockMongoCollection:
    return MockMongoCollection("oauth_sessions")


@pytest.fixture
def mock_activity_collection() -> MockMongoCollection:
    return MockMongoCollection("oauth_activity_logs")


@pytest.fixture
def jwt_secret() -> str:
    return "test-oauth-secret-key"


@pytest.fixture
def jwt_algorithm() -> str:
    return "HS256"


@pytest.fixture
def encryption_key() -> str:
    from taolib.testing.oauth.crypto.token_encryption import generate_encryption_key

    return generate_encryption_key()


@pytest.fixture(autouse=True)
def clean_collections(
    mock_connection_collection,
    mock_credential_collection,
    mock_session_collection,
    mock_activity_collection,
    mock_redis,
) -> Generator[None, Any]:
    """Automatically clean all mock collections before each test."""
    for coll in [
        mock_connection_collection,
        mock_credential_collection,
        mock_session_collection,
        mock_activity_collection,
    ]:
        coll._documents.clear()
        coll._next_id = 1
    mock_redis._data.clear()
    mock_redis._ttl.clear()
    yield



