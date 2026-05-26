"""OAuth 依赖注入模块。

提供 FastAPI 依赖注入函数。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..cache.state_store import OAuthStateStore
from ..crypto.token_encryption import TokenEncryptor
from ..providers import ProviderRegistry
from ..repository.activity_repo import OAuthActivityLogRepository
from ..repository.connection_repo import OAuthConnectionRepository
from ..repository.credential_repo import OAuthAppCredentialRepository
from ..repository.session_repo import OAuthSessionRepository
from ..services.account_service import OAuthAccountService
from ..services.admin_service import OAuthAdminService
from ..services.flow_service import OAuthFlowService
from ..services.session_service import OAuthSessionService
from ..services.token_service import OAuthTokenService
from .config import settings

_provider_registry = ProviderRegistry()
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth/token", auto_error=False)


async def get_mongo_client() -> AsyncIOMotorClient:
    """获取 MongoDB 客户端。"""
    client = AsyncIOMotorClient(settings.mongo_url)
    try:
        yield client
    finally:
        client.close()


async def get_mongo_db(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """获取 MongoDB 数据库。"""
    return client[settings.mongo_db]


async def get_connection_collection(
    db=Depends(get_mongo_db),
) -> AsyncIOMotorCollection:
    """获取 OAuth 连接集合。"""
    return db.oauth_connections


async def get_credential_collection(
    db=Depends(get_mongo_db),
) -> AsyncIOMotorCollection:
    """获取 OAuth 凭证集合。"""
    return db.oauth_credentials


async def get_session_collection(
    db=Depends(get_mongo_db),
) -> AsyncIOMotorCollection:
    """获取 OAuth 会话集合。"""
    return db.oauth_sessions


async def get_activity_collection(
    db=Depends(get_mongo_db),
) -> AsyncIOMotorCollection:
    """获取 OAuth 活动日志集合。"""
    return db.oauth_activity_logs


async def get_connection_repo(
    collection=Depends(get_connection_collection),
) -> OAuthConnectionRepository:
    """获取 OAuth 连接 Repository。"""
    return OAuthConnectionRepository(collection)


async def get_credential_repo(
    collection=Depends(get_credential_collection),
) -> OAuthAppCredentialRepository:
    """获取 OAuth 凭证 Repository。"""
    return OAuthAppCredentialRepository(collection)


async def get_session_repo(
    collection=Depends(get_session_collection),
) -> OAuthSessionRepository:
    """获取 OAuth 会话 Repository。"""
    return OAuthSessionRepository(collection)


async def get_activity_repo(
    collection=Depends(get_activity_collection),
) -> OAuthActivityLogRepository:
    """获取 OAuth 活动日志 Repository。"""
    return OAuthActivityLogRepository(collection)


def get_token_encryptor() -> TokenEncryptor:
    """获取 Token 加密器。"""
    if not settings.encryption_key:
        from ..crypto.token_encryption import generate_encryption_key

        return TokenEncryptor(generate_encryption_key())
    return TokenEncryptor(settings.encryption_key)


def get_provider_registry() -> ProviderRegistry:
    """获取提供商注册表。"""
    return _provider_registry


async def get_redis_client():
    """获取 Redis 客户端。"""
    from taolib.testing._base.redis_pool import get_redis_client

    return await get_redis_client(settings.redis_url)


async def get_state_store(
    redis_client=Depends(get_redis_client),
) -> OAuthStateStore:
    """获取 CSRF State 存储。"""
    return OAuthStateStore(redis_client, ttl_seconds=settings.state_ttl_seconds)


async def get_flow_service(
    credential_repo=Depends(get_credential_repo),
    state_store=Depends(get_state_store),
    encryptor=Depends(get_token_encryptor),
) -> OAuthFlowService:
    """获取 OAuth 流程服务。"""
    return OAuthFlowService(
        credential_repo=credential_repo,
        state_store=state_store,
        provider_registry=get_provider_registry(),
        token_encryptor=encryptor,
    )


async def get_account_service(
    connection_repo=Depends(get_connection_repo),
    activity_repo=Depends(get_activity_repo),
    encryptor=Depends(get_token_encryptor),
) -> OAuthAccountService:
    """获取 OAuth 账户服务。"""
    return OAuthAccountService(
        connection_repo=connection_repo,
        activity_repo=activity_repo,
        token_encryptor=encryptor,
    )


async def get_token_service(
    connection_repo=Depends(get_connection_repo),
    credential_repo=Depends(get_credential_repo),
    activity_repo=Depends(get_activity_repo),
    encryptor=Depends(get_token_encryptor),
) -> OAuthTokenService:
    """获取 OAuth Token 服务。"""
    return OAuthTokenService(
        token_encryptor=encryptor,
        connection_repo=connection_repo,
        credential_repo=credential_repo,
        activity_repo=activity_repo,
        provider_registry=get_provider_registry(),
    )


async def get_session_service(
    session_repo=Depends(get_session_repo),
    redis_client=Depends(get_redis_client),
) -> OAuthSessionService:
    """获取 OAuth 会话服务。"""
    return OAuthSessionService(
        session_repo=session_repo,
        redis_client=redis_client,
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


async def get_admin_service(
    credential_repo=Depends(get_credential_repo),
    activity_repo=Depends(get_activity_repo),
    connection_repo=Depends(get_connection_repo),
    encryptor=Depends(get_token_encryptor),
) -> OAuthAdminService:
    """获取 OAuth 管理服务。"""
    return OAuthAdminService(
        credential_repo=credential_repo,
        activity_repo=activity_repo,
        connection_repo=connection_repo,
        token_encryptor=encryptor,
    )


async def get_current_user_id(
    token: str = Depends(_oauth2_scheme),
) -> str:
    """从 JWT Token 中提取当前用户 ID。"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


