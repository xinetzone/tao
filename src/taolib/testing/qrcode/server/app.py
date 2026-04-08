from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from taolib.testing.qrcode.server.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="QR Code Studio API",
        description="Advanced QR code generation with logo embedding and SVG export",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    return app


