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
    def __init__(
        self,
        client: GitHubAppClient,
        cache: InMemoryInstallationTokenCache,
        settings: GitHubAppSettings,
    ) -> None:
        self.client = client
        self.cache = cache
        self.settings = settings
        self._refresh_locks: dict[str, asyncio.Lock] = {}

    def build_cache_key(
        self,
        request: InstallationTokenRequest,
        effective: EffectiveTokenStrategy | None = None,
    ) -> str:
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
        return (
            requested in {
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
