"""依赖注入模块。

提供 FastAPI 依赖注入函数。
"""

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..cache.config_cache import ConfigCacheProtocol, RedisConfigCache
from ..cache.redis_client import get_redis_client
from ..events.publisher import EventPublisher
from ..models.enums import Environment
from ..models.user import UserDocument
from ..repository.audit_repo import AuditLogRepository
from ..repository.config_repo import ConfigRepository
from ..repository.role_repo import RoleRepository
from ..repository.user_repo import UserRepository
from ..repository.version_repo import VersionRepository
from ..server.auth.jwt_handler import verify_access_token
from ..server.auth.oauth2 import oauth2_scheme
from ..server.auth.rbac import RBACService
from ..server.config import settings

# RBAC 服务实例
rbac_service = RBACService()


async def get_mongo_client() -> AsyncIOMotorClient:
    """获取 MongoDB 客户端。"""
    client = AsyncIOMotorClient(settings.mongo_url)
    try:
        yield client
    finally:
        client.close()


async def get_mongo_db(client: AsyncIOMotorClient = Depends(get_mongo_client)):
    """获取 MongoDB 数据库。"""
    return client[settings.mongo_db]


async def get_user_collection(db=Depends(get_mongo_db)) -> AsyncIOMotorCollection:
    """获取用户集合。"""
    return db.users


async def get_config_collection(db=Depends(get_mongo_db)) -> AsyncIOMotorCollection:
    """获取配置集合。"""
    return db.configs


async def get_version_collection(db=Depends(get_mongo_db)) -> AsyncIOMotorCollection:
    """获取版本集合。"""
    return db.config_versions


async def get_audit_collection(db=Depends(get_mongo_db)) -> AsyncIOMotorCollection:
    """获取审计日志集合。"""
    return db.audit_logs


async def get_role_collection(db=Depends(get_mongo_db)) -> AsyncIOMotorCollection:
    """获取角色集合。"""
    return db.roles


async def get_user_repo(
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> UserRepository:
    """获取用户 Repository。"""
    return UserRepository(collection)


async def get_config_repo(
    collection: AsyncIOMotorCollection = Depends(get_config_collection),
) -> ConfigRepository:
    """获取配置 Repository。"""
    return ConfigRepository(collection)


async def get_version_repo(
    collection: AsyncIOMotorCollection = Depends(get_version_collection),
) -> VersionRepository:
    """获取版本 Repository。"""
    return VersionRepository(collection)


async def get_audit_repo(
    collection: AsyncIOMotorCollection = Depends(get_audit_collection),
) -> AuditLogRepository:
    """获取审计日志 Repository。"""
    return AuditLogRepository(collection)


async def get_role_repo(
    collection: AsyncIOMotorCollection = Depends(get_role_collection),
) -> RoleRepository:
    """获取角色 Repository。"""
    return RoleRepository(collection)


async def get_cache() -> ConfigCacheProtocol:
    """获取配置缓存。"""
    redis_client = await get_redis_client(settings.redis_url)
    return RedisConfigCache(redis_client)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserDocument:
    """获取当前用户。

    Args:
        token: JWT Token
        user_repo: 用户 Repository

    Returns:
        用户文档实例

    Raises:
        HTTPException: 如果 Token 无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


def require_permission(resource: str, action: str):
    """权限检查依赖。

    Args:
        resource: 资源类型
        action: 操作类型

    Returns:
        依赖注入函数
    """

    async def _check_permission(
        current_user: UserDocument = Depends(get_current_user),
        user_repo: UserRepository = Depends(get_user_repo),
        role_collection: AsyncIOMotorCollection = Depends(get_role_collection),
    ) -> UserDocument:
        # 从数据库加载用户角色
        user_roles = await user_repo.get_user_roles(current_user.id, role_collection)
        if not rbac_service.has_permission(user_roles, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user

    return _check_permission


def require_environment_access(environment: Environment):
    """环境访问检查依赖。

    Args:
        environment: 环境类型

    Returns:
        依赖注入函数
    """

    async def _check_environment(
        current_user: UserDocument = Depends(get_current_user),
        user_repo: UserRepository = Depends(get_user_repo),
        role_collection: AsyncIOMotorCollection = Depends(get_role_collection),
    ) -> UserDocument:
        # 从数据库加载用户角色
        user_roles = await user_repo.get_user_roles(current_user.id, role_collection)
        # 生产环境需要显式授权
        if environment == Environment.PRODUCTION:
            if not rbac_service.can_access_environment(user_roles, environment):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问生产环境配置",
                )
        return current_user

    return _check_environment


async def get_event_publisher(request: Request) -> EventPublisher | None:
    """获取事件发布器（从 app.state）。"""
    return getattr(request.app.state, "event_publisher", None)


