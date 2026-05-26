"""OAuth 活动日志数据模型模块。

定义 OAuth 认证活动日志相关的 Pydantic 模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import OAuthActivityAction, OAuthActivityStatus, OAuthProvider


class OAuthActivityLogResponse(BaseModel):
    """OAuth 活动日志响应模型。"""

    id: str = Field(..., description="日志 ID")
    action: OAuthActivityAction = Field(..., description="操作类型")
    status: OAuthActivityStatus = Field(..., description="操作状态")
    provider: OAuthProvider | None = Field(default=None, description="OAuth 提供商")
    user_id: str | None = Field(default=None, description="用户 ID")
    connection_id: str | None = Field(default=None, description="连接 ID")
    ip_address: str = Field(default="", description="客户端 IP 地址")
    user_agent: str = Field(default="", description="客户端 User-Agent")
    metadata: dict[str, Any] = Field(default_factory=dict, description="额外上下文")
    timestamp: datetime = Field(..., description="时间戳")

    model_config: dict[str, Any] = {"from_attributes": True}


class OAuthActivityLogDocument(BaseModel):
    """MongoDB OAuth 活动日志文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    action: OAuthActivityAction = Field(..., description="操作类型")
    status: OAuthActivityStatus = Field(..., description="操作状态")
    provider: OAuthProvider | None = Field(default=None, description="OAuth 提供商")
    user_id: str | None = Field(default=None, description="用户 ID")
    connection_id: str | None = Field(default=None, description="连接 ID")
    ip_address: str = Field(default="", description="客户端 IP 地址")
    user_agent: str = Field(default="", description="客户端 User-Agent")
    metadata: dict[str, Any] = Field(default_factory=dict, description="额外上下文")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="时间戳"
    )

    model_config: dict[str, Any] = {"populate_by_name": True}

    def to_response(self) -> OAuthActivityLogResponse:
        """转换为响应模型。"""
        return OAuthActivityLogResponse(
            id=self.id,
            action=self.action,
            status=self.status,
            provider=self.provider,
            user_id=self.user_id,
            connection_id=self.connection_id,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            metadata=self.metadata,
            timestamp=self.timestamp,
        )


