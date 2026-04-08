"""OAuth 健康检查 API 模块。

提供服务健康检查端点。
"""

from fastapi import APIRouter

router = APIRouter(tags=["健康检查"])


@router.get("/health")
async def health_check():
    """服务健康检查。

    Returns:
        健康状态响应
    """
    return {"status": "ok", "service": "oauth"}


