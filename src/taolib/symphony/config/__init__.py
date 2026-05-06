"""Symphony 配置子包。

提供工作流加载、配置模型、TOML 解析、配置合并与文件监视功能。

使用方式：

    from taolib.symphony.config import (
        WorkflowDefinition,
        load_workflow,
        SymphonyConfig,
        resolve_config,
        WorkflowWatcher,
    )
"""

from taolib.symphony.config.loader import WorkflowDefinition, load_workflow
from taolib.symphony.config.resolver import (
    deep_merge,
    resolve_config,
    resolve_env_vars,
    resolve_paths,
)
from taolib.symphony.config.schema import (
    AgentConfig,
    CodexConfig,
    HooksConfig,
    PollingConfig,
    ServerConfig,
    SymphonyConfig,
    TrackerConfig,
    WorkerConfig,
    WorkspaceConfig,
)
from taolib.symphony.config.toml_config import load_toml
from taolib.symphony.config.watcher import WorkflowWatcher

__all__ = [
    # Loader
    "WorkflowDefinition",
    "load_workflow",
    # Schema
    "TrackerConfig",
    "PollingConfig",
    "WorkspaceConfig",
    "HooksConfig",
    "AgentConfig",
    "CodexConfig",
    "WorkerConfig",
    "ServerConfig",
    "SymphonyConfig",
    # TOML
    "load_toml",
    # Resolver
    "deep_merge",
    "resolve_env_vars",
    "resolve_paths",
    "resolve_config",
    # Watcher
    "WorkflowWatcher",
]
