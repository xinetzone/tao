"""CLI 入口模块。

使用 argparse 和 uvicorn 启动文件存储服务。
"""

import argparse

from taolib.testing.file_storage.server.app import create_app
from taolib.testing.file_storage.server.config import settings


def main() -> None:
    """CLI 入口点。"""
    parser = argparse.ArgumentParser(description="文件存储服务")
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"监听地址 (默认: {settings.host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"监听端口 (默认: {settings.port})",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载（开发模式）",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="日志级别 (默认: info)",
    )

    args = parser.parse_args()

    import uvicorn

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


