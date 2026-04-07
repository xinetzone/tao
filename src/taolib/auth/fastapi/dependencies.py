"""FastAPI 依赖注入工厂。

提供认证和授权相关的 FastAPI 依赖注入函数。
"""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from ..api_key import APIKeyLookupProtocol
from ..blacklist import NullTokenBlacklist, TokenBlacklistProtocol
from ..errors import (
    TokenExpiredError,
    TokenInvalidError,
)
from ..models import AuthenticatedUser
from ..rbac import RBACPolicy
from ..tokens import JWTService
from .schemes import create_api_key_header, create_oauth2_scheme

# 认证依赖的类型别名
AuthDependency = Callable[..., Coroutine[Any, Any, AuthenticatedUser]]


def create_auth_dependency(
    jwt_service: JWTService,
    blacklist: TokenBlacklistProtocol | None = None,
    api_key_lookup: APIKeyLookupProtocol | None = None,
    oauth2_scheme: OAuth2PasswordBearer | None = None,
    api_key_header: APIKeyHeader | None = None,
) -> AuthDependency:
    """创建认证依赖注入函数。

    返回一个可直接用于 ``Depends()`` 的异步函数，支持 JWT Bearer 和
    API Key 双通道认证。

    Args:
        jwt_service: JWT 令牌服务
        blacklist: 令牌黑名单实现（默认 NullTokenBlacklist）
        api_key_lookup: API 密钥查找实现（None 表示不启用 API Key 认证）
        oauth2_scheme: OAuth2 安全方案（None 使用默认配置）
        api_key_header: API Key Header 安全方案（None 使用默认配置）

    Returns:
        FastAPI 依赖注入函数
    """
    if blacklist is None:
        blacklist = NullTokenBlacklist()
    if oauth2_scheme is None:
        oauth2_scheme = create_oauth2_scheme()
    if api_key_lookup is not None and api_key_header is None:
        api_key_header = create_api_key_header()

    _oauth2 = oauth2_scheme
    _api_key_hdr = api_key_header
    _blacklist = blacklist
    _api_key_lookup = api_key_lookup

    async def _authenticate(
        request: Request,
        bearer_token: str | None = Depends(_oauth2),
        api_key: str | None = Depends(_api_key_hdr) if _api_key_hdr else None,
    ) -> AuthenticatedUser:
        # 1. 尝试 JWT Bearer 认证
        if bearer_token:
            return await _authenticate_jwt(bearer_token)

        # 2. 尝试 API Key 认证
        if _api_key_lookup is not None:
            resolved_key = api_key or _extract_api_key_from_auth_header(request)
            if resolved_key:
                return await _authenticate_api_key(resolved_key)

        # 3. 都失败
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def _authenticate_jwt(token: str) -> AuthenticatedUser:
        try:
            payload = jwt_service.verify_access_token(token)
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期，请刷新",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except TokenInvalidError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查黑名单
        if payload.jti and await _blacklist.is_blacklisted(payload.jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已被吊销",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return AuthenticatedUser(
            user_id=payload.sub,
            roles=payload.roles,
            auth_method="jwt",
            metadata={"jti": payload.jti},
        )

    async def _authenticate_api_key(key: str) -> AuthenticatedUser:
        assert _api_key_lookup is not None
        user = await _api_key_lookup.lookup(key)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 API 密钥",
            )
        return user

    # 如果没有 API Key 依赖，简化函数签名
    if _api_key_hdr is None:

        async def _auth_jwt_only(
            request: Request,
            bearer_token: str | None = Depends(_oauth2),
        ) -> AuthenticatedUser:
            if bearer_token:
                return await _authenticate_jwt(bearer_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return _auth_jwt_only

    return _authenticate


def _extract_api_key_from_auth_header(request: Request) -> str | None:
    """从 Authorization 头部提取 API Key。

    支持格式: ``Authorization: ApiKey <key>``

    Args:
        request: FastAPI 请求对象

    Returns:
        API Key 字符串，未找到返回 None
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("apikey "):
        return auth_header[7:].strip()
    return None


def require_roles(
    *roles: str,
    auth_dependency: AuthDependency | None = None,
) -> Callable[..., Coroutine[Any, Any, AuthenticatedUser]]:
    """角色检查依赖工厂。

    要求用户至少拥有指定角色之一。

    Args:
        roles: 允许的角色名称
        auth_dependency: 认证依赖（None 时需要在路由中单独注入）

    Returns:
        FastAPI 依赖注入函数
    """
    required = set(roles)

    if auth_dependency is not None:

        async def _check_roles_with_auth(
            user: AuthenticatedUser = Depends(auth_dependency),
        ) -> AuthenticatedUser:
            if not required.intersection(user.roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足，需要角色: " + ", ".join(sorted(required)),
                )
            return user

        return _check_roles_with_auth

    async def _check_roles(user: AuthenticatedUser) -> AuthenticatedUser:
        if not required.intersection(user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，需要角色: " + ", ".join(sorted(required)),
            )
        return user

    return _check_roles


def require_permissions(
    resource: str,
    action: str,
    rbac_policy: RBACPolicy,
    auth_dependency: AuthDependency | None = None,
) -> Callable[..., Coroutine[Any, Any, AuthenticatedUser]]:
    """权限检查依赖工厂。

    通过 RBAC 策略检查用户是否有指定资源的操作权限。

    Args:
        resource: 资源类型
        action: 操作类型
        rbac_policy: RBAC 策略引擎
        auth_dependency: 认证依赖

    Returns:
        FastAPI 依赖注入函数
    """
    if auth_dependency is not None:

        async def _check_perm_with_auth(
            user: AuthenticatedUser = Depends(auth_dependency),
        ) -> AuthenticatedUser:
            if not rbac_policy.has_permission(user.roles, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要 {resource}:{action} 权限",
                )
            return user

        return _check_perm_with_auth

    async def _check_perm(user: AuthenticatedUser) -> AuthenticatedUser:
        if not rbac_policy.has_permission(user.roles, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要 {resource}:{action} 权限",
            )
        return user

    return _check_perm


def require_scope(
    scope_type: str,
    scope_value: str,
    rbac_policy: RBACPolicy,
    auth_dependency: AuthDependency | None = None,
) -> Callable[..., Coroutine[Any, Any, AuthenticatedUser]]:
    """作用域检查依赖工厂。

    通过 RBAC 策略检查用户角色是否在指定作用域内。

    Args:
        scope_type: 作用域类型
        scope_value: 作用域值
        rbac_policy: RBAC 策略引擎
        auth_dependency: 认证依赖

    Returns:
        FastAPI 依赖注入函数
    """
    if auth_dependency is not None:

        async def _check_scope_with_auth(
            user: AuthenticatedUser = Depends(auth_dependency),
        ) -> AuthenticatedUser:
            if not rbac_policy.has_scope(user.roles, scope_type, scope_value):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权访问 {scope_type}:{scope_value}",
                )
            return user

        return _check_scope_with_auth

    async def _check_scope(user: AuthenticatedUser) -> AuthenticatedUser:
        if not rbac_policy.has_scope(user.roles, scope_type, scope_value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权访问 {scope_type}:{scope_value}",
            )
        return user

    return _check_scope
