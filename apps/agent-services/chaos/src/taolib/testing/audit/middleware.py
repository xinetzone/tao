"""FastAPI 审计日志中间件。

自动记录所有 API 请求的审计日志。
"""
import logging
import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logger import AuditLogger
from .models import AuditAction, AuditStatus

logger = logging.getLogger(__name__)

DEFAULT_EXCLUDE_PATHS = {
    "/health",
    "/healthz",
    "/metrics",
    "/favicon.ico",
    "/openapi.json",
    "/docs",
    "/redoc",
}

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
}


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
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    if request.client:
        return request.client.host

    return "unknown"


def extract_user_id(request: Request) -> str | None:
    """尝试从请求中提取用户 ID。

    从 request.state.user 或自定义头 X-User-ID 提取。

    Args:
        request: FastAPI 请求对象

    Returns:
        用户 ID 或 None
    """
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id.strip()

    user = getattr(request.state, "user", None)
    if user is not None:
        return getattr(user, "user_id", None)

    return None


def filter_headers(headers: dict[str, str]) -> dict[str, str]:
    """过滤敏感请求头。

    Args:
        headers: 原始请求头

    Returns:
        过滤后的请求头
    """
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


class AuditMiddleware(BaseHTTPMiddleware):
    """FastAPI 审计日志中间件。

    自动记录所有 API 请求的审计日志，包括：
    - 请求方法和路径
    - 客户端 IP 和 User-Agent
    - 用户 ID（如果已认证）
    - 响应状态码和响应时间

    Args:
        app: ASGI 应用
        audit_logger: 审计日志记录器
        exclude_paths: 排除的路径前缀集合
        include_request_body: 是否记录请求体
        include_response_body: 是否记录响应体
        sensitive_body_paths: 包含敏感数据的路径前缀集合
    """

    def __init__(
        self,
        app: Any,
        audit_logger: AuditLogger,
        exclude_paths: set[str] | None = None,
        include_request_body: bool = False,
        include_response_body: bool = False,
        sensitive_body_paths: set[str] | None = None,
    ) -> None:
        """初始化审计中间件。

        Args:
            app: ASGI 应用
            audit_logger: 审计日志记录器
            exclude_paths: 排除的路径前缀集合
            include_request_body: 是否记录请求体
            include_response_body: 是否记录响应体
            sensitive_body_paths: 包含敏感数据的路径前缀集合
        """
        super().__init__(app)
        self._audit_logger = audit_logger
        self._exclude_paths = exclude_paths or DEFAULT_EXCLUDE_PATHS
        self._include_request_body = include_request_body
        self._include_response_body = include_response_body
        self._sensitive_body_paths = sensitive_body_paths or {
            "/auth/login",
            "/auth/register",
            "/auth/password",
            "/users/password",
        }

    def _should_skip(self, path: str) -> bool:
        """检查路径是否应跳过审计。

        Args:
            path: 请求路径

        Returns:
            是否跳过
        """
        for exclude_path in self._exclude_paths:
            if path.startswith(exclude_path) or path == exclude_path:
                return True
        return False

    def _is_sensitive_path(self, path: str) -> bool:
        """检查路径是否包含敏感数据。

        Args:
            path: 请求路径

        Returns:
            是否敏感
        """
        for sensitive_path in self._sensitive_body_paths:
            if path.startswith(sensitive_path):
                return True
        return False

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """处理请求并记录审计日志。

        Args:
            request: 接收的请求
            call_next: 下一个处理函数

        Returns:
            响应对象
        """
        path = request.url.path
        method = request.method

        if self._should_skip(path):
            return await call_next(request)

        start_time = time.perf_counter()

        user_id = extract_user_id(request)
        ip_address = extract_client_ip(request)
        user_agent = request.headers.get("User-Agent")

        query_params = dict(request.query_params)
        headers = filter_headers(dict(request.headers))

        details: dict[str, Any] = {
            "method": method,
            "path": path,
            "query_params": query_params,
            "headers": headers,
        }

        if self._include_request_body and not self._is_sensitive_path(path):
            try:
                body = await request.body()
                if body:
                    details["request_body_size"] = len(body)
                    if len(body) < 1024:
                        try:
                            details["request_body"] = body.decode("utf-8")
                        except UnicodeDecodeError:
                            details["request_body"] = "[BINARY]"
            except Exception:
                pass

        response = await call_next(request)

        response_time_ms = (time.perf_counter() - start_time) * 1000
        details["response_time_ms"] = round(response_time_ms, 2)
        details["status_code"] = response.status_code

        status = AuditStatus.SUCCESS if response.status_code < 400 else AuditStatus.FAILED

        action = self._determine_action(method, path)

        try:
            await self._audit_logger.log(
                action=action.value,
                resource_type="api",
                resource_id=None,
                user_id=user_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status.value,
            )
        except Exception:
            logger.exception("Failed to save audit log")

        return response

    def _determine_action(self, method: str, path: str) -> AuditAction:
        """根据请求方法和路径确定操作类型。

        Args:
            method: HTTP 方法
            path: 请求路径

        Returns:
            操作类型
        """
        if "/login" in path.lower():
            return AuditAction.LOGIN
        if "/logout" in path.lower():
            return AuditAction.LOGOUT

        method_action_map = {
            "GET": AuditAction.READ,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE,
        }

        return method_action_map.get(method.upper(), AuditAction.ACCESS)


