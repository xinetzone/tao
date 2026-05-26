"""FastAPI 应用工厂模块。

创建和配置 FastAPI 应用实例。
"""

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from ..cache.redis_client import close_redis_client, get_redis_client
from ..events.publisher import EventPublisher
from ..repository.audit_repo import AuditLogRepository
from ..repository.config_repo import ConfigRepository
from ..repository.user_repo import UserRepository
from ..server.api.router import api_router
from ..server.config import settings
from ..server.websocket.manager import WebSocketConnectionManager
from ..server.websocket.message_buffer import RedisMessageBuffer
from ..server.websocket.presence import RedisPresenceTracker
from ..server.websocket.pubsub_bridge import PubSubBridge


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    # 启动时执行
    print("Starting config center server...")

    # 初始化 MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_client[settings.mongo_db]

    # 初始化 Redis
    redis_client = await get_redis_client(settings.redis_url)
    app.state.redis_client = redis_client

    # 创建索引
    config_repo = ConfigRepository(app.state.mongo_db.configs)
    await config_repo.create_indexes()

    user_repo = UserRepository(app.state.mongo_db.users)
    await user_repo.create_indexes()

    audit_repo = AuditLogRepository(app.state.mongo_db.audit_logs)
    await audit_repo.create_indexes()

    # 创建系统角色（如果不存在）
    await _init_system_roles(app.state.mongo_db.roles)

    # 初始化推送服务
    instance_id = settings.push_instance_id or uuid.uuid4().hex[:8]

    message_buffer = RedisMessageBuffer(
        redis_client,
        max_user_messages=settings.push_buffer_max_size,
        user_buffer_ttl=settings.push_buffer_ttl,
    )
    app.state.message_buffer = message_buffer

    presence_tracker = RedisPresenceTracker(redis_client)
    app.state.presence_tracker = presence_tracker

    push_manager = WebSocketConnectionManager(
        presence_tracker=presence_tracker,
        message_buffer=message_buffer,
        instance_id=instance_id,
        heartbeat_interval=settings.push_heartbeat_interval,
        heartbeat_timeout=settings.push_heartbeat_timeout,
        ack_timeout=settings.push_ack_timeout,
        max_retries=settings.push_max_retries,
    )
    await push_manager.start()
    app.state.push_manager = push_manager

    pubsub_bridge = PubSubBridge(
        redis_client,
        push_manager,
        instance_id=instance_id,
    )
    await pubsub_bridge.start()
    app.state.pubsub_bridge = pubsub_bridge

    event_publisher = EventPublisher(
        redis_client,
        message_buffer=message_buffer,
        instance_id=instance_id,
    )
    app.state.event_publisher = event_publisher

    print("Config center server started.")

    yield

    # 关闭时执行
    print("Shutting down config center server...")
    await pubsub_bridge.stop()
    await push_manager.stop()
    mongo_client.close()
    await close_redis_client()
    print("Config center server shut down.")


async def _init_system_roles(role_collection) -> None:
    """初始化系统角色。"""
    from ..server.auth.rbac import RBACService

    for role_name, role_data in RBACService.SYSTEM_ROLES.items():
        existing = await role_collection.find_one({"name": role_name})
        if existing is None:
            await role_collection.insert_one(
                {
                    "name": role_name,
                    "description": role_data["description"],
                    "permissions": role_data["permissions"],
                    "environment_scope": role_data["environment_scope"],
                    "service_scope": role_data["service_scope"],
                    "is_system": True,
                }
            )
            print(f"Created system role: {role_name}")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="Config Center",
        description="中心化配置管理系统",
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


