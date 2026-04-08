"""FastAPI dependencies for rate limiter.

Provides dependency injection functions for use in FastAPI routes.
"""
from fastapi import Request

from .limiter import RateLimiter
from .stats import RateLimitStatsService
from .violation_tracker import ViolationTracker


def get_rate_limiter(request: Request) -> RateLimiter:
    """获取限流引擎实例。

    Usage in routes:
        @router.get("/path")
        async def endpoint(limiter: RateLimiter = Depends(get_rate_limiter)):
            ...

    Args:
        request: FastAPI 请求对象

    Returns:
        限流引擎实例
    """
    return request.app.state.rate_limiter


def get_violation_tracker(request: Request) -> ViolationTracker | None:
    """获取违规追踪器实例。

    Args:
        request: FastAPI 请求对象

    Returns:
        违规追踪器实例或 None
    """
    return getattr(request.app.state, "violation_tracker", None)


def get_stats_service(request: Request) -> RateLimitStatsService:
    """获取统计服务实例。

    Args:
        request: FastAPI 请求对象

    Returns:
        统计服务实例
    """
    return request.app.state.rate_limit_stats_service


