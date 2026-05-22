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
    normalized = api_url.rstrip("/")
    if normalized == "https://api.github.com":
        return EnvironmentKind.CLOUD
    if normalized.endswith("/api/v3"):
        return EnvironmentKind.GHES
    return EnvironmentKind.UNKNOWN


def _parse_bool(raw_value: str, *, default: bool) -> bool:
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(slots=True)
class GitHubAppSettings:
    app_id: str
    installation_id: str
    private_key: str
    api_url: str
    default_strategy: RequestedTokenStrategy
    eager_refresh_seconds: int
    allow_header_fallback: bool
    runtime_profile: GitHubRuntimeProfile

    @classmethod
    def from_env(cls) -> "GitHubAppSettings":
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
