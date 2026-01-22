"""远端探测接口（uname -> conda 检查 -> 探测命令）。

该模块提供兼容接口 `probe_remote`，并暴露默认命令常量。
更可扩展的用法可以直接使用 `RemoteProber`、`RemoteProbeCommands` 与 `RemoteProbeRunOptions`。
"""
from collections.abc import Mapping
from typing import Any

from .connection import ConnectionFactory
from .probe_models import (
    DEFAULT_CONDA_ACTIVATE_CMD,
    DEFAULT_ENCODING,
    DEFAULT_PROBE_CMD,
    DEFAULT_TOOLS_ENV_CMD,
    RemoteProbeCommands,
    RemoteProbeReport,
    RemoteProbeRunOptions,
)
from .probe_runner import RemoteProber, probe_remote as _probe_remote_compat


def probe_remote(
    ssh_config: Mapping[str, Any],
    *,
    tools_env_cmd: str = DEFAULT_TOOLS_ENV_CMD,
    conda_activate_cmd: str = DEFAULT_CONDA_ACTIVATE_CMD,
    probe_cmd: str = DEFAULT_PROBE_CMD,
    encoding: str = DEFAULT_ENCODING,
    check_conda_cmd: str = "command -v conda",
    uname_cmd: str = "uname -a",
    connection_factory: ConnectionFactory | None = None,
    run_kwargs: Mapping[str, Any] | None = None,
    raise_on_conda_missing: bool = False,
    raise_on_probe_failure: bool = False,
) -> RemoteProbeReport:
    """兼容接口：连接远端并执行探测命令，返回结构化结果。"""

    return _probe_remote_compat(
        ssh_config,
        tools_env_cmd=tools_env_cmd,
        conda_activate_cmd=conda_activate_cmd,
        probe_cmd=probe_cmd,
        encoding=encoding,
        check_conda_cmd=check_conda_cmd,
        uname_cmd=uname_cmd,
        connection_factory=connection_factory,
        run_kwargs=run_kwargs,
        raise_on_conda_missing=raise_on_conda_missing,
        raise_on_probe_failure=raise_on_probe_failure,
    )


__all__ = [
    "DEFAULT_CONDA_ACTIVATE_CMD",
    "DEFAULT_ENCODING",
    "DEFAULT_PROBE_CMD",
    "DEFAULT_TOOLS_ENV_CMD",
    "RemoteProbeCommands",
    "RemoteProbeReport",
    "RemoteProbeRunOptions",
    "RemoteProber",
    "probe_remote",
]
