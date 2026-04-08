"""路由聚合模块。

组装所有 API 路由到统一的路由器。
"""

from fastapi import APIRouter

from .audit import router as audit_router
from .auth import router as auth_router
from .configs import router as configs_router
from .health import router as health_router
from .push import router as push_router
from .roles import router as roles_router
from .users import router as users_router
from .versions import router as versions_router

api_router = APIRouter(prefix="/api/v1")

# 注册所有路由
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(configs_router)
api_router.include_router(versions_router)
api_router.include_router(audit_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(push_router)


