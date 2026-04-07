from fastapi import APIRouter

from taolib.qrcode.server.api import batch, generate, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(generate.router, prefix="/generate", tags=["generate"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
