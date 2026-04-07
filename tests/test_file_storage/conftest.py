"""文件存储测试夹具和 Mock 类。"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.file_storage.models.enums import AccessLevel, UploadStatus


class MockMongoCollection:
    """内存中的 MongoDB 集合模拟。"""

    def __init__(self, name: str = "mock") -> None:
        self.name = name
        self._documents: dict[str, dict[str, Any]] = {}
        self._next_id = 1
        self.indexes: list[dict[str, Any]] = []

    async def insert_one(self, document: dict[str, Any]) -> Any:
        doc_id = str(self._next_id)
        self._next_id += 1
        document["_id"] = doc_id
        self._documents[doc_id] = document.copy()
        mock_result = MagicMock()
        mock_result.inserted_id = doc_id
        return mock_result

    async def find_one(
        self, filter: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any] | None:
        filter = filter or {}
        for doc in self._documents.values():
            if self._matches_filter(doc, filter):
                return doc.copy()
        return None

    def find(self, filter: dict[str, Any] | None = None) -> Any:
        filter = filter or {}
        docs = [
            doc.copy()
            for doc in self._documents.values()
            if self._matches_filter(doc, filter)
        ]
        mock_cursor = MagicMock()
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=docs)
        return mock_cursor

    async def update_one(
        self,
        filter: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ) -> Any:
        mock_result = MagicMock()
        mock_result.matched_count = 0
        mock_result.modified_count = 0
        for _doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        doc[k] = doc.get(k, 0) + v
                mock_result.matched_count = 1
                mock_result.modified_count = 1
                break
        return mock_result

    async def find_one_and_update(
        self,
        filter: dict[str, Any],
        update: dict[str, Any],
        return_document: bool = False,
    ) -> dict[str, Any] | None:
        for _doc_id, doc in self._documents.items():
            if self._matches_filter(doc, filter):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        doc[k] = doc.get(k, 0) + v
                return doc.copy()
        return None

    async def delete_one(self, filter: dict[str, Any]) -> Any:
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        for doc_id in list(self._documents.keys()):
            doc = self._documents[doc_id]
            if self._matches_filter(doc, filter):
                del self._documents[doc_id]
                mock_result.deleted_count = 1
                break
        return mock_result

    async def delete_many(self, filter: dict[str, Any]) -> Any:
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        for doc_id in list(self._documents.keys()):
            doc = self._documents[doc_id]
            if self._matches_filter(doc, filter):
                del self._documents[doc_id]
                mock_result.deleted_count += 1
        return mock_result

    async def count_documents(self, filter: dict[str, Any]) -> int:
        return sum(
            1 for doc in self._documents.values() if self._matches_filter(doc, filter)
        )

    async def create_index(self, keys: Any, unique: bool = False, **kwargs: Any) -> str:
        self.indexes.append({"keys": keys, "unique": unique, **kwargs})
        return "mock_index"

    def _matches_filter(self, doc: dict[str, Any], filter: dict[str, Any]) -> bool:
        if not filter:
            return True
        for key, value in filter.items():
            if key not in doc:
                return False
            if isinstance(value, dict):
                for op, operand in value.items():
                    if op == "$in":
                        if doc[key] not in operand:
                            return False
                    elif op == "$ne":
                        if doc[key] == operand:
                            return False
                    elif op == "$all":
                        if not all(v in doc[key] for v in operand):
                            return False
            else:
                if doc[key] != value:
                    return False
        return True


@pytest.fixture
def mock_collection() -> MockMongoCollection:
    """提供模拟的 MongoDB 集合。"""
    return MockMongoCollection()


@pytest.fixture
def mock_mongo_db() -> MagicMock:
    """提供模拟的 MongoDB 数据库对象。"""
    db = MagicMock()
    db.buckets = MockMongoCollection("buckets")
    db.files = MockMongoCollection("files")
    db.upload_sessions = MockMongoCollection("upload_sessions")
    db.chunks = MockMongoCollection("chunks")
    db.file_versions = MockMongoCollection("file_versions")
    db.thumbnails = MockMongoCollection("thumbnails")
    return db


@pytest.fixture
def sample_bucket_data() -> dict[str, Any]:
    """提供示例存储桶数据。"""
    return {
        "name": "test-bucket",
        "description": "测试存储桶",
        "access_level": AccessLevel.PRIVATE,
        "max_file_size_bytes": 5 * 1024 * 1024 * 1024,
        "allowed_mime_types": [],
        "storage_class": "standard",
        "tags": ["test"],
        "lifecycle_rules": None,
        "file_count": 0,
        "total_size_bytes": 0,
        "created_by": "admin",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.fixture
def sample_file_data() -> dict[str, Any]:
    """提供示例文件数据。"""
    return {
        "bucket_id": "test-bucket",
        "object_key": "test/image.jpg",
        "original_filename": "image.jpg",
        "content_type": "image/jpeg",
        "size_bytes": 102400,
        "media_type": "image",
        "access_level": AccessLevel.PRIVATE,
        "description": "测试图片",
        "tags": ["test"],
        "custom_metadata": {},
        "storage_path": "test-bucket/test/image.jpg",
        "checksum_sha256": "abc123",
        "version": 1,
        "status": "active",
        "cdn_url": None,
        "thumbnails": [],
        "expires_at": None,
        "created_by": "admin",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.fixture
def sample_upload_session(sample_bucket_data: dict) -> dict[str, Any]:
    """提供示例上传会话数据。"""
    now = datetime.now(UTC)
    return {
        "bucket_id": sample_bucket_data["name"],
        "object_key": "test/video.mp4",
        "original_filename": "video.mp4",
        "content_type": "video/mp4",
        "total_size_bytes": 10 * 1024 * 1024,
        "chunk_size_bytes": 5 * 1024 * 1024,
        "total_chunks": 2,
        "status": UploadStatus.INITIATED,
        "uploaded_chunks": [],
        "uploaded_bytes": 0,
        "backend_upload_id": "mock-upload-id",
        "created_by": "admin",
        "expires_at": now.replace(year=now.year + 1),
        "created_at": now,
        "updated_at": now,
    }
