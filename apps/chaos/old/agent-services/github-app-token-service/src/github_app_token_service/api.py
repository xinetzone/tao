"""FastAPI 路由定义。

封装 taolib 的 GitHub App 令牌管理能力，暴露为 RESTful API。
"""

from fastapi import APIRouter, HTTPException, status

from github_app_token_service.models import (
    CacheClearResponse,
    HealthResponse,
    TokenRequest,
    TokenResponse,
)
from taolib.github_app.errors import GitHubAppError
from taolib.github_app.models import InstallationTokenRequest, RequestedTokenStrategy

router = APIRouter()


def _mask_app_id(app_id: str) -> str:
    """脱敏 App ID，仅显示前四位。"""
    if len(app_id) <= 4:
        return "****"
    return app_id[:4] + "****"


@router.post("/tokens", response_model=TokenResponse)
async def create_token(request: TokenRequest) -> TokenResponse:
    """为指定安装实例获取 GitHub App 安装令牌。

    本端点是令牌获取的主入口，支持自定义权限、仓库范围和策略。
    令牌结果内部经过缓存与 Singleflight 并发控制，避免重复请求 GitHub API。
    """
    from github_app_token_service.main import get_token_manager

    manager = get_token_manager()

    try:
        result = await manager.get_token(
            InstallationTokenRequest(
                installation_id=request.installation_id,
                permissions=request.permissions,
                repositories=request.repositories,
                strategy=RequestedTokenStrategy(request.strategy.value),
            )
        )
    except GitHubAppError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return TokenResponse(
        token=result.token,
        expires_at=result.expires_at,
        token_kind=result.token_kind.value,
        requested_strategy=result.requested_strategy,
        effective_strategy=result.effective_strategy,
        degraded=result.degraded,
    )


@router.get("/tokens/{installation_id}", response_model=TokenResponse)
async def get_token_simple(installation_id: str) -> TokenResponse:
    """使用默认策略和权限获取安装令牌（简化接口）。

    适合不需要自定义权限或仓库范围的场景，直接传入 installation_id 即可。
    """
    from github_app_token_service.main import get_token_manager

    manager = get_token_manager()

    try:
        result = await manager.get_token(
            InstallationTokenRequest(
                installation_id=installation_id,
                permissions={},
                repositories=[],
                strategy=RequestedTokenStrategy.AUTO,
            )
        )
    except GitHubAppError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return TokenResponse(
        token=result.token,
        expires_at=result.expires_at,
        token_kind=result.token_kind.value,
        requested_strategy=result.requested_strategy,
        effective_strategy=result.effective_strategy,
        degraded=result.degraded,
    )


@router.delete("/tokens/cache", response_model=CacheClearResponse)
async def clear_cache() -> CacheClearResponse:
    """清除令牌缓存。

    强制清空内存中的令牌缓存，使后续请求重新向 GitHub API 获取新令牌。
    适用于令牌疑似失效或需要立即刷新策略的场景。
    """
    from github_app_token_service.main import get_token_manager

    manager = get_token_manager()
    # InMemoryInstallationTokenCache 未暴露 clear 方法，直接操作内部存储
    manager.cache._items.clear()

    return CacheClearResponse(
        cleared=True,
        message="Token cache cleared successfully.",
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """健康检查端点。

    返回服务运行状态及脱敏后的 GitHub App 配置信息，便于负载均衡器或服务网格探测。
    """
    from github_app_token_service.main import get_config

    config = get_config()

    return HealthResponse(
        status="healthy",
        github_app_id=_mask_app_id(config.github_settings.app_id),
        environment=config.github_settings.runtime_profile.environment.value,
    )
