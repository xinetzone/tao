"""健康检查端点。"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def health_check(request: Request):
    """系统健康检查。"""
    result = {
        "status": "ok",
        "database": False,
        "redis": False,
        "providers": [],
        "queue": {},
    }

    # 检查 MongoDB
    try:
        await request.app.state.db.command("ping")
        result["database"] = True
    except Exception:
        result["database"] = False

    # 检查 Redis
    try:
        await request.app.state.redis.ping()
        result["redis"] = True
    except Exception:
        result["redis"] = False

    # 提供商状态
    if request.app.state.provider_manager:
        result["providers"] = [
            {
                "provider_name": s.provider_name,
                "is_healthy": s.is_healthy,
                "consecutive_failures": s.consecutive_failures,
            }
            for s in request.app.state.provider_manager.get_provider_statuses()
        ]

    # 队列状态
    try:
        result["queue"] = await request.app.state.queue.size()
    except Exception:
        result["queue"] = {}

    # 总状态
    if not result["database"] or not result["redis"]:
        result["status"] = "degraded"

    return result
