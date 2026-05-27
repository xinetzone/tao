"""存储后端协议和数据类。

定义 StorageBackendProtocol 及相关数据类。
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ObjectInfo:
    """存储对象信息。"""

    key: str
    size: int
    last_modified: datetime
    etag: str
    content_type: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PartInfo:
    """分片上传部分信息。"""

    part_number: int
    etag: str


@dataclass(frozen=True, slots=True)
class PutObjectResult:
    """对象写入结果。"""

    storage_path: str
    etag: str
    version_id: str | None = None


class StorageBackendProtocol(Protocol):
    """存储后端协议。

    定义文件存储后端需要实现的所有操作。
    支持 S3 兼容存储、本地文件系统等多种后端。
    """

    async def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes | AsyncIterator[bytes],
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> PutObjectResult:
        """上传对象。"""
        ...

    async def get_object(self, bucket: str, key: str) -> AsyncIterator[bytes]:
        """下载对象（流式）。"""
        ...

    async def delete_object(self, bucket: str, key: str) -> bool:
        """删除对象。"""
        ...

    async def copy_object(
        self,
        src_bucket: str,
        src_key: str,
        dst_bucket: str,
        dst_key: str,
    ) -> PutObjectResult:
        """复制对象。"""
        ...

    async def head_object(self, bucket: str, key: str) -> ObjectInfo:
        """获取对象元信息。"""
        ...

    async def object_exists(self, bucket: str, key: str) -> bool:
        """检查对象是否存在。"""
        ...

    async def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> tuple[list[ObjectInfo], str | None]:
        """列出对象。

        Returns:
            (对象列表, 下一页 token 或 None)
        """
        ...

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """生成预签名 URL。"""
        ...

    async def create_multipart_upload(
        self, bucket: str, key: str, content_type: str = "application/octet-stream"
    ) -> str:
        """创建分片上传会话。

        Returns:
            upload_id
        """
        ...

    async def upload_part(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> PartInfo:
        """上传分片。"""
        ...

    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[PartInfo],
    ) -> PutObjectResult:
        """完成分片上传。"""
        ...

    async def abort_multipart_upload(
        self, bucket: str, key: str, upload_id: str
    ) -> None:
        """中止分片上传。"""
        ...

    async def create_bucket(self, bucket: str) -> None:
        """创建存储桶。"""
        ...

    async def delete_bucket(self, bucket: str) -> None:
        """删除存储桶。"""
        ...

    async def bucket_exists(self, bucket: str) -> bool:
        """检查存储桶是否存在。"""
        ...
