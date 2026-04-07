"""存储后端模块。

导出存储协议和后端实现。
"""

from taolib.file_storage.storage.local_backend import LocalStorageBackend
from taolib.file_storage.storage.protocols import (
    ObjectInfo,
    PartInfo,
    PutObjectResult,
    StorageBackendProtocol,
)
from taolib.file_storage.storage.s3_backend import S3StorageBackend

__all__ = [
    "LocalStorageBackend",
    "ObjectInfo",
    "PartInfo",
    "PutObjectResult",
    "S3StorageBackend",
    "StorageBackendProtocol",
]
