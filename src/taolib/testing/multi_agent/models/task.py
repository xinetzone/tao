"""任务数据模型。

定义 Task 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.testing.multi_agent.models.enums import TaskStatus


class TaskConstraint(BaseModel):
    """任务约束条件。"""

    max_duration_seconds: int | None = Field(None, ge=60, description="最大持续时间(秒)")
    max_cost: float | None = Field(None, ge=0.0, description="最大成本")
    required_skills: list[str] = Field(default_factory=list, description="必需技能")
    forbidden_skills: list[str] = Field(default_factory=list, description="禁止使用的技能")
    priority: int = Field(default=5, ge=1, le=10, description="优先级(1-10)")


class TaskProgress(BaseModel):
    """任务进度。"""

    current_step: str = Field("", description="当前步骤")
    step_description: str = Field("", description="步骤描述")
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="进度百分比")
    completed_steps: list[str] = Field(default_factory=list, description="已完成步骤")
    estimated_remaining_seconds: int | None = Field(None, ge=0, description="预计剩余时间(秒)")


class TaskResult(BaseModel):
    """任务结果。"""

    success: bool = Field(False, description="是否成功")
    summary: str = Field("", description="结果摘要")
    details: dict[str, Any] = Field(default_factory=dict, description="详细结果")
    output_files: list[str] = Field(default_factory=list, description="输出文件路径")
    artifacts: dict[str, Any] = Field(default_factory=dict, description="产物数据")
    warnings: list[str] = Field(default_factory=list, description="警告信息")
    errors: list[str] = Field(default_factory=list, description="错误信息")


class SubTask(BaseModel):
    """子任务。"""

    id: str = Field(..., description="子任务ID")
    name: str = Field(..., description="子任务名称")
    description: str = Field("", description="子任务描述")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="子任务状态")
    assigned_agent_id: str | None = Field(None, description="分配的智能体ID")
    result: TaskResult | None = Field(None, description="子任务结果")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = Field(None, description="完成时间")


class TaskBase(BaseModel):
    """任务基础字段。"""

    name: str = Field(..., description="任务名称", min_length=1, max_length=255)
    description: str = Field("", description="任务描述", max_length=5000)
    user_input: str = Field("", description="用户输入", max_length=10000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    constraints: TaskConstraint = Field(default_factory=TaskConstraint, description="约束条件")
    progress: TaskProgress = Field(default_factory=TaskProgress, description="进度")
    result: TaskResult | None = Field(None, description="结果")
    subtasks: list[SubTask] = Field(default_factory=list, description="子任务列表")
    assigned_agent_id: str | None = Field(None, description="分配的主智能体ID")
    tags: list[str] = Field(default_factory=list, description="标签")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class TaskCreate(TaskBase):
    """创建任务的输入模型。"""

    pass


class TaskUpdate(BaseModel):
    """更新任务的输入模型(所有字段可选)。"""

    name: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    constraints: TaskConstraint | None = None
    progress: TaskProgress | None = None
    result: TaskResult | None = None
    subtasks: list[SubTask] | None = None
    assigned_agent_id: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class TaskResponse(TaskBase):
    """任务的 API 响应模型。"""

    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_seconds: float | None = Field(None, ge=0.0, description="执行耗时(秒)")

    model_config = {"from_attributes": True}


class TaskDocument(TaskBase):
    """任务的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_seconds: float | None = None

    model_config = {"populate_by_name": True}

    def to_response(self) -> TaskResponse:
        """转换为 API 响应。"""
        return TaskResponse(
            _id=self.id,
            name=self.name,
            description=self.description,
            user_input=self.user_input,
            status=self.status,
            constraints=self.constraints,
            progress=self.progress,
            result=self.result,
            subtasks=self.subtasks,
            assigned_agent_id=self.assigned_agent_id,
            tags=self.tags,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            execution_seconds=self.execution_seconds,
        )
