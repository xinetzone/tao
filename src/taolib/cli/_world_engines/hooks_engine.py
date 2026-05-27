"""Fragment 生命周期钩子执行引擎。

负责在 ``install`` / ``remove`` 等阶段调用 manifest 中声明的 shell 钩子，
统一日志格式与超时 / 异常处理策略。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from taolib.cli._world_engines.manifest_parser import FragmentManifest

DEFAULT_HOOK_TIMEOUT = 60
"""默认单个钩子最大执行时长（秒）。"""


def _emit(message: str) -> None:
    """以统一前缀写入标准输出。

    Args:
        message: 待输出的文本。
    """
    print(message, file=sys.stdout, flush=True)


def run_hook(hook_cmd: str, cwd: Path, timeout: int = DEFAULT_HOOK_TIMEOUT) -> int:
    """执行一条 shell 钩子命令。

    Args:
        hook_cmd: shell 命令字符串。
        cwd: 子进程工作目录。
        timeout: 最大允许的执行时长（秒），超时返回 ``-1``。

    Returns:
        子进程退出码；若发生超时或其他执行异常，则统一返回 ``-1``。
    """
    _emit(f"Running hook: {hook_cmd}")
    try:
        result = subprocess.run(
            hook_cmd,
            shell=True,
            cwd=str(cwd),
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        _emit(f"Warning: hook timed out after {timeout}s: {hook_cmd}")
        return -1
    except (OSError, subprocess.SubprocessError) as exc:
        _emit(f"Warning: hook execution failed: {exc}")
        return -1

    return result.returncode


def execute_lifecycle_hooks(
    manifest: FragmentManifest,
    agents_dir: Path,
    phase: str,
    timeout: int = DEFAULT_HOOK_TIMEOUT,
) -> bool:
    """根据生命周期阶段执行 manifest 中声明的钩子。

    若 ``manifest.hooks`` 中不存在对应 ``phase``，视作成功（无操作）；
    若钩子执行返回非零退出码，则记录警告但不中断主流程。

    Args:
        manifest: 解析后的 Fragment manifest。
        agents_dir: 钩子运行所在目录（通常为目标 ``.agents/``）。
        phase: 生命周期阶段名称，例如 ``"post-install"``、``"pre-remove"``。
        timeout: 钩子执行的最大超时时长（秒）。

    Returns:
        钩子缺省或退出码为 0 时返回 ``True``；否则返回 ``False``，调用方
        可据此决定是否记录额外日志。
    """
    hook_cmd = manifest.hooks.get(phase)
    if not hook_cmd:
        return True

    rc = run_hook(hook_cmd, agents_dir, timeout=timeout)
    if rc == 0:
        _emit(f"Hook '{phase}' completed successfully.")
        return True

    _emit(f"Hook '{phase}' exited with code {rc}, continuing...")
    return False
