"""FastAPI 应用工厂模块。

创建和配置 OAuth 服务的 FastAPI 应用实例。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from ..crypto.token_encryption import TokenEncryptor
from ..repository.activity_repo import OAuthActivityLogRepository
from ..repository.connection_repo import OAuthConnectionRepository
from ..repository.credential_repo import OAuthAppCredentialRepository
from ..repository.session_repo import OAuthSessionRepository
from .api.router import api_router
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    print("Starting OAuth server...")

    # 初始化 MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_client[settings.mongo_db]

    # 初始化 Redis
    from taolib._base.redis_pool import get_redis_client

    redis_client = await get_redis_client(settings.redis_url)
    app.state.redis_client = redis_client

    # 创建索引
    db = app.state.mongo_db

    conn_repo = OAuthConnectionRepository(db.oauth_connections)
    await conn_repo.create_indexes()

    cred_repo = OAuthAppCredentialRepository(db.oauth_credentials)
    await cred_repo.create_indexes()

    session_repo = OAuthSessionRepository(db.oauth_sessions)
    await session_repo.create_indexes()

    activity_repo = OAuthActivityLogRepository(db.oauth_activity_logs)
    await activity_repo.create_indexes()

    # 引导凭证（从环境变量自动创建）
    await _bootstrap_credentials(db, cred_repo)

    print("OAuth server started.")

    yield

    # 关闭
    print("Shutting down OAuth server...")
    mongo_client.close()
    from taolib._base.redis_pool import close_redis_client

    await close_redis_client()
    print("OAuth server shut down.")


async def _bootstrap_credentials(db, cred_repo: OAuthAppCredentialRepository) -> None:
    """从环境变量引导 OAuth 凭证。"""
    if not settings.encryption_key:
        return

    encryptor = TokenEncryptor(settings.encryption_key)
    base_uri = settings.default_redirect_uri

    providers = [
        (
            "google",
            settings.google_client_id,
            settings.google_client_secret,
            ["openid", "email", "profile"],
        ),
        (
            "github",
            settings.github_client_id,
            settings.github_client_secret,
            ["user:email", "read:user"],
        ),
    ]

    for provider_name, client_id, client_secret, scopes in providers:
        if not client_id or not client_secret:
            continue

        existing = await cred_repo.find_by_provider(provider_name)
        if existing:
            continue

        callback_uri = base_uri.rsplit("/callback", 1)[0] + f"/callback/{provider_name}"
        await cred_repo.create(
            {
                "provider": provider_name,
                "client_id": client_id,
                "client_secret_encrypted": encryptor.encrypt(client_secret),
                "display_name": f"{provider_name.title()} OAuth",
                "enabled": True,
                "allowed_scopes": scopes,
                "redirect_uri": callback_uri,
                "created_by": "system",
            }
        )
        print(f"Bootstrapped OAuth credential: {provider_name}")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="OAuth Service",
        description="OAuth2 第三方登录服务",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(api_router)

    return app
