"""同步作业数据模型。

定义 SyncJob 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.data_sync.models.enums import FailureAction, SyncMode, SyncScope


class SyncConnectionConfig(BaseModel):
    """数据库连接配置。"""

    mongo_url: str = "mongodb://localhost:27017"
    database: str
    collections: list[str] | None = None


class SyncJobBase(BaseModel):
    """同步作业基础字段。"""

    name: str = Field(..., description="作业名称（唯一）", min_length=1, max_length=255)
    description: str = Field("", description="作业描述", max_length=1000)
    scope: SyncScope = Field(default=SyncScope.DATABASE, description="同步范围")
    mode: SyncMode = Field(default=SyncMode.INCREMENTAL, description="同步模式")
    source: SyncConnectionConfig = Field(..., description="源数据库连接")
    target: SyncConnectionConfig = Field(..., description="目标数据库连接")
    transform_module: str | None = Field(None, description="Python 转换函数模块路径")
    field_mapping: dict[str, str] | None = Field(None, description="字段映射")
    filter_query: dict[str, Any] | None = Field(None, description="MongoDB 查询过滤")
    schedule_cron: str | None = Field(None, description="cron 表达式（如 '0 * * * *'）")
    batch_size: int = Field(default=1000, description="每批文档数", ge=1, le=10000)
    failure_action: FailureAction = Field(
        default=FailureAction.SKIP, description="失败处理动作"
    )
    max_retries: int = Field(default=3, description="最大重试次数", ge=0, le=10)
    enabled: bool = Field(default=True, description="是否启用")
    tags: list[str] = Field(default_factory=list, description="标签")


class SyncJobCreate(SyncJobBase):
    """创建同步作业的输入模型。"""

    pass


class SyncJobUpdate(BaseModel):
    """更新同步作业的输入模型（所有字段可选）。"""

    description: str | None = None
    scope: SyncScope | None = None
    mode: SyncMode | None = None
    source: SyncConnectionConfig | None = None
    target: SyncConnectionConfig | None = None
    transform_module: str | None = None
    field_mapping: dict[str, str] | None = None
    filter_query: dict[str, Any] | None = None
    schedule_cron: str | None = None
    batch_size: int | None = None
    failure_action: FailureAction | None = None
    max_retries: int | None = None
    enabled: bool | None = None
    tags: list[str] | None = None


class SyncJobResponse(SyncJobBase):
    """同步作业的 API 响应模型。"""

    id: str = Field(alias="_id")
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None = None
    last_run_status: str | None = None

    model_config = {"from_attributes": True}


class SyncJobDocument(SyncJobBase):
    """同步作业的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    created_by: str = "system"
    updated_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_run_at: datetime | None = None
    last_run_status: str | None = None

    model_config = {"populate_by_name": True}

    def to_response(self) -> SyncJobResponse:
        """转换为 API 响应。"""
        return SyncJobResponse(
            _id=self.id,
            name=self.name,
            description=self.description,
            scope=self.scope,
            mode=self.mode,
            source=self.source,
            target=self.target,
            transform_module=self.transform_module,
            field_mapping=self.field_mapping,
            filter_query=self.filter_query,
            schedule_cron=self.schedule_cron,
            batch_size=self.batch_size,
            failure_action=self.failure_action,
            max_retries=self.max_retries,
            enabled=self.enabled,
            tags=self.tags,
            created_by=self.created_by,
            updated_by=self.updated_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_run_at=self.last_run_at,
            last_run_status=self.last_run_status,
        )
