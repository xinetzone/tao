"""API 路由模块。"""

from fastapi import APIRouter

from . import failures, health, jobs, logs, metrics

api_router = APIRouter(prefix="/api/v1")

# 注册子路由
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(failures.router, prefix="/failures", tags=["Failures"])
