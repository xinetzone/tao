import argparse
import asyncio
import json
import os

from taolib.github_app import (
    GitHubAppSettings,
    GitHubInstallationTokenManager,
    InstallationTokenRequest,
    RequestedTokenStrategy,
)
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient
from taolib.github_app.models import EnvironmentKind, InstallationTokenResult


def build_parser() -> argparse.ArgumentParser:
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
    args = build_parser().parse_args(argv)
    if args.command == "profile":
        _emit_json(_build_profile_payload(args))
        return 0

    manager = build_manager(args)
    result = asyncio.run(manager.get_token(build_request(args)))
    _emit_json(_build_token_payload(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
