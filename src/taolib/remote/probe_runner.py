"""远端探测执行器。

默认流程：
1. 连接远端并执行 uname_cmd，验证连接并提取基础信息；
2. 在 prefix( tools_env_cmd + conda_activate_cmd ) 的叠加上下文中：

   - 执行 check_conda_cmd 判断 conda 是否可用；
   - conda 可用时执行 probe_cmd。
"""
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .connection import ConnectionFactory, ConnectionLike, RunResult, fabric_connection_factory
from .errors import RemoteConfigError, RemoteExecutionError
from .probe_models import RemoteProbeCommands, RemoteProbeReport, RemoteProbeRunOptions
from .session import remote_prefixes


def validate_ssh_config_minimal(ssh_config: Mapping[str, Any]) -> None:
    """校验最小可用 SSH 配置。

    该校验仅保证能建立最基础的 SSH 连接：
    - host: 非空字符串
    - user: 非空字符串
    """

    host = ssh_config.get("host")
    user = ssh_config.get("user")
    if not isinstance(host, str) or not host.strip():
        raise RemoteConfigError("SSH 配置缺少 host")
    if not isinstance(user, str) or not user.strip():
        raise RemoteConfigError("SSH 配置缺少 user")


def run_remote_handling_interrupt(connection: ConnectionLike, command: str, **kwargs: Any) -> RunResult:
    """执行远端命令并尽可能将 Windows 下的中断异常归一化为 KeyboardInterrupt。

    某些 Windows 终端场景下，中断可能以 `ValueError: I/O operation on closed file` 形式抛出。
    为保持调用侧统一处理逻辑，这里将其映射为 KeyboardInterrupt。
    """

    try:
        return connection.run(command, **kwargs)
    except KeyboardInterrupt:
        raise
    except ValueError as exc:
        message = str(exc).lower()
        if "closed file" in message:
            raise KeyboardInterrupt from exc
        raise


@dataclass(frozen=True, slots=True)
class RemoteProber:
    """远端探测执行器（可注入连接工厂，便于测试与扩展）。"""

    connection_factory: ConnectionFactory
    commands: RemoteProbeCommands = RemoteProbeCommands()
    options: RemoteProbeRunOptions = RemoteProbeRunOptions()

    def probe(self, ssh_config: Mapping[str, Any]) -> RemoteProbeReport:
        validate_ssh_config_minimal(ssh_config)
        ssh_kwargs = dict(ssh_config)
        merged_run_kwargs = self.options.merged_run_kwargs()

        with self.connection_factory(**ssh_kwargs) as conn:
            uname_result = run_remote_handling_interrupt(
                conn,
                self.commands.uname_cmd,
                **{"hide": True, **merged_run_kwargs},
            )
            if not bool(getattr(uname_result, "ok", False)):
                raise RemoteExecutionError(
                    "uname 执行失败，可能连接失败或命令错误",
                    command=self.commands.uname_cmd,
                )
            uname = (getattr(uname_result, "stdout", "") or "").strip()
            if not uname:
                raise RemoteExecutionError(
                    "uname 输出为空，可能连接失败或命令未执行",
                    command=self.commands.uname_cmd,
                )

            with remote_prefixes(conn, self.commands.tools_env_cmd, self.commands.conda_activate_cmd):
                conda_result = run_remote_handling_interrupt(
                    conn,
                    self.commands.check_conda_cmd,
                    **{"warn": True, "hide": True, **merged_run_kwargs},
                )
                if not getattr(conda_result, "ok", False):
                    if self.options.raise_on_conda_missing:
                        raise RemoteExecutionError(
                            "conda 不可用或未找到",
                            command=self.commands.check_conda_cmd,
                        )
                    return RemoteProbeReport(
                        uname=uname,
                        conda_available=False,
                        probe_attempted=False,
                        probe_ok=None,
                    )

                probe_result = run_remote_handling_interrupt(
                    conn,
                    self.commands.probe_cmd,
                    **{"warn": True, **merged_run_kwargs},
                )
                if self.options.raise_on_probe_failure and not getattr(probe_result, "ok", False):
                    raise RemoteExecutionError("探测命令执行失败", command=self.commands.probe_cmd)
                return RemoteProbeReport(
                    uname=uname,
                    conda_available=True,
                    probe_attempted=True,
                    probe_ok=bool(getattr(probe_result, "ok", False)),
                )


def probe_remote(
    ssh_config: Mapping[str, Any],
    *,
    tools_env_cmd: str,
    conda_activate_cmd: str,
    probe_cmd: str,
    encoding: str,
    check_conda_cmd: str,
    uname_cmd: str,
    connection_factory: ConnectionFactory | None,
    run_kwargs: Mapping[str, Any] | None,
    raise_on_conda_missing: bool,
    raise_on_probe_failure: bool,
) -> RemoteProbeReport:
    """兼容接口：连接远端并执行探测命令，返回结构化结果。

    该函数保持既有 `taolib.remote.probe.probe_remote` 形态不变。
    更推荐的扩展方式是直接使用 RemoteProber，并通过 RemoteProbeCommands/RemoteProbeRunOptions 注入自定义行为。
    """

    commands = RemoteProbeCommands(
        tools_env_cmd=tools_env_cmd,
        conda_activate_cmd=conda_activate_cmd,
        probe_cmd=probe_cmd,
        check_conda_cmd=check_conda_cmd,
        uname_cmd=uname_cmd,
    )
    options = RemoteProbeRunOptions(
        encoding=encoding,
        run_kwargs=run_kwargs,
        raise_on_conda_missing=raise_on_conda_missing,
        raise_on_probe_failure=raise_on_probe_failure,
    )
    factory = connection_factory or fabric_connection_factory()
    return RemoteProber(connection_factory=factory, commands=commands, options=options).probe(ssh_config)
