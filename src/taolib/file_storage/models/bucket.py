"""存储桶数据模型。

定义 Bucket 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from taolib.file_storage.models.enums import AccessLevel, StorageClass


class LifecycleRules(BaseModel):
    """生命周期策略配置。"""

    auto_expire_days: int | None = Field(
        None, description="自动过期天数（None 表示不过期）", ge=1
    )
    versioning_enabled: bool = Field(default=False, description="是否启用版本控制")
    max_versions: int = Field(default=5, description="最大版本数", ge=1, le=100)


class BucketBase(BaseModel):
    """存储桶基础字段。"""

    name: str = Field(..., description="桶名称（唯一）", min_length=1, max_length=63)
    description: str = Field("", description="桶描述", max_length=1000)
    access_level: AccessLevel = Field(
        default=AccessLevel.PRIVATE, description="默认访问级别"
    )
    max_file_size_bytes: int = Field(
        default=5 * 1024 * 1024 * 1024,
        description="单文件最大大小（字节）",
        ge=1,
    )
    allowed_mime_types: list[str] = Field(
        default_factory=list, description="允许的 MIME 类型（空表示全部允许）"
    )
    storage_class: StorageClass = Field(
        default=StorageClass.STANDARD, description="存储类型"
    )
    tags: list[str] = Field(default_factory=list, description="标签")
    lifecycle_rules: LifecycleRules | None = Field(None, description="生命周期策略")


class BucketCreate(BucketBase):
    """创建存储桶的输入模型。"""


class BucketUpdate(BaseModel):
    """更新存储桶的输入模型（所有字段可选）。"""

    description: str | None = None
    access_level: AccessLevel | None = None
    max_file_size_bytes: int | None = None
    allowed_mime_types: list[str] | None = None
    storage_class: StorageClass | None = None
    tags: list[str] | None = None
    lifecycle_rules: LifecycleRules | None = None


class BucketResponse(BucketBase):
    """存储桶的 API 响应模型。"""

    id: str = Field(alias="_id")
    file_count: int = Field(default=0, description="文件数量")
    total_size_bytes: int = Field(default=0, description="总存储大小")
    created_by: str = Field(..., description="创建人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class BucketDocument(BucketBase):
    """存储桶的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    file_count: int = 0
    total_size_bytes: int = 0
    created_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    def to_response(self) -> BucketResponse:
        """转换为 API 响应。"""
        return BucketResponse(
            _id=self.id,
            name=self.name,
            description=self.description,
            access_level=self.access_level,
            max_file_size_bytes=self.max_file_size_bytes,
            allowed_mime_types=self.allowed_mime_types,
            storage_class=self.storage_class,
            tags=self.tags,
            lifecycle_rules=self.lifecycle_rules,
            file_count=self.file_count,
            total_size_bytes=self.total_size_bytes,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
