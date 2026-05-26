"""同步检查点数据模型。

定义 Checkpoint 模型（同步位点）。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class SyncCheckpoint(BaseModel):
    """同步检查点模型。"""

    id: str = Field(alias="_id")
    job_id: str = Field(..., description="作业 ID")
    collection_name: str = Field(..., description="集合名称")
    last_synced_timestamp: datetime | None = Field(None, description="最后同步的时间戳")
    last_synced_id: str | None = Field(None, description="最后同步的文档 ID")
    total_synced: int = Field(default=0, description="累计同步文档数")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}


