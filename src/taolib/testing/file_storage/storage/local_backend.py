"""本地文件系统存储后端。

用于开发和测试环境。
"""

import hashlib
import shutil
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from taolib.testing.file_storage.errors import StorageBackendError
from taolib.testing.file_storage.storage.protocols import (
    ObjectInfo,
    PartInfo,
    PutObjectResult,
)


class LocalStorageBackend:
    """本地文件系统存储后端实现。"""

    def __init__(self, base_path: str = "./storage") -> None:
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._multipart_uploads: dict[str, dict[str, Any]] = {}

    def _bucket_path(self, bucket: str) -> Path:
        return self._base_path / bucket

    def _object_path(self, bucket: str, key: str) -> Path:
        return self._bucket_path(bucket) / key

    async def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes | AsyncIterator[bytes],
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> PutObjectResult:
        """上传对象到本地文件系统。"""
        obj_path = self._object_path(bucket, key)
        obj_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(data, bytes):
            content = data
        else:
            chunks = []
            async for chunk in data:
                chunks.append(chunk)
            content = b"".join(chunks)

        obj_path.write_bytes(content)
        etag = hashlib.md5(content).hexdigest()
        return PutObjectResult(storage_path=f"{bucket}/{key}", etag=etag)

    async def get_object(self, bucket: str, key: str) -> AsyncIterator[bytes]:
        """从本地文件系统读取对象。"""
        obj_path = self._object_path(bucket, key)
        if not obj_path.exists():
            raise StorageBackendError(f"对象不存在: {bucket}/{key}")

        async def _stream() -> AsyncIterator[bytes]:
            chunk_size = 8192
            with open(obj_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        return _stream()

    async def delete_object(self, bucket: str, key: str) -> bool:
        """从本地文件系统删除对象。"""
        obj_path = self._object_path(bucket, key)
        if obj_path.exists():
            obj_path.unlink()
            return True
        return False

    async def copy_object(
        self,
        src_bucket: str,
        src_key: str,
        dst_bucket: str,
        dst_key: str,
    ) -> PutObjectResult:
        """复制本地文件。"""
        src_path = self._object_path(src_bucket, src_key)
        if not src_path.exists():
            raise StorageBackendError(f"源对象不存在: {src_bucket}/{src_key}")
        dst_path = self._object_path(dst_bucket, dst_key)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        content = dst_path.read_bytes()
        etag = hashlib.md5(content).hexdigest()
        return PutObjectResult(storage_path=f"{dst_bucket}/{dst_key}", etag=etag)

    async def head_object(self, bucket: str, key: str) -> ObjectInfo:
        """获取本地文件元信息。"""
        obj_path = self._object_path(bucket, key)
        if not obj_path.exists():
            raise StorageBackendError(f"对象不存在: {bucket}/{key}")
        stat = obj_path.stat()
        content = obj_path.read_bytes()
        etag = hashlib.md5(content).hexdigest()
        return ObjectInfo(
            key=key,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
            etag=etag,
            content_type="application/octet-stream",
        )

    async def object_exists(self, bucket: str, key: str) -> bool:
        """检查本地文件是否存在。"""
        return self._object_path(bucket, key).exists()

    async def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> tuple[list[ObjectInfo], str | None]:
        """列出本地文件。"""
        bucket_path = self._bucket_path(bucket)
        if not bucket_path.exists():
            return [], None

        objects: list[ObjectInfo] = []
        for path in sorted(bucket_path.rglob("*")):
            if path.is_file():
                rel_key = path.relative_to(bucket_path).as_posix()
                if prefix and not rel_key.startswith(prefix):
                    continue
                stat = path.stat()
                objects.append(
                    ObjectInfo(
                        key=rel_key,
                        size=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                        etag="",
                        content_type="application/octet-stream",
                    )
                )
                if len(objects) >= max_keys:
                    break
        return objects, None

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """生成本地文件伪签名 URL（仅用于开发）。"""
        return f"file://{self._object_path(bucket, key)}"

    async def create_multipart_upload(
        self,
        bucket: str,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """创建本地分片上传会话。"""
        upload_id = uuid.uuid4().hex
        tmp_dir = self._base_path / "_multipart" / upload_id
        tmp_dir.mkdir(parents=True, exist_ok=True)
        self._multipart_uploads[upload_id] = {
            "bucket": bucket,
            "key": key,
            "content_type": content_type,
            "tmp_dir": tmp_dir,
            "parts": {},
        }
        return upload_id

    async def upload_part(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> PartInfo:
        """上传分片到本地临时目录。"""
        if upload_id not in self._multipart_uploads:
            raise StorageBackendError(f"分片上传会话不存在: {upload_id}")
        upload = self._multipart_uploads[upload_id]
        part_path = upload["tmp_dir"] / f"part_{part_number:05d}"
        part_path.write_bytes(data)
        etag = hashlib.md5(data).hexdigest()
        upload["parts"][part_number] = {"path": part_path, "etag": etag}
        return PartInfo(part_number=part_number, etag=etag)

    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[PartInfo],
    ) -> PutObjectResult:
        """完成本地分片上传（合并文件）。"""
        if upload_id not in self._multipart_uploads:
            raise StorageBackendError(f"分片上传会话不存在: {upload_id}")
        upload = self._multipart_uploads[upload_id]
        obj_path = self._object_path(bucket, key)
        obj_path.parent.mkdir(parents=True, exist_ok=True)

        hasher = hashlib.md5()
        with open(obj_path, "wb") as out:
            for part in sorted(parts, key=lambda p: p.part_number):
                part_data = upload["parts"][part.part_number]
                content = part_data["path"].read_bytes()
                out.write(content)
                hasher.update(content)

        # 清理临时目录
        shutil.rmtree(upload["tmp_dir"], ignore_errors=True)
        del self._multipart_uploads[upload_id]

        return PutObjectResult(storage_path=f"{bucket}/{key}", etag=hasher.hexdigest())

    async def abort_multipart_upload(
        self, bucket: str, key: str, upload_id: str
    ) -> None:
        """中止本地分片上传。"""
        if upload_id in self._multipart_uploads:
            upload = self._multipart_uploads[upload_id]
            shutil.rmtree(upload["tmp_dir"], ignore_errors=True)
            del self._multipart_uploads[upload_id]

    async def create_bucket(self, bucket: str) -> None:
        """创建本地存储桶目录。"""
        self._bucket_path(bucket).mkdir(parents=True, exist_ok=True)

    async def delete_bucket(self, bucket: str) -> None:
        """删除本地存储桶目录。"""
        bucket_path = self._bucket_path(bucket)
        if bucket_path.exists():
            shutil.rmtree(bucket_path)

    async def bucket_exists(self, bucket: str) -> bool:
        """检查本地存储桶目录是否存在。"""
        return self._bucket_path(bucket).exists()


