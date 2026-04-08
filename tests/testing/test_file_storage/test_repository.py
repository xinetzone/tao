"""测试存储库层。"""

from datetime import UTC, datetime

import pytest

from taolib.testing.file_storage.models.enums import (
    AccessLevel,
    UploadStatus,
)
from taolib.testing.file_storage.repository.bucket_repo import BucketRepository
from taolib.testing.file_storage.repository.chunk_repo import ChunkRepository
from taolib.testing.file_storage.repository.upload_repo import UploadSessionRepository

from .conftest import MockMongoCollection


class TestBucketRepository:
    """测试 BucketRepository。"""

    @pytest.fixture
    def repo(self, mock_collection: MockMongoCollection) -> BucketRepository:
        return BucketRepository(mock_collection)

    @pytest.mark.asyncio
    async def test_create_and_get(self, repo: BucketRepository) -> None:
        doc = {
            "_id": "test-bucket",
            "name": "test-bucket",
            "description": "测试桶",
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
        # 直接写入 mock 集合以保留 _id
        repo._collection._documents["test-bucket"] = doc.copy()

        found = await repo.get_by_id("test-bucket")
        assert found is not None
        assert found.id == "test-bucket"
        assert found.name == "test-bucket"

    @pytest.mark.asyncio
    async def test_find_by_name(self, repo: BucketRepository) -> None:
        doc = {
            "_id": "my-bucket",
            "name": "my-bucket",
            "description": "",
            "access_level": "private",
            "max_file_size_bytes": 5 * 1024 * 1024 * 1024,
            "allowed_mime_types": [],
            "storage_class": "standard",
            "tags": [],
            "lifecycle_rules": None,
            "file_count": 0,
            "total_size_bytes": 0,
            "created_by": "admin",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        await repo.create(doc)

        found = await repo.find_by_name("my-bucket")
        assert found is not None
        assert found.name == "my-bucket"

    @pytest.mark.asyncio
    async def test_find_by_name_not_found(self, repo: BucketRepository) -> None:
        found = await repo.find_by_name("nonexistent")
        assert found is None

    @pytest.mark.asyncio
    async def test_increment_file_count(self, repo: BucketRepository) -> None:
        doc = {
            "_id": "stats-bucket",
            "name": "stats-bucket",
            "description": "",
            "access_level": "private",
            "max_file_size_bytes": 5 * 1024 * 1024 * 1024,
            "allowed_mime_types": [],
            "storage_class": "standard",
            "tags": [],
            "lifecycle_rules": None,
            "file_count": 0,
            "total_size_bytes": 0,
            "created_by": "admin",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        # 直接写入 mock 集合以保留 _id
        repo._collection._documents["stats-bucket"] = doc.copy()

        result = await repo.increment_file_count(
            "stats-bucket", count_delta=1, size_delta=102400
        )
        assert result is not None
        assert result.file_count == 1
        assert result.total_size_bytes == 102400


class TestUploadSessionRepository:
    """测试 UploadSessionRepository。"""

    @pytest.fixture
    def repo(self, mock_collection: MockMongoCollection) -> UploadSessionRepository:
        return UploadSessionRepository(mock_collection)

    @pytest.mark.asyncio
    async def test_create_session(self, repo: UploadSessionRepository) -> None:
        now = datetime.now(UTC)
        doc = {
            "_id": "session-1",
            "bucket_id": "test-bucket",
            "object_key": "test/file.bin",
            "original_filename": "file.bin",
            "content_type": "application/octet-stream",
            "total_size_bytes": 10000,
            "chunk_size_bytes": 5 * 1024 * 1024,  # 5MB (最小有效值)
            "total_chunks": 2,
            "status": UploadStatus.INITIATED,
            "uploaded_chunks": [],
            "uploaded_bytes": 0,
            "backend_upload_id": "backend-123",
            "created_by": "admin",
            "expires_at": now.replace(year=now.year + 1),
            "created_at": now,
            "updated_at": now,
        }
        # 直接写入 mock 集合以保留 _id
        repo._collection._documents["session-1"] = doc.copy()
        session = await repo.get_by_id("session-1")
        assert session is not None
        assert session.id == "session-1"
        assert session.status == UploadStatus.INITIATED


class TestChunkRepository:
    """测试 ChunkRepository。"""

    @pytest.fixture
    def repo(self, mock_collection: MockMongoCollection) -> ChunkRepository:
        return ChunkRepository(mock_collection)

    @pytest.mark.asyncio
    async def test_create_and_find(self, repo: ChunkRepository) -> None:
        doc = {
            "_id": "chunk-1:0",
            "session_id": "session-1",
            "chunk_index": 0,
            "size_bytes": 5000,
            "checksum_sha256": "abc123",
            "storage_path": "",
            "etag": "etag-abc",
            "uploaded_at": datetime.now(UTC),
        }
        # 直接写入 mock 集合以保留 _id
        repo._collection._documents["chunk-1:0"] = doc.copy()

        chunks = await repo.find_by_session("session-1")
        assert len(chunks) == 1
        assert chunks[0].chunk_index == 0

    @pytest.mark.asyncio
    async def test_delete_by_session(self, repo: ChunkRepository) -> None:
        # 直接写入 mock 集合以保留 _id
        for i in range(3):
            doc = {
                "_id": f"session-2:{i}",
                "session_id": "session-2",
                "chunk_index": i,
                "size_bytes": 1000,
                "checksum_sha256": f"hash{i}",
                "storage_path": "",
                "etag": None,
                "uploaded_at": datetime.now(UTC),
            }
            repo._collection._documents[f"session-2:{i}"] = doc.copy()

        count = await repo.delete_by_session("session-2")
        assert count == 3

        remaining = await repo.find_by_session("session-2")
        assert len(remaining) == 0



