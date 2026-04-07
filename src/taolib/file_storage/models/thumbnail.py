"""缩略图数据模型。

定义缩略图信息和文档模型。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from taolib.file_storage.models.enums import ThumbnailSize


class ThumbnailInfo(BaseModel):
    """缩略图信息（嵌入式轻量模型）。"""

    size: ThumbnailSize = Field(..., description="尺寸规格")
    width: int = Field(..., description="实际宽度", ge=1)
    height: int = Field(..., description="实际高度", ge=1)
    url: str = Field("", description="访问 URL")
    storage_path: str = Field(..., description="存储路径")
    size_bytes: int = Field(..., description="缩略图文件大小", ge=0)


class ThumbnailDocument(BaseModel):
    """缩略图的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    file_id: str = Field(..., description="关联文件 ID")
    size: ThumbnailSize = Field(..., description="尺寸规格")
    width: int = Field(..., description="实际宽度", ge=1)
    height: int = Field(..., description="实际高度", ge=1)
    content_type: str = Field(default="image/webp", description="缩略图 MIME 类型")
    storage_path: str = Field(..., description="存储路径")
    size_bytes: int = Field(..., description="缩略图文件大小", ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    def to_info(self, url: str = "") -> ThumbnailInfo:
        """转换为嵌入式信息模型。"""
        return ThumbnailInfo(
            size=self.size,
            width=self.width,
            height=self.height,
            url=url,
            storage_path=self.storage_path,
            size_bytes=self.size_bytes,
        )
