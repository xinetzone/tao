"""Symphony HTTP 服务器（可选）。

提供 REST JSON API 和 HTML 仪表板，用于监控编排状态。
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from ..observability.logging import get_logger
from .dashboard import get_dashboard_html
from .routes import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    # 启动时：引用由外部注入的 orchestrator state
    logger.info("symphony_server_starting")
    yield
    # 关闭时：无需清理
    logger.info("symphony_server_stopped")


def create_app(orchestrator: object | None = None) -> FastAPI:
    """创建 Symphony FastAPI 应用实例。

    Args:
        orchestrator: 编排器实例，会被挂载到 app.state.orchestrator，
            供路由通过 request.app.state.orchestrator 访问。

    Returns:
        配置好的 FastAPI 应用。
    """
    app = FastAPI(
        title="Symphony API",
        description="Symphony 编排服务监控 API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载编排器实例到应用状态
    app.state.orchestrator = orchestrator

    # 注册 API 路由
    app.include_router(api_router)

    # 注册仪表板路由
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        """Symphony 监控仪表板。"""
        return get_dashboard_html()

    return app
