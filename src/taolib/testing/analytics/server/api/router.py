"""API 路由模块。"""

from fastapi import APIRouter

from . import analytics, events, health

api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])


