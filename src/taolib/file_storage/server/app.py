"""FastAPI 应用工厂模块。

创建和配置 FastAPI 应用实例。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from taolib.file_storage.cdn.generic import GenericCDNProvider
from taolib.file_storage.processing.pipeline import ProcessingPipeline
from taolib.file_storage.processing.validator import DefaultFileValidator
from taolib.file_storage.repository.bucket_repo import BucketRepository
from taolib.file_storage.repository.chunk_repo import ChunkRepository
from taolib.file_storage.repository.file_repo import FileRepository
from taolib.file_storage.repository.thumbnail_repo import ThumbnailRepository
from taolib.file_storage.repository.upload_repo import UploadSessionRepository
from taolib.file_storage.repository.version_repo import FileVersionRepository
from taolib.file_storage.server.api.router import api_router
from taolib.file_storage.server.config import settings
from taolib.file_storage.storage.local_backend import LocalStorageBackend
from taolib.file_storage.storage.s3_backend import S3StorageBackend

# 可选缩略图生成器
_thumbnail_generator = None
try:
    from taolib.file_storage.processing.thumbnail import PillowThumbnailGenerator

    _thumbnail_generator = PillowThumbnailGenerator()
except ImportError:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    print("Starting file storage server...")

    # 初始化 MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[settings.mongo_db]

    # 初始化 Redis（可选）
    try:
        app.state.redis = Redis.from_url(settings.redis_url)
        await app.state.redis.ping()
    except Exception:
        app.state.redis = None

    # 初始化存储后端
    if settings.storage_backend == "s3":
        app.state.storage_backend = S3StorageBackend(
            endpoint_url=settings.s3_endpoint_url,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            region=settings.s3_region,
        )
    else:
        app.state.storage_backend = LocalStorageBackend(settings.local_storage_path)

    # 初始化 CDN（可选）
    if settings.cdn_enabled and settings.cdn_base_url:
        app.state.cdn_provider = GenericCDNProvider(
            base_url=settings.cdn_base_url,
            signing_key=settings.cdn_signing_key,
        )
    else:
        app.state.cdn_provider = None

    # 初始化处理管道
    validator = DefaultFileValidator()
    app.state.pipeline = ProcessingPipeline(
        validator=validator,
        thumbnail_generator=_thumbnail_generator
        if settings.thumbnail_enabled
        else None,
    )

    # 创建索引
    bucket_repo = BucketRepository(app.state.db.buckets)
    await bucket_repo.create_indexes()

    file_repo = FileRepository(app.state.db.files)
    await file_repo.create_indexes()

    upload_repo = UploadSessionRepository(app.state.db.upload_sessions)
    await upload_repo.create_indexes()

    chunk_repo = ChunkRepository(app.state.db.chunks)
    await chunk_repo.create_indexes()

    version_repo = FileVersionRepository(app.state.db.file_versions)
    await version_repo.create_indexes()

    thumbnail_repo = ThumbnailRepository(app.state.db.thumbnails)
    await thumbnail_repo.create_indexes()

    print("File storage server started.")

    yield

    # 关闭
    print("Shutting down file storage server...")
    mongo_client.close()
    if app.state.redis:
        await app.state.redis.aclose()
    print("File storage server shut down.")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="File Storage API",
        description="文件上传和存储管理系统",
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
