"""传输层抽象。

定义智能体进程启动和钩子执行的传输接口，
并提供本地（LocalTransport）和 SSH（SSHTransport）两种实现。
"""

import asyncio
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass

import asyncssh

__all__ = ["AgentProcess", "AgentTransport", "LocalTransport", "SSHTransport"]


@dataclass
class AgentProcess:
    """智能体子进程的 I/O 句柄。"""

    stdin: asyncio.StreamWriter
    stdout: asyncio.StreamReader
    stderr: asyncio.StreamReader
    pid: str | None = None


class AgentTransport(ABC):
    """传输层抽象基类。

    定义启动智能体进程和执行钩子脚本的接口，
    使编排器可与本地或远程执行环境解耦。
    """

    @abstractmethod
    async def start_process(self, command: str, cwd: str) -> AgentProcess:
        """启动智能体进程。

        Args:
            command: 要执行的命令。
            cwd: 工作目录。

        Returns:
            进程 I/O 句柄。
        """

    @abstractmethod
    async def run_hook(self, script: str, cwd: str, timeout_ms: int) -> int:
        """执行钩子脚本。

        Args:
            script: Shell 命令。
            cwd: 工作目录。
            timeout_ms: 超时毫秒数。

        Returns:
            进程退出码。
        """


class LocalTransport(AgentTransport):
    """本地传输实现。

    在本机以 asyncio 子进程方式启动智能体和执行钩子。
    """

    async def start_process(self, command: str, cwd: str) -> AgentProcess:
        """在本机启动子进程。"""
        proc = await asyncio.create_subprocess_exec(
            "bash",
            "-lc",
            command,
            cwd=cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return AgentProcess(
            stdin=proc.stdin,
            stdout=proc.stdout,
            stderr=proc.stderr,
            pid=str(proc.pid),
        )

    async def run_hook(self, script: str, cwd: str, timeout_ms: int) -> int:
        """在本机执行钩子脚本。"""
        proc = await asyncio.create_subprocess_shell(
            script,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout_ms / 1000)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        return proc.returncode


class SSHTransport(AgentTransport):
    """SSH 远程传输实现。

    通过 asyncssh 连接远程主机，在远端启动智能体进程和执行钩子。
    使用前必须先调用 ``connect()`` 建立连接。
    """

    def __init__(self, host: str, **ssh_opts: object) -> None:
        self._host = host
        self._ssh_opts = ssh_opts
        self._conn: asyncssh.SSHClientConnection | None = None

    async def connect(self) -> None:
        """建立 SSH 连接。"""
        self._conn = await asyncssh.connect(self._host, **self._ssh_opts)

    async def start_process(self, command: str, cwd: str) -> AgentProcess:
        """在远程主机启动子进程。"""
        if self._conn is None:
            msg = "SSH 连接未建立，请先调用 connect()"
            raise RuntimeError(msg)
        full_cmd = f"cd {shlex.quote(cwd)} && bash -lc {shlex.quote(command)}"
        process = await self._conn.create_process(full_cmd)
        return AgentProcess(
            stdin=process.stdin,
            stdout=process.stdout,
            stderr=process.stderr,
        )

    async def run_hook(self, script: str, cwd: str, timeout_ms: int) -> int:
        """在远程主机执行钩子脚本。"""
        if self._conn is None:
            msg = "SSH 连接未建立，请先调用 connect()"
            raise RuntimeError(msg)
        full_cmd = f"cd {shlex.quote(cwd)} && bash -lc {shlex.quote(script)}"
        process = await self._conn.create_process(full_cmd)
        try:
            result = await asyncio.wait_for(process.wait(), timeout=timeout_ms / 1000)
        except TimeoutError:
            process.close()
            raise
        return result.exit_status

    async def disconnect(self) -> None:
        """关闭 SSH 连接。"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
