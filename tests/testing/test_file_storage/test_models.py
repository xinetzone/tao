"""测试文件存储模块 - 模型验证。"""

import pytest
from pydantic import ValidationError

from taolib.testing.file_storage.models.bucket import BucketCreate, LifecycleRules
from taolib.testing.file_storage.models.enums import (
    AccessLevel,
    FileStatus,
    MediaType,
    StorageClass,
    ThumbnailSize,
    UploadStatus,
)
from taolib.testing.file_storage.models.file import FileMetadataCreate, FileMetadataUpdate
from taolib.testing.file_storage.models.stats import BucketStatsResponse
from taolib.testing.file_storage.models.thumbnail import ThumbnailInfo
from taolib.testing.file_storage.models.upload import UploadSessionCreate
from taolib.testing.file_storage.models.version import FileVersionResponse


class TestEnums:
    """测试枚举值。"""

    def test_access_level_values(self) -> None:
        assert AccessLevel.PUBLIC == "public"
        assert AccessLevel.PRIVATE == "private"
        assert AccessLevel.SIGNED_URL == "signed_url"

    def test_file_status_values(self) -> None:
        assert FileStatus.ACTIVE == "active"
        assert FileStatus.PENDING == "pending"
        assert FileStatus.DELETED == "deleted"

    def test_upload_status_values(self) -> None:
        assert UploadStatus.INITIATED == "initiated"
        assert UploadStatus.COMPLETED == "completed"
        assert UploadStatus.IN_PROGRESS == "in_progress"

    def test_storage_class_values(self) -> None:
        assert StorageClass.STANDARD == "standard"
        assert StorageClass.ARCHIVE == "archive"

    def test_thumbnail_size_values(self) -> None:
        assert ThumbnailSize.SMALL == "small"
        assert ThumbnailSize.MEDIUM == "medium"
        assert ThumbnailSize.LARGE == "large"

    def test_media_type_values(self) -> None:
        assert MediaType.IMAGE == "image"
        assert MediaType.VIDEO == "video"
        assert MediaType.DOCUMENT == "document"


class TestBucketModels:
    """测试 Bucket 模型。"""

    def test_bucket_create_valid(self) -> None:
        bucket = BucketCreate(name="my-bucket")
        assert bucket.name == "my-bucket"
        assert bucket.access_level == AccessLevel.PRIVATE
        assert bucket.max_file_size_bytes == 5 * 1024 * 1024 * 1024
        assert bucket.allowed_mime_types == []
        assert bucket.tags == []

    def test_bucket_create_with_lifecycle(self) -> None:
        rules = LifecycleRules(
            auto_expire_days=30, versioning_enabled=True, max_versions=10
        )
        bucket = BucketCreate(name="versioned-bucket", lifecycle_rules=rules)
        assert bucket.lifecycle_rules is not None
        assert bucket.lifecycle_rules.auto_expire_days == 30
        assert bucket.lifecycle_rules.versioning_enabled is True

    def test_bucket_create_name_too_long(self) -> None:
        with pytest.raises(ValidationError):
            BucketCreate(name="a" * 64)

    def test_bucket_create_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            BucketCreate(name="")


class TestFileModels:
    """测试 File 模型。"""

    def test_file_metadata_create_valid(self) -> None:
        file_meta = FileMetadataCreate(
            bucket_id="bucket-1",
            object_key="test/image.jpg",
            original_filename="image.jpg",
            content_type="image/jpeg",
            size_bytes=102400,
            media_type=MediaType.IMAGE,
        )
        assert file_meta.bucket_id == "bucket-1"
        assert file_meta.access_level == AccessLevel.PRIVATE
        assert file_meta.tags == []

    def test_file_metadata_update_partial(self) -> None:
        update = FileMetadataUpdate(
            access_level=AccessLevel.PUBLIC, description="Updated"
        )
        data = update.model_dump(exclude_unset=True)
        assert "access_level" in data
        assert "description" in data
        assert "tags" not in data

    def test_file_metadata_size_zero(self) -> None:
        file_meta = FileMetadataCreate(
            bucket_id="bucket-1",
            object_key="test/empty.txt",
            original_filename="empty.txt",
            content_type="text/plain",
            size_bytes=0,
            media_type=MediaType.DOCUMENT,
        )
        assert file_meta.size_bytes == 0

    def test_file_metadata_negative_size(self) -> None:
        with pytest.raises(ValidationError):
            FileMetadataCreate(
                bucket_id="bucket-1",
                object_key="test/neg.txt",
                original_filename="neg.txt",
                content_type="text/plain",
                size_bytes=-1,
                media_type=MediaType.DOCUMENT,
            )


class TestUploadModels:
    """测试 Upload 模型。"""

    def test_upload_session_create_valid(self) -> None:
        session = UploadSessionCreate(
            bucket_id="bucket-1",
            object_key="test/video.mp4",
            original_filename="video.mp4",
            content_type="video/mp4",
            total_size_bytes=10 * 1024 * 1024,
            total_chunks=2,
        )
        assert session.total_chunks == 2
        assert session.chunk_size_bytes == 5 * 1024 * 1024

    def test_upload_session_chunk_size_too_small(self) -> None:
        with pytest.raises(ValidationError):
            UploadSessionCreate(
                bucket_id="bucket-1",
                object_key="test/file.bin",
                original_filename="file.bin",
                content_type="application/octet-stream",
                total_size_bytes=1000,
                chunk_size_bytes=1024,  # < 1MB
                total_chunks=1,
            )


class TestThumbnailModels:
    """测试 Thumbnail 模型。"""

    def test_thumbnail_info(self) -> None:
        info = ThumbnailInfo(
            size=ThumbnailSize.SMALL,
            width=150,
            height=100,
            url="https://example.com/thumb.webp",
            storage_path="bucket/_thumbnails/small.webp",
            size_bytes=5120,
        )
        assert info.size == ThumbnailSize.SMALL
        assert info.width == 150


class TestVersionModels:
    """测试 Version 模型。"""

    def test_file_version_response(self) -> None:
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        version = FileVersionResponse(
            id="v1",
            file_id="file-1",
            version_number=1,
            size_bytes=102400,
            checksum_sha256="abc123",
            storage_path="bucket/test/image.jpg",
            created_by="admin",
            created_at=now,
        )
        assert version.version_number == 1


class TestStatsModels:
    """测试 Stats 模型。"""

    def test_bucket_stats_response(self) -> None:
        stats = BucketStatsResponse(
            bucket_id="bucket-1",
            bucket_name="test-bucket",
            file_count=10,
            total_size_bytes=1024000,
            upload_count=5,
            download_count=20,
        )
        assert stats.file_count == 10
        assert stats.total_size_bytes == 1024000



