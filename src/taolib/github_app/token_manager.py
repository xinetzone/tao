"""GitHub App 安装令牌生命周期管理器。

本模块是令牌获取的唯一接入点，负责策略解析、缓存存取与 Singleflight
并发控制，避免下游重复向 GitHub 发起令牌请求。
"""

import asyncio
from dataclasses import replace

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import (
    EffectiveTokenStrategy,
    EnvironmentKind,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
)


class GitHubInstallationTokenManager:
    """安装令牌的生命周期管理器。

    负责三项核心职责：

    1. 根据运行环境将调用方请求的策略转为实际生效策略；
    2. 读写外部注入的缓存，在提前刷新窗口内触发刷新；
    3. 以 Singleflight 机制避免同一缓存键同时刷新造成的重复请求。
    """

    def __init__(
        self,
        client: GitHubAppClient,
        cache: InMemoryInstallationTokenCache,
        settings: GitHubAppSettings,
    ) -> None:
        """初始化令牌管理器。

        Args:
            client: 与 GitHub API 交互的客户端。
            cache: 外部注入的令牌缓存实现。
            settings: GitHub App 运行时配置。
        """
        self.client = client
        self.cache = cache
        self.settings = settings
        self._refresh_locks: dict[str, asyncio.Lock] = {}

    def build_cache_key(
        self,
        request: InstallationTokenRequest,
        effective: EffectiveTokenStrategy | None = None,
    ) -> str:
        """为一个令牌请求构建唯一缓存键。

        键值由 ``installation_id`` 、排序后的 ``permissions`` 、
        排序后的 ``repositories`` 与生效策略拼接，确保不同权限与仓库
        组合的令牌隔离存储。

        Args:
            request: 调用方传入的令牌请求。
            effective: 已推断出的生效策略，为 ``None`` 时内部调用
                :meth:`resolve_effective_strategy` 推断。

        Returns:
            唯一识别本次请求的缓存键字符串。
        """
        effective = effective or self.resolve_effective_strategy(request.strategy)
        return (
            f"{request.installation_id}|"
            f"{sorted(request.permissions.items())}|"
            f"{sorted(request.repositories)}|"
            f"{effective.value}"
        )

    def resolve_effective_strategy(
        self, requested: RequestedTokenStrategy
    ) -> EffectiveTokenStrategy:
        """将调用方请求的策略转换为实际生效的策略。

        核心规则：

        - 运行环境为 :attr:`EnvironmentKind.GHES` 时，强制降级为
          :attr:`EffectiveTokenStrategy.NONE`。
        - :attr:`RequestedTokenStrategy.ENABLED` → :attr:`EffectiveTokenStrategy.ENABLED`。
        - :attr:`RequestedTokenStrategy.DISABLED` → :attr:`EffectiveTokenStrategy.DISABLED`。
        - :attr:`RequestedTokenStrategy.AUTO` → :attr:`EffectiveTokenStrategy.NONE`。

        Args:
            requested: 调用方表达的策略意图。

        Returns:
            推断出的生效策略。
        """
        if self.settings.runtime_profile.environment is EnvironmentKind.GHES:
            return EffectiveTokenStrategy.NONE
        if requested is RequestedTokenStrategy.ENABLED:
            return EffectiveTokenStrategy.ENABLED
        if requested is RequestedTokenStrategy.DISABLED:
            return EffectiveTokenStrategy.DISABLED
        return EffectiveTokenStrategy.NONE

    def _was_degraded(
        self,
        requested: RequestedTokenStrategy,
        effective: EffectiveTokenStrategy,
    ) -> bool:
        """判断是否发生了策略降级。

        调用方明确表达 ENABLED/DISABLED，但最终生效为 NONE 时认为发生降级。
        """
        return (
            requested
            in {
                RequestedTokenStrategy.ENABLED,
                RequestedTokenStrategy.DISABLED,
            }
            and effective is EffectiveTokenStrategy.NONE
        )

    def _project_result_for_request(
        self,
        result: InstallationTokenResult,
        request: InstallationTokenRequest,
        effective: EffectiveTokenStrategy,
    ) -> InstallationTokenResult:
        """为本次请求填充策略与降级信息，产出调用方可见的结果。"""
        return replace(
            result,
            requested_strategy=request.strategy.value,
            effective_strategy=effective.value,
            degraded=result.degraded or self._was_degraded(request.strategy, effective),
        )

    async def _request_and_store(
        self,
        cache_key: str,
        request: InstallationTokenRequest,
        effective: EffectiveTokenStrategy,
    ) -> InstallationTokenResult:
        """向客户端请求新令牌并写入缓存。"""
        result = await self.client.create_installation_token(
            installation_id=request.installation_id,
            strategy=effective,
            permissions=request.permissions,
            repositories=request.repositories,
        )
        stored = self._project_result_for_request(result, request, effective)
        await self.cache.set(cache_key, stored)
        return stored

    async def _refresh_with_singleflight(
        self,
        cache_key: str,
        request: InstallationTokenRequest,
        effective: EffectiveTokenStrategy,
    ) -> InstallationTokenResult:
        """在同一缓存键上以互斥锁保证同时只有一个刷新任务。"""
        lock = self._refresh_locks.setdefault(cache_key, asyncio.Lock())
        async with lock:
            cached = await self.cache.get(cache_key)
            if cached and not self.cache.is_stale(
                cached,
                self.settings.eager_refresh_seconds,
            ):
                return self._project_result_for_request(cached, request, effective)
            return await self._request_and_store(cache_key, request, effective)

    async def get_token(
        self, request: InstallationTokenRequest
    ) -> InstallationTokenResult:
        """获取安装令牌的主入口。

        执行流程：

        1. 根据调用方策略推断生效策略。
        2. 构建缓存键并尝试读取缓存。
        3. 缓存命中且未进入提前刷新窗口时直接返回。
        4. 否则进入 Singleflight 刷新流程，刷新后写回缓存并返回。

        Args:
            request: 调用方提供的令牌请求。

        Returns:
            为本次请求量身填充了策略与降级信息的 :class:`InstallationTokenResult`。

        Raises:
            GitHubAppClientError: 需要刷新但调用 GitHub API 失败。
        """
        effective = self.resolve_effective_strategy(request.strategy)
        cache_key = self.build_cache_key(request, effective)
        cached = await self.cache.get(cache_key)
        if cached and not self.cache.is_stale(
            cached,
            self.settings.eager_refresh_seconds,
        ):
            return self._project_result_for_request(cached, request, effective)
        return await self._refresh_with_singleflight(
            cache_key,
            request,
            effective,
        )
