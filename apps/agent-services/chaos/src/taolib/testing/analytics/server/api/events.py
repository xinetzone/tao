"""事件摄入路由。"""

from fastapi import APIRouter, HTTPException, Request, status

from ...models import EventBatchCreate, EventCreate
from ..config import settings

router = APIRouter()


def verify_api_key(request: Request) -> None:
    """验证 API Key。

    如果 settings.api_keys 为空列表则跳过认证。
    """
    if not settings.api_keys:
        return

    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或缺失的 API Key",
        )


def get_analytics_service(request: Request):
    """获取 AnalyticsService 实例。"""
    from ...repository.event_repo import EventRepository
    from ...repository.session_repo import SessionRepository
    from ...services.analytics_service import AnalyticsService

    event_repo = EventRepository(request.app.state.db.analytics_events)
    session_repo = SessionRepository(request.app.state.db.analytics_sessions)
    return AnalyticsService(event_repo, session_repo)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_event(request: Request, data: EventCreate):
    """上报单个事件。"""
    verify_api_key(request)
    service = get_analytics_service(request)
    result = await service.ingest_events([data])
    return {"status": "accepted", **result}


@router.post("/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_events_batch(request: Request, data: EventBatchCreate):
    """批量上报事件。"""
    verify_api_key(request)

    if len(data.events) > settings.max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"批量事件数量超过限制 ({settings.max_batch_size})",
        )

    service = get_analytics_service(request)
    result = await service.ingest_events(data.events)
    return result
