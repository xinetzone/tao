"""远端探测模型与可配置项。

该模块专注于“数据与配置”，不包含任何网络/远端执行逻辑，便于复用与测试。
"""
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

DEFAULT_TOOLS_ENV_CMD = os.environ.get("TAOLIB_REMOTE_TOOLS_ENV_CMD", ":")
DEFAULT_CONDA_ACTIVATE_CMD = os.environ.get("TAOLIB_REMOTE_CONDA_ACTIVATE_CMD", ":")
DEFAULT_PROBE_CMD = os.environ.get("TAOLIB_REMOTE_PROBE_CMD", "python -V")
DEFAULT_ENCODING = os.environ.get("TAOLIB_REMOTE_ENCODING", "utf-8")


@dataclass(frozen=True, slots=True)
class RemoteProbeReport:
    """远端探测结果。

    语义约定：
    - conda_available=False 时，不会尝试执行 probe_cmd（probe_attempted=False, probe_ok=None）。
    - conda_available=True 且 probe_attempted=True 时，probe_ok 表示探测命令退出状态是否成功。
    """

    uname: str
    conda_available: bool
    probe_attempted: bool
    probe_ok: bool | None


@dataclass(frozen=True, slots=True)
class RemoteProbeCommands:
    """远端探测使用的命令集合。

    命令分为两类：
    - prefix 命令：tools_env_cmd、conda_activate_cmd，会在同一执行上下文中叠加生效；
    - 常规命令：uname_cmd、check_conda_cmd、probe_cmd，会在远端依次运行。
    """

    tools_env_cmd: str = DEFAULT_TOOLS_ENV_CMD
    conda_activate_cmd: str = DEFAULT_CONDA_ACTIVATE_CMD
    probe_cmd: str = DEFAULT_PROBE_CMD
    check_conda_cmd: str = "command -v conda"
    uname_cmd: str = "uname -a"


@dataclass(frozen=True, slots=True)
class RemoteProbeRunOptions:
    """远端命令执行选项与错误处理策略。

    encoding 与 run_kwargs 会被合并用于 Connection.run(...)。
    raise_on_* 用于控制缺少 conda 或 probe 失败时，是返回结构化结果还是抛出异常。
    """

    encoding: str = DEFAULT_ENCODING
    run_kwargs: Mapping[str, Any] | None = None
    raise_on_conda_missing: bool = False
    raise_on_probe_failure: bool = False

    def merged_run_kwargs(self) -> dict[str, Any]:
        merged: dict[str, Any] = {"encoding": self.encoding}
        if self.run_kwargs:
            merged.update(dict(self.run_kwargs))
        return merged
