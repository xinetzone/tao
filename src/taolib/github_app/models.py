from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RequestedTokenStrategy(StrEnum):
    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class EnvironmentKind(StrEnum):
    CLOUD = "cloud"
    GHES = "ghes"
    UNKNOWN = "unknown"


class EffectiveTokenStrategy(StrEnum):
    NONE = "none"
    ENABLED = "enabled"
    DISABLED = "disabled"


class TokenKind(StrEnum):
    STATEFUL = "stateful"
    STATELESS = "stateless"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class GitHubRuntimeProfile:
    base_url: str
    environment: EnvironmentKind


@dataclass(slots=True)
class InstallationTokenRequest:
    installation_id: str
    permissions: dict[str, str]
    repositories: list[str]
    strategy: RequestedTokenStrategy


@dataclass(slots=True)
class InstallationTokenResult:
    token: str
    expires_at: datetime
    token_kind: TokenKind
    requested_strategy: str
    effective_strategy: str
    degraded: bool
