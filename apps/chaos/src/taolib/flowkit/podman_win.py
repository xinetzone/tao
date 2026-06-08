"""Podman Python SDK Windows 适配层.

通过 SSH TCP 隧道方式在 Windows 上使用 PodmanPy 连接 podman machine。
核心思路：ssh -L PORT:/run/user/1000/podman/podman.sock 将 VM 内
Unix socket 转发为本地 TCP 端口，然后使用 tcp:// scheme 连接。

使用方式:
    from taolib.flowkit.podman_win import PodmanSSHClient, quick_client

    # 方式1: context manager（推荐，自动管理隧道生命周期）
    with PodmanSSHClient() as client:
        if client.ping():
            images = client.images.list()

    # 方式2: 快速获取
    client = quick_client()
    containers = client.containers.list(all=True)
    client.close()

运行环境: Windows + Python 3.10+ + podman>=5.8.0 + OpenSSH
"""
from __future__ import annotations

import atexit
import json
import socket
import subprocess
import time
from typing import Optional


# ── 读取 podman machine 配置 ──────────────────────────────────────────

def _get_machine_config(name: str = "podman-machine-default") -> dict:
    result = subprocess.run(
        ["podman", "machine", "inspect", name],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"podman machine inspect 失败: {result.stderr}")
    machines = json.loads(result.stdout)
    if not machines:
        raise RuntimeError(f"未找到 podman machine: {name}")
    return machines[0]


# ── SSH TCP 隧道 ─────────────────────────────────────────────────────

class SSHTunnel:
    """通过 SSH 建立 TCP → podman socket 的隧道."""

    _instances: list[SSHTunnel] = []

    @classmethod
    def _cleanup_all(cls):
        for t in cls._instances:
            t.stop()

    def __init__(
        self,
        ssh_port: int = 49376,
        ssh_user: str = "user",
        ssh_identity: str = "",
        remote_socket: str = "/run/user/1000/podman/podman.sock",
        local_port: int = 0,  # 0 = 自动分配
    ):
        self._ssh_port = ssh_port
        self._ssh_user = ssh_user
        self._ssh_identity = ssh_identity
        self._remote_socket = remote_socket
        self._local_port = local_port
        self._proc: Optional[subprocess.Popen] = None
        self._instances.append(self)

    def start(self) -> int:
        """启动 SSH 隧道，返回本地端口号."""
        if self._proc is not None:
            return self._local_port

        # 自动分配端口
        if self._local_port == 0:
            self._local_port = self._find_free_port()

        cmd = [
            "ssh", "-N",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ExitOnForwardFailure=yes",
            "-L", f"{self._local_port}:{self._remote_socket}",
            "-p", str(self._ssh_port),
            "-i", self._ssh_identity,
            f"{self._ssh_user}@localhost",
        ]

        # 尝试 Unix socket 转发；如果 OpenSSH 不支持，
        # 则降级为通过 SSH 在 machine 内启动 TCP 服务
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            # 等待隧道就绪
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                time.sleep(0.3)
                if self._proc.poll() is not None:
                    break  # 进程已退出，降级尝试
                try:
                    s = socket.create_connection(
                        ("localhost", self._local_port), timeout=1
                    )
                    s.close()
                    return self._local_port
                except (OSError, ConnectionRefusedError):
                    continue

            # 初次尝试失败，清理并降级
            self._proc.terminate()
            self._proc.wait()
            self._proc = None

        except FileNotFoundError:
            pass  # ssh 命令不可用

        # 降级方案：通过 SSH 在 machine 内启动 podman system service tcp
        return self._start_fallback()

    def _start_fallback(self) -> int:
        """降级方案：通过 SSH 在 machine 内部启动 TCP 服务."""
        if self._local_port == 0:
            self._local_port = self._find_free_port()

        # 在 machine 内启动 podman API 监听 TCP
        remote_cmd = (
            f"nohup podman system service --time=0 tcp:0.0.0.0:{self._local_port} "
            f">/dev/null 2>&1 &"
        )
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-p", str(self._ssh_port),
            "-i", self._ssh_identity,
            f"{self._ssh_user}@localhost",
            remote_cmd,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # 建立 TCP 转发
        forward_cmd = [
            "ssh", "-N",
            "-o", "StrictHostKeyChecking=no",
            "-L", f"{self._local_port}:localhost:{self._local_port}",
            "-p", str(self._ssh_port),
            "-i", self._ssh_identity,
            f"{self._ssh_user}@localhost",
        ]
        self._proc = subprocess.Popen(
            forward_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # 等待就绪
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            time.sleep(0.5)
            if self._proc.poll() is not None:
                raise RuntimeError("SSH 隧道进程意外退出")
            try:
                s = socket.create_connection(
                    ("localhost", self._local_port), timeout=1
                )
                s.close()
                return self._local_port
            except (OSError, ConnectionRefusedError):
                continue

        raise RuntimeError("SSH 隧道启动超时")

    def stop(self):
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @property
    def port(self) -> int:
        return self._local_port


atexit.register(SSHTunnel._cleanup_all)


# ── 便捷客户端 ────────────────────────────────────────────────────────

class PodmanSSHClient:
    """自动管理 SSH 隧道 + PodmanClient 的便捷包装.

    读取 podman machine inspect 获取 SSH 配置，自动建立隧道，
    支持 context manager 协议。

    Example:
        with PodmanSSHClient() as client:
            if client.ping():
                images = client.images.list()
    """

    def __init__(
        self,
        machine_name: str = "podman-machine-default",
        local_port: int = 0,
        **kwargs,
    ):
        cfg = _get_machine_config(machine_name)
        ssh = cfg["SSHConfig"]

        self._tunnel = SSHTunnel(
            ssh_port=ssh["Port"],
            ssh_user=ssh["RemoteUsername"],
            ssh_identity=ssh["IdentityPath"],
            local_port=local_port,
        )
        self._port = self._tunnel.start()
        self._base_url = f"tcp://localhost:{self._port}"
        self._kwargs = kwargs

        self._client = None

    def __enter__(self):
        from podman import PodmanClient
        self._client = PodmanClient(base_url=self._base_url, **self._kwargs)
        return self._client

    def __exit__(self, *args):
        if self._client:
            self._client.close()
        self._tunnel.stop()

    def client(self):
        """返回 PodmanClient 实例（需手动 close）."""
        from podman import PodmanClient
        self._client = PodmanClient(base_url=self._base_url, **self._kwargs)
        return self._client


# ── 快速入口 ──────────────────────────────────────────────────────────

def quick_client(machine_name: str = "podman-machine-default", **kwargs):
    """快速创建带 SSH 隧道的 PodmanClient.

    Args:
        machine_name: podman machine 名称
        **kwargs: 传递给 PodmanClient 的额外参数

    Returns:
        PodmanClient 实例（需手动调用 close() 释放隧道）
    """
    wrapper = PodmanSSHClient(machine_name=machine_name, **kwargs)
    return wrapper.client()
