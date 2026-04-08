"""分片上传服务。

编排大文件分片上传流程。
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from taolib.testing.file_storage.errors import (
    BucketNotFoundError,
    ChunkMismatchError,
    FileValidationError,
    UploadSessionExpiredError,
    UploadSessionNotFoundError,
)
from taolib.testing.file_storage.models.enums import FileStatus, UploadStatus
from taolib.testing.file_storage.models.file import FileMetadataResponse
from taolib.testing.file_storage.models.upload import (
    ChunkRecord,
    UploadSessionCreate,
    UploadSessionResponse,
)
from taolib.testing.file_storage.repository.bucket_repo import BucketRepository
from taolib.testing.file_storage.repository.chunk_repo import ChunkRepository
from taolib.testing.file_storage.repository.file_repo import FileRepository
from taolib.testing.file_storage.repository.upload_repo import UploadSessionRepository
from taolib.testing.file_storage.storage.protocols import StorageBackendProtocol


class UploadService:
    """分片上传服务。"""

    def __init__(
        self,
        upload_repo: UploadSessionRepository,
        chunk_repo: ChunkRepository,
        file_repo: FileRepository,
        bucket_repo: BucketRepository,
        storage_backend: StorageBackendProtocol,
        upload_session_ttl_hours: int = 24,
    ) -> None:
        self._upload_repo = upload_repo
        self._chunk_repo = chunk_repo
        self._file_repo = file_repo
        self._bucket_repo = bucket_repo
        self._storage_backend = storage_backend
        self._ttl_hours = upload_session_ttl_hours

    async def init_upload(
        self,
        data: UploadSessionCreate,
        user_id: str = "system",
    ) -> UploadSessionResponse:
        """初始化分片上传会话。"""
        # 验证桶存在
        bucket = await self._bucket_repo.get_by_id(data.bucket_id)
        if bucket is None:
            raise BucketNotFoundError(f"存储桶不存在: {data.bucket_id}")

        # 验证文件大小
        if data.total_size_bytes > bucket.max_file_size_bytes:
            raise FileValidationError(
                f"文件大小 {data.total_size_bytes} 字节超出限制 "
                f"{bucket.max_file_size_bytes} 字节"
            )

        # 在后端创建分片上传
        backend_upload_id = await self._storage_backend.create_multipart_upload(
            bucket=data.bucket_id,
            key=data.object_key,
            content_type=data.content_type,
        )

        now = datetime.now(UTC)
        session_id = uuid.uuid4().hex
        doc = {
            "_id": session_id,
            **data.model_dump(),
            "status": UploadStatus.INITIATED,
            "uploaded_chunks": [],
            "uploaded_bytes": 0,
            "backend_upload_id": backend_upload_id,
            "created_by": user_id,
            "expires_at": now + timedelta(hours=self._ttl_hours),
            "created_at": now,
            "updated_at": now,
        }
        session = await self._upload_repo.create(doc)
        return session.to_response()

    async def upload_chunk(
        self,
        session_id: str,
        chunk_index: int,
        data: bytes,
        checksum: str | None = None,
    ) -> ChunkRecord:
        """上传分片。"""
        session = await self._upload_repo.get_by_id(session_id)
        if session is None:
            raise UploadSessionNotFoundError(f"上传会话不存在: {session_id}")

        if session.status in (
            UploadStatus.COMPLETED,
            UploadStatus.ABORTED,
            UploadStatus.EXPIRED,
        ):
            raise UploadSessionExpiredError(f"上传会话已结束: {session.status}")

        if datetime.now(UTC) > session.expires_at:
            await self._upload_repo.update_status(session_id, UploadStatus.EXPIRED)
            raise UploadSessionExpiredError("上传会话已过期")

        if chunk_index >= session.total_chunks or chunk_index < 0:
            raise ChunkMismatchError(
                f"分片索引 {chunk_index} 超出范围 [0, {session.total_chunks})"
            )

        # 验证校验和
        actual_checksum = hashlib.sha256(data).hexdigest()
        if checksum and checksum != actual_checksum:
            raise ChunkMismatchError(
                f"分片校验和不匹配: 期望 {checksum}, 实际 {actual_checksum}"
            )

        # 上传到后端（part_number 从 1 开始）
        part_info = await self._storage_backend.upload_part(
            bucket=session.bucket_id,
            key=session.object_key,
            upload_id=session.backend_upload_id,
            part_number=chunk_index + 1,
            data=data,
        )

        # 记录分片
        chunk_id = f"{session_id}:{chunk_index}"
        now = datetime.now(UTC)
        chunk_doc = {
            "_id": chunk_id,
            "session_id": session_id,
            "chunk_index": chunk_index,
            "size_bytes": len(data),
            "checksum_sha256": actual_checksum,
            "storage_path": "",
            "etag": part_info.etag,
            "uploaded_at": now,
        }
        chunk = await self._chunk_repo.create(chunk_doc)

        # 更新会话进度
        await self._upload_repo.add_uploaded_chunk(session_id, chunk_index, len(data))

        return chunk

    async def complete_upload(
        self, session_id: str, user_id: str = "system"
    ) -> FileMetadataResponse:
        """完成分片上传。"""
        session = await self._upload_repo.get_by_id(session_id)
        if session is None:
            raise UploadSessionNotFoundError(f"上传会话不存在: {session_id}")

        # 验证所有分片已上传
        chunks = await self._chunk_repo.find_by_session(session_id)
        if len(chunks) != session.total_chunks:
            raise ChunkMismatchError(
                f"分片数量不匹配: 已上传 {len(chunks)}, 总共 {session.total_chunks}"
            )

        # 更新状态
        await self._upload_repo.update_status(session_id, UploadStatus.COMPLETING)

        # 完成后端分片上传
        from taolib.testing.file_storage.storage.protocols import PartInfo

        parts = [
            PartInfo(part_number=c.chunk_index + 1, etag=c.etag or "") for c in chunks
        ]
        put_result = await self._storage_backend.complete_multipart_upload(
            bucket=session.bucket_id,
            key=session.object_key,
            upload_id=session.backend_upload_id,
            parts=parts,
        )

        # 计算完整文件的校验和（用分片校验和拼接替代）
        combined_checksums = ":".join(
            c.checksum_sha256 for c in sorted(chunks, key=lambda c: c.chunk_index)
        )
        file_checksum = hashlib.sha256(combined_checksums.encode()).hexdigest()

        # 获取桶配置
        bucket = await self._bucket_repo.get_by_id(session.bucket_id)
        expires_at = None
        if (
            bucket
            and bucket.lifecycle_rules
            and bucket.lifecycle_rules.auto_expire_days
        ):
            expires_at = datetime.now(UTC) + timedelta(
                days=bucket.lifecycle_rules.auto_expire_days
            )

        # 通过文件扩展名推断媒体类型
        from taolib.testing.file_storage.processing.validator import (
            _classify_media_type,
        )

        media_type = _classify_media_type(session.content_type)

        # 创建文件元数据记录
        now = datetime.now(UTC)
        file_id = uuid.uuid4().hex
        file_doc = {
            "_id": file_id,
            "bucket_id": session.bucket_id,
            "object_key": session.object_key,
            "original_filename": session.original_filename,
            "content_type": session.content_type,
            "size_bytes": session.total_size_bytes,
            "media_type": media_type,
            "access_level": "private",
            "description": "",
            "tags": [],
            "custom_metadata": {},
            "storage_path": put_result.storage_path,
            "checksum_sha256": file_checksum,
            "version": 1,
            "status": FileStatus.ACTIVE,
            "cdn_url": None,
            "thumbnails": [],
            "expires_at": expires_at,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now,
        }
        file = await self._file_repo.create(file_doc)

        # 更新桶统计
        await self._bucket_repo.increment_file_count(
            session.bucket_id,
            count_delta=1,
            size_delta=session.total_size_bytes,
        )

        # 完成会话
        await self._upload_repo.update_status(session_id, UploadStatus.COMPLETED)

        # 清理分片记录
        await self._chunk_repo.delete_by_session(session_id)

        return file.to_response()

    async def abort_upload(self, session_id: str) -> bool:
        """中止分片上传。"""
        session = await self._upload_repo.get_by_id(session_id)
        if session is None:
            raise UploadSessionNotFoundError(f"上传会话不存在: {session_id}")

        # 中止后端上传
        if session.backend_upload_id:
            await self._storage_backend.abort_multipart_upload(
                bucket=session.bucket_id,
                key=session.object_key,
                upload_id=session.backend_upload_id,
            )

        # 清理分片记录
        await self._chunk_repo.delete_by_session(session_id)

        # 更新状态
        await self._upload_repo.update_status(session_id, UploadStatus.ABORTED)
        return True

    async def get_upload_status(self, session_id: str) -> UploadSessionResponse | None:
        """获取上传状态。"""
        session = await self._upload_repo.get_by_id(session_id)
        if session is None:
            return None
        return session.to_response()

    async def cleanup_expired_sessions(self) -> int:
        """清理过期的上传会话。"""
        expired = await self._upload_repo.find_expired_sessions(datetime.now(UTC))
        count = 0
        for session in expired:
            try:
                await self.abort_upload(session.id)
                count += 1
            except Exception:
                continue
        return count


