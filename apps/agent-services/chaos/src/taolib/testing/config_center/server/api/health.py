"""健康检查 API 模块。

实现系统健康检查和就绪检查端点。
"""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from taolib.testing._base.redis_pool import get_redis_client

from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("")
async def health_check() -> dict:
    """健康检查。

    Returns:
        系统健康状态
    """
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check():
    """就绪检查（检查 MongoDB 和 Redis 连接）。

    Returns:
        数据库连接就绪状态
    """
    mongodb_status = "disconnected"
    redis_status = "disconnected"

    # 检查 MongoDB 连接
    try:
        client = AsyncIOMotorClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        mongodb_status = "connected"
        client.close()
    except Exception as e:
        logger.error(f"MongoDB 连接检查失败: {e}")
        mongodb_status = "error"

    # 检查 Redis 连接
    try:
        redis_client = await get_redis_client(settings.redis_url)
        await redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        logger.error(f"Redis 连接检查失败: {e}")
        redis_status = "error"

    # 综合状态
    all_ready = mongodb_status == "connected" and redis_status == "connected"
    status_code = 200 if all_ready else 503

    return JSONResponse(
        content={
            "status": "ready" if all_ready else "not_ready",
            "mongodb": mongodb_status,
            "redis": redis_status,
        },
        status_code=status_code,
    )


