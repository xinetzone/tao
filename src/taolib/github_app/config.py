"""GitHub App 运行时配置。

本模块提供从环境变量加载配置的一站式入口，是 CLI、客户端与令牌管理器
共享的唯一事实来源。调用方应优先使用 :meth:`GitHubAppSettings.from_env`
构造实例，避免手工拼装造成不一致。
"""

import os
from dataclasses import dataclass
from pathlib import Path

from taolib.github_app.errors import GitHubAppConfigurationError
from taolib.github_app.models import (
    EnvironmentKind,
    GitHubRuntimeProfile,
    RequestedTokenStrategy,
)


def _detect_environment(api_url: str) -> EnvironmentKind:
    """根据 API 基地址推断 GitHub 运行环境。

    Args:
        api_url: GitHub API 基地址，允许带有尾部斜杠。

    Returns:
        匹配到的 :class:`EnvironmentKind`，未能识别时返回
        :attr:`EnvironmentKind.UNKNOWN`。
    """
    normalized = api_url.rstrip("/")
    if normalized == "https://api.github.com":
        return EnvironmentKind.CLOUD
    if normalized.endswith("/api/v3"):
        return EnvironmentKind.GHES
    return EnvironmentKind.UNKNOWN


def _parse_bool(raw_value: str, *, default: bool) -> bool:
    """宽容地解析环境变量中的布尔表达。

    Args:
        raw_value: 原始字符串（容忍大小写与首尾空格）。
        default: 无法识别时采用的默认值。

    Returns:
        解析后的布尔值。``1/true/yes/on`` 为真，``0/false/no/off`` 为假，
        其他返回 ``default``。
    """
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(slots=True)
class GitHubAppSettings:
    """GitHub App 的全局配置聚合。

    本类是 GitHub App 子模块各组件（客户端、令牌管理器、CLI）
    读取运行时参数的唯一源头，推荐通过 :meth:`from_env` 加载。

    Attributes:
        app_id: GitHub App 的 App ID。
        installation_id: 默认的安装实例 ID。
        private_key: PEM 格式的 RSA 私钥内容。
        api_url: GitHub API 基地址（未去除尾部斜杠，严格以环境变量输入为准）。
        default_strategy: 默认的 Token 策略。
        eager_refresh_seconds: 令牌过期前提前刷新的秒数。
        allow_header_fallback: 是否允许在环境不支持覆盖头时降级使用默认行为。
        runtime_profile: 运行时环境画像。
    """

    app_id: str
    installation_id: str
    private_key: str
    api_url: str
    default_strategy: RequestedTokenStrategy
    eager_refresh_seconds: int
    allow_header_fallback: bool
    runtime_profile: GitHubRuntimeProfile

    @classmethod
    def from_env(cls) -> GitHubAppSettings:
        """从操作系统环境变量读取配置并构造实例。

        支持的环境变量：

        - ``GITHUB_APP_ID``（必填）：App ID。
        - ``GITHUB_APP_INSTALLATION_ID``（必填）：安装实例 ID。
        - ``GITHUB_APP_PRIVATE_KEY`` / ``GITHUB_APP_PRIVATE_KEY_FILE``（二选一）：
          私钥内容或私钥文件路径。
        - ``GITHUB_API_URL``（默认 ``https://api.github.com``）：API 基地址。
        - ``GITHUB_APP_TOKEN_STRATEGY``（默认 ``auto``）：默认策略，
          取值 ``auto`` / ``enabled`` / ``disabled``。
        - ``GITHUB_APP_TOKEN_EAGER_REFRESH_SECONDS``（默认 ``90``）：
          提前刷新秒数。
        - ``GITHUB_APP_ALLOW_HEADER_FALLBACK``（默认 ``true``）：
          是否允许环境不支持覆盖头时降级。

        Returns:
            根据环境变量构造的 :class:`GitHubAppSettings` 实例。

        Raises:
            GitHubAppConfigurationError: 私钥既未通过环境变量传入，也未通过
                ``GITHUB_APP_PRIVATE_KEY_FILE`` 指向可读取的文件路径。
        """
        private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
        private_key_file = os.getenv("GITHUB_APP_PRIVATE_KEY_FILE")

        if not private_key and private_key_file:
            private_key = Path(private_key_file).read_text(encoding="utf-8")

        if not private_key:
            raise GitHubAppConfigurationError("GitHub App private key is required.")

        api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        runtime_profile = GitHubRuntimeProfile(
            base_url=api_url,
            environment=_detect_environment(api_url),
        )

        return cls(
            app_id=os.environ["GITHUB_APP_ID"],
            installation_id=os.environ["GITHUB_APP_INSTALLATION_ID"],
            private_key=private_key,
            api_url=api_url,
            default_strategy=RequestedTokenStrategy(
                os.getenv("GITHUB_APP_TOKEN_STRATEGY", "auto")
            ),
            eager_refresh_seconds=int(
                os.getenv("GITHUB_APP_TOKEN_EAGER_REFRESH_SECONDS", "90")
            ),
            allow_header_fallback=_parse_bool(
                os.getenv("GITHUB_APP_ALLOW_HEADER_FALLBACK", "true"),
                default=True,
            ),
            runtime_profile=runtime_profile,
        )
