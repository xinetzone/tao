"""任务数据模型。

定义 Task 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.task_queue.models.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """任务基础字段。"""

    task_type: str = Field(..., description="任务类型", min_length=1, max_length=255)
    params: dict[str, Any] = Field(default_factory=dict, description="任务参数")
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="任务优先级"
    )
    max_retries: int = Field(default=3, description="最大重试次数", ge=0, le=10)
    retry_delays: list[int] = Field(
        default_factory=lambda: [60, 300, 900],
        description="重试延迟（秒），依次递增",
    )
    idempotency_key: str | None = Field(None, description="幂等键（防止重复提交）")
    tags: list[str] = Field(default_factory=list, description="标签")


class TaskCreate(TaskBase):
    """创建任务的输入模型。"""

    pass


class TaskUpdate(BaseModel):
    """更新任务的输入模型（所有字段可选）。"""

    status: TaskStatus | None = None
    retry_count: int | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None
    error_traceback: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    next_retry_at: datetime | None = None


class TaskResponse(TaskBase):
    """任务的 API 响应模型。"""

    id: str = Field(alias="_id")
    status: TaskStatus
    retry_count: int
    result: dict[str, Any] | None = None
    error_message: str | None = None
    error_traceback: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    next_retry_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskDocument(TaskBase):
    """任务的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    retry_count: int = Field(default=0)
    result: dict[str, Any] | None = None
    error_message: str | None = None
    error_traceback: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    next_retry_at: datetime | None = None

    model_config = {"populate_by_name": True}

    def to_response(self) -> TaskResponse:
        """转换为 API 响应。"""
        return TaskResponse(
            _id=self.id,
            task_type=self.task_type,
            params=self.params,
            priority=self.priority,
            max_retries=self.max_retries,
            retry_delays=self.retry_delays,
            idempotency_key=self.idempotency_key,
            tags=self.tags,
            status=self.status,
            retry_count=self.retry_count,
            result=self.result,
            error_message=self.error_message,
            error_traceback=self.error_traceback,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            next_retry_at=self.next_retry_at,
        )
