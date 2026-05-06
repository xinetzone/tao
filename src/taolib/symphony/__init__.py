"""Symphony 编排服务模块。

长期运行的编排服务，轮询 Linear 问题跟踪器，
为每个活跃问题创建隔离工作区并运行 Codex app-server 会话。

使用方式：

    from taolib.symphony import SymphonyConfig, Orchestrator
    from taolib.symphony.cli import app as cli_app
"""

from taolib.symphony.config.schema import SymphonyConfig
from taolib.symphony.errors import (
    AgentError,
    ConfigError,
    HookError,
    PromptError,
    SymphonyError,
    TrackerError,
    TransportError,
    WorkflowLoadError,
    WorkspaceError,
)

__version__ = "0.1.0"

__all__ = [
    # 版本
    "__version__",
    # 异常
    "SymphonyError",
    "ConfigError",
    "WorkflowLoadError",
    "TrackerError",
    "WorkspaceError",
    "AgentError",
    "HookError",
    "TransportError",
    "PromptError",
    # 配置
    "SymphonyConfig",
]
