"""文件服务。

提供文件上传、下载和元数据管理的业务逻辑。
"""

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

from taolib.file_storage.cdn.protocols import CDNProviderProtocol
from taolib.file_storage.errors import (
    BucketNotFoundError,
    FileNotFoundError_,
)
from taolib.file_storage.models.enums import (
    AccessLevel,
    FileStatus,
)
from taolib.file_storage.models.file import (
    FileMetadataResponse,
    FileMetadataUpdate,
)
from taolib.file_storage.processing.pipeline import ProcessingPipeline
from taolib.file_storage.repository.bucket_repo import BucketRepository
from taolib.file_storage.repository.file_repo import FileRepository
from taolib.file_storage.repository.thumbnail_repo import ThumbnailRepository
from taolib.file_storage.storage.protocols import StorageBackendProtocol


class FileService:
    """文件管理服务。"""

    def __init__(
        self,
        file_repo: FileRepository,
        bucket_repo: BucketRepository,
        thumbnail_repo: ThumbnailRepository,
        storage_backend: StorageBackendProtocol,
        pipeline: ProcessingPipeline,
        cdn_provider: CDNProviderProtocol | None = None,
    ) -> None:
        self._file_repo = file_repo
        self._bucket_repo = bucket_repo
        self._thumbnail_repo = thumbnail_repo
        self._storage_backend = storage_backend
        self._pipeline = pipeline
        self._cdn_provider = cdn_provider

    async def upload_file(
        self,
        bucket_id: str,
        object_key: str,
        data: bytes,
        filename: str,
        content_type: str,
        user_id: str = "system",
        access_level: AccessLevel = AccessLevel.PRIVATE,
        tags: list[str] | None = None,
        custom_metadata: dict[str, str] | None = None,
    ) -> FileMetadataResponse:
        """上传文件（简单上传，适用于小文件）。"""
        # 获取桶配置
        bucket = await self._bucket_repo.get_by_id(bucket_id)
        if bucket is None:
            raise BucketNotFoundError(f"存储桶不存在: {bucket_id}")

        # 处理文件（验证 + 校验和）
        result = await self._pipeline.process_upload(
            filename=filename,
            declared_content_type=content_type,
            data=data,
            allowed_mime_types=bucket.allowed_mime_types or None,
            max_file_size_bytes=bucket.max_file_size_bytes,
        )

        # 存储到后端
        put_result = await self._storage_backend.put_object(
            bucket=bucket_id,
            key=object_key,
            data=data,
            content_type=result.validated_content_type,
            metadata=custom_metadata,
        )

        # 计算过期时间
        expires_at = None
        if bucket.lifecycle_rules and bucket.lifecycle_rules.auto_expire_days:
            expires_at = datetime.now(UTC) + timedelta(
                days=bucket.lifecycle_rules.auto_expire_days
            )

        # CDN URL
        cdn_url = None
        if self._cdn_provider:
            cdn_url = self._cdn_provider.generate_url(bucket_id, object_key)

        now = datetime.now(UTC)
        file_id = uuid.uuid4().hex
        doc = {
            "_id": file_id,
            "bucket_id": bucket_id,
            "object_key": object_key,
            "original_filename": filename,
            "content_type": result.validated_content_type,
            "size_bytes": result.size_bytes,
            "media_type": result.media_type,
            "access_level": access_level,
            "description": "",
            "tags": tags or [],
            "custom_metadata": custom_metadata or {},
            "storage_path": put_result.storage_path,
            "checksum_sha256": result.checksum_sha256,
            "version": 1,
            "status": FileStatus.ACTIVE,
            "cdn_url": cdn_url,
            "thumbnails": [],
            "expires_at": expires_at,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now,
        }
        file_doc = await self._file_repo.create(doc)

        # 更新桶统计
        await self._bucket_repo.increment_file_count(
            bucket_id, count_delta=1, size_delta=result.size_bytes
        )

        # 异步生成缩略图
        thumbnails = await self._pipeline.generate_thumbnails(
            data, result.validated_content_type
        )
        thumb_infos = []
        for thumb in thumbnails:
            thumb_key = f"_thumbnails/{file_id}/{thumb.size}.webp"
            await self._storage_backend.put_object(
                bucket=bucket_id,
                key=thumb_key,
                data=thumb.data,
                content_type=thumb.content_type,
            )
            thumb_id = uuid.uuid4().hex
            thumb_doc = {
                "_id": thumb_id,
                "file_id": file_id,
                "size": thumb.size,
                "width": thumb.width,
                "height": thumb.height,
                "content_type": thumb.content_type,
                "storage_path": f"{bucket_id}/{thumb_key}",
                "size_bytes": len(thumb.data),
                "created_at": now,
            }
            saved_thumb = await self._thumbnail_repo.create(thumb_doc)
            thumb_url = ""
            if self._cdn_provider:
                thumb_url = self._cdn_provider.generate_url(bucket_id, thumb_key)
            thumb_infos.append(saved_thumb.to_info(url=thumb_url))

        # 更新文件的缩略图列表
        if thumb_infos:
            await self._file_repo.update(
                file_id,
                {
                    "thumbnails": [t.model_dump() for t in thumb_infos],
                    "updated_at": datetime.now(UTC),
                },
            )
            file_doc = await self._file_repo.get_by_id(file_id)

        return file_doc.to_response()

    async def get_file(self, file_id: str) -> FileMetadataResponse | None:
        """获取文件元数据。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            return None
        return file.to_response()

    async def download_file(self, file_id: str) -> AsyncIterator[bytes]:
        """下载文件（流式）。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")
        return await self._storage_backend.get_object(file.bucket_id, file.object_key)

    async def update_metadata(
        self,
        file_id: str,
        data: FileMetadataUpdate,
        user_id: str = "system",
    ) -> FileMetadataResponse | None:
        """更新文件元数据。"""
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return await self.get_file(file_id)
        updates["updated_at"] = datetime.now(UTC)
        file = await self._file_repo.update(file_id, updates)
        if file is None:
            return None
        return file.to_response()

    async def delete_file(self, file_id: str, user_id: str = "system") -> bool:
        """删除文件。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")

        # 删除后端存储
        await self._storage_backend.delete_object(file.bucket_id, file.object_key)

        # 删除缩略图
        thumbnails = await self._thumbnail_repo.find_by_file(file_id)
        for thumb in thumbnails:
            parts = thumb.storage_path.split("/", 1)
            if len(parts) == 2:
                await self._storage_backend.delete_object(parts[0], parts[1])
        await self._thumbnail_repo.delete_by_file(file_id)

        # 更新桶统计
        await self._bucket_repo.increment_file_count(
            file.bucket_id,
            count_delta=-1,
            size_delta=-file.size_bytes,
        )

        # 标记为删除
        await self._file_repo.update(
            file_id,
            {
                "status": FileStatus.DELETED,
                "updated_at": datetime.now(UTC),
            },
        )
        return True

    async def list_files(
        self,
        bucket_id: str | None = None,
        prefix: str | None = None,
        tags: list[str] | None = None,
        media_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FileMetadataResponse]:
        """列出文件。"""
        if bucket_id:
            files = await self._file_repo.find_by_bucket(bucket_id, prefix, skip, limit)
        else:
            filters = {"status": {"$ne": FileStatus.DELETED}}
            if tags:
                filters["tags"] = {"$all": tags}
            if media_type:
                filters["media_type"] = media_type
            files = await self._file_repo.list(filters=filters, skip=skip, limit=limit)
        return [f.to_response() for f in files]

    async def get_file_url(self, file_id: str, expires_in: int = 3600) -> str:
        """获取文件访问 URL。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")

        # 公开访问：返回 CDN URL
        if file.access_level == AccessLevel.PUBLIC and self._cdn_provider:
            return self._cdn_provider.generate_url(file.bucket_id, file.object_key)

        # 其他情况：返回预签名 URL
        return await self._storage_backend.generate_presigned_url(
            file.bucket_id, file.object_key, expires_in
        )
