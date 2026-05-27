"""同步失败记录数据模型。

定义 FailureRecord 模型（失败文档）。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class FailureRecordDocument(BaseModel):
    """失败记录文档模型。"""

    id: str = Field(alias="_id")
    job_id: str = Field(..., description="作业 ID")
    log_id: str = Field(..., description="日志 ID")
    collection_name: str = Field(..., description="集合名称")
    document_id: str = Field(..., description="源文档 ID")
    phase: str = Field(..., description="失败阶段（extract/transform/load）")
    error_type: str = Field(..., description="异常类型")
    error_message: str = Field(..., description="错误消息")
    document_snapshot: dict | None = Field(None, description="文档快照（截断至 4KB）")
    retry_count: int = Field(default=0, description="重试次数")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}
