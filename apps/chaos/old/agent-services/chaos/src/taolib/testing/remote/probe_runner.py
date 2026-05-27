"""远端探测执行器。

默认流程：
1. 连接远端并执行 uname_cmd，验证连接并提取基础信息；
2. 在 prefix( tools_env_cmd + conda_activate_cmd ) 的叠加上下文中：

   - 执行 check_conda_cmd 判断 conda 是否可用；
   - conda 可用时执行 probe_cmd。
"""

import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .connection import (
    ConnectionFactory,
    ConnectionLike,
    RunResult,
    fabric_connection_factory,
)
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


def run_remote_with_retry(
    connection: ConnectionLike,
    command: str,
    retry: int = 0,
    retry_delay: float = 1.0,
    **kwargs: Any,
) -> RunResult:
    """执行远端命令，支持重试机制。

    Args:
        connection: 连接对象。
        command: 要执行的命令。
        retry: 最大重试次数，默认为 0（不重试）。
        retry_delay: 重试间隔时间（秒），默认为 1.0 秒。
        **kwargs: 传递给 connection.run 的其他参数。

    Returns:
        RunResult: 命令执行结果。

    Raises:
        KeyboardInterrupt: 用户中断。
        RemoteExecutionError: 命令执行失败且重试次数耗尽。
    """
    last_exception: Exception | None = None
    attempts = retry + 1

    for attempt in range(attempts):
        try:
            return connection.run(command, **kwargs)
        except KeyboardInterrupt:
            raise
        except ValueError as exc:
            message = str(exc).lower()
            if "closed file" in message:
                raise KeyboardInterrupt from exc
            last_exception = exc
            if attempt < attempts - 1:
                time.sleep(retry_delay)
        except Exception as exc:
            last_exception = exc
            if attempt < attempts - 1:
                time.sleep(retry_delay)

    raise RemoteExecutionError(
        f"命令执行失败，已重试 {retry} 次: {command}",
        command=command,
    ) from last_exception


def run_remote_handling_interrupt(
    connection: ConnectionLike, command: str, **kwargs: Any
) -> RunResult:
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

    connection_factory: ConnectionFactory | None = None
    commands: RemoteProbeCommands = field(default_factory=RemoteProbeCommands)
    options: RemoteProbeRunOptions = field(default_factory=RemoteProbeRunOptions)

    def probe(self, ssh_config: Mapping[str, Any]) -> RemoteProbeReport:
        validate_ssh_config_minimal(ssh_config)
        ssh_kwargs = dict(ssh_config)
        merged_run_kwargs = self.options.merged_run_kwargs()
        retry = self.options.retry
        retry_delay = self.options.retry_delay

        factory = self.connection_factory
        if factory is None or factory is fabric_connection_factory:
            factory = fabric_connection_factory()

        with factory(**ssh_kwargs) as conn:
            uname_result = run_remote_with_retry(
                conn,
                self.commands.uname_cmd,
                retry=retry,
                retry_delay=retry_delay,
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

            with remote_prefixes(
                conn, self.commands.tools_env_cmd, self.commands.conda_activate_cmd
            ):
                combined_probe_cmd = f"{self.commands.check_conda_cmd} >/dev/null 2>&1 || exit 127; {self.commands.probe_cmd}"
                combined_result = run_remote_with_retry(
                    conn,
                    combined_probe_cmd,
                    retry=retry,
                    retry_delay=retry_delay,
                    **{"warn": True, **merged_run_kwargs},
                )
                if getattr(combined_result, "ok", False):
                    return RemoteProbeReport(
                        uname=uname,
                        conda_available=True,
                        probe_attempted=True,
                        probe_ok=True,
                    )

                exited = getattr(combined_result, "exited", None)
                if exited == 127:
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
                if exited is not None:
                    if self.options.raise_on_probe_failure:
                        raise RemoteExecutionError(
                            "探测命令执行失败", command=self.commands.probe_cmd
                        )
                    return RemoteProbeReport(
                        uname=uname,
                        conda_available=True,
                        probe_attempted=True,
                        probe_ok=False,
                    )

                conda_result = run_remote_with_retry(
                    conn,
                    self.commands.check_conda_cmd,
                    retry=retry,
                    retry_delay=retry_delay,
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

                if self.options.raise_on_probe_failure:
                    raise RemoteExecutionError(
                        "探测命令执行失败", command=self.commands.probe_cmd
                    )
                return RemoteProbeReport(
                    uname=uname,
                    conda_available=True,
                    probe_attempted=True,
                    probe_ok=False,
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
    timeout: int | None = None,
    retry: int = 0,
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
        timeout=timeout,
        retry=retry,
    )
    factory = connection_factory or fabric_connection_factory()
    return RemoteProber(
        connection_factory=factory, commands=commands, options=options
    ).probe(ssh_config)
