"""认证领域模型。

定义认证流程中使用的核心数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class TokenPayload:
    """JWT 令牌解码后的 payload。

    Args:
        sub: 用户 ID（JWT 标准 subject 声明）
        roles: 用户角色列表
        exp: 过期时间
        iat: 签发时间
        type: 令牌类型（``"access"`` 或 ``"refresh"``）
        jti: 令牌唯一标识（JWT ID），用于黑名单
    """

    sub: str
    roles: list[str]
    exp: datetime
    iat: datetime
    type: str
    jti: str


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """已认证的用户信息。

    附加到 ``request.state.user``，供下游处理使用。

    Args:
        user_id: 用户 ID
        roles: 用户角色列表
        auth_method: 认证方式（``"jwt"`` 或 ``"api_key"``）
        metadata: 扩展信息（如 API Key 名称、JWT 额外声明等）
    """

    user_id: str
    roles: list[str]
    auth_method: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TokenPair:
    """令牌对，包含 Access Token 和 Refresh Token。

    Args:
        access_token: 访问令牌
        refresh_token: 刷新令牌
        token_type: 令牌类型标识
        expires_in: Access Token 有效秒数
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


