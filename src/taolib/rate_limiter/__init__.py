"""
Rate Limiter Module

滑动窗口限流中间件，基于 Redis 实现，为 FastAPI 应用提供：
- 按用户/IP 差异化限流
- 接口级限流配置
- 白名单机制
- 违规监控与统计

Usage:
    from taolib.rate_limiter import RateLimiter, RateLimitMiddleware
"""

from .config import RateLimitConfig
from .errors import RateLimitExceededError
from .limiter import RateLimiter
from .middleware import RateLimitMiddleware

__all__ = [
    "RateLimitConfig",
    "RateLimitExceededError",
    "RateLimitMiddleware",
    "RateLimiter",
]
