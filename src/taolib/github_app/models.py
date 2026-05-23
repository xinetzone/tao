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
    """

    AUTO = "auto"
    """根据运行环境自动选择，不主动下发 ``X-GitHub-Stateless-S2S-Token`` 头。"""

    ENABLED = "enabled"
    """主动请求启用无状态 S2S 令牌。"""

    DISABLED = "disabled"
    """主动请求禁用无状态 S2S 令牌。"""


class EnvironmentKind(StrEnum):
    """GitHub API 运行环境类型。

    识别规则由 API 基地址判定：

    - ``api_url == "https://api.github.com"`` → :attr:`CLOUD`
    - ``api_url`` 以 ``/api/v3`` 结尾 → :attr:`GHES`
    - 其他 → :attr:`UNKNOWN`
    """

    CLOUD = "cloud"
    """GitHub.com 公有云。"""

    GHES = "ghes"
    """GitHub Enterprise Server 私部署。"""

    UNKNOWN = "unknown"
    """未识别的环境。"""


class EffectiveTokenStrategy(StrEnum):
    """结合环境与调用方意图后实际生效的策略。"""

    NONE = "none"
    """不发送 ``X-GitHub-Stateless-S2S-Token`` 头。"""

    ENABLED = "enabled"
    """发送 ``X-GitHub-Stateless-S2S-Token: enabled``。"""

    DISABLED = "disabled"
    """发送 ``X-GitHub-Stateless-S2S-Token: disabled``。"""


class TokenKind(StrEnum):
    """GitHub App 安装令牌的类型。

    由 :meth:`taolib.github_app.client.GitHubAppClient.classify_token_kind`
    根据令牌字符串的前缀与结构特征判定。
    """

    STATEFUL = "stateful"
    """有状态令牌（``ghs_`` 开头但不含两个 ``.``）。"""

    STATELESS = "stateless"
    """无状态令牌（``ghs_`` 开头且后缀含恰好两个 ``.``）。"""

    UNKNOWN = "unknown"
    """未能识别的令牌。"""


@dataclass(slots=True)
class GitHubRuntimeProfile:
    """GitHub API 运行时环境画像。"""

    base_url: str
    """GitHub API 基地址（标准化后去除尾部斜杠）。"""

    environment: EnvironmentKind
    """根据 ``base_url`` 推断出的环境类型。"""


@dataclass(slots=True)
class InstallationTokenRequest:
    """调用方传入令牌管理器的请求参数。"""

    installation_id: str
    """GitHub App 安装实例 ID。"""

    permissions: dict[str, str]
    """限定令牌能力的权限映射，空字典表示默认权限。"""

    repositories: list[str]
    """限定令牌可访问的仓库列表，空列表表示不限定。"""

    strategy: RequestedTokenStrategy
    """调用方期望的 Token 策略。"""


@dataclass(slots=True)
class InstallationTokenResult:
    """令牌管理器返回给调用方的令牌结果。"""

    token: str
    """安装令牌明文。"""

    expires_at: datetime
    """令牌过期时间（UTC）。"""

    token_kind: TokenKind
    """令牌类型判定结果。"""

    requested_strategy: str
    """调用方原始请求的策略值。"""

    effective_strategy: str
    """实际生效的策略值。"""

    degraded: bool
    """是否因环境约束发生了策略降级。"""
