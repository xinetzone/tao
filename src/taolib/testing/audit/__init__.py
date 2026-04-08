"""审计日志模块。

提供审计日志的记录、存储和查询功能。

Example:
    基本使用::

        from taolib.testing.audit import AuditLogger, InMemoryAuditStorage

        # 创建存储后端
        storage = InMemoryAuditStorage()

        # 创建审计日志记录器
        audit_logger = AuditLogger(storage)

        # 记录日志
        await audit_logger.log_create(
            resource_type="user",
            resource_id="user-123",
            user_id="admin",
            details={"name": "John Doe"},
        )

    FastAPI 中间件::

        from fastapi import FastAPI
        from taolib.testing.audit import AuditMiddleware, AuditLogger, InMemoryAuditStorage

        app = FastAPI()
        storage = InMemoryAuditStorage()
        audit_logger = AuditLogger(storage)
        app.add_middleware(AuditMiddleware, audit_logger=audit_logger)

    MongoDB 存储::

        from motor.motor_asyncio import AsyncIOMotorClient
        from taolib.testing.audit import AuditLogger, MongoDBAuditStorage

        client = AsyncIOMotorClient("mongodb://localhost:27017")
        storage = MongoDBAuditStorage(client, database_name="myapp")
        await storage.create_indexes()
        audit_logger = AuditLogger(storage)
"""

from .errors import AuditConfigError, AuditError, AuditStorageError
from .logger import (
    AuditLogger,
    AuditStorageProtocol,
    FileAuditStorage,
    InMemoryAuditStorage,
    MongoDBAuditStorage,
)
from .middleware import AuditMiddleware, extract_client_ip, extract_user_id
from .models import (
    AuditAction,
    AuditLog,
    AuditLogCreate,
    AuditLogFilter,
    AuditLogListResponse,
    AuditLogResponse,
    AuditStatus,
    RequestAuditInfo,
)

__all__ = [
    "AuditAction",
    "AuditConfigError",
    "AuditError",
    "AuditLog",
    "AuditLogCreate",
    "AuditLogFilter",
    "AuditLogListResponse",
    "AuditLogResponse",
    "AuditLogger",
    "AuditMiddleware",
    "AuditStatus",
    "AuditStorageError",
    "AuditStorageProtocol",
    "FileAuditStorage",
    "InMemoryAuditStorage",
    "MongoDBAuditStorage",
    "RequestAuditInfo",
    "extract_client_ip",
    "extract_user_id",
]


