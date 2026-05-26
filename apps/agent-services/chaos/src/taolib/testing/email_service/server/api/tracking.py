"""追踪分析端点。"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query, Request

router = APIRouter()


@router.get("/analytics")
async def get_analytics(
    request: Request,
    days: int = Query(7, ge=1, le=365, description="统计天数"),
):
    """获取分析数据。"""
    end = datetime.now(UTC)
    start = end - timedelta(days=days)
    return await request.app.state.tracking_service.get_analytics(start, end)


@router.get("/daily")
async def get_daily_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="统计天数"),
):
    """获取按日统计数据。"""
    end = datetime.now(UTC)
    start = end - timedelta(days=days)
    return await request.app.state.tracking_service.get_daily_stats(start, end)


@router.get("/events")
async def list_events(
    request: Request,
    email_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询追踪事件。"""
    if email_id:
        return await request.app.state.tracking_service.get_events_for_email(email_id)
    docs = await request.app.state.tracking_repo.list(
        skip=skip, limit=limit, sort=[("timestamp", -1)]
    )
    return [d.to_response() for d in docs]


