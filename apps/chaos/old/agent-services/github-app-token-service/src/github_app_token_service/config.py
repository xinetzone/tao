"""服务级配置聚合。

本模块将环境变量配置与服务级运行时参数（监听地址、端口等）整合，
作为服务启动时的唯一配置来源。
"""

import os

from taolib.github_app.config import GitHubAppSettings


class ServiceConfig:
    """服务运行时配置。

    Attributes:
        host: 服务监听地址。
        port: 服务监听端口。
        github_settings: 从环境变量加载的 GitHub App 配置。
    """

    def __init__(self) -> None:
        self.host = os.getenv("SERVICE_HOST", "0.0.0.0")
        self.port = int(os.getenv("SERVICE_PORT", "8000"))
        self.github_settings = GitHubAppSettings.from_env()
