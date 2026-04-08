"""健康检查路由。"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str
    database: str


@router.get("", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """健康检查端点。"""
    try:
        # 尝试 ping MongoDB
        await request.app.state.mongo_client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        database=db_status,
    )


