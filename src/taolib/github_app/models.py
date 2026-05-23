"""GitHub App 模块的核心枚举与数据模型。

本模块集中定义 GitHub App 安装令牌请求与运行时环境拏描所需的不变量类型，
是配置、客户端、缓存与管理器之间流动的公共词汇表。
保持本文件“零依赖、零副作用”：仅 dataclass 与枚举，无运行时逻辑。
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RequestedTokenStrategy(StrEnum):
    """调用方请求安装令牌时表达的策略意图。

    该枚举反映调用方的愿望，是否应用最终取决于运行环境，参见
    :class:`EffectiveTokenStrategy`。

    Attributes:
        AUTO: 根据运行环境自动选择，不主动下发 ``X-GitHub-Stateless-S2S-Token`` 头。
        ENABLED: 主动请求启用无状态 S2S 令牌。
        DISABLED: 主动请求禁用无状态 S2S 令牌。
    """

    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class EnvironmentKind(StrEnum):
    """GitHub API 运行环境类型。

    识别规则由 API 基地址判定：

    - ``api_url == "https://api.github.com"`` → :attr:`CLOUD`
    - ``api_url`` 以 ``/api/v3`` 结尾 → :attr:`GHES`
    - 其他 → :attr:`UNKNOWN`

    Attributes:
        CLOUD: GitHub.com 公有云。
        GHES: GitHub Enterprise Server 私部署。
        UNKNOWN: 未识别的环境。
    """

    CLOUD = "cloud"
    GHES = "ghes"
    UNKNOWN = "unknown"


class EffectiveTokenStrategy(StrEnum):
    """结合环境与调用方意图后实际生效的策略。

    Attributes:
        NONE: 不发送 ``X-GitHub-Stateless-S2S-Token`` 头。
        ENABLED: 发送 ``X-GitHub-Stateless-S2S-Token: enabled``。
        DISABLED: 发送 ``X-GitHub-Stateless-S2S-Token: disabled``。
    """

    NONE = "none"
    ENABLED = "enabled"
    DISABLED = "disabled"


class TokenKind(StrEnum):
    """GitHub App 安装令牌的类型。

    由 :meth:`taolib.github_app.client.GitHubAppClient.classify_token_kind`
    根据令牌字符串的前缀与结构特征判定。

    Attributes:
        STATEFUL: 有状态令牌（``ghs_`` 开头但不含两个 ``.``）。
        STATELESS: 无状态令牌（``ghs_`` 开头且后缀含恰好两个 ``.``）。
        UNKNOWN: 未能识别的令牌。
    """

    STATEFUL = "stateful"
    STATELESS = "stateless"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class GitHubRuntimeProfile:
    """GitHub API 运行时环境画像。

    Attributes:
        base_url: GitHub API 基地址（标准化后去除尾部斜杠）。
        environment: 根据 ``base_url`` 推断出的环境类型。
    """

    base_url: str
    environment: EnvironmentKind


@dataclass(slots=True)
class InstallationTokenRequest:
    """调用方传入令牌管理器的请求参数。

    Attributes:
        installation_id: GitHub App 安装实例 ID。
        permissions: 限定令牌能力的权限映射，空字典表示默认权限。
        repositories: 限定令牌可访问的仓库列表，空列表表示不限定。
        strategy: 调用方期望的 Token 策略。
    """

    installation_id: str
    permissions: dict[str, str]
    repositories: list[str]
    strategy: RequestedTokenStrategy


@dataclass(slots=True)
class InstallationTokenResult:
    """令牌管理器返回给调用方的令牌结果。

    Attributes:
        token: 安装令牌明文。
        expires_at: 令牌过期时间（UTC）。
        token_kind: 令牌类型判定结果。
        requested_strategy: 调用方原始请求的策略值。
        effective_strategy: 实际生效的策略值。
        degraded: 是否因环境约束发生了策略降级。
    """

    token: str
    expires_at: datetime
    token_kind: TokenKind
    requested_strategy: str
    effective_strategy: str
    degraded: bool
