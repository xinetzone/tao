"""智能体数据模型。

定义 Agent 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.testing.multi_agent.models.enums import AgentStatus, AgentType


class AgentCapability(BaseModel):
    """智能体能力描述。"""

    name: str = Field(..., description="能力名称")
    description: str = Field("", description="能力描述")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="置信度")
    tags: list[str] = Field(default_factory=list, description="能力标签")


class AgentConfig(BaseModel):
    """智能体配置。"""

    max_concurrent_tasks: int = Field(default=3, ge=1, description="最大并发任务数")
    timeout_seconds: int = Field(default=300, ge=30, description="任务超时时间(秒)")
    preferred_model: str | None = Field(None, description="偏好的模型")
    system_prompt: str | None = Field(None, description="系统提示词")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")


class AgentTemplate(BaseModel):
    """智能体模板。"""

    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field("", description="模板描述")
    agent_type: AgentType = Field(default=AgentType.SUB, description="智能体类型")
    capabilities: list[AgentCapability] = Field(default_factory=list, description="预设能力")
    config: AgentConfig = Field(default_factory=AgentConfig, description="默认配置")
    skills: list[str] = Field(default_factory=list, description="预加载的技能ID列表")
    tags: list[str] = Field(default_factory=list, description="模板标签")


class AgentBase(BaseModel):
    """智能体基础字段。"""

    name: str = Field(..., description="智能体名称", min_length=1, max_length=255)
    description: str = Field("", description="智能体描述", max_length=1000)
    agent_type: AgentType = Field(default=AgentType.SUB, description="智能体类型")
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="智能体状态")
    capabilities: list[AgentCapability] = Field(default_factory=list, description="能力列表")
    config: AgentConfig = Field(default_factory=AgentConfig, description="配置")
    template_id: str | None = Field(None, description="基于的模板ID")
    skills: list[str] = Field(default_factory=list, description="已加载的技能ID列表")
    tags: list[str] = Field(default_factory=list, description="标签")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class AgentCreate(AgentBase):
    """创建智能体的输入模型。"""

    pass


class AgentUpdate(BaseModel):
    """更新智能体的输入模型(所有字段可选)。"""

    name: str | None = None
    description: str | None = None
    status: AgentStatus | None = None
    capabilities: list[AgentCapability] | None = None
    config: AgentConfig | None = None
    skills: list[str] | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class AgentResponse(AgentBase):
    """智能体的 API 响应模型。"""

    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime | None = None
    current_task_id: str | None = None
    completed_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)

    model_config = {"from_attributes": True}


class AgentDocument(AgentBase):
    """智能体的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_active_at: datetime | None = None
    current_task_id: str | None = None
    completed_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)

    model_config = {"populate_by_name": True}

    def to_response(self) -> AgentResponse:
        """转换为 API 响应。"""
        return AgentResponse(
            _id=self.id,
            name=self.name,
            description=self.description,
            agent_type=self.agent_type,
            status=self.status,
            capabilities=self.capabilities,
            config=self.config,
            template_id=self.template_id,
            skills=self.skills,
            tags=self.tags,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_active_at=self.last_active_at,
            current_task_id=self.current_task_id,
            completed_tasks=self.completed_tasks,
            failed_tasks=self.failed_tasks,
        )
