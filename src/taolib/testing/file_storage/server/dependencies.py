"""依赖注入模块。

提供 FastAPI 依赖注入函数。
"""

from typing import Any

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from redis.asyncio import Redis

from taolib.testing.file_storage.cdn.protocols import CDNProviderProtocol
from taolib.testing.file_storage.processing.pipeline import ProcessingPipeline
from taolib.testing.file_storage.repository.bucket_repo import BucketRepository
from taolib.testing.file_storage.repository.chunk_repo import ChunkRepository
from taolib.testing.file_storage.repository.file_repo import FileRepository
from taolib.testing.file_storage.repository.thumbnail_repo import ThumbnailRepository
from taolib.testing.file_storage.repository.upload_repo import UploadSessionRepository
from taolib.testing.file_storage.repository.version_repo import FileVersionRepository
from taolib.testing.file_storage.services.access_service import AccessService
from taolib.testing.file_storage.services.bucket_service import BucketService
from taolib.testing.file_storage.services.file_service import FileService
from taolib.testing.file_storage.services.lifecycle_service import LifecycleService
from taolib.testing.file_storage.services.stats_service import StatsService
from taolib.testing.file_storage.services.upload_service import UploadService
from taolib.testing.file_storage.storage.protocols import StorageBackendProtocol

# 可选的缩略图生成器
_thumbnail_generator = None
try:
    from taolib.testing.file_storage.processing.thumbnail import (
        PillowThumbnailGenerator,
    )

    _thumbnail_generator = PillowThumbnailGenerator()
except ImportError:
    pass


def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    """获取 MongoDB 客户端。"""
    return request.app.state.mongo_client


def get_mongo_db(request: Request) -> Any:
    """获取 MongoDB 数据库。"""
    return request.app.state.db


def get_redis(request: Request) -> Redis | None:
    """获取 Redis 客户端。"""
    return getattr(request.app.state, "redis", None)


def get_storage_backend(request: Request) -> StorageBackendProtocol:
    """获取存储后端。"""
    return request.app.state.storage_backend


def get_cdn_provider(request: Request) -> CDNProviderProtocol | None:
    """获取 CDN 提供商。"""
    return getattr(request.app.state, "cdn_provider", None)


def get_pipeline(request: Request) -> ProcessingPipeline:
    """获取处理管道。"""
    return request.app.state.pipeline


# === 存储桶端点 ===


def get_bucket_collection(request) -> AsyncIOMotorCollection:
    return request.app.state.db.buckets


def get_bucket_repo(
    collection: AsyncIOMotorCollection = get_bucket_collection,
) -> BucketRepository:
    return BucketRepository(collection)


# === 文件端点 ===


def get_file_collection(request) -> AsyncIOMotorCollection:
    return request.app.state.db.files


def get_file_repo(
    collection: AsyncIOMotorCollection = get_file_collection,
) -> FileRepository:
    return FileRepository(collection)


# === 上传会话端点 ===


def get_upload_collection(request) -> AsyncIOMotorCollection:
    return request.app.state.db.upload_sessions


def get_upload_repo(
    collection: AsyncIOMotorCollection = get_upload_collection,
) -> UploadSessionRepository:
    return UploadSessionRepository(collection)


# === 分片记录 ===


def get_chunk_collection(request) -> AsyncIOMotorCollection:
    return request.app.state.db.chunks


def get_chunk_repo(
    collection: AsyncIOMotorCollection = get_chunk_collection,
) -> ChunkRepository:
    return ChunkRepository(collection)


# === 版本 ===


def get_version_collection(request) -> AsyncIOMotorCollection:
    return request.app.state.db.file_versions


def get_version_repo(
    collection: AsyncIOMotorCollection = get_version_collection,
) -> FileVersionRepository:
    return FileVersionRepository(collection)


# === 缩略图 ===


def get_thumbnail_collection(request) -> AsyncIOMotorCollection:
    return request.app.state.db.thumbnails


def get_thumbnail_repo(
    collection: AsyncIOMotorCollection = get_thumbnail_collection,
) -> ThumbnailRepository:
    return ThumbnailRepository(collection)


# === 服务 ===


def get_bucket_service(
    bucket_repo: BucketRepository = get_bucket_repo,
    backend: StorageBackendProtocol = get_storage_backend,
) -> BucketService:
    return BucketService(bucket_repo, backend)


def get_file_service(
    file_repo: FileRepository = get_file_repo,
    bucket_repo: BucketRepository = get_bucket_repo,
    thumbnail_repo: ThumbnailRepository = get_thumbnail_repo,
    backend: StorageBackendProtocol = get_storage_backend,
    pipeline: ProcessingPipeline = get_pipeline,
    cdn: CDNProviderProtocol | None = get_cdn_provider,
) -> FileService:
    return FileService(file_repo, bucket_repo, thumbnail_repo, backend, pipeline, cdn)


def get_upload_service(
    upload_repo: UploadSessionRepository = get_upload_repo,
    chunk_repo: ChunkRepository = get_chunk_repo,
    file_repo: FileRepository = get_file_repo,
    bucket_repo: BucketRepository = get_bucket_repo,
    backend: StorageBackendProtocol = get_storage_backend,
    request: Request = get_mongo_client,
) -> UploadService:
    from taolib.testing.file_storage.server.config import settings

    return UploadService(
        upload_repo,
        chunk_repo,
        file_repo,
        bucket_repo,
        backend,
        upload_session_ttl_hours=settings.upload_session_ttl_hours,
    )


def get_access_service(
    file_repo: FileRepository = get_file_repo,
    backend: StorageBackendProtocol = get_storage_backend,
    cdn: CDNProviderProtocol | None = get_cdn_provider,
) -> AccessService:
    from taolib.testing.file_storage.server.config import settings

    return AccessService(file_repo, backend, cdn, settings.signed_url_secret)


def get_lifecycle_service(
    file_repo: FileRepository = get_file_repo,
    version_repo: FileVersionRepository = get_version_repo,
    thumbnail_repo: ThumbnailRepository = get_thumbnail_repo,
    upload_repo: UploadSessionRepository = get_upload_repo,
    chunk_repo: ChunkRepository = get_chunk_repo,
    bucket_repo: BucketRepository = get_bucket_repo,
    backend: StorageBackendProtocol = get_storage_backend,
) -> LifecycleService:
    return LifecycleService(
        file_repo,
        version_repo,
        thumbnail_repo,
        upload_repo,
        chunk_repo,
        bucket_repo,
        backend,
    )


def get_stats_service(
    bucket_repo: BucketRepository = get_bucket_repo,
    file_repo: FileRepository = get_file_repo,
    upload_repo: UploadSessionRepository = get_upload_repo,
) -> StatsService:
    return StatsService(bucket_repo, file_repo, upload_repo)


