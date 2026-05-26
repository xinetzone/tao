"""配置数据模型模块。

定义配置相关的 Pydantic 模型，用于 API 请求/响应和 MongoDB 文档映射。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import ConfigStatus, ConfigValueType, Environment


class ConfigBase(BaseModel):
    """配置基础模型。"""

    key: str = Field(..., description="配置键", min_length=1, max_length=255)
    environment: Environment = Field(..., description="环境类型")
    service: str = Field(..., description="服务名称", min_length=1, max_length=255)
    value: Any = Field(..., description="配置值")
    value_type: ConfigValueType = Field(..., description="配置值类型")
    description: str = Field(default="", description="配置描述", max_length=1000)
    schema_id: str | None = Field(default=None, description="关联的校验 Schema ID")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    status: ConfigStatus = Field(default=ConfigStatus.DRAFT, description="配置状态")


class ConfigCreate(ConfigBase):
    """创建配置请求模型。"""

    pass


class ConfigUpdate(BaseModel):
    """更新配置请求模型。"""

    value: Any | None = Field(default=None, description="配置值")
    value_type: ConfigValueType | None = Field(default=None, description="配置值类型")
    description: str | None = Field(
        default=None, description="配置描述", max_length=1000
    )
    schema_id: str | None = Field(default=None, description="关联的校验 Schema ID")
    tags: list[str] | None = Field(default=None, description="标签列表")
    status: ConfigStatus | None = Field(default=None, description="配置状态")


class ConfigResponse(ConfigBase):
    """配置响应模型。"""

    id: str = Field(..., description="配置 ID")
    version: int = Field(..., description="当前版本号")
    created_by: str = Field(..., description="创建人用户 ID")
    updated_by: str = Field(..., description="最后更新人用户 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config = {"from_attributes": True}


class ConfigDocument(BaseModel):
    """MongoDB 配置文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    key: str = Field(..., description="配置键")
    environment: Environment = Field(..., description="环境类型")
    service: str = Field(..., description="服务名称")
    value: Any = Field(..., description="配置值")
    value_type: ConfigValueType = Field(..., description="配置值类型")
    description: str = Field(default="", description="配置描述")
    schema_id: str | None = Field(default=None, description="关联的校验 Schema ID")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    status: ConfigStatus = Field(default=ConfigStatus.DRAFT, description="配置状态")
    version: int = Field(default=1, description="当前版本号")
    created_by: str = Field(..., description="创建人用户 ID")
    updated_by: str = Field(..., description="最后更新人用户 ID")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="最后更新时间"
    )

    model_config = {"populate_by_name": True}

    def to_response(self) -> ConfigResponse:
        """转换为响应模型。"""
        return ConfigResponse(
            id=self.id,
            key=self.key,
            environment=self.environment,
            service=self.service,
            value=self.value,
            value_type=self.value_type,
            description=self.description,
            schema_id=self.schema_id,
            tags=self.tags,
            status=self.status,
            version=self.version,
            created_by=self.created_by,
            updated_by=self.updated_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


