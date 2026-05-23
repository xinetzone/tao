"""``taolib-github-app`` 命令行入口。

本模块提供两个子命令：

- ``profile``：查询当前运行环境画像，无需有效私钥即可执行。
- ``token``：获取安装令牌并以脱敏后的 JSON 输出。

详细环境变量与输出示例请参阅 :class:`taolib.github_app.config.GitHubAppSettings`。
"""

import argparse
import asyncio
import json
import os
import sys

from taolib.github_app import (
    GitHubAppSettings,
    GitHubInstallationTokenManager,
    InstallationTokenRequest,
    RequestedTokenStrategy,
)
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.errors import GitHubAppClientError, GitHubAppConfigurationError
from taolib.github_app.models import EnvironmentKind, InstallationTokenResult


def build_parser() -> argparse.ArgumentParser:
    """构造 CLI 参数解析器。

    Returns:
        包含 ``profile`` 与 ``token`` 两个子命令的 :class:`argparse.ArgumentParser`。
    """
    parser = argparse.ArgumentParser(prog="taolib-github-app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_parser = subparsers.add_parser("profile")
    profile_parser.add_argument("--api-url")
    profile_parser.add_argument(
        "--strategy",
        choices=["auto", "enabled", "disabled"],
        default=None,
    )

    token_parser = subparsers.add_parser("token")
    token_parser.add_argument("--installation-id")
    token_parser.add_argument(
        "--strategy",
        choices=["auto", "enabled", "disabled"],
        default=None,
    )
    return parser


def _detect_environment(api_url: str) -> EnvironmentKind:
    normalized = api_url.rstrip("/")
    if normalized == "https://api.github.com":
        return EnvironmentKind.CLOUD
    if normalized.endswith("/api/v3"):
        return EnvironmentKind.GHES
    return EnvironmentKind.UNKNOWN


def _mask_secret(secret: str) -> str:
    if len(secret) <= 11:
        return f"{secret[:4]}...{secret[-2:]}"
    return f"{secret[:7]}...{secret[-4:]}"


def _resolve_api_url(args: argparse.Namespace) -> str:
    return args.api_url or os.getenv("GITHUB_API_URL", "https://api.github.com")


def _resolve_strategy(args: argparse.Namespace) -> RequestedTokenStrategy:
    raw_value = args.strategy or os.getenv("GITHUB_APP_TOKEN_STRATEGY", "auto")
    return RequestedTokenStrategy(raw_value)


def build_manager(args: argparse.Namespace) -> GitHubInstallationTokenManager:
    """从环境变量装配出可用的令牌管理器。

    Args:
        args: 仅为接口一致性保留，不参与现有逻辑。

    Returns:
        依赖内存缓存与默认客户端的 :class:`GitHubInstallationTokenManager` 实例。
    """
    del args
    settings = GitHubAppSettings.from_env()
    client = GitHubAppClient(
        app_id=settings.app_id,
        private_key=settings.private_key,
        api_url=settings.api_url,
    )
    return GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=settings,
    )


def build_request(args: argparse.Namespace) -> InstallationTokenRequest:
    """根据命令行参数与环境变量拼装令牌请求。

    Args:
        args: 已解析的命令行参数。

    Returns:
        可用于 :meth:`GitHubInstallationTokenManager.get_token` 的请求对象。
    """
    installation_id = args.installation_id or os.environ["GITHUB_APP_INSTALLATION_ID"]
    return InstallationTokenRequest(
        installation_id=installation_id,
        permissions={},
        repositories=[],
        strategy=_resolve_strategy(args),
    )


def _build_profile_payload(args: argparse.Namespace) -> dict[str, str]:
    api_url = _resolve_api_url(args)
    return {
        "api_url": api_url,
        "default_strategy": _resolve_strategy(args).value,
        "environment": _detect_environment(api_url).value,
    }


def _build_token_payload(result: InstallationTokenResult) -> dict[str, object]:
    return {
        "degraded": result.degraded,
        "effective_strategy": result.effective_strategy,
        "expires_at": result.expires_at.isoformat(),
        "requested_strategy": result.requested_strategy,
        "token_kind": result.token_kind.value,
        "token_preview": _mask_secret(result.token),
    }


def _emit_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    """CLI 主入口。

    Args:
        argv: 可选参数列表，为 ``None`` 时默认使用 :data:`sys.argv`。

    Returns:
        进程退出码：``0`` 表示成功，``1`` 表示配置错误，``2`` 表示客户端错误。
    """
    try:
        args = build_parser().parse_args(argv)
        if args.command == "profile":
            _emit_json(_build_profile_payload(args))
            return 0
        manager = build_manager(args)
        result = asyncio.run(manager.get_token(build_request(args)))
        _emit_json(_build_token_payload(result))
        return 0
    except GitHubAppConfigurationError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    except GitHubAppClientError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
