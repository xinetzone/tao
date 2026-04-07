"""FastAPI middleware for rate limiting."""
import logging
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .errors import RateLimitExceededError
from .limiter import RateLimiter
from .models import RateLimitErrorResponse
from .violation_tracker import ViolationTracker


def extract_client_ip(request: Request) -> str:
    """提取客户端 IP 地址。

    优先级：
    1. X-Forwarded-For 第一个 IP（代理场景）
    2. X-Real-IP
    3. request.client.host（直接连接）

    Args:
        request: FastAPI 请求对象

    Returns:
        客户端 IP 地址
    """
    # Check X-Forwarded-For
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback to direct connection
    if request.client:
        return request.client.host

    return "unknown"


def extract_user_id(request: Request) -> str | None:
    """尝试从请求中提取用户 ID。

    从 JWT token 的 sub 字段或自定义头 X-User-ID 提取。

    Args:
        request: FastAPI 请求对象

    Returns:
        用户 ID 或 None
    """
    # Check custom header (simple case)
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id.strip()

    # In production, you would parse the Authorization header
    # and extract the user ID from the JWT token
    # This is a simplified implementation
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI 限流中间件。

    功能：
    - 提取用户标识符（用户 ID 或 IP）
    - 检查白名单和 bypass 路径
    - 调用限流引擎检查请求
    - 注入限流响应头
    - 记录违规行为

    Args:
        app: ASGI 应用
        limiter: 限流引擎实例
        violation_tracker: 违规追踪器实例（可选）
        logger: 日志记录器
    """

    def __init__(
        self,
        app: Any,
        limiter: RateLimiter,
        violation_tracker: ViolationTracker | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = limiter
        self._violation_tracker = violation_tracker
        self._logger = logger or logging.getLogger("taolib.rate_limiter")

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """处理请求。

        Args:
            request: 接收的请求
            call_next: 下一个处理函数

        Returns:
            响应对象
        """
        # Skip if rate limiting is disabled
        if not self._limiter._config.enabled:
            return await call_next(request)

        path = request.url.path
        method = request.method

        # Check bypass paths
        if self._limiter.is_bypass_path(path):
            return await call_next(request)

        # Extract identifier
        user_id = extract_user_id(request)
        client_ip = extract_client_ip(request)

        if user_id:
            identifier = f"user:{user_id}"
            # Check user whitelist
            if self._limiter.is_whitelisted_user(user_id):
                return await call_next(request)
        else:
            identifier = f"ip:{client_ip}"
            # Check IP whitelist
            if self._limiter.is_whitelisted_ip(client_ip):
                return await call_next(request)

        # Check rate limit
        try:
            result = await self._limiter.check_limit(identifier, path, method)
        except RateLimitExceededError as exc:
            # Log violation
            self._logger.warning(
                "Rate limit exceeded: identifier=%s, path=%s, method=%s, limit=%d",
                identifier,
                path,
                method,
                exc.limit,
            )

            # Record violation to MongoDB
            if self._violation_tracker:
                try:
                    await self._violation_tracker.record_violation(
                        identifier=identifier,
                        ip_address=client_ip,
                        path=path,
                        method=method,
                        request_count=0,  # Will be filled by limiter
                        limit=exc.limit,
                        window_seconds=exc.window_seconds,
                        retry_after=exc.retry_after,
                        user_id=user_id,
                        user_agent=request.headers.get("User-Agent"),
                    )
                except Exception:
                    self._logger.exception("Failed to record violation")

            # Return 429 response
            error_response = RateLimitErrorResponse(
                retry_after=exc.retry_after,
                limit=exc.limit,
                window_seconds=exc.window_seconds,
            )

            return JSONResponse(
                status_code=429,
                content=error_response.model_dump(),
                headers={
                    "Retry-After": str(exc.retry_after),
                    "X-RateLimit-Limit": str(exc.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(exc.reset_timestamp)),
                },
            )

        # Request allowed - process it
        response = await call_next(request)

        # Record the request in background
        try:
            await self._limiter.record_request(identifier, path, method)
        except Exception:
            self._logger.exception("Failed to record request")

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(result.reset_timestamp))

        return response
