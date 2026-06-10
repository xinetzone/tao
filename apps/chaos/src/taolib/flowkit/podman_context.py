"""Podman Python SDK 上下文工具.

提供基于 Podman Python SDK 的高级容器运行抽象，自动处理跨平台路径转换和客户端创建。
与 container.py 不同，本模块使用 Podman Python SDK（而非 CLI）进行容器操作，
适用于需要细粒度容器控制和实时日志流的场景。

ContainerRun 支持同步和异步上下文管理器，每个实例管理独立的 Podman 连接和容器生命周期。
主命令可留空（默认 sleep infinity），通过 exec/exec_many 在容器内串行或并行执行多个子命令。
多容器之间天然支持多线程/asyncio 并行。

运行环境要求: Python 3.10+, Windows 需配合 podman_win 模块
"""

import asyncio
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Any, Self


class ContainerRunError(Exception):
    """容器运行错误，不退出进程，由调用方决定如何处理."""

    pass


@dataclass
class ExecResult:
    """容器内命令执行结果.

    Attributes:
        exit_code: 退出码（0 表示成功）。
        output: 标准输出内容。
    """

    exit_code: int
    output: str


@dataclass
class PodmanContext:
    """Podman 客户端上下文，包含连接客户端和转换后的宿主机路径。

    Attributes:
        host_path_str: 转换后的宿主机路径，Unix 格式。
        ctx: Podman 客户端实例（PodmanClient 或 PodmanSSHClient）。
    """

    host_path_str: str
    ctx: Any


