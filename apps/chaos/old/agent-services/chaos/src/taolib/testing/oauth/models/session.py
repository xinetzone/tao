"""OAuth 会话数据模型模块。

定义跨服务 OAuth 会话相关的 Pydantic 模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import OAuthProvider


class OAuthSessionResponse(BaseModel):
    """OAuth 会话响应模型。"""

    id: str = Field(..., description="会话 ID")
    user_id: str = Field(..., description="用户 ID")
    provider: OAuthProvider = Field(..., description="认证提供商")
    ip_address: str = Field(default="", description="客户端 IP 地址")
    user_agent: str = Field(default="", description="客户端 User-Agent")
    is_active: bool = Field(default=True, description="会话是否活跃")
    created_at: datetime = Field(..., description="创建时间")
    expires_at: datetime = Field(..., description="过期时间")
    last_activity_at: datetime = Field(..., description="最后活跃时间")

    model_config: dict[str, Any] = {"from_attributes": True}


class OAuthSessionDocument(BaseModel):
    """MongoDB OAuth 会话文档模型。"""

    id: str = Field(default="", alias="_id", description="会话 ID (UUID)")
    user_id: str = Field(..., description="用户 ID")
    provider: OAuthProvider = Field(..., description="认证提供商")
    connection_id: str = Field(..., description="关联的 OAuth 连接 ID")
    jwt_access_token: str = Field(..., description="JWT Access Token")
    jwt_refresh_token: str = Field(..., description="JWT Refresh Token")
    ip_address: str = Field(default="", description="客户端 IP 地址")
    user_agent: str = Field(default="", description="客户端 User-Agent")
    is_active: bool = Field(default=True, description="会话是否活跃")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="创建时间"
    )
    expires_at: datetime = Field(..., description="过期时间")
    last_activity_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="最后活跃时间"
    )

    model_config: dict[str, Any] = {"populate_by_name": True}

    def to_response(self) -> OAuthSessionResponse:
        """转换为响应模型（不包含 JWT Token）。"""
        return OAuthSessionResponse(
            id=self.id,
            user_id=self.user_id,
            provider=self.provider,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            is_active=self.is_active,
            created_at=self.created_at,
            expires_at=self.expires_at,
            last_activity_at=self.last_activity_at,
        )
