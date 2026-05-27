"""API 路由模块。"""

from fastapi import APIRouter

from . import health, stats, tasks

api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