@dataclass
class ContainerRun:
    """容器运行任务（上下文管理器）。

    自动根据平台创建客户端、转换路径。自动清理同名旧容器。
    每个实例管理独立的 Podman 连接，支持并行执行多个容器。

    Attributes:
        image: 容器镜像名称。
        host_path: 宿主机目录路径，为 None 时不挂载 bind 卷。
        target: 容器内挂载目标路径，为 None 时不挂载 bind 卷。
        working_dir: 容器内工作目录，为 None 时使用镜像默认值。
        name: 容器名称，为 None 时由 Podman 自动生成。
        command: 容器主命令列表，默认为 ["sleep", "infinity"] 以保持容器存活。
        run_kwargs: 透传给 containers.run() 的额外关键字参数。
        network_mode: 容器网络模式（如 "bridge"、"host"、"none"），为 None 时使用 Podman 默认值。
        start_container: 是否启动容器，默认 True。置为 False 时只建立客户端连接。

    Example:
        # 单命令模式
        >>> with ContainerRun(
        ...     host_path=Path("/some/path"),
        ...     name="my_container",
        ...     target="/mnt",
        ...     working_dir="/mnt",
        ...     image="python:3.13",
        ...     command=["python", "-c", "print(42)"],
        ... ) as cr:
        ...     if cr.wait() != 0:
        ...         raise ContainerRunError("容器异常退出")

        # 多命令模式（主命令留空 + exec）
        >>> with ContainerRun(
        ...     host_path=Path("."), name="worker", target="/mnt",
        ...     working_dir="/mnt", image="python:3.13",
        ... ) as cr:
        ...     r1 = cr.exec(["python", "task1.py"])
        ...     r2 = cr.exec(["python", "task2.py"])

        # 容器内并行执行多个子命令
        >>> with ContainerRun(
        ...     host_path=Path("."), name="worker", target="/mnt",
        ...     working_dir="/mnt", image="python:3.13",
        ... ) as cr:
        ...     results = cr.exec_many([
        ...         ["python", "task1.py"],
        ...         ["python", "task2.py"],
        ...     ])
        ...     for r in results:
        ...         if r.exit_code != 0:
        ...             raise ContainerRunError(r.output)

        # 线程池并行执行多个容器
        >>> from concurrent.futures import ThreadPoolExecutor, as_completed
        >>> def task(cr):
        ...     with cr:
        ...         return cr.wait()
        >>> runs = [ContainerRun(...), ContainerRun(...)]
        >>> with ThreadPoolExecutor() as ex:
        ...     for f in as_completed([ex.submit(task, cr) for cr in runs]):
        ...         print(f.result())

        # asyncio 并行执行多个容器
        >>> async def main():
        ...     async def task(cr):
        ...         async with cr:
        ...             return await cr.async_wait()
        ...     runs = [ContainerRun(...), ContainerRun(...)]
        ...     results = await asyncio.gather(*(task(cr) for cr in runs))
        >>> asyncio.run(main())
    """

    image: str
    host_path: Path | None = None
    target: str | None = None
    working_dir: str | None = None
    name: str | None = None
    command: list[str] = field(default_factory=list)
    volumes: dict[str, str] = field(default_factory=dict)
    client_kwargs: dict[str, Any] = field(default_factory=dict)
    run_kwargs: dict[str, Any] = field(default_factory=dict)
    network_mode: str | None = None
    start_container: bool = True

    # 内部状态
    _pctx: PodmanContext | None = field(default=None, init=False)
    _client: Any = field(default=None, init=False)
    _container: Any = field(default=None, init=False)
    _exit_code: int | None = field(default=None, init=False)

    # ── 上下文管理器协议 ──────────────────────────────────────────

    def __enter__(self) -> Self:
        self._start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        self._cleanup()
        return False

    async def __aenter__(self) -> Self:
        await asyncio.to_thread(self._start)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        await asyncio.to_thread(self._cleanup)
        return False

    # ── 公共方法 ──────────────────────────────────────────────────

    def wait(self, *, stream_logs: bool = True) -> int:
        """等待容器结束，返回退出码。

        Args:
            stream_logs: 是否实时输出容器日志到 stdout，默认 True。

        Returns:
            容器退出码（0 表示成功）。

        Raises:
            RuntimeError: 容器尚未启动（未进入上下文）。
        """
        if not self._container:
            raise RuntimeError("容器未启动，请先通过 with 语句进入上下文")

        # 流式输出容器日志：逐块读取并实时打印到标准输出
        if stream_logs:
            for chunk in self._container.logs(stream=True, follow=True):
                print(chunk.decode(errors="replace"), end="")

        # wait() 在不同 SDK 版本中返回值不同：dict 或 int，兼容处理
        result = self._container.wait()
        self._exit_code = result["StatusCode"] if isinstance(result, dict) else result
        return self._exit_code

    async def async_wait(self, *, stream_logs: bool = True) -> int:
        """异步等待容器结束，返回退出码。

        通过 asyncio.to_thread 将阻塞的日志流和等待操作移出事件循环。
        """
        return await asyncio.to_thread(self.wait, stream_logs=stream_logs)

    def exec(self, cmd: list[str], *, workdir: str | None = None) -> ExecResult:
        """在运行中的容器内执行命令，返回退出码和输出。

        主命令和额外命令可以并行执行（容器以 detach 模式运行）。

        Args:
            cmd: 要执行的命令列表。
            workdir: 容器内工作目录，默认使用容器默认工作目录。

        Returns:
            ExecResult，包含 exit_code 和 output。

        Raises:
            RuntimeError: 容器尚未启动。

        Example:
            >>> with cr:
            ...     r1 = cr.exec(["python", "task1.py"])
            ...     r2 = cr.exec(["python", "task2.py"])
            ...     if r1.exit_code != 0:
            ...         raise ContainerRunError(f"task1 失败: {r1.output}")
        """
        if not self._container:
            raise RuntimeError("容器未启动，请先通过 with 语句进入上下文")

        exit_code, output = self._container.exec_run(
            cmd,
            # workdir or self.working_dir 为 None 时，exec_run 使用容器默认工作目录
            workdir=workdir or self.working_dir,
            tty=True,
        )
        # exec_run 的 output 在不同模式下返回 bytes 或 str，统一处理
        if isinstance(output, bytes):
            sys.stdout.buffer.write(output)
            sys.stdout.buffer.flush()
            text = output.decode(errors="replace")
        else:
            text = str(output)
            sys.stdout.write(text)
        return ExecResult(exit_code=exit_code, output=text)

    async def async_exec(
        self, cmd: list[str], *, workdir: str | None = None
    ) -> ExecResult:
        """异步在运行中的容器内执行命令。

        通过 asyncio.to_thread 将阻塞操作移出事件循环。
        """
        return await asyncio.to_thread(self.exec, cmd, workdir=workdir)

    def exec_many(
        self,
        commands: list[list[str]],
        *,
        workdir: str | None = None,
    ) -> list[ExecResult]:
        """并行执行多个命令，返回结果列表。

        通过 ThreadPoolExecutor 在容器内并行执行，适合与 with 同步上下文配合。

        Args:
            commands: 命令列表（每个元素为命令参数列表）。
            workdir: 容器内工作目录。

        Returns:
            ExecResult 列表，顺序与 commands 对应。
        """
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor() as ex:
            futures = [ex.submit(self.exec, cmd, workdir=workdir) for cmd in commands]
            return [f.result() for f in futures]

    async def async_exec_many(
        self,
        commands: list[list[str]],
        *,
        workdir: str | None = None,
    ) -> list[ExecResult]:
        """异步并行执行多个命令。

        通过 asyncio.gather + async_exec 并发执行，适合与 async with 上下文配合。
        """
        return await asyncio.gather(
            *(self.async_exec(cmd, workdir=workdir) for cmd in commands),
        )

    @property
    def exit_code(self) -> int | None:
        """容器退出码，wait() 调用前为 None。"""
        return self._exit_code

    # ── 内部方法 ──────────────────────────────────────────────────

    def _start(self) -> None:
        """创建 Podman 连接、挂载卷、清理同名旧容器、启动后台容器。

        执行流程：
        1. 根据 host_path 是否为空，选择不同的客户端创建策略
        2. 构建挂载列表（bind 挂载 + 命名卷）
        3. 若指定了容器名，清理可能的同名旧容器
        4. 若 start_container 为 True，启动后台容器

        Raises:
            ContainerRunError: 容器启动失败。
        """
        try:
            # ── 1. 创建 Podman 客户端 ──
            if self.host_path is not None:
                # 有宿主机路径：走跨平台路径转换流程
                # Windows 下 PodmanSSHClient 返回的是包装对象，需调用 .client()
                # Linux/macOS 下 _get_podman_context 直接返回 PodmanClient
                self._pctx = _get_podman_context(
                    self.host_path, **self.client_kwargs
                )
                self._client = (
                    self._pctx.ctx.client()
                    if sys.platform == "win32"
                    else self._pctx.ctx
                )
            else:
                # 无宿主机路径：直接创建 PodmanClient，不做路径转换
                from podman import PodmanClient

                self._client = PodmanClient(**self.client_kwargs)

            # ── 2. 构建挂载列表 ──
            mounts: list[dict[str, Any]] = []
            # bind 挂载：将宿主机目录映射到容器内
            if self.host_path is not None and self.target is not None:
                mounts.append(
                    {
                        "type": "bind",
                        "source": self._pctx.host_path_str,
                        "target": self.target,
                    },
                )
            # 命名卷挂载：Podman 管理的持久化存储卷
            for vol_src, vol_target in self.volumes.items():
                mounts.append(
                    {"type": "volume", "source": vol_src, "target": vol_target}
                )

            # ── 3. 清理同名旧容器 ──
            # 仅在显式指定容器名时才清理，避免误删自动命名的容器
            if self.name is not None:
                try:
                    old = self._client.containers.get(self.name)
                    old.remove(force=True)
                except Exception:
                    pass

            # ── 4. 仅建连接模式 ──
            # start_container=False 时跳过容器创建，仅管理客户端生命周期
            if not self.start_container:
                return

            # ── 5. 构建容器运行参数并启动 ──
            # 固定参数：所有容器都必须的配置
            run_params: dict[str, Any] = {
                "image": self.image,
                "command": self.command or ["sleep", "infinity"],
                "tty": True,
                "stdin_open": True,
                "detach": True,
            }
            # 条件参数：仅在显式设置时才传入，避免覆盖 SDK 默认行为
            if self.name is not None:
                run_params["name"] = self.name
            if mounts:
                run_params["mounts"] = mounts
            if self.working_dir is not None:
                run_params["working_dir"] = self.working_dir
            if self.network_mode is not None:
                run_params["network_mode"] = self.network_mode
            # 用户自定义参数最后合并，允许覆盖以上所有参数
            run_params.update(self.run_kwargs)

            self._container = self._client.containers.run(**run_params)
        except Exception as exc:
            self._cleanup()
            raise ContainerRunError(f"容器启动失败: {exc}") from exc

    def _cleanup(self) -> None:
        """清理资源：容器 → 客户端 → SSH 隧道。

        按顺序释放：先强制删除容器，再关闭客户端连接，
        Windows 下还需关闭 SSH 隧道进程。
        所有清理操作均忽略异常，确保不会因清理失败而中断退出流程。
        """
        # 强制删除容器 + 关闭客户端连接
        for obj, action in [
            (self._container, lambda o: o.remove(force=True)),
            (self._client, lambda o: o.close()),
        ]:
            if obj is not None:
                try:
                    action(obj)
                except Exception:
                    pass

        # Windows 下 SSH 客户端通过子进程隧道连接，需额外关闭隧道进程
        if (
            sys.platform == "win32"
            and self._pctx is not None
            and hasattr(self._pctx.ctx, "_tunnel")
        ):
            try:
                self._pctx.ctx._tunnel.stop()
            except Exception:
                pass

        self._container = None
        self._client = None


