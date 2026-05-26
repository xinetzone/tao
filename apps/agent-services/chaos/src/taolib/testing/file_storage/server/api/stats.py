"""统计端点。"""

from fastapi import APIRouter, Depends

from taolib.testing.file_storage.models.stats import (
    StorageOverviewResponse,
    UploadStatsResponse,
)
from taolib.testing.file_storage.services.stats_service import StatsService

router = APIRouter()


@router.get("/overview", response_model=StorageOverviewResponse, summary="全局存储概览")
async def get_storage_overview(
    stats_service: StatsService = Depends(),
):
    """获取全局存储概览。"""
    return await stats_service.get_storage_overview()


@router.get("/uploads", response_model=UploadStatsResponse, summary="上传统计")
async def get_upload_stats(
    stats_service: StatsService = Depends(),
):
    """获取上传统计。"""
    return await stats_service.get_upload_stats()


