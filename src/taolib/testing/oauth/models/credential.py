"""OAuth 应用凭证数据模型模块。

定义 OAuth 应用凭证（client_id/client_secret）相关的 Pydantic 模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import OAuthProvider


class OAuthAppCredentialBase(BaseModel):
    """OAuth 应用凭证基础模型。"""

    provider: OAuthProvider = Field(..., description="OAuth 提供商")
    client_id: str = Field(..., description="Client ID", min_length=1)
    display_name: str = Field(default="", description="人类可读标签", max_length=255)
    enabled: bool = Field(default=True, description="是否启用")
    allowed_scopes: list[str] = Field(
        default_factory=list, description="允许的授权范围"
    )
    redirect_uri: str = Field(..., description="回调 URI")


class OAuthAppCredentialCreate(OAuthAppCredentialBase):
    """创建 OAuth 应用凭证请求模型。"""

    client_secret: str = Field(..., description="Client Secret", min_length=1)


class OAuthAppCredentialUpdate(BaseModel):
    """更新 OAuth 应用凭证请求模型。"""

    client_id: str | None = Field(default=None, description="Client ID")
    client_secret: str | None = Field(default=None, description="Client Secret")
    display_name: str | None = Field(default=None, description="人类可读标签")
    enabled: bool | None = Field(default=None, description="是否启用")
    allowed_scopes: list[str] | None = Field(default=None, description="允许的授权范围")
    redirect_uri: str | None = Field(default=None, description="回调 URI")


class OAuthAppCredentialResponse(BaseModel):
    """OAuth 应用凭证响应模型。

    不包含 client_secret。
    """

    id: str = Field(..., description="凭证 ID")
    provider: OAuthProvider = Field(..., description="OAuth 提供商")
    client_id: str = Field(..., description="Client ID")
    display_name: str = Field(default="", description="人类可读标签")
    enabled: bool = Field(default=True, description="是否启用")
    allowed_scopes: list[str] = Field(
        default_factory=list, description="允许的授权范围"
    )
    redirect_uri: str = Field(..., description="回调 URI")
    created_by: str = Field(default="", description="创建者用户 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config: dict[str, Any] = {"from_attributes": True}


class OAuthAppCredentialDocument(BaseModel):
    """MongoDB OAuth 应用凭证文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    provider: OAuthProvider = Field(..., description="OAuth 提供商")
    client_id: str = Field(..., description="Client ID")
    client_secret_encrypted: str = Field(..., description="加密后的 Client Secret")
    display_name: str = Field(default="", description="人类可读标签")
    enabled: bool = Field(default=True, description="是否启用")
    allowed_scopes: list[str] = Field(
        default_factory=list, description="允许的授权范围"
    )
    redirect_uri: str = Field(..., description="回调 URI")
    created_by: str = Field(default="", description="创建者用户 ID")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="最后更新时间"
    )

    model_config: dict[str, Any] = {"populate_by_name": True}

    def to_response(self) -> OAuthAppCredentialResponse:
        """转换为响应模型（不包含 client_secret）。"""
        return OAuthAppCredentialResponse(
            id=self.id,
            provider=self.provider,
            client_id=self.client_id,
            display_name=self.display_name,
            enabled=self.enabled,
            allowed_scopes=self.allowed_scopes,
            redirect_uri=self.redirect_uri,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


