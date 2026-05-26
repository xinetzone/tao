"""CLI 入口模块。

提供命令行启动脚本。
"""

import argparse

import uvicorn

from .app import create_app
from .config import settings


def main() -> None:
    """CLI 入口函数。"""
    parser = argparse.ArgumentParser(description="启动任务队列服务器")
    parser.add_argument(
        "--host", default=settings.host, help=f"监听地址 (默认: {settings.host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"监听端口 (默认: {settings.port})",
    )
    parser.add_argument(
        "--reload", action="store_true", help="启用自动重载（开发模式）"
    )
    parser.add_argument("--log-level", default="info", help="日志级别 (默认: info)")

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


