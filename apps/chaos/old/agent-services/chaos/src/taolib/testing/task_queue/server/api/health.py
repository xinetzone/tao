"""健康检查路由。"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str
    database: str
    redis: str


@router.get("", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """健康检查端点。"""
    # 检查 MongoDB
    try:
        await request.app.state.mongo_client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # 检查 Redis
    try:
        await request.app.state.redis.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    overall = (
        "healthy"
        if db_status == "connected" and redis_status == "connected"
        else "unhealthy"
    )

    return HealthResponse(
        status=overall,
        database=db_status,
        redis=redis_status,
    )
