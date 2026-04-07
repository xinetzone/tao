"""生命周期管理服务。

提供文件过期、版本管理和垃圾回收。
"""

import uuid
from datetime import UTC, datetime

from taolib.file_storage.errors import FileNotFoundError_
from taolib.file_storage.models.enums import FileStatus
from taolib.file_storage.models.version import (
    FileVersionResponse,
)
from taolib.file_storage.repository.bucket_repo import BucketRepository
from taolib.file_storage.repository.chunk_repo import ChunkRepository
from taolib.file_storage.repository.file_repo import FileRepository
from taolib.file_storage.repository.thumbnail_repo import ThumbnailRepository
from taolib.file_storage.repository.upload_repo import UploadSessionRepository
from taolib.file_storage.repository.version_repo import FileVersionRepository
from taolib.file_storage.storage.protocols import StorageBackendProtocol


class LifecycleService:
    """生命周期管理服务。"""

    def __init__(
        self,
        file_repo: FileRepository,
        version_repo: FileVersionRepository,
        thumbnail_repo: ThumbnailRepository,
        upload_repo: UploadSessionRepository,
        chunk_repo: ChunkRepository,
        bucket_repo: BucketRepository,
        storage_backend: StorageBackendProtocol,
    ) -> None:
        self._file_repo = file_repo
        self._version_repo = version_repo
        self._thumbnail_repo = thumbnail_repo
        self._upload_repo = upload_repo
        self._chunk_repo = chunk_repo
        self._bucket_repo = bucket_repo
        self._storage_backend = storage_backend

    async def expire_files(self) -> int:
        """处理已过期文件。"""
        expired = await self._file_repo.find_expired_files(datetime.now(UTC))
        count = 0
        for file in expired:
            # 从后端删除
            await self._storage_backend.delete_object(file.bucket_id, file.object_key)
            # 删除缩略图
            thumbnails = await self._thumbnail_repo.find_by_file(file.id)
            for thumb in thumbnails:
                parts = thumb.storage_path.split("/", 1)
                if len(parts) == 2:
                    await self._storage_backend.delete_object(parts[0], parts[1])
            await self._thumbnail_repo.delete_by_file(file.id)
            # 标记为删除
            await self._file_repo.update(
                file.id,
                {
                    "status": FileStatus.DELETED,
                    "updated_at": datetime.now(UTC),
                },
            )
            # 更新桶统计
            await self._bucket_repo.increment_file_count(
                file.bucket_id,
                count_delta=-1,
                size_delta=-file.size_bytes,
            )
            count += 1
        return count

    async def create_file_version(
        self,
        file_id: str,
        user_id: str = "system",
    ) -> FileVersionResponse:
        """为当前文件创建版本快照。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")

        # 获取最新版本号
        latest = await self._version_repo.find_latest(file_id)
        version_number = (latest.version_number + 1) if latest else 1

        # 创建版本记录
        version_id = uuid.uuid4().hex
        doc = {
            "_id": version_id,
            "file_id": file_id,
            "version_number": version_number,
            "size_bytes": file.size_bytes,
            "checksum_sha256": file.checksum_sha256,
            "storage_path": file.storage_path,
            "created_by": user_id,
            "created_at": datetime.now(UTC),
        }
        version = await self._version_repo.create(doc)

        # 检查桶的版本保留策略
        bucket = await self._bucket_repo.get_by_id(file.bucket_id)
        if (
            bucket
            and bucket.lifecycle_rules
            and bucket.lifecycle_rules.versioning_enabled
        ):
            max_versions = bucket.lifecycle_rules.max_versions
            await self._version_repo.delete_oldest(file_id, max_versions)

        return version.to_response()

    async def rollback_to_version(
        self,
        file_id: str,
        version_number: int,
        user_id: str = "system",
    ) -> FileVersionResponse | None:
        """回滚到指定版本。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")

        versions = await self._version_repo.find_by_file(file_id)
        target = None
        for v in versions:
            if v.version_number == version_number:
                target = v
                break
        if target is None:
            return None

        # 复制版本文件到当前路径
        src_parts = target.storage_path.split("/", 1)
        if len(src_parts) == 2:
            await self._storage_backend.copy_object(
                src_bucket=src_parts[0],
                src_key=src_parts[1],
                dst_bucket=file.bucket_id,
                dst_key=file.object_key,
            )

        # 更新文件元数据
        await self._file_repo.update(
            file_id,
            {
                "size_bytes": target.size_bytes,
                "checksum_sha256": target.checksum_sha256,
                "version": target.version_number,
                "updated_at": datetime.now(UTC),
            },
        )

        return target.to_response()

    async def gc_deleted_files(self) -> int:
        """清理已删除状态的文件记录。"""
        deleted = await self._file_repo.list(
            filters={"status": FileStatus.DELETED}, limit=1000
        )
        count = 0
        for file in deleted:
            await self._thumbnail_repo.delete_by_file(file.id)
            await self._file_repo.delete(file.id)
            count += 1
        return count
