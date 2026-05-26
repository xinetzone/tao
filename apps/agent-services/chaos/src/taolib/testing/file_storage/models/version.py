"""文件版本数据模型。

定义文件版本的文档和响应模型。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class FileVersionResponse(BaseModel):
    """文件版本的 API 响应模型。"""

    id: str
    file_id: str
    version_number: int
    size_bytes: int
    checksum_sha256: str
    storage_path: str
    created_by: str
    created_at: datetime


class FileVersionDocument(BaseModel):
    """文件版本的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    file_id: str = Field(..., description="关联文件 ID")
    version_number: int = Field(..., description="版本号", ge=1)
    size_bytes: int = Field(..., description="该版本文件大小", ge=0)
    checksum_sha256: str = Field(..., description="SHA-256 校验和")
    storage_path: str = Field(..., description="存储路径")
    created_by: str = Field(default="system", description="上传用户")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    def to_response(self) -> FileVersionResponse:
        """转换为 API 响应。"""
        return FileVersionResponse(
            id=self.id,
            file_id=self.file_id,
            version_number=self.version_number,
            size_bytes=self.size_bytes,
            checksum_sha256=self.checksum_sha256,
            storage_path=self.storage_path,
            created_by=self.created_by,
            created_at=self.created_at,
        )


