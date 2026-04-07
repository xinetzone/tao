"""JWT 处理模块。

提供 JWT Token 的生成和验证功能。
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from ..config import settings


def create_access_token(
    user_id: str,
    roles: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    """生成 Access Token。

    Args:
        user_id: 用户 ID
        roles: 用户角色列表
        expires_delta: 过期时间增量，如果为 None 则使用默认配置

    Returns:
        JWT Token 字符串
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(UTC) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": user_id,
        "roles": roles,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """生成 Refresh Token。

    Args:
        user_id: 用户 ID

    Returns:
        JWT Token 字符串
    """
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    expire = datetime.now(UTC) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """解码并验证 JWT Token。

    Args:
        token: JWT Token 字符串

    Returns:
        Token 中的 payload 字典

    Raises:
        JWTError: 如果 Token 无效或已过期
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def verify_access_token(token: str) -> dict[str, Any]:
    """验证 Access Token 并返回 payload。

    Args:
        token: JWT Token 字符串

    Returns:
        Token 中的 payload 字典

    Raises:
        JWTError: 如果 Token 无效、已过期或类型不正确
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload
