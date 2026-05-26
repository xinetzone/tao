"""技能数据模型。

定义 Skill 的 4-tier Pydantic 模型：
Base → Create/Update → Response → Document
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.testing.multi_agent.models.enums import SkillStatus, SkillType


class SkillTestResult(BaseModel):
    """技能测试结果。"""

    test_name: str = Field(..., description="测试名称")
    success: bool = Field(False, description="是否通过")
    input_data: dict[str, Any] = Field(default_factory=dict, description="输入数据")
    expected_output: dict[str, Any] = Field(default_factory=dict, description="预期输出")
    actual_output: dict[str, Any] = Field(default_factory=dict, description="实际输出")
    error_message: str = Field("", description="错误信息")
    execution_time_seconds: float = Field(default=0.0, ge=0.0, description="执行时间(秒)")


class SkillEvaluation(BaseModel):
    """技能评估。"""

    overall_score: float = Field(default=0.0, ge=0.0, le=1.0, description="总体评分")
    accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="准确性")
    efficiency: float = Field(default=0.0, ge=0.0, le=1.0, description="效率")
    reliability: float = Field(default=0.0, ge=0.0, le=1.0, description="可靠性")
    test_results: list[SkillTestResult] = Field(default_factory=list, description="测试结果")
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evaluator: str = Field("system", description="评估者")
    comments: str = Field("", description="评估意见")


class SkillParameter(BaseModel):
    """技能参数。"""

    name: str = Field(..., description="参数名称")
    type: str = Field(default="str", description="参数类型")
    description: str = Field("", description="参数描述")
    required: bool = Field(default=False, description="是否必需")
    default: Any = Field(None, description="默认值")
    constraints: dict[str, Any] = Field(default_factory=dict, description="约束条件")


class SkillBase(BaseModel):
    """技能基础字段。"""

    name: str = Field(..., description="技能名称", min_length=1, max_length=255)
    description: str = Field("", description="技能描述", max_length=2000)
    skill_type: SkillType = Field(default=SkillType.PROMPT, description="技能类型")
    status: SkillStatus = Field(default=SkillStatus.DRAFT, description="技能状态")
    version: str = Field(default="1.0.0", description="版本号")
    content: str = Field("", description="技能内容(prompt或代码)")
    parameters: list[SkillParameter] = Field(default_factory=list, description="参数列表")
    tags: list[str] = Field(default_factory=list, description="标签")
    categories: list[str] = Field(default_factory=list, description="分类")
    dependencies: list[str] = Field(default_factory=list, description="依赖的技能ID列表")
    evaluation: SkillEvaluation | None = Field(None, description="评估结果")
    usage_count: int = Field(default=0, ge=0, description="使用次数")
    success_count: int = Field(default=0, ge=0, description="成功次数")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class SkillCreate(SkillBase):
    """创建技能的输入模型。"""

    pass


class SkillUpdate(BaseModel):
    """更新技能的输入模型(所有字段可选)。"""

    name: str | None = None
    description: str | None = None
    skill_type: SkillType | None = None
    status: SkillStatus | None = None
    version: str | None = None
    content: str | None = None
    parameters: list[SkillParameter] | None = None
    tags: list[str] | None = None
    categories: list[str] | None = None
    dependencies: list[str] | None = None
    evaluation: SkillEvaluation | None = None
    metadata: dict[str, Any] | None = None


class SkillResponse(SkillBase):
    """技能的 API 响应模型。"""

    id: str = Field(alias="_id")
    created_by: str = Field(default="system", description="创建者")
    updated_by: str = Field(default="system", description="更新者")
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None = None

    model_config = {"from_attributes": True}


class SkillDocument(SkillBase):
    """技能的 MongoDB 文档模型。"""

    id: str = Field(alias="_id")
    created_by: str = "system"
    updated_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_used_at: datetime | None = None

    model_config = {"populate_by_name": True}

    def to_response(self) -> SkillResponse:
        """转换为 API 响应。"""
        return SkillResponse(
            _id=self.id,
            name=self.name,
            description=self.description,
            skill_type=self.skill_type,
            status=self.status,
            version=self.version,
            content=self.content,
            parameters=self.parameters,
            tags=self.tags,
            categories=self.categories,
            dependencies=self.dependencies,
            evaluation=self.evaluation,
            usage_count=self.usage_count,
            success_count=self.success_count,
            metadata=self.metadata,
            created_by=self.created_by,
            updated_by=self.updated_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_used_at=self.last_used_at,
        )
