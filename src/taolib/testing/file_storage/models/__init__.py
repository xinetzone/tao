"""文件存储模型模块。

导出所有 Pydantic 数据模型。
"""

from taolib.testing.file_storage.models.bucket import (
    BucketBase,
    BucketCreate,
    BucketDocument,
    BucketResponse,
    BucketUpdate,
    LifecycleRules,
)
from taolib.testing.file_storage.models.enums import (
    AccessLevel,
    FileStatus,
    MediaType,
    StorageClass,
    ThumbnailSize,
    UploadStatus,
)
from taolib.testing.file_storage.models.file import (
    FileMetadataBase,
    FileMetadataCreate,
    FileMetadataDocument,
    FileMetadataResponse,
    FileMetadataUpdate,
)
from taolib.testing.file_storage.models.stats import (
    BucketStatsResponse,
    StorageOverviewResponse,
    UploadStatsResponse,
)
from taolib.testing.file_storage.models.thumbnail import ThumbnailDocument, ThumbnailInfo
from taolib.testing.file_storage.models.upload import (
    ChunkRecord,
    UploadSessionCreate,
    UploadSessionDocument,
    UploadSessionResponse,
)
from taolib.testing.file_storage.models.version import (
    FileVersionDocument,
    FileVersionResponse,
)

__all__ = [
    # 枚举
    "AccessLevel",
    "FileStatus",
    "MediaType",
    "StorageClass",
    "ThumbnailSize",
    "UploadStatus",
    # Bucket
    "BucketBase",
    "BucketCreate",
    "BucketDocument",
    "BucketResponse",
    "BucketUpdate",
    "LifecycleRules",
    # File
    "FileMetadataBase",
    "FileMetadataCreate",
    "FileMetadataDocument",
    "FileMetadataResponse",
    "FileMetadataUpdate",
    # Upload
    "ChunkRecord",
    "UploadSessionCreate",
    "UploadSessionDocument",
    "UploadSessionResponse",
    # Thumbnail
    "ThumbnailDocument",
    "ThumbnailInfo",
    # Version
    "FileVersionDocument",
    "FileVersionResponse",
    # Stats
    "BucketStatsResponse",
    "StorageOverviewResponse",
    "UploadStatsResponse",
]


