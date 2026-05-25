"""FastAPI 应用入口。

负责应用生命周期管理、全局依赖初始化与路由挂载。
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from github_app_token_service.api import router
from github_app_token_service.config import ServiceConfig
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.token_manager import GitHubInstallationTokenManager

# 全局单例，懒加载初始化
_token_manager: GitHubInstallationTokenManager | None = None
_service_config: ServiceConfig | None = None


def get_config() -> ServiceConfig:
    """获取服务配置（懒加载）。"""
    global _service_config
    if _service_config is None:
        _service_config = ServiceConfig()
    return _service_config


def get_token_manager() -> GitHubInstallationTokenManager:
    """获取令牌管理器（懒加载）。

    首次调用时根据配置初始化 GitHubAppClient、InMemoryInstallationTokenCache
    与 GitHubInstallationTokenManager，后续调用直接返回已创建的实例。
    """
    global _token_manager
    if _token_manager is None:
        config = get_config()
        client = GitHubAppClient(
            app_id=config.github_settings.app_id,
            private_key=config.github_settings.private_key,
            api_url=config.github_settings.api_url,
        )
        cache = InMemoryInstallationTokenCache()
        _token_manager = GitHubInstallationTokenManager(
            client=client,
            cache=cache,
            settings=config.github_settings,
        )
    return _token_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期上下文管理器。

    启动时：初始化配置、启动后台缓存过期清理协程。
    关闭时：取消后台任务、关闭 HTTP 客户端连接池。
    """
    config = get_config()
    manager = get_token_manager()

    # 启动后台缓存清理任务（每 300 秒清理一次过期条目）
    purge_task = manager.cache.start_purge_task(interval_seconds=300)

    yield

    # 应用关闭清理
    manager.cache.stop_purge_task()
    purge_task.cancel()
    try:
        await purge_task
    except asyncio.CancelledError:
        pass
    await manager.client._http.aclose()


app = FastAPI(
    title="GitHub App Token Service",
    description="基于 taolib 的 GitHub App 安装令牌管理 RESTful API 服务",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    uvicorn.run(
        "github_app_token_service.main:app",
        host=config.host,
        port=config.port,
        reload=True,
    )
