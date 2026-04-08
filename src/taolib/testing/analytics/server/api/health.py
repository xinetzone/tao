"""健康检查路由。"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def health_check(request: Request):
    """健康检查端点。"""
    try:
        await request.app.state.mongo_client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
    }


