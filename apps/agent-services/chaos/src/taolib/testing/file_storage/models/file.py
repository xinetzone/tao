"""文件元数据模型。

定义 FileMetadata 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.testing.file_storage.models.enums import (
    AccessLevel,
    FileStatus,
    MediaType,
)
from taolib.testing.file_storage.models.thumbnail import ThumbnailInfo


class FileMetadataBase(BaseModel):
    """文件元数据基础字段。"""

    bucket_id: str = Field(..., description="所属桶 ID")
    object_key: str = Field(
        ..., description="对象键（桶内路径）", min_length=1, max_length=1024
    )
    original_filename: str = Field(..., description="原始文件名", max_length=255)
    content_type: str = Field(..., description="MIME 类型", max_length=255)
    size_bytes: int = Field(..., description="文件大小（字节）", ge=0)
    media_type: MediaType = Field(..., description="媒体类型分类")
    access_level: AccessLevel = Field(
        default=AccessLevel.PRIVATE, description="访问级别"
    )
    description: str = Field("", description="文件描述", max_length=1000)
    tags: list[str] = Field(default_factory=list, description="标签")
    custom_metadata: dict[str, Any] = Field(
        default_factory=dict, description="自定义元数据"
    )


class FileMetadataCreate(FileMetadataBase):
    """创建文件元数据的输入模型。"""


class FileMetadataUpdate(BaseModel):
    """更新文件元数据的输入模型（所有字段可选）。"""

    access_level: AccessLevel | None = None
    description: str | None = None
    tags: list[str] | None = None
    custom_metadata: dict[str, Any] | None = None


class FileMetadataResponse(FileMetadataBase):
    """文件元数据的 API 响应模型。"""

    id: str = Field(alias="_id")
    storage_path: str = Field(..., description="后端存储路径")
    checksum_sha256: str = Field(..., description="SHA-256 校验和")
    version: int = Field(default=1, description="当前版本号")
    status: FileStatus = Field(default=FileStatus.ACTIVE, description="文件状态")
    cdn_url: str | None = Field(None, description="CDN 访问 URL")
    thumbnails: list[ThumbnailInfo] = Field(
        default_factory=list, description="缩略图列表"
    )
    expires_at: datetime | None = Field(None, description="过期时间")
    created_by: str = Field(..., description="上传用户")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class FileMetadataDocument(FileMetadataBase):
    """文件元数据的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    storage_path: str = ""
    checksum_sha256: str = ""
    version: int = 1
    status: FileStatus = FileStatus.ACTIVE
    cdn_url: str | None = None
    thumbnails: list[ThumbnailInfo] = Field(default_factory=list)
    expires_at: datetime | None = None
    created_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    def to_response(self) -> FileMetadataResponse:
        """转换为 API 响应。"""
        return FileMetadataResponse(
            _id=self.id,
            bucket_id=self.bucket_id,
            object_key=self.object_key,
            original_filename=self.original_filename,
            content_type=self.content_type,
            size_bytes=self.size_bytes,
            media_type=self.media_type,
            access_level=self.access_level,
            description=self.description,
            tags=self.tags,
            custom_metadata=self.custom_metadata,
            storage_path=self.storage_path,
            checksum_sha256=self.checksum_sha256,
            version=self.version,
            status=self.status,
            cdn_url=self.cdn_url,
            thumbnails=self.thumbnails,
            expires_at=self.expires_at,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


