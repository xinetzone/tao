"""OAuth 服务器入口模块。

提供 CLI 入口启动 OAuth 服务。
"""

import argparse


def main() -> None:
    """启动 OAuth 服务器。"""
    parser = argparse.ArgumentParser(description="OAuth Service")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8002, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="开发模式自动重载")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "taolib.oauth.server.app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True,
    )


if __name__ == "__main__":
    main()


