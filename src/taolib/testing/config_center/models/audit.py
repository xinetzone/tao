"""审计日志数据模型模块。

定义审计日志相关的 Pydantic 模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import AuditAction, AuditStatus


class AuditLogBase(BaseModel):
    """审计日志基础模型。"""

    action: AuditAction = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型", max_length=100)
    resource_id: str = Field(..., description="资源 ID")
    resource_key: str = Field(default="", description="资源标识", max_length=500)
    actor_id: str = Field(..., description="操作人用户 ID")
    actor_name: str = Field(..., description="操作人名称", max_length=255)
    actor_ip: str = Field(default="", description="操作人 IP", max_length=45)
    old_value: Any | None = Field(default=None, description="变更前值")
    new_value: Any | None = Field(default=None, description="变更后值")
    metadata: dict[str, Any] = Field(default_factory=dict, description="附加元数据")


class AuditLogCreate(AuditLogBase):
    """创建审计日志请求模型。"""

    status: AuditStatus = Field(default=AuditStatus.SUCCESS, description="操作状态")


class AuditLogResponse(AuditLogBase):
    """审计日志响应模型。"""

    id: str = Field(..., description="日志 ID")
    status: AuditStatus = Field(..., description="操作状态")
    timestamp: datetime = Field(..., description="操作时间")

    model_config = {"from_attributes": True}


class AuditLogDocument(BaseModel):
    """MongoDB 审计日志文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    action: AuditAction = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: str = Field(..., description="资源 ID")
    resource_key: str = Field(default="", description="资源标识")
    actor_id: str = Field(..., description="操作人用户 ID")
    actor_name: str = Field(..., description="操作人名称")
    actor_ip: str = Field(default="", description="操作人 IP")
    old_value: Any | None = Field(default=None, description="变更前值")
    new_value: Any | None = Field(default=None, description="变更后值")
    metadata: dict[str, Any] = Field(default_factory=dict, description="附加元数据")
    status: AuditStatus = Field(default=AuditStatus.SUCCESS, description="操作状态")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="操作时间"
    )

    model_config = {"populate_by_name": True}

    def to_response(self) -> AuditLogResponse:
        """转换为响应模型。"""
        return AuditLogResponse(
            id=self.id,
            action=self.action,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            resource_key=self.resource_key,
            actor_id=self.actor_id,
            actor_name=self.actor_name,
            actor_ip=self.actor_ip,
            old_value=self.old_value,
            new_value=self.new_value,
            metadata=self.metadata,
            status=self.status,
            timestamp=self.timestamp,
        )


