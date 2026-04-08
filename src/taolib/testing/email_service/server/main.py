"""邮件服务 CLI 入口。"""

import argparse

import uvicorn

from .app import create_app
from .config import settings


def main() -> None:
    """启动邮件服务。"""
    parser = argparse.ArgumentParser(description="Email Service Server")
    parser.add_argument("--host", default=settings.host, help="Listen address")
    parser.add_argument("--port", type=int, default=settings.port, help="Listen port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()
    app = create_app()

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()


