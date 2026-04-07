"""同步日志数据模型。

定义 SyncLog 的 4-tier Pydantic 模型（执行记录）。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.data_sync.models.enums import SyncMode, SyncStatus


class SyncMetrics(BaseModel):
    """同步指标。"""

    total_extracted: int = 0
    total_transformed: int = 0
    total_loaded: int = 0
    total_skipped: int = 0
    total_failed: int = 0
    bytes_transferred: int = 0


class SyncLogBase(BaseModel):
    """同步日志基础字段。"""

    job_id: str = Field(..., description="作业 ID")
    job_name: str = Field(..., description="作业名称（冗余）")
    status: SyncStatus = Field(default=SyncStatus.PENDING)
    mode: SyncMode = Field(..., description="同步模式")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    source_database: str = Field(..., description="源数据库名")
    target_database: str = Field(..., description="目标数据库名")
    collections_synced: list[str] = Field(default_factory=list)
    metrics: SyncMetrics = Field(default_factory=SyncMetrics)
    error_message: str | None = None
    checkpoint_snapshot: dict[str, Any] | None = None


class SyncLogCreate(SyncLogBase):
    """创建同步日志的输入模型。"""

    pass


class SyncLogResponse(SyncLogBase):
    """同步日志的 API 响应模型。"""

    id: str = Field(alias="_id")

    model_config = {"from_attributes": True}


class SyncLogDocument(SyncLogBase):
    """同步日志的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}

    def to_response(self) -> SyncLogResponse:
        """转换为 API 响应。"""
        return SyncLogResponse(
            _id=self.id,
            job_id=self.job_id,
            job_name=self.job_name,
            status=self.status,
            mode=self.mode,
            started_at=self.started_at,
            finished_at=self.finished_at,
            duration_seconds=self.duration_seconds,
            source_database=self.source_database,
            target_database=self.target_database,
            collections_synced=self.collections_synced,
            metrics=self.metrics,
            error_message=self.error_message,
            checkpoint_snapshot=self.checkpoint_snapshot,
        )
