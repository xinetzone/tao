"""Rate limit statistics API routes."""
from fastapi import APIRouter, Depends, Query

from taolib.rate_limiter.dependencies import get_stats_service
from taolib.rate_limiter.stats import RateLimitStatsService

router = APIRouter(prefix="/stats", tags=["rate-limit-stats"])


@router.get("/top-users")
async def get_top_users(
    period_hours: int = Query(24, ge=1, le=168, description="统计时间范围（小时）"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    stats_service: RateLimitStatsService = Depends(get_stats_service),
):
    """获取请求量最大的用户列表。

    Args:
        period_hours: 统计时间范围
        limit: 返回数量限制

    Returns:
        Top Users 列表
    """
    users = await stats_service.get_top_users(limit)
    return {"users": users}


@router.get("/violations")
async def get_violation_stats(
    period_hours: int = Query(24, ge=1, le=168, description="统计时间范围（小时）"),
    stats_service: RateLimitStatsService = Depends(get_stats_service),
):
    """获取违规统计。

    Args:
        period_hours: 统计时间范围

    Returns:
        违规统计列表
    """
    violations = await stats_service.get_violation_stats(period_hours)
    return {"violations": violations}


@router.get("/realtime")
async def get_realtime_stats(
    window_seconds: int = Query(60, ge=10, le=300, description="统计窗口（秒）"),
    stats_service: RateLimitStatsService = Depends(get_stats_service),
):
    """获取实时请求统计。

    Args:
        window_seconds: 统计窗口

    Returns:
        实时统计数据
    """
    realtime = await stats_service.get_realtime(window_seconds)
    return realtime