def _win_to_unix(path: str) -> str:
    """将 Windows 路径转为 Unix 路径，供 Linux Podman 主机使用。

    Windows Podman 通过虚拟机运行，容器内的 Linux 需要 Unix 风格路径。
    盘符（如 C:）会被映射到 $PODMAN_WIN_MNT_PREFIX（默认 /mnt）下。

    Args:
        path: Windows 风格路径字符串，如 "C:\\Users\\foo\\bar"。

    Returns:
        Unix 风格路径字符串，如 "/mnt/c/Users/foo/bar"。
    """
    prefix = os.environ.get("PODMAN_WIN_MNT_PREFIX", "/mnt")
    # 统一反斜杠为正斜杠
    path = path.replace("\\", "/")
    # 检测盘符（如 "C:"），映射为 /mnt/c 格式
    if len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        path = f"{prefix}/{drive}{path[2:]}"
    return path


def _get_active_podman_machine() -> str:
    """获取当前正在运行的 podman machine 名称。

    通过 `podman machine list` 解析输出，找到 LastUp 不为空
    和 "Never" 的机器。未找到运行中的 machine 时，fallback 到默认名称
    "podman-machine-default"。

    Returns:
        运行中的 podman machine 名称。
    """
    import subprocess as _sp

    try:
        # --format 输出格式为 "机器名 最后启动时间"
        r = _sp.run(
            ["podman", "machine", "list", "--format", "{{.Name}} {{.LastUp}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in r.stdout.strip().splitlines():
            parts = line.split(maxsplit=1)
            # 第二列为空或 "Never" 表示从未启动，跳过
            if len(parts) == 2 and parts[1].strip() not in ("", "Never"):
                # 去除当前活跃标记（* 后缀）
                return parts[0].rstrip("*")
    except Exception:
        pass
    return "podman-machine-default"


def _get_podman_context(host_path: Path, **kwargs: Any) -> PodmanContext:
    """根据平台获取 Podman 客户端和宿主机路径字符串。

    Windows 下 Podman 运行在虚拟机中，需要通过 SSH 连接，并且宿主机
    路径需要转换为 Unix 格式。Linux/macOS 下 Podman 直接运行在宿主机上，
    通过 Unix socket 连接。

    Args:
        host_path: 宿主机目录路径。
        **kwargs: 透传给 PodmanClient 或 PodmanSSHClient 的额外参数。

    Returns:
        PodmanContext 实例，包含路径字符串和客户端。
    """
    if sys.platform == "win32":
        # Windows：路径转 Unix + SSH 连接
        host_path_str = _win_to_unix(str(host_path))
        from .podman_win import PodmanSSHClient

        machine = _get_active_podman_machine()
        ctx = PodmanSSHClient(machine_name=machine, **kwargs)
    else:
        # Linux/macOS：路径原样 + Unix socket 连接
        host_path_str = str(host_path)
        from podman import PodmanClient

        ctx = PodmanClient(**kwargs)
    return PodmanContext(host_path_str=host_path_str, ctx=ctx)
