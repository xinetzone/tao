"""OAuth API 路由聚合模块。

将所有 API 子路由统一注册到 /api/v1 前缀。
"""

from fastapi import APIRouter

from .accounts import router as accounts_router
from .admin import router as admin_router
from .flow import router as flow_router
from .health import router as health_router
from .onboarding import router as onboarding_router
from .sessions import router as sessions_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(flow_router)
api_router.include_router(accounts_router)
api_router.include_router(sessions_router)
api_router.include_router(onboarding_router)
api_router.include_router(admin_router)


