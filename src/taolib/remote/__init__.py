"""远端 SSH 自动化接口集合。

提供 SSH 配置读取/脱敏、prefix 上下文管理与远端探测接口（可注入 connection_factory 便于测试）。
更完整的使用说明见文档：doc/libs/python/Fabric/taolib_remote.md。
"""

from .config import SshConfig, load_ssh_config, redact_ssh_config
from .errors import (
    RemoteConfigError,
    RemoteDependencyError,
    RemoteExecutionError,
)
from .probe import (
    DEFAULT_CONDA_ACTIVATE_CMD,
    DEFAULT_ENCODING,
    DEFAULT_PROBE_CMD,
    DEFAULT_TOOLS_ENV_CMD,
    RemoteProbeCommands,
    RemoteProbeReport,
    RemoteProbeRunOptions,
    RemoteProber,
    probe_remote,
)
from .session import remote_prefixes

__all__ = [
    "DEFAULT_CONDA_ACTIVATE_CMD",
    "DEFAULT_ENCODING",
    "DEFAULT_PROBE_CMD",
    "DEFAULT_TOOLS_ENV_CMD",
    "RemoteConfigError",
    "RemoteDependencyError",
    "RemoteExecutionError",
    "RemoteProbeCommands",
    "RemoteProbeReport",
    "RemoteProbeRunOptions",
    "RemoteProber",
    "SshConfig",
    "load_ssh_config",
    "probe_remote",
    "redact_ssh_config",
    "remote_prefixes",
]
