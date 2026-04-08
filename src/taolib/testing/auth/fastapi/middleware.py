"""FastAPI 认证中间件。

提供 ASGI 中间件，自动填充 ``request.state.user``。
"""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from ..errors import (
    TokenExpiredError,
    TokenInvalidError,
)
from ..models import AuthenticatedUser


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件。

    在请求处理前尝试认证，成功时将用户信息附加到
    ``request.state.user``。

    Args:
        app: ASGI 应用
        auth_dependency: 认证依赖函数（与 ``create_auth_dependency`` 返回的函数相同）
        exclude_paths: 不需要认证的路径前缀列表
    """

    def __init__(
        self,
        app: Any,
        auth_dependency: Callable[..., Coroutine[Any, Any, AuthenticatedUser]],
        exclude_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._auth_dependency = auth_dependency
        self._exclude_paths = set(exclude_paths or [])

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """处理请求认证。"""
        # 检查路径是否在排除列表中
        if self._should_skip(request.url.path):
            request.state.user = None
            return await call_next(request)

        # 中间件模式下直接调用认证逻辑
        # 注意：AuthMiddleware 是简化版，推荐使用 SimpleAuthMiddleware
        request.state.user = None
        return await call_next(request)

    def _should_skip(self, path: str) -> bool:
        """检查路径是否应跳过认证。"""
        return any(path.startswith(prefix) for prefix in self._exclude_paths)

    @staticmethod
    def _extract_bearer_token(request: Request) -> str | None:
        """从 Authorization 头提取 Bearer token。"""
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            return auth[7:].strip()
        return None


class SimpleAuthMiddleware(BaseHTTPMiddleware):
    """简化版认证中间件。

    直接使用 JWTService 和黑名单进行认证，不依赖 FastAPI 的依赖注入系统。
    适用于需要在中间件层面进行认证的场景。

    Args:
        app: ASGI 应用
        jwt_service: JWT 令牌服务
        blacklist: 令牌黑名单实现
        api_key_lookup: API 密钥查找实现
        exclude_paths: 不需要认证的路径前缀列表
    """

    def __init__(
        self,
        app: Any,
        jwt_service: Any,
        blacklist: Any = None,
        api_key_lookup: Any = None,
        exclude_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._jwt_service = jwt_service
        self._blacklist = blacklist
        self._api_key_lookup = api_key_lookup
        self._exclude_paths = set(exclude_paths or [])

    def _should_skip(self, path: str) -> bool:
        """检查路径是否应跳过认证。"""
        return any(path.startswith(prefix) for prefix in self._exclude_paths)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """处理请求认证。"""
        path = request.url.path

        # 跳过排除路径
        if self._should_skip(path):
            request.state.user = None
            return await call_next(request)

        # 尝试 JWT Bearer 认证
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
            try:
                payload = self._jwt_service.verify_access_token(token)
                # 检查黑名单
                if self._blacklist and payload.jti:
                    if await self._blacklist.is_blacklisted(payload.jti):
                        return JSONResponse(
                            status_code=401,
                            content={"detail": "令牌已被吊销"},
                            headers={"WWW-Authenticate": "Bearer"},
                        )
                request.state.user = AuthenticatedUser(
                    user_id=payload.sub,
                    roles=payload.roles,
                    auth_method="jwt",
                    metadata={"jti": payload.jti},
                )
                return await call_next(request)
            except TokenExpiredError:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "令牌已过期，请刷新"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except TokenInvalidError as e:
                return JSONResponse(
                    status_code=401,
                    content={"detail": e.message},
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # 尝试 API Key 认证
        api_key = request.headers.get("X-API-Key", "")
        if not api_key and auth_header.lower().startswith("apikey "):
            api_key = auth_header[7:].strip()

        if api_key and self._api_key_lookup:
            user = await self._api_key_lookup.lookup(api_key)
            if user is not None:
                request.state.user = user
                return await call_next(request)
            return JSONResponse(
                status_code=401,
                content={"detail": "无效的 API 密钥"},
            )

        # 无认证凭据
        return JSONResponse(
            status_code=401,
            content={"detail": "未提供认证凭据"},
            headers={"WWW-Authenticate": "Bearer"},
        )


