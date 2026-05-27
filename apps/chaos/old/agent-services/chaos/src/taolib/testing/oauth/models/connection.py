"""OAuth 连接数据模型模块。

定义 OAuth 连接（用户与第三方提供商的关联）相关的 Pydantic 模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import OAuthConnectionStatus, OAuthProvider


class OAuthConnectionBase(BaseModel):
    """OAuth 连接基础模型。"""

    provider: OAuthProvider = Field(..., description="OAuth 提供商")
    provider_user_id: str = Field(..., description="提供商侧用户 ID")
    email: str | None = Field(default=None, description="提供商邮箱")
    display_name: str = Field(default="", description="提供商显示名称")
    avatar_url: str = Field(default="", description="提供商头像 URL")


class OAuthConnectionCreate(OAuthConnectionBase):
    """创建 OAuth 连接请求模型。"""

    user_id: str = Field(..., description="本地用户 ID")
    access_token_encrypted: str = Field(..., description="加密后的 Access Token")
    refresh_token_encrypted: str | None = Field(
        default=None, description="加密后的 Refresh Token"
    )
    token_expires_at: datetime | None = Field(
        default=None, description="Token 过期时间"
    )
    scopes: list[str] = Field(default_factory=list, description="授权范围")


class OAuthConnectionUpdate(BaseModel):
    """更新 OAuth 连接请求模型。"""

    access_token_encrypted: str | None = Field(
        default=None, description="加密后的 Access Token"
    )
    refresh_token_encrypted: str | None = Field(
        default=None, description="加密后的 Refresh Token"
    )
    token_expires_at: datetime | None = Field(
        default=None, description="Token 过期时间"
    )
    status: OAuthConnectionStatus | None = Field(default=None, description="连接状态")
    display_name: str | None = Field(default=None, description="显示名称")
    avatar_url: str | None = Field(default=None, description="头像 URL")
    email: str | None = Field(default=None, description="邮箱")
    last_used_at: datetime | None = Field(default=None, description="最后使用时间")


class OAuthConnectionResponse(OAuthConnectionBase):
    """OAuth 连接响应模型。

    不包含加密的 Token 信息。
    """

    id: str = Field(..., description="连接 ID")
    user_id: str = Field(..., description="本地用户 ID")
    status: OAuthConnectionStatus = Field(..., description="连接状态")
    scopes: list[str] = Field(default_factory=list, description="授权范围")
    token_expires_at: datetime | None = Field(
        default=None, description="Token 过期时间"
    )
    last_used_at: datetime | None = Field(default=None, description="最后使用时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config: dict[str, Any] = {"from_attributes": True}


class OAuthConnectionDocument(OAuthConnectionBase):
    """MongoDB OAuth 连接文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    user_id: str = Field(..., description="本地用户 ID")
    access_token_encrypted: str = Field(..., description="加密后的 Access Token")
    refresh_token_encrypted: str | None = Field(
        default=None, description="加密后的 Refresh Token"
    )
    token_expires_at: datetime | None = Field(
        default=None, description="Token 过期时间"
    )
    scopes: list[str] = Field(default_factory=list, description="授权范围")
    status: OAuthConnectionStatus = Field(
        default=OAuthConnectionStatus.ACTIVE, description="连接状态"
    )
    last_used_at: datetime | None = Field(default=None, description="最后使用时间")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="最后更新时间"
    )

    model_config: dict[str, Any] = {"populate_by_name": True}

    def to_response(self) -> OAuthConnectionResponse:
        """转换为响应模型（不包含加密 Token）。"""
        return OAuthConnectionResponse(
            id=self.id,
            user_id=self.user_id,
            provider=self.provider,
            provider_user_id=self.provider_user_id,
            email=self.email,
            display_name=self.display_name,
            avatar_url=self.avatar_url,
            status=self.status,
            scopes=self.scopes,
            token_expires_at=self.token_expires_at,
            last_used_at=self.last_used_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
