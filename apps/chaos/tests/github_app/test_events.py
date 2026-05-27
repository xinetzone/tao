"""事件 hook 机制的单元测试。"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.errors import GitHubAppClientError
from taolib.github_app.events import NullTokenEventHook
from taolib.github_app.models import (
    EffectiveTokenStrategy,
    EnvironmentKind,
    GitHubRuntimeProfile,
    InstallationTokenRequest,
    InstallationTokenResult,
    RequestedTokenStrategy,
    TokenKind,
)
from taolib.github_app.token_manager import GitHubInstallationTokenManager


def _make_settings():
    profile = GitHubRuntimeProfile(
        base_url="https://api.github.com",
        environment=EnvironmentKind.CLOUD,
    )
    return SimpleNamespace(
        app_id="123",
        installation_id="456",
        private_key="fake",
        api_url="https://api.github.com",
        default_strategy=RequestedTokenStrategy.AUTO,
        eager_refresh_seconds=90,
        allow_header_fallback=False,
        runtime_profile=profile,
    )


def _make_result(token="ghs_test"):
    return InstallationTokenResult(
        token=token,
        expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
        token_kind=TokenKind.STATEFUL,
        requested_strategy=RequestedTokenStrategy.AUTO.value,
        effective_strategy=EffectiveTokenStrategy.NONE.value,
        degraded=False,
    )


def _make_request():
    return InstallationTokenRequest(
        installation_id="456",
        permissions={"contents": "read"},
        repositories=["repo1"],
        strategy=RequestedTokenStrategy.AUTO,
    )


class RecordingHook:
    """记录所有事件调用的测试 hook。"""

    def __init__(self):
        self.refreshed_calls = []
        self.failed_calls = []

    async def on_token_refreshed(self, cache_key, result):
        self.refreshed_calls.append((cache_key, result))

    async def on_token_refresh_failed(self, cache_key, error):
        self.failed_calls.append((cache_key, error))


@pytest.mark.asyncio
async def test_null_hook_does_not_affect_normal_flow():
    """默认 NullTokenEventHook 不影响正常流程。"""

    async def fake_create_token(**kwargs):
        return _make_result()

    client = SimpleNamespace(create_installation_token=fake_create_token)
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=_make_settings(),
        event_hook=NullTokenEventHook(),
    )
    result = await manager.get_token(_make_request())
    assert result.token == "ghs_test"


@pytest.mark.asyncio
async def test_custom_hook_called_on_refresh_success():
    """自定义 hook 在刷新成功时被调用。"""

    async def fake_create_token(**kwargs):
        return _make_result()

    hook = RecordingHook()
    client = SimpleNamespace(create_installation_token=fake_create_token)
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=_make_settings(),
        event_hook=hook,
    )
    await manager.get_token(_make_request())

    assert len(hook.refreshed_calls) == 1
    assert hook.refreshed_calls[0][1].token == "ghs_test"
    assert len(hook.failed_calls) == 0


@pytest.mark.asyncio
async def test_custom_hook_called_on_refresh_failure():
    """自定义 hook 在刷新失败时被调用。"""

    async def fake_create_token(**kwargs):
        raise GitHubAppClientError("API failed")

    hook = RecordingHook()
    client = SimpleNamespace(create_installation_token=fake_create_token)
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=_make_settings(),
        event_hook=hook,
    )

    with pytest.raises(GitHubAppClientError):
        await manager.get_token(_make_request())

    assert len(hook.failed_calls) == 1
    assert isinstance(hook.failed_calls[0][1], GitHubAppClientError)
    assert len(hook.refreshed_calls) == 0


@pytest.mark.asyncio
async def test_hook_exception_propagates():
    """hook 自身抛出异常时应透传（不吞没）。"""

    async def fake_create_token(**kwargs):
        return _make_result()

    class FailingHook:
        async def on_token_refreshed(self, cache_key, result):
            raise RuntimeError("hook exploded")

        async def on_token_refresh_failed(self, cache_key, error):
            pass

    client = SimpleNamespace(create_installation_token=fake_create_token)
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=_make_settings(),
        event_hook=FailingHook(),
    )

    with pytest.raises(RuntimeError, match="hook exploded"):
        await manager.get_token(_make_request())


@pytest.mark.asyncio
async def test_no_hook_parameter_uses_null_hook():
    """不传 event_hook 参数时使用 NullTokenEventHook。"""

    async def fake_create_token(**kwargs):
        return _make_result()

    client = SimpleNamespace(create_installation_token=fake_create_token)
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=_make_settings(),
    )
    # 应正常执行，不抛异常
    result = await manager.get_token(_make_request())
    assert result.token == "ghs_test"
