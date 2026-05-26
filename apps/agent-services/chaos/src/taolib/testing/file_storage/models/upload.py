"""分片上传数据模型。

定义上传会话和分片记录模型。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from taolib.testing.file_storage.models.enums import UploadStatus


class UploadSessionBase(BaseModel):
    """上传会话基础字段。"""

    bucket_id: str = Field(..., description="目标桶 ID")
    object_key: str = Field(
        ..., description="目标对象键", min_length=1, max_length=1024
    )
    original_filename: str = Field(..., description="原始文件名", max_length=255)
    content_type: str = Field(..., description="MIME 类型", max_length=255)
    total_size_bytes: int = Field(..., description="文件总大小（字节）", ge=1)
    chunk_size_bytes: int = Field(
        default=5 * 1024 * 1024,
        description="分片大小（字节）",
        ge=1024 * 1024,
        le=100 * 1024 * 1024,
    )
    total_chunks: int = Field(..., description="总分片数", ge=1)


class UploadSessionCreate(UploadSessionBase):
    """创建上传会话的输入模型。"""


class UploadSessionResponse(UploadSessionBase):
    """上传会话的 API 响应模型。"""

    id: str = Field(alias="_id")
    status: UploadStatus = Field(..., description="上传状态")
    uploaded_chunks: list[int] = Field(
        default_factory=list, description="已上传分片索引"
    )
    uploaded_bytes: int = Field(default=0, description="已上传字节数")
    progress_percent: float = Field(default=0.0, description="上传进度百分比")
    backend_upload_id: str | None = Field(None, description="后端 multipart upload ID")
    created_by: str = Field(..., description="发起用户")
    expires_at: datetime = Field(..., description="过期时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class UploadSessionDocument(UploadSessionBase):
    """上传会话的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    status: UploadStatus = UploadStatus.INITIATED
    uploaded_chunks: list[int] = Field(default_factory=list)
    uploaded_bytes: int = 0
    backend_upload_id: str | None = None
    created_by: str = "system"
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    @property
    def progress_percent(self) -> float:
        """计算上传进度百分比。"""
        if self.total_chunks == 0:
            return 0.0
        return round(len(self.uploaded_chunks) / self.total_chunks * 100, 2)

    def to_response(self) -> UploadSessionResponse:
        """转换为 API 响应。"""
        return UploadSessionResponse(
            _id=self.id,
            bucket_id=self.bucket_id,
            object_key=self.object_key,
            original_filename=self.original_filename,
            content_type=self.content_type,
            total_size_bytes=self.total_size_bytes,
            chunk_size_bytes=self.chunk_size_bytes,
            total_chunks=self.total_chunks,
            status=self.status,
            uploaded_chunks=self.uploaded_chunks,
            uploaded_bytes=self.uploaded_bytes,
            progress_percent=self.progress_percent,
            backend_upload_id=self.backend_upload_id,
            created_by=self.created_by,
            expires_at=self.expires_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class ChunkRecord(BaseModel):
    """分片记录模型。"""

    id: str = Field(alias="_id")
    session_id: str = Field(..., description="会话 ID")
    chunk_index: int = Field(..., description="分片索引（从 0 开始）", ge=0)
    size_bytes: int = Field(..., description="分片大小", ge=0)
    checksum_sha256: str = Field(..., description="分片 SHA-256 校验和")
    storage_path: str = Field("", description="临时存储路径")
    etag: str | None = Field(None, description="后端返回的 ETag")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}


