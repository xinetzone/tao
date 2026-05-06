"""工作区生命周期钩子。

通过 asyncio 子进程执行钩子脚本，支持超时控制，
防止编排器因挂起的钩子而阻塞。
"""

import asyncio
from pathlib import Path

from ..errors import HookError

__all__ = ["HookTimeoutError", "run_hook"]


class HookTimeoutError(HookError):
    """钩子脚本执行超时。"""


async def run_hook(script: str, cwd: Path, timeout_ms: int) -> int:
    """执行钩子脚本，超时则终止。

    在指定工作目录中以 shell 方式执行脚本，
    捕获 stdout/stderr 用于错误报告。

    Args:
        script: 要执行的 shell 命令。
        cwd: 工作目录。
        timeout_ms: 超时毫秒数。

    Returns:
        进程退出码。

    Raises:
        HookTimeoutError: 执行超时。
        HookError: 脚本返回非零退出码。
    """
    proc = await asyncio.create_subprocess_shell(
        script,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        await asyncio.wait_for(proc.wait(), timeout=timeout_ms / 1000)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise HookTimeoutError(f"Hook timed out after {timeout_ms}ms") from None

    if proc.returncode != 0:
        stdout = (await proc.stdout.read()).decode(errors="replace") if proc.stdout else ""
        stderr = (await proc.stderr.read()).decode(errors="replace") if proc.stderr else ""
        msg = (
            f"Hook exited with code {proc.returncode}\n"
            f"  command: {script}\n"
            f"  stdout: {stdout[:500]}\n"
            f"  stderr: {stderr[:500]}"
        )
        raise HookError(msg)

    return proc.returncode
