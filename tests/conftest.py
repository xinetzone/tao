"""
Root test conftest: shared mock classes and generic fixtures.

Provides MockCursor, MockMongoCollection, MockRedis, MockRedisPipeline,
MockRedisPubSub, and FakeWebSocket for use across all test modules.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Self
from unittest.mock import MagicMock

import pytest

# Ensure src/ is in sys.path for all test modules
_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ---------------------------------------------------------------------------
# Mock MongoDB classes
# ---------------------------------------------------------------------------


class MockCursor:
    """Mock Motor cursor supporting async chaining (.skip/.limit/.sort/.to_list)."""

    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self._documents = list(documents)
        self._skip = 0
        self._limit: int | None = None
        self._sort_fields: list[tuple[str, int]] | None = None

    def skip(self, n: int) -> Self:
        self._skip = n
        return self

    def limit(self, n: int) -> Self:
        self._limit = n
        return self

    def sort(self, key_or_list, direction: int | None = None) -> Self:
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
    """Mock MongoDB collection for testing without real MongoDB."""

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

        # Handle sort kwarg (used by VersionRepository.get_latest_version)
        sort_fields = kwargs.get("sort")
        if sort_fields and isinstance(sort_fields, list):
            for field, order in reversed(sort_fields):
                results.sort(key=lambda x: x.get(field, ""), reverse=(order == -1))

        return results[0]

    def find(self, filter: dict[str, Any] | None = None, **kwargs: Any) -> MockCursor:
        """Return a MockCursor (synchronous, matching Motor's non-awaited find)."""
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
        for _doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                return doc.copy()
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

        for _doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$setOnInsert" in update and upsert:
                    doc.update(update["$setOnInsert"])
                mock_result.modified_count = 1
                return mock_result

        if upsert:
            new_doc = filter.copy()
            if "$set" in update:
                new_doc.update(update["$set"])
            await self.insert_one(new_doc)
            mock_result.upserted_id = str(self._next_id - 1)

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

    async def create_index(
        self, keys: list[tuple[str, int]], unique: bool = False, **kwargs: Any
    ) -> str:
        index_name = "_".join(f"{field}_{order}" for field, order in keys)
        self.indexes.append({"keys": keys, "unique": unique, "name": index_name})
        return index_name

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
            elif key == "$in":
                if document.get(key.split(".")[-1]) not in value:
                    return False
            elif key == "$gte":
                continue  # Handled in nested key matching
            elif "." in key:
                # Nested field access
                parts = key.split(".")
                current = document
                for part in parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        return False
                if current != value:
                    return False
            else:
                if document.get(key) != value:
                    return False
        return True

    async def count_documents(self, filter: dict[str, Any]) -> int:
        count = 0
        for doc in self._documents.values():
            if self._matches_filter(doc, filter):
                count += 1
        return count


# ---------------------------------------------------------------------------
# Mock Redis classes
# ---------------------------------------------------------------------------


class MockRedis:
    """Mock Redis client for testing without real Redis.

    Supports STRING, LIST, HASH commands and pipeline batching.
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._lists: dict[str, list[str]] = {}
        self._hashes: dict[str, dict[str, str]] = {}
        self._ttl: dict[str, int] = {}
        self._pubsub_channels: dict[str, list] = {}

    # -- STRING commands ---------------------------------------------------

    async def get(self, key: str) -> str | None:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self._data[key] = value
        if ex:
            self._ttl[key] = ex
        return True

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            for store in (self._data, self._lists, self._hashes):
                if key in store:
                    del store[key]
                    count += 1
        return count

    async def keys(self, pattern: str) -> list[str]:
        import fnmatch

        all_keys = (
            set(self._data.keys()) | set(self._lists.keys()) | set(self._hashes.keys())
        )
        return [k for k in all_keys if fnmatch.fnmatch(k, pattern)]

    async def expire(self, key: str, seconds: int) -> bool:
        self._ttl[key] = seconds
        return True

    # -- LIST commands -----------------------------------------------------

    async def lpush(self, key: str, *values: str) -> int:
        if key not in self._lists:
            self._lists[key] = []
        for v in values:
            self._lists[key].insert(0, v)
        return len(self._lists[key])

    async def ltrim(self, key: str, start: int, stop: int) -> bool:
        if key in self._lists:
            self._lists[key] = (
                self._lists[key][start : stop + 1]
                if stop >= 0
                else self._lists[key][start:]
            )
        return True

    async def lrange(self, key: str, start: int, stop: int) -> list[str]:
        if key not in self._lists:
            return []
        lst = self._lists[key]
        stop = len(lst) + stop + 1 if stop < 0 else stop + 1
        return lst[start:stop]

    async def llen(self, key: str) -> int:
        return len(self._lists.get(key, []))

    # -- HASH commands -----------------------------------------------------

    async def hset(
        self, key: str, mapping: dict[str, str] | None = None, **kwargs: str
    ) -> int:
        if key not in self._hashes:
            self._hashes[key] = {}
        data = mapping or {}
        data.update(kwargs)
        self._hashes[key].update(data)
        return len(data)

    async def hget(self, key: str, field: str) -> str | None:
        return self._hashes.get(key, {}).get(field)

    async def hgetall(self, key: str) -> dict[str, str]:
        return dict(self._hashes.get(key, {}))

    async def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        if key not in self._hashes:
            self._hashes[key] = {}
        current = int(self._hashes[key].get(field, "0"))
        new_val = current + amount
        self._hashes[key][field] = str(new_val)
        return new_val

    async def hdel(self, key: str, *fields: str) -> int:
        if key not in self._hashes:
            return 0
        count = 0
        for f in fields:
            if f in self._hashes[key]:
                del self._hashes[key][f]
                count += 1
        return count

    # -- SCAN --------------------------------------------------------------

    async def scan(
        self, cursor: int, match: str = "*", count: int = 100
    ) -> tuple[int, list[str]]:
        import fnmatch

        all_keys = (
            set(self._data.keys()) | set(self._lists.keys()) | set(self._hashes.keys())
        )
        matched = [k for k in all_keys if fnmatch.fnmatch(k, match)]
        return (0, matched)

    # -- PubSub ------------------------------------------------------------

    async def publish(self, channel: str, message: str) -> int:
        if channel not in self._pubsub_channels:
            self._pubsub_channels[channel] = []
        self._pubsub_channels[channel].append(message)
        return 1

    def pubsub(self) -> MockRedisPubSub:
        return MockRedisPubSub(self)

    # -- Pipeline ----------------------------------------------------------

    def pipeline(self) -> MockRedisPipeline:
        return MockRedisPipeline(self)

    # -- Misc --------------------------------------------------------------

    async def ping(self) -> bool:
        return True

    async def flushdb(self) -> bool:
        self._data.clear()
        self._lists.clear()
        self._hashes.clear()
        self._ttl.clear()
        return True


class MockRedisPipeline:
    """Mock Redis pipeline for batched commands."""

    def __init__(self, redis: MockRedis) -> None:
        self._redis = redis
        self._commands: list[tuple[str, tuple, dict]] = []

    def lpush(self, key: str, *values: str) -> MockRedisPipeline:
        self._commands.append(("lpush", (key, *values), {}))
        return self

    def ltrim(self, key: str, start: int, stop: int) -> MockRedisPipeline:
        self._commands.append(("ltrim", (key, start, stop), {}))
        return self

    def lrange(self, key: str, start: int, stop: int) -> MockRedisPipeline:
        self._commands.append(("lrange", (key, start, stop), {}))
        return self

    def expire(self, key: str, seconds: int) -> MockRedisPipeline:
        self._commands.append(("expire", (key, seconds), {}))
        return self

    def hset(
        self, key: str, mapping: dict[str, str] | None = None, **kwargs: str
    ) -> MockRedisPipeline:
        self._commands.append(("hset", (key,), {"mapping": mapping, **kwargs}))
        return self

    def hincrby(self, key: str, field: str, amount: int = 1) -> MockRedisPipeline:
        self._commands.append(("hincrby", (key, field, amount), {}))
        return self

    def publish(self, channel: str, message: str) -> MockRedisPipeline:
        self._commands.append(("publish", (channel, message), {}))
        return self

    def set(self, key: str, value: str, ex: int | None = None) -> MockRedisPipeline:
        self._commands.append(("set", (key, value), {"ex": ex}))
        return self

    async def execute(self) -> list[Any]:
        results = []
        for cmd, args, kwargs in self._commands:
            method = getattr(self._redis, cmd)
            result = await method(*args, **kwargs)
            results.append(result)
        self._commands.clear()
        return results


class MockRedisPubSub:
    """Mock Redis PubSub for testing."""

    def __init__(self, redis: MockRedis) -> None:
        self._redis = redis
        self._channels: list[str] = []
        self._patterns: list[str] = []

    async def subscribe(self, *channels: str) -> None:
        self._channels.extend(channels)

    async def psubscribe(self, *patterns: str) -> None:
        self._patterns.extend(patterns)

    async def punsubscribe(self, *patterns: str) -> None:
        for p in patterns:
            if p in self._patterns:
                self._patterns.remove(p)

    async def get_message(
        self, ignore_subscribe_messages: bool = True, timeout: float | None = None
    ) -> dict | None:
        return None

    async def unsubscribe(self, *channels: str) -> None:
        for ch in channels:
            if ch in self._channels:
                self._channels.remove(ch)

    async def aclose(self) -> None:
        self._channels.clear()
        self._patterns.clear()

    async def listen(self):
        """Async generator that yields nothing (tests inject messages directly)."""
        while False:
            yield


# ---------------------------------------------------------------------------
# FakeWebSocket for testing WebSocket manager
# ---------------------------------------------------------------------------


class FakeWebSocket:
    """Fake WebSocket for unit testing WebSocketConnectionManager.

    Records sent messages and simulates accept/close/send_text/send_json.
    """

    def __init__(self, *, client_id: str = "test") -> None:
        self.client_id = client_id
        self.accepted = False
        self.closed = False
        self.close_code: int | None = None
        self.close_reason: str | None = None
        self.sent_messages: list[str] = []
        self.sent_json_messages: list[dict] = []

    async def accept(self) -> None:
        self.accepted = True

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    async def send_text(self, data: str) -> None:
        if self.closed:
            raise RuntimeError("WebSocket is closed")
        self.sent_messages.append(data)

    async def send_json(self, data: dict) -> None:
        if self.closed:
            raise RuntimeError("WebSocket is closed")
        self.sent_json_messages.append(data)

    def __hash__(self) -> int:
        return hash(id(self))

    def __eq__(self, other: object) -> bool:
        return self is other


# ---------------------------------------------------------------------------
# Generic fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_redis() -> MockRedis:
    """Create a mock Redis client (available to all test modules)."""
    return MockRedis()
