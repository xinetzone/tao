"""文件存储服务层测试。

覆盖 FileService、BucketService、UploadService、LifecycleService、StatsService。
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.file_storage.errors import (
    BucketNotEmptyError,
    BucketNotFoundError,
    ChunkMismatchError,
    DuplicateObjectError,
    FileNotFoundError_,
    FileValidationError,
    UploadSessionExpiredError,
    UploadSessionNotFoundError,
)
from taolib.testing.file_storage.models.enums import (
    AccessLevel,
    FileStatus,
    MediaType,
    UploadStatus,
)
from taolib.testing.file_storage.services.bucket_service import BucketService
from taolib.testing.file_storage.services.file_service import FileService
from taolib.testing.file_storage.services.lifecycle_service import LifecycleService
from taolib.testing.file_storage.services.stats_service import StatsService
from taolib.testing.file_storage.services.upload_service import UploadService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_bucket_doc(
    bucket_id="test-bucket",
    file_count=0,
    total_size_bytes=0,
    max_file_size_bytes=5 * 1024 * 1024 * 1024,
    allowed_mime_types=None,
    lifecycle_rules=None,
):
    doc = MagicMock()
    doc.id = bucket_id
    doc.name = bucket_id
    doc.file_count = file_count
    doc.total_size_bytes = total_size_bytes
    doc.max_file_size_bytes = max_file_size_bytes
    doc.allowed_mime_types = allowed_mime_types or []
    doc.lifecycle_rules = lifecycle_rules
    doc.to_response.return_value = MagicMock(
        id=bucket_id, name=bucket_id, file_count=file_count
    )
    return doc


def _make_file_doc(
    file_id="file-001",
    bucket_id="test-bucket",
    object_key="test/image.jpg",
    size_bytes=1024,
    access_level=AccessLevel.PRIVATE,
    status=FileStatus.ACTIVE,
    storage_path="test-bucket/test/image.jpg",
    checksum_sha256="abc123",
    expires_at=None,
):
    doc = MagicMock()
    doc.id = file_id
    doc.bucket_id = bucket_id
    doc.object_key = object_key
    doc.size_bytes = size_bytes
    doc.access_level = access_level
    doc.status = status
    doc.storage_path = storage_path
    doc.checksum_sha256 = checksum_sha256
    doc.expires_at = expires_at
    resp = MagicMock(id=file_id, bucket_id=bucket_id, status=status)
    doc.to_response.return_value = resp
    return doc


def _make_upload_session(
    session_id="sess-001",
    bucket_id="test-bucket",
    object_key="test/video.mp4",
    total_chunks=3,
    total_size_bytes=15 * 1024 * 1024,
    status=UploadStatus.INITIATED,
    backend_upload_id="backend-upload-123",
    content_type="video/mp4",
    original_filename="video.mp4",
    uploaded_bytes=0,
):
    s = MagicMock()
    s.id = session_id
    s.bucket_id = bucket_id
    s.object_key = object_key
    s.total_chunks = total_chunks
    s.total_size_bytes = total_size_bytes
    s.status = status
    s.backend_upload_id = backend_upload_id
    s.content_type = content_type
    s.original_filename = original_filename
    s.uploaded_bytes = uploaded_bytes
    s.expires_at = datetime.now(UTC) + timedelta(hours=24)
    s.to_response.return_value = MagicMock(id=session_id, status=status)
    return s


def _make_chunk(chunk_index=0, checksum="abc", etag="etag-1"):
    c = MagicMock()
    c.chunk_index = chunk_index
    c.checksum_sha256 = checksum
    c.etag = etag
    return c


def _make_version(
    version_number=1, size_bytes=1024, checksum="abc", storage_path="bucket/key"
):
    v = MagicMock()
    v.version_number = version_number
    v.size_bytes = size_bytes
    v.checksum_sha256 = checksum
    v.storage_path = storage_path
    v.to_response.return_value = MagicMock(version_number=version_number)
    return v


def _create_service_deps():
    """创建通用 mock 依赖。"""
    return {
        "file_repo": AsyncMock(),
        "bucket_repo": AsyncMock(),
        "thumbnail_repo": AsyncMock(),
        "storage_backend": AsyncMock(),
        "pipeline": AsyncMock(),
        "cdn_provider": MagicMock(),
    }


# ===========================================================================
# BucketService Tests
# ===========================================================================


class TestBucketService:
    """存储桶服务测试。"""

    def _make_service(self):
        bucket_repo = AsyncMock()
        storage_backend = AsyncMock()
        return BucketService(bucket_repo, storage_backend), bucket_repo, storage_backend

    @pytest.mark.asyncio
    async def test_create_bucket_success(self):
        svc, repo, backend = self._make_service()
        repo.find_by_name.return_value = None
        bucket_doc = _make_bucket_doc()
        repo.create.return_value = bucket_doc

        data = MagicMock()
        data.name = "test-bucket"
        data.model_dump.return_value = {"name": "test-bucket", "description": "test"}

        result = await svc.create_bucket(data, user_id="admin")

        repo.find_by_name.assert_awaited_once_with("test-bucket")
        backend.create_bucket.assert_awaited_once_with("test-bucket")
        repo.create.assert_awaited_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_bucket_duplicate_raises(self):
        svc, repo, _ = self._make_service()
        repo.find_by_name.return_value = _make_bucket_doc()

        data = MagicMock()
        data.name = "test-bucket"

        with pytest.raises(DuplicateObjectError, match="存储桶已存在"):
            await svc.create_bucket(data)

    @pytest.mark.asyncio
    async def test_get_bucket_found(self):
        svc, repo, _ = self._make_service()
        repo.get_by_id.return_value = _make_bucket_doc()

        result = await svc.get_bucket("test-bucket")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_bucket_not_found(self):
        svc, repo, _ = self._make_service()
        repo.get_by_id.return_value = None

        result = await svc.get_bucket("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_bucket_with_data(self):
        svc, repo, _ = self._make_service()
        updated_doc = _make_bucket_doc()
        repo.update.return_value = updated_doc

        data = MagicMock()
        data.model_dump.return_value = {"description": "updated"}

        result = await svc.update_bucket("test-bucket", data)
        repo.update.assert_awaited_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_bucket_empty_data_returns_current(self):
        svc, repo, _ = self._make_service()
        repo.get_by_id.return_value = _make_bucket_doc()

        data = MagicMock()
        data.model_dump.return_value = {}

        result = await svc.update_bucket("test-bucket", data)
        repo.update.assert_not_awaited()
        assert result is not None

    @pytest.mark.asyncio
    async def test_delete_bucket_success(self):
        svc, repo, backend = self._make_service()
        repo.get_by_id.return_value = _make_bucket_doc(file_count=0)
        repo.delete.return_value = True

        result = await svc.delete_bucket("test-bucket")
        backend.delete_bucket.assert_awaited_once_with("test-bucket")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_bucket_not_found_raises(self):
        svc, repo, _ = self._make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(BucketNotFoundError):
            await svc.delete_bucket("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_bucket_not_empty_raises(self):
        svc, repo, _ = self._make_service()
        repo.get_by_id.return_value = _make_bucket_doc(file_count=5)

        with pytest.raises(BucketNotEmptyError, match="5 个文件"):
            await svc.delete_bucket("test-bucket")

    @pytest.mark.asyncio
    async def test_delete_bucket_force(self):
        svc, repo, backend = self._make_service()
        repo.get_by_id.return_value = _make_bucket_doc(file_count=5)
        repo.delete.return_value = True

        result = await svc.delete_bucket("test-bucket", force=True)
        assert result is True

    @pytest.mark.asyncio
    async def test_list_buckets(self):
        svc, repo, _ = self._make_service()
        repo.list.return_value = [_make_bucket_doc("b1"), _make_bucket_doc("b2")]

        result = await svc.list_buckets(skip=0, limit=10)
        assert len(result) == 2


# ===========================================================================
# FileService Tests
# ===========================================================================


class TestFileService:
    """文件服务测试。"""

    def _make_service(self, with_cdn=True):
        deps = _create_service_deps()
        cdn = deps.pop("cdn_provider") if with_cdn else None
        if not with_cdn:
            deps.pop("cdn_provider", None)
        return (
            FileService(
                file_repo=deps["file_repo"],
                bucket_repo=deps["bucket_repo"],
                thumbnail_repo=deps["thumbnail_repo"],
                storage_backend=deps["storage_backend"],
                pipeline=deps["pipeline"],
                cdn_provider=cdn,
            ),
            deps,
            cdn,
        )

    @pytest.mark.asyncio
    async def test_upload_file_bucket_not_found(self):
        svc, deps, _ = self._make_service()
        deps["bucket_repo"].get_by_id.return_value = None

        with pytest.raises(BucketNotFoundError, match="存储桶不存在"):
            await svc.upload_file(
                bucket_id="missing",
                object_key="test.jpg",
                data=b"data",
                filename="test.jpg",
                content_type="image/jpeg",
            )

    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        svc, deps, cdn = self._make_service()
        bucket = _make_bucket_doc()
        deps["bucket_repo"].get_by_id.return_value = bucket

        process_result = MagicMock()
        process_result.validated_content_type = "image/jpeg"
        process_result.size_bytes = 100
        process_result.checksum_sha256 = "sha256hash"
        process_result.media_type = MediaType.IMAGE
        deps["pipeline"].process_upload.return_value = process_result

        put_result = MagicMock()
        put_result.storage_path = "test-bucket/test.jpg"
        deps["storage_backend"].put_object.return_value = put_result

        cdn.generate_url.return_value = "https://cdn.example.com/test.jpg"

        deps["pipeline"].generate_thumbnails.return_value = []

        file_doc = _make_file_doc()
        deps["file_repo"].create.return_value = file_doc

        result = await svc.upload_file(
            bucket_id="test-bucket",
            object_key="test.jpg",
            data=b"imagedata",
            filename="test.jpg",
            content_type="image/jpeg",
            user_id="user1",
            tags=["photo"],
        )

        assert result is not None
        deps["bucket_repo"].increment_file_count.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_file_found(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()

        result = await svc.get_file("file-001")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_file_not_found(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = None

        result = await svc.get_file("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_download_file_success(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()

        mock_stream = AsyncMock()
        deps["storage_backend"].get_object.return_value = mock_stream

        result = await svc.download_file("file-001")
        deps["storage_backend"].get_object.assert_awaited_once()
        assert result is mock_stream

    @pytest.mark.asyncio
    async def test_download_file_not_found(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_, match="文件不存在"):
            await svc.download_file("nonexistent")

    @pytest.mark.asyncio
    async def test_update_metadata(self):
        svc, deps, _ = self._make_service()
        updated_doc = _make_file_doc()
        deps["file_repo"].update.return_value = updated_doc

        data = MagicMock()
        data.model_dump.return_value = {"description": "new desc"}

        result = await svc.update_metadata("file-001", data)
        deps["file_repo"].update.assert_awaited_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_metadata_empty_returns_current(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()

        data = MagicMock()
        data.model_dump.return_value = {}

        result = await svc.update_metadata("file-001", data)
        deps["file_repo"].update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_file_success(self):
        svc, deps, _ = self._make_service()
        file_doc = _make_file_doc()
        deps["file_repo"].get_by_id.return_value = file_doc
        deps["thumbnail_repo"].find_by_file.return_value = []

        result = await svc.delete_file("file-001")
        assert result is True
        deps["storage_backend"].delete_object.assert_awaited_once()
        deps["bucket_repo"].increment_file_count.assert_awaited_once()
        deps["file_repo"].update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_file_not_found(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_):
            await svc.delete_file("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_file_with_thumbnails(self):
        svc, deps, _ = self._make_service()
        file_doc = _make_file_doc()
        deps["file_repo"].get_by_id.return_value = file_doc

        thumb = MagicMock()
        thumb.storage_path = "test-bucket/_thumbnails/file-001/small.webp"
        deps["thumbnail_repo"].find_by_file.return_value = [thumb]

        result = await svc.delete_file("file-001")
        assert result is True
        assert deps["storage_backend"].delete_object.await_count == 2

    @pytest.mark.asyncio
    async def test_list_files_by_bucket(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].find_by_bucket.return_value = [
            _make_file_doc(),
            _make_file_doc(),
        ]

        result = await svc.list_files(bucket_id="test-bucket")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_files_global_filter(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].list.return_value = [_make_file_doc()]

        result = await svc.list_files(tags=["photo"], media_type="image")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_file_url_public_with_cdn(self):
        svc, deps, cdn = self._make_service()
        file_doc = _make_file_doc(access_level=AccessLevel.PUBLIC)
        deps["file_repo"].get_by_id.return_value = file_doc
        cdn.generate_url.return_value = "https://cdn.example.com/img.jpg"

        result = await svc.get_file_url("file-001")
        assert result == "https://cdn.example.com/img.jpg"

    @pytest.mark.asyncio
    async def test_get_file_url_private_presigned(self):
        svc, deps, _ = self._make_service()
        file_doc = _make_file_doc(access_level=AccessLevel.PRIVATE)
        deps["file_repo"].get_by_id.return_value = file_doc
        deps[
            "storage_backend"
        ].generate_presigned_url.return_value = "https://s3.example.com/signed"

        result = await svc.get_file_url("file-001", expires_in=7200)
        deps["storage_backend"].generate_presigned_url.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_file_url_not_found(self):
        svc, deps, _ = self._make_service()
        deps["file_repo"].get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_):
            await svc.get_file_url("nonexistent")


# ===========================================================================
# UploadService Tests
# ===========================================================================


class TestUploadService:
    """分片上传服务测试。"""

    def _make_service(self):
        upload_repo = AsyncMock()
        chunk_repo = AsyncMock()
        file_repo = AsyncMock()
        bucket_repo = AsyncMock()
        storage_backend = AsyncMock()
        svc = UploadService(
            upload_repo=upload_repo,
            chunk_repo=chunk_repo,
            file_repo=file_repo,
            bucket_repo=bucket_repo,
            storage_backend=storage_backend,
        )
        return svc, upload_repo, chunk_repo, file_repo, bucket_repo, storage_backend

    @pytest.mark.asyncio
    async def test_init_upload_success(self):
        svc, upload_repo, _, _, bucket_repo, backend = self._make_service()
        bucket_repo.get_by_id.return_value = _make_bucket_doc()
        backend.create_multipart_upload.return_value = "upload-id-123"
        session = _make_upload_session()
        upload_repo.create.return_value = session

        data = MagicMock()
        data.bucket_id = "test-bucket"
        data.object_key = "test/video.mp4"
        data.content_type = "video/mp4"
        data.total_size_bytes = 10 * 1024 * 1024
        data.model_dump.return_value = {
            "bucket_id": "test-bucket",
            "object_key": "test/video.mp4",
            "content_type": "video/mp4",
            "total_size_bytes": 10 * 1024 * 1024,
            "chunk_size_bytes": 5 * 1024 * 1024,
            "total_chunks": 2,
            "original_filename": "video.mp4",
        }

        result = await svc.init_upload(data)
        assert result is not None
        backend.create_multipart_upload.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_init_upload_bucket_not_found(self):
        svc, _, _, _, bucket_repo, _ = self._make_service()
        bucket_repo.get_by_id.return_value = None

        data = MagicMock()
        data.bucket_id = "nonexistent"

        with pytest.raises(BucketNotFoundError):
            await svc.init_upload(data)

    @pytest.mark.asyncio
    async def test_init_upload_file_too_large(self):
        svc, _, _, _, bucket_repo, _ = self._make_service()
        bucket_repo.get_by_id.return_value = _make_bucket_doc(max_file_size_bytes=1024)

        data = MagicMock()
        data.bucket_id = "test-bucket"
        data.total_size_bytes = 2048

        with pytest.raises(FileValidationError, match="超出限制"):
            await svc.init_upload(data)

    @pytest.mark.asyncio
    async def test_upload_chunk_success(self):
        svc, upload_repo, chunk_repo, _, _, backend = self._make_service()
        session = _make_upload_session(total_chunks=3)
        upload_repo.get_by_id.return_value = session

        part_info = MagicMock()
        part_info.etag = "etag-1"
        backend.upload_part.return_value = part_info

        chunk_doc = _make_chunk()
        chunk_repo.create.return_value = chunk_doc

        import hashlib

        test_data = b"chunk data"
        expected_checksum = hashlib.sha256(test_data).hexdigest()

        result = await svc.upload_chunk("sess-001", 0, test_data, expected_checksum)
        assert result is not None
        backend.upload_part.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_upload_chunk_session_not_found(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = None

        with pytest.raises(UploadSessionNotFoundError):
            await svc.upload_chunk("nonexistent", 0, b"data")

    @pytest.mark.asyncio
    async def test_upload_chunk_session_completed(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session(
            status=UploadStatus.COMPLETED
        )

        with pytest.raises(UploadSessionExpiredError, match="已结束"):
            await svc.upload_chunk("sess-001", 0, b"data")

    @pytest.mark.asyncio
    async def test_upload_chunk_session_expired(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        session = _make_upload_session()
        session.expires_at = datetime.now(UTC) - timedelta(hours=1)
        upload_repo.get_by_id.return_value = session

        with pytest.raises(UploadSessionExpiredError, match="已过期"):
            await svc.upload_chunk("sess-001", 0, b"data")

    @pytest.mark.asyncio
    async def test_upload_chunk_index_out_of_range(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session(total_chunks=3)

        with pytest.raises(ChunkMismatchError, match="超出范围"):
            await svc.upload_chunk("sess-001", 5, b"data")

    @pytest.mark.asyncio
    async def test_upload_chunk_negative_index(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session(total_chunks=3)

        with pytest.raises(ChunkMismatchError, match="超出范围"):
            await svc.upload_chunk("sess-001", -1, b"data")

    @pytest.mark.asyncio
    async def test_upload_chunk_checksum_mismatch(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session(total_chunks=3)

        with pytest.raises(ChunkMismatchError, match="校验和不匹配"):
            await svc.upload_chunk("sess-001", 0, b"data", checksum="wrong-checksum")

    @pytest.mark.asyncio
    async def test_complete_upload_success(self):
        svc, upload_repo, chunk_repo, file_repo, bucket_repo, backend = (
            self._make_service()
        )
        session = _make_upload_session(total_chunks=2)
        upload_repo.get_by_id.return_value = session
        bucket_repo.get_by_id.return_value = _make_bucket_doc()

        chunks = [_make_chunk(0, "hash0", "e0"), _make_chunk(1, "hash1", "e1")]
        chunk_repo.find_by_session.return_value = chunks

        put_result = MagicMock()
        put_result.storage_path = "test-bucket/test/video.mp4"
        backend.complete_multipart_upload.return_value = put_result

        file_doc = _make_file_doc()
        file_repo.create.return_value = file_doc

        result = await svc.complete_upload("sess-001")
        assert result is not None
        upload_repo.update_status.assert_any_await("sess-001", UploadStatus.COMPLETING)
        chunk_repo.delete_by_session.assert_awaited_once_with("sess-001")

    @pytest.mark.asyncio
    async def test_complete_upload_chunks_mismatch(self):
        svc, upload_repo, chunk_repo, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session(total_chunks=3)
        chunk_repo.find_by_session.return_value = [_make_chunk(0)]

        with pytest.raises(ChunkMismatchError, match="分片数量不匹配"):
            await svc.complete_upload("sess-001")

    @pytest.mark.asyncio
    async def test_abort_upload_success(self):
        svc, upload_repo, chunk_repo, _, _, backend = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session()

        result = await svc.abort_upload("sess-001")
        assert result is True
        backend.abort_multipart_upload.assert_awaited_once()
        chunk_repo.delete_by_session.assert_awaited_once()
        upload_repo.update_status.assert_awaited_once_with(
            "sess-001", UploadStatus.ABORTED
        )

    @pytest.mark.asyncio
    async def test_abort_upload_not_found(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = None

        with pytest.raises(UploadSessionNotFoundError):
            await svc.abort_upload("nonexistent")

    @pytest.mark.asyncio
    async def test_get_upload_status(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = _make_upload_session()

        result = await svc.get_upload_status("sess-001")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_upload_status_not_found(self):
        svc, upload_repo, _, _, _, _ = self._make_service()
        upload_repo.get_by_id.return_value = None

        result = await svc.get_upload_status("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self):
        svc, upload_repo, chunk_repo, _, _, backend = self._make_service()
        expired_sessions = [
            _make_upload_session("sess-1"),
            _make_upload_session("sess-2"),
        ]
        upload_repo.find_expired_sessions.return_value = expired_sessions
        # abort_upload 内部会再次调用 get_by_id
        upload_repo.get_by_id.side_effect = expired_sessions

        count = await svc.cleanup_expired_sessions()
        assert count == 2


# ===========================================================================
# LifecycleService Tests
# ===========================================================================


class TestLifecycleService:
    """生命周期服务测试。"""

    def _make_service(self):
        deps = {
            "file_repo": AsyncMock(),
            "version_repo": AsyncMock(),
            "thumbnail_repo": AsyncMock(),
            "upload_repo": AsyncMock(),
            "chunk_repo": AsyncMock(),
            "bucket_repo": AsyncMock(),
            "storage_backend": AsyncMock(),
        }
        svc = LifecycleService(**deps)
        return svc, deps

    @pytest.mark.asyncio
    async def test_expire_files_processes_expired(self):
        svc, deps = self._make_service()
        expired_files = [
            _make_file_doc("f1", expires_at=datetime.now(UTC) - timedelta(days=1)),
            _make_file_doc("f2", expires_at=datetime.now(UTC) - timedelta(days=2)),
        ]
        deps["file_repo"].find_expired_files.return_value = expired_files
        deps["thumbnail_repo"].find_by_file.return_value = []

        count = await svc.expire_files()
        assert count == 2
        assert deps["storage_backend"].delete_object.await_count == 2
        assert deps["bucket_repo"].increment_file_count.await_count == 2

    @pytest.mark.asyncio
    async def test_expire_files_no_expired(self):
        svc, deps = self._make_service()
        deps["file_repo"].find_expired_files.return_value = []

        count = await svc.expire_files()
        assert count == 0

    @pytest.mark.asyncio
    async def test_create_file_version_success(self):
        svc, deps = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()
        deps["version_repo"].find_latest.return_value = _make_version(version_number=2)
        deps["bucket_repo"].get_by_id.return_value = _make_bucket_doc()
        version_doc = _make_version(version_number=3)
        deps["version_repo"].create.return_value = version_doc

        result = await svc.create_file_version("file-001")
        assert result is not None
        create_call = deps["version_repo"].create.call_args[0][0]
        assert create_call["version_number"] == 3

    @pytest.mark.asyncio
    async def test_create_file_version_first_version(self):
        svc, deps = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()
        deps["version_repo"].find_latest.return_value = None
        deps["bucket_repo"].get_by_id.return_value = _make_bucket_doc()
        version_doc = _make_version(version_number=1)
        deps["version_repo"].create.return_value = version_doc

        result = await svc.create_file_version("file-001")
        create_call = deps["version_repo"].create.call_args[0][0]
        assert create_call["version_number"] == 1

    @pytest.mark.asyncio
    async def test_create_file_version_file_not_found(self):
        svc, deps = self._make_service()
        deps["file_repo"].get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_):
            await svc.create_file_version("nonexistent")

    @pytest.mark.asyncio
    async def test_rollback_to_version_success(self):
        svc, deps = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()
        target_version = _make_version(version_number=2, storage_path="bucket/old-key")
        deps["version_repo"].find_by_file.return_value = [
            _make_version(1),
            target_version,
        ]

        result = await svc.rollback_to_version("file-001", 2)
        assert result is not None
        deps["storage_backend"].copy_object.assert_awaited_once()
        deps["file_repo"].update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rollback_to_version_not_found(self):
        svc, deps = self._make_service()
        deps["file_repo"].get_by_id.return_value = _make_file_doc()
        deps["version_repo"].find_by_file.return_value = [_make_version(1)]

        result = await svc.rollback_to_version("file-001", 99)
        assert result is None

    @pytest.mark.asyncio
    async def test_rollback_file_not_found(self):
        svc, deps = self._make_service()
        deps["file_repo"].get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_):
            await svc.rollback_to_version("nonexistent", 1)

    @pytest.mark.asyncio
    async def test_gc_deleted_files(self):
        svc, deps = self._make_service()
        deleted = [_make_file_doc("f1"), _make_file_doc("f2"), _make_file_doc("f3")]
        deps["file_repo"].list.return_value = deleted

        count = await svc.gc_deleted_files()
        assert count == 3
        assert deps["thumbnail_repo"].delete_by_file.await_count == 3
        assert deps["file_repo"].delete.await_count == 3

    @pytest.mark.asyncio
    async def test_gc_deleted_files_empty(self):
        svc, deps = self._make_service()
        deps["file_repo"].list.return_value = []

        count = await svc.gc_deleted_files()
        assert count == 0


# ===========================================================================
# StatsService Tests
# ===========================================================================


class TestStatsService:
    """统计服务测试。"""

    def _make_service(self):
        bucket_repo = AsyncMock()
        file_repo = AsyncMock()
        upload_repo = AsyncMock()
        svc = StatsService(bucket_repo, file_repo, upload_repo)
        return svc, bucket_repo, file_repo, upload_repo

    @pytest.mark.asyncio
    async def test_get_bucket_stats_found(self):
        svc, bucket_repo, _, upload_repo = self._make_service()
        bucket_repo.get_by_id.return_value = _make_bucket_doc(
            file_count=10, total_size_bytes=1024000
        )
        upload_repo.count.return_value = 5

        result = await svc.get_bucket_stats("test-bucket")
        assert result is not None
        assert result.file_count == 10
        assert result.total_size_bytes == 1024000
        assert result.upload_count == 5

    @pytest.mark.asyncio
    async def test_get_bucket_stats_not_found(self):
        svc, bucket_repo, _, _ = self._make_service()
        bucket_repo.get_by_id.return_value = None

        result = await svc.get_bucket_stats("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_storage_overview(self):
        svc, bucket_repo, file_repo, upload_repo = self._make_service()
        bucket_repo.count.return_value = 3
        file_repo.count.return_value = 100
        bucket_repo.list.return_value = [
            _make_bucket_doc("b1", total_size_bytes=500),
            _make_bucket_doc("b2", total_size_bytes=300),
        ]
        upload_repo.count.return_value = 2

        result = await svc.get_storage_overview()
        assert result.total_buckets == 3
        assert result.total_files == 100
        assert result.total_size_bytes == 800
        assert result.active_uploads == 2

    @pytest.mark.asyncio
    async def test_get_upload_stats(self):
        svc, _, _, upload_repo = self._make_service()
        upload_repo.count.side_effect = [50, 40, 5, 3]
        session1 = MagicMock()
        session1.uploaded_bytes = 1000
        session2 = MagicMock()
        session2.uploaded_bytes = 2000
        upload_repo.list.return_value = [session1, session2]

        result = await svc.get_upload_stats()
        assert result.total_uploads == 50
        assert result.completed == 40
        assert result.failed == 5
        assert result.in_progress == 3
        assert result.total_bytes_uploaded == 3000


# ===========================================================================
# AccessService Tests
# ===========================================================================


class TestAccessService:
    """访问控制服务测试。"""

    def _make_service(self, *, with_cdn=True, secret="test-hmac-secret-key"):
        file_repo = AsyncMock()
        storage_backend = AsyncMock()
        cdn_provider = MagicMock() if with_cdn else None
        from taolib.testing.file_storage.services.access_service import AccessService

        svc = AccessService(
            file_repo=file_repo,
            storage_backend=storage_backend,
            cdn_provider=cdn_provider,
            signed_url_secret=secret,
        )
        return svc, file_repo, storage_backend, cdn_provider

    # --- generate_signed_url ---

    @pytest.mark.asyncio
    async def test_generate_signed_url_with_cdn(self):
        svc, file_repo, storage_backend, cdn = self._make_service()
        file_repo.get_by_id.return_value = _make_file_doc()
        cdn.generate_url.return_value = "https://cdn.example.com/file"
        cdn.sign_url.return_value = "https://cdn.example.com/file?sig=abc"

        result = await svc.generate_signed_url("file-001")
        assert result == "https://cdn.example.com/file?sig=abc"
        cdn.generate_url.assert_called_once()
        cdn.sign_url.assert_called_once()
        storage_backend.generate_presigned_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_signed_url_without_cdn(self):
        svc, file_repo, storage_backend, _ = self._make_service(with_cdn=False)
        file_repo.get_by_id.return_value = _make_file_doc()
        storage_backend.generate_presigned_url.return_value = "https://s3/presigned"

        result = await svc.generate_signed_url("file-001")
        assert result == "https://s3/presigned"
        storage_backend.generate_presigned_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_signed_url_file_not_found(self):
        svc, file_repo, _, _ = self._make_service()
        file_repo.get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_):
            await svc.generate_signed_url("nonexistent")

    @pytest.mark.asyncio
    async def test_generate_signed_url_custom_expires(self):
        svc, file_repo, _, cdn = self._make_service()
        file_repo.get_by_id.return_value = _make_file_doc()
        cdn.generate_url.return_value = "https://cdn/f"
        cdn.sign_url.return_value = "https://cdn/f?s=x"

        await svc.generate_signed_url("file-001", expires_in=7200)
        cdn.sign_url.assert_called_once_with("https://cdn/f", 7200)

    @pytest.mark.asyncio
    async def test_generate_signed_url_put_method(self):
        svc, file_repo, storage_backend, _ = self._make_service(with_cdn=False)
        file_repo.get_by_id.return_value = _make_file_doc()
        storage_backend.generate_presigned_url.return_value = "https://s3/put"

        await svc.generate_signed_url("file-001", method="PUT")
        args = storage_backend.generate_presigned_url.call_args
        assert args[0][3] == "PUT" or args.kwargs.get("method") == "PUT"

    @pytest.mark.asyncio
    async def test_generate_signed_url_passes_bucket_and_key(self):
        svc, file_repo, _, cdn = self._make_service()
        f = _make_file_doc(bucket_id="my-bucket", object_key="path/to/file.txt")
        file_repo.get_by_id.return_value = f
        cdn.generate_url.return_value = "u"
        cdn.sign_url.return_value = "u"

        await svc.generate_signed_url("file-001")
        cdn.generate_url.assert_called_once_with("my-bucket", "path/to/file.txt")

    # --- generate_token ---

    def test_generate_token_structure(self):
        svc, *_ = self._make_service()
        token = svc.generate_token("file-001")
        assert "file_id" in token
        assert "expires" in token
        assert "signature" in token
        assert token["file_id"] == "file-001"

    def test_generate_token_expires_calculation(self):
        import time

        svc, *_ = self._make_service()
        before = int(time.time()) + 3600
        token = svc.generate_token("file-001", expires_in=3600)
        after = int(time.time()) + 3600
        assert before <= token["expires"] <= after

    def test_generate_token_signature_is_hex_sha256(self):
        svc, *_ = self._make_service()
        token = svc.generate_token("file-001")
        sig = token["signature"]
        assert len(sig) == 64
        assert all(c in "0123456789abcdef" for c in sig)

    def test_generate_token_different_files_different_signatures(self):
        svc, *_ = self._make_service()
        t1 = svc.generate_token("file-001")
        t2 = svc.generate_token("file-002")
        assert t1["signature"] != t2["signature"]

    def test_generate_token_deterministic_with_fixed_time(self):
        from unittest.mock import patch

        svc, *_ = self._make_service()
        with patch("taolib.testing.file_storage.services.access_service.time") as mock_time:
            mock_time.time.return_value = 1000000.0
            t1 = svc.generate_token("file-001", expires_in=60)
            mock_time.time.return_value = 1000000.0
            t2 = svc.generate_token("file-001", expires_in=60)
        assert t1["signature"] == t2["signature"]
        assert t1["expires"] == t2["expires"]

    def test_generate_token_custom_expires(self):
        from unittest.mock import patch

        svc, *_ = self._make_service()
        with patch("taolib.testing.file_storage.services.access_service.time") as mock_time:
            mock_time.time.return_value = 1000000.0
            token = svc.generate_token("f", expires_in=60)
        assert token["expires"] == 1000060

    # --- validate_token ---

    def test_validate_token_valid(self):
        svc, *_ = self._make_service()
        token = svc.generate_token("file-001")
        assert svc.validate_token(
            token["file_id"], token["expires"], token["signature"]
        )

    def test_validate_token_expired(self):
        from unittest.mock import patch

        svc, *_ = self._make_service()
        with patch("taolib.testing.file_storage.services.access_service.time") as mock_time:
            mock_time.time.return_value = 1000000.0
            token = svc.generate_token("file-001", expires_in=60)
        # 过期后验证
        with patch("taolib.testing.file_storage.services.access_service.time") as mock_time:
            mock_time.time.return_value = 1000061.0
            assert not svc.validate_token(
                token["file_id"], token["expires"], token["signature"]
            )

    def test_validate_token_wrong_signature(self):
        svc, *_ = self._make_service()
        token = svc.generate_token("file-001")
        assert not svc.validate_token(token["file_id"], token["expires"], "bad" * 16)

    def test_validate_token_wrong_file_id(self):
        svc, *_ = self._make_service()
        token = svc.generate_token("file-001")
        assert not svc.validate_token("file-999", token["expires"], token["signature"])

    def test_validate_token_empty_secret(self):
        svc, *_ = self._make_service(secret="")
        token = svc.generate_token("file-001")
        assert svc.validate_token(
            token["file_id"], token["expires"], token["signature"]
        )

    def test_validate_token_boundary_not_expired(self):
        from unittest.mock import patch

        svc, *_ = self._make_service()
        with patch("taolib.testing.file_storage.services.access_service.time") as mock_time:
            mock_time.time.return_value = 1000000.0
            token = svc.generate_token("file-001", expires_in=60)
        # 刚好未过期
        with patch("taolib.testing.file_storage.services.access_service.time") as mock_time:
            mock_time.time.return_value = 1000059.0
            assert svc.validate_token(
                token["file_id"], token["expires"], token["signature"]
            )

    # --- check_access ---

    @pytest.mark.asyncio
    async def test_check_access_public(self):
        svc, file_repo, _, _ = self._make_service()
        f = _make_file_doc(access_level=AccessLevel.PUBLIC)
        f.created_by = "owner"
        file_repo.get_by_id.return_value = f

        assert await svc.check_access("file-001", user_id="anyone") is True

    @pytest.mark.asyncio
    async def test_check_access_public_no_user(self):
        svc, file_repo, _, _ = self._make_service()
        f = _make_file_doc(access_level=AccessLevel.PUBLIC)
        f.created_by = "owner"
        file_repo.get_by_id.return_value = f

        assert await svc.check_access("file-001", user_id=None) is True

    @pytest.mark.asyncio
    async def test_check_access_private_owner(self):
        svc, file_repo, _, _ = self._make_service()
        f = _make_file_doc(access_level=AccessLevel.PRIVATE)
        f.created_by = "user-A"
        file_repo.get_by_id.return_value = f

        assert await svc.check_access("file-001", user_id="user-A") is True

    @pytest.mark.asyncio
    async def test_check_access_private_wrong_user(self):
        svc, file_repo, _, _ = self._make_service()
        f = _make_file_doc(access_level=AccessLevel.PRIVATE)
        f.created_by = "user-A"
        file_repo.get_by_id.return_value = f

        assert await svc.check_access("file-001", user_id="user-B") is False

    @pytest.mark.asyncio
    async def test_check_access_private_no_user(self):
        svc, file_repo, _, _ = self._make_service()
        f = _make_file_doc(access_level=AccessLevel.PRIVATE)
        f.created_by = "user-A"
        file_repo.get_by_id.return_value = f

        assert await svc.check_access("file-001") is False

    @pytest.mark.asyncio
    async def test_check_access_signed_url_returns_false(self):
        svc, file_repo, _, _ = self._make_service()
        f = _make_file_doc(access_level=AccessLevel.SIGNED_URL)
        f.created_by = "owner"
        file_repo.get_by_id.return_value = f

        assert await svc.check_access("file-001", user_id="owner") is False

    @pytest.mark.asyncio
    async def test_check_access_file_not_found(self):
        svc, file_repo, _, _ = self._make_service()
        file_repo.get_by_id.return_value = None

        with pytest.raises(FileNotFoundError_):
            await svc.check_access("nonexistent")


# ===========================================================================
# StatsService Extended Tests
# ===========================================================================


class TestStatsServiceEdgeCases:
    """统计服务边界条件测试。"""

    def _make_service(self):
        bucket_repo = AsyncMock()
        file_repo = AsyncMock()
        upload_repo = AsyncMock()
        svc = StatsService(bucket_repo, file_repo, upload_repo)
        return svc, bucket_repo, file_repo, upload_repo

    @pytest.mark.asyncio
    async def test_get_bucket_stats_zero_uploads(self):
        svc, bucket_repo, _, upload_repo = self._make_service()
        bucket_repo.get_by_id.return_value = _make_bucket_doc(
            file_count=0, total_size_bytes=0
        )
        upload_repo.count.return_value = 0

        result = await svc.get_bucket_stats("empty-bucket")
        assert result is not None
        assert result.file_count == 0
        assert result.upload_count == 0

    @pytest.mark.asyncio
    async def test_get_storage_overview_zero_buckets(self):
        svc, bucket_repo, file_repo, upload_repo = self._make_service()
        bucket_repo.count.return_value = 0
        file_repo.count.return_value = 0
        bucket_repo.list.return_value = []
        upload_repo.count.return_value = 0

        result = await svc.get_storage_overview()
        assert result.total_buckets == 0
        assert result.total_files == 0
        assert result.total_size_bytes == 0
        assert result.active_uploads == 0

    @pytest.mark.asyncio
    async def test_get_storage_overview_multiple_buckets_sum(self):
        svc, bucket_repo, file_repo, upload_repo = self._make_service()
        bucket_repo.count.return_value = 3
        file_repo.count.return_value = 50
        bucket_repo.list.return_value = [
            _make_bucket_doc("b1", total_size_bytes=1000),
            _make_bucket_doc("b2", total_size_bytes=2000),
            _make_bucket_doc("b3", total_size_bytes=3000),
        ]
        upload_repo.count.return_value = 1

        result = await svc.get_storage_overview()
        assert result.total_size_bytes == 6000

    @pytest.mark.asyncio
    async def test_get_upload_stats_zero_sessions(self):
        svc, _, _, upload_repo = self._make_service()
        upload_repo.count.side_effect = [0, 0, 0, 0]
        upload_repo.list.return_value = []

        result = await svc.get_upload_stats()
        assert result.total_uploads == 0
        assert result.total_bytes_uploaded == 0

    @pytest.mark.asyncio
    async def test_get_upload_stats_no_completed(self):
        svc, _, _, upload_repo = self._make_service()
        upload_repo.count.side_effect = [5, 0, 2, 3]
        upload_repo.list.return_value = []

        result = await svc.get_upload_stats()
        assert result.total_uploads == 5
        assert result.completed == 0
        assert result.total_bytes_uploaded == 0

    @pytest.mark.asyncio
    async def test_get_upload_stats_large_bytes(self):
        svc, _, _, upload_repo = self._make_service()
        upload_repo.count.side_effect = [2, 2, 0, 0]
        s1 = MagicMock()
        s1.uploaded_bytes = 5 * 1024 * 1024 * 1024  # 5 GB
        s2 = MagicMock()
        s2.uploaded_bytes = 3 * 1024 * 1024 * 1024  # 3 GB
        upload_repo.list.return_value = [s1, s2]

        result = await svc.get_upload_stats()
        assert result.total_bytes_uploaded == 8 * 1024 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_get_bucket_stats_propagates_bucket_id(self):
        svc, bucket_repo, _, upload_repo = self._make_service()
        bucket_repo.get_by_id.return_value = _make_bucket_doc("specific-bucket")
        upload_repo.count.return_value = 0

        await svc.get_bucket_stats("specific-bucket")
        bucket_repo.get_by_id.assert_called_once_with("specific-bucket")

    @pytest.mark.asyncio
    async def test_get_storage_overview_active_uploads_count(self):
        svc, bucket_repo, file_repo, upload_repo = self._make_service()
        bucket_repo.count.return_value = 1
        file_repo.count.return_value = 10
        bucket_repo.list.return_value = [_make_bucket_doc("b1", total_size_bytes=100)]
        upload_repo.count.return_value = 7

        result = await svc.get_storage_overview()
        assert result.active_uploads == 7


# ===========================================================================
# BucketService Extended Tests
# ===========================================================================


class TestBucketServiceEdgeCases:
    """Bucket 服务边界条件测试。"""

    def _make_service(self):
        bucket_repo = AsyncMock()
        storage_backend = AsyncMock()
        svc = BucketService(bucket_repo, storage_backend)
        return svc, bucket_repo, storage_backend

    @pytest.mark.asyncio
    async def test_update_bucket_not_found(self):
        svc, bucket_repo, _ = self._make_service()
        bucket_repo.update.return_value = None

        from taolib.testing.file_storage.models.bucket import BucketUpdate

        result = await svc.update_bucket("nonexistent", BucketUpdate(description="x"))
        bucket_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_bucket_force_with_zero_files(self):
        svc, bucket_repo, storage_backend = self._make_service()
        bucket_repo.get_by_id.return_value = _make_bucket_doc(file_count=0)
        bucket_repo.delete.return_value = True

        result = await svc.delete_bucket("test-bucket", force=True)
        assert result is True

    @pytest.mark.asyncio
    async def test_list_buckets_empty(self):
        svc, bucket_repo, _ = self._make_service()
        bucket_repo.list.return_value = []

        result = await svc.list_buckets()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_buckets_pagination(self):
        svc, bucket_repo, _ = self._make_service()
        bucket_repo.list.return_value = [_make_bucket_doc("b1")]

        await svc.list_buckets(skip=50, limit=5)
        bucket_repo.list.assert_called_once_with(skip=50, limit=5)

    @pytest.mark.asyncio
    async def test_create_bucket_backend_failure(self):
        svc, bucket_repo, storage_backend = self._make_service()
        bucket_repo.find_by_name.return_value = None
        storage_backend.create_bucket.side_effect = RuntimeError("Backend down")

        with pytest.raises(RuntimeError, match="Backend down"):
            await svc.create_bucket(MagicMock(name="new-bucket"))



