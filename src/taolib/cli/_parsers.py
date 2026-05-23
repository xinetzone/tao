"""CLI 参数解析与环境解析工具。

本模块负责构造 CLI 参数解析器，以及从参数或环境变量中推断 API URL、
策略和环境类型等配置项。
"""

import argparse
import os

from taolib.github_app import RequestedTokenStrategy
from taolib.github_app.models import EnvironmentKind


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

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--installation-id", required=True)
    status_parser.add_argument(
        "--strategy",
        choices=["auto", "enabled", "disabled"],
        default=None,
    )
    return parser


def _detect_environment(api_url: str) -> EnvironmentKind:
    """根据 API URL 判断 GitHub 环境类型。

    Args:
        api_url: GitHub API 的 URL 字符串。

    Returns:
        对应的 :class:`~taolib.github_app.models.EnvironmentKind` 枚举值。
    """
    normalized = api_url.rstrip("/")
    if normalized == "https://api.github.com":
        return EnvironmentKind.CLOUD
    if normalized.endswith("/api/v3"):
        return EnvironmentKind.GHES
    return EnvironmentKind.UNKNOWN


def _resolve_api_url(args: argparse.Namespace) -> str:
    """从参数或环境变量获取 API URL。

    Args:
        args: 已解析的命令行参数，可包含 ``api_url`` 属性。

    Returns:
        最终使用的 API URL 字符串，默认为 ``https://api.github.com``。
    """
    return args.api_url or os.getenv("GITHUB_API_URL", "https://api.github.com")


def _resolve_strategy(args: argparse.Namespace) -> RequestedTokenStrategy:
    """从参数或环境变量获取令牌策略。

    Args:
        args: 已解析的命令行参数，可包含 ``strategy`` 属性。

    Returns:
        对应的 :class:`~taolib.github_app.RequestedTokenStrategy` 枚举值。
    """
    raw_value = args.strategy or os.getenv("GITHUB_APP_TOKEN_STRATEGY", "auto")
    return RequestedTokenStrategy(raw_value)
