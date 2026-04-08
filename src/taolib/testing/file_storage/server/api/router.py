"""API 路由聚合模块。

将所有子路由聚合到统一的 APIRouter。
"""

from fastapi import APIRouter

from taolib.testing.file_storage.server.api.buckets import router as buckets_router
from taolib.testing.file_storage.server.api.files import router as files_router
from taolib.testing.file_storage.server.api.health import router as health_router
from taolib.testing.file_storage.server.api.signed_urls import router as signed_urls_router
from taolib.testing.file_storage.server.api.stats import router as stats_router
from taolib.testing.file_storage.server.api.uploads import router as uploads_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(buckets_router, prefix="/buckets", tags=["Buckets"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["Uploads"])
api_router.include_router(
    signed_urls_router, prefix="/signed-urls", tags=["Signed URLs"]
)
api_router.include_router(stats_router, prefix="/stats", tags=["Stats"])
api_router.include_router(health_router, tags=["Health"])


