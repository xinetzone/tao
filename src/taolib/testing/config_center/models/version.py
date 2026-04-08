"""配置版本数据模型模块。

定义配置版本历史相关的 Pydantic 模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import ChangeType


class ConfigVersionBase(BaseModel):
    """配置版本基础模型。"""

    config_id: str = Field(..., description="关联配置的 ID")
    config_key: str = Field(..., description="配置键")
    version: int = Field(..., description="版本号")
    value: Any = Field(..., description="该版本的配置值")
    changed_by: str = Field(..., description="变更人用户 ID")
    change_reason: str = Field(default="", description="变更原因", max_length=1000)
    change_type: ChangeType = Field(..., description="变更类型")
    diff_summary: dict[str, Any] | None = Field(default=None, description="差异摘要")


class ConfigVersionCreate(ConfigVersionBase):
    """创建配置版本请求模型。"""

    is_rollback_target: bool = Field(default=False, description="是否为回滚目标")


class ConfigVersionResponse(ConfigVersionBase):
    """配置版本响应模型。"""

    id: str = Field(..., description="版本 ID")
    is_rollback_target: bool = Field(default=False, description="是否为回滚目标")
    created_at: datetime = Field(..., description="变更时间")

    model_config = {"from_attributes": True}


class ConfigVersionDocument(BaseModel):
    """MongoDB 配置版本文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    config_id: str = Field(..., description="关联配置的 ID")
    config_key: str = Field(..., description="配置键")
    version: int = Field(..., description="版本号")
    value: Any = Field(..., description="该版本的配置值")
    changed_by: str = Field(..., description="变更人用户 ID")
    change_reason: str = Field(default="", description="变更原因")
    change_type: ChangeType = Field(..., description="变更类型")
    diff_summary: dict[str, Any] | None = Field(default=None, description="差异摘要")
    is_rollback_target: bool = Field(default=False, description="是否为回滚目标")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="变更时间"
    )

    model_config = {"populate_by_name": True}

    def to_response(self) -> ConfigVersionResponse:
        """转换为响应模型。"""
        return ConfigVersionResponse(
            id=self.id,
            config_id=self.config_id,
            config_key=self.config_key,
            version=self.version,
            value=self.value,
            changed_by=self.changed_by,
            change_reason=self.change_reason,
            change_type=self.change_type,
            diff_summary=self.diff_summary,
            is_rollback_target=self.is_rollback_target,
            created_at=self.created_at,
        )


