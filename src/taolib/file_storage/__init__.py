"""文件上传和存储管理模块。

提供大文件分片上传、云存储集成、CDN 分发、访问控制、生命周期管理等功能。

版本: 0.1.0
"""

from importlib import metadata

from taolib.file_storage.client import FileStorageClient
from taolib.file_storage.errors import StorageError
from taolib.file_storage.models.enums import (
    AccessLevel,
    FileStatus,
    MediaType,
    StorageClass,
    ThumbnailSize,
    UploadStatus,
)

try:
    __version__ = metadata.version("taolib")
except metadata.PackageNotFoundError:
    import os

    __version__ = os.environ.get("TAOLIB_VERSION", "0.0.0")

__all__ = [
    # 客户端
    "FileStorageClient",
    # 异常
    "StorageError",
    # 枚举
    "AccessLevel",
    "FileStatus",
    "MediaType",
    "StorageClass",
    "ThumbnailSize",
    "UploadStatus",
]
