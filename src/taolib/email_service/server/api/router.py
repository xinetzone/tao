"""API 路由聚合。"""

from fastapi import APIRouter

from . import emails, health, subscriptions, templates, tracking, webhooks

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
api_router.include_router(
    subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"]
)
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
