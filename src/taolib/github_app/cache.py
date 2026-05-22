from datetime import UTC, datetime, timedelta

from taolib.github_app.models import InstallationTokenResult


class InMemoryInstallationTokenCache:
    def __init__(self) -> None:
        self._items: dict[str, InstallationTokenResult] = {}

    async def get(self, key: str) -> InstallationTokenResult | None:
        return self._items.get(key)

    async def set(self, key: str, result: InstallationTokenResult) -> None:
        self._items[key] = result

    def is_stale(
        self, result: InstallationTokenResult, eager_refresh_seconds: int
    ) -> bool:
        refresh_at = result.expires_at - timedelta(seconds=eager_refresh_seconds)
        return datetime.now(tz=UTC) >= refresh_at
