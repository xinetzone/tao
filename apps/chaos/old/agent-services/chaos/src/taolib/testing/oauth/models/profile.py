"""OAuth 用户资料与引导数据模型模块。

定义标准化的用户信息和首次登录引导流程相关的 Pydantic 模型。
"""

from typing import Any

from pydantic import BaseModel, Field

from .enums import OAuthProvider


class OAuthUserInfo(BaseModel):
    """标准化的 OAuth 用户信息。

    从不同提供商的响应中提取的统一格式用户信息。
    """

    provider: OAuthProvider = Field(..., description="OAuth 提供商")
    provider_user_id: str = Field(..., description="提供商侧用户 ID")
    email: str | None = Field(default=None, description="邮箱地址")
    display_name: str = Field(default="", description="显示名称")
    avatar_url: str = Field(default="", description="头像 URL")
    raw_data: dict[str, Any] = Field(
        default_factory=dict, description="提供商原始响应数据"
    )


class OnboardingData(BaseModel):
    """首次登录引导数据模型。

    新用户通过 OAuth 首次登录时需要填写的资料。
    """

    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    display_name: str | None = Field(
        default=None, description="显示名称（覆盖提供商名称）", max_length=255
    )
