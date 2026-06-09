"""通用容器生命周期管理.

提供容器化构建的核心能力,支持 Podman 和 Docker 双引擎:
- 容器启动/停止/执行命令 (Container)
- 镜像构建/加载/导出 (build_image, load_image, save_image)
- 孤儿容器清理 (cleanup_orphan_containers)

运行环境要求: Python 3.10+, 需要安装 podman 或 docker CLI
"""

from __future__ import annotations

import datetime
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from .models import (
    ContainerConfig,
    ImageConfig,
    StepResult,
    compute_sha256,
)


class ContainerRuntimeError(Exception):
    """容器运行时错误."""

    pass


class ContainerNotFoundError(Exception):
    """容器或镜像不存在."""

    pass


def _detect_container_engine() -> str:
    """自动检测可用的容器引擎.

    Returns:
        "podman" 或 "docker"

    Raises:
        ContainerRuntimeError: 未找到可用引擎
    """
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise ContainerRuntimeError(
        "未找到可用的容器引擎 (podman 或 docker), 请安装其中之一"
    )


@dataclass
class Container:
    """管理容器生命周期.

    自动检测并使用 podman 或 docker,提供统一的容器操作接口.

    Attributes:
        config: 容器运行配置
        engine: 容器引擎 ("podman" 或 "docker"), None 表示自动检测

    Example:
        >>> config = ContainerConfig(image="python:3.13", name_prefix="test")
        >>> container = Container(config)
        >>> container.start()
        >>> result = container.exec("python --version")
        >>> print(result.output)
        >>> container.stop()
    """

    config: ContainerConfig
    engine: str | None = field(default=None)
    container_id: str | None = field(default=None, init=False)

    def __post_init__(self):
        """初始化时检测容器引擎."""
        if self.engine is None:
            self.engine = _detect_container_engine()
        elif self.engine not in ("podman", "docker"):
            raise ValueError(
                f"不支持的容器引擎: {self.engine}, 请使用 'podman' 或 'docker'"
            )

    def _run(
        self,
        args: list[str],
        *,
        timeout: int = 300,
        check: bool = False,
    ) -> subprocess.CompletedProcess:
        """执行容器引擎命令.

        Args:
            args: 命令参数列表 (不含引擎名称)
            timeout: 超时时间 (秒)
            check: 是否检查返回码

        Returns:
            subprocess.CompletedProcess 实例
        """
        cmd = [self.engine, *args]
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            check=check,
        )

    def _volume_args(self) -> list[str]:
        """生成 -v 参数列表."""
        result = []
        for v in self.config.volumes:
            mode = "ro" if v.readonly else "rw"
            result.extend(["-v", f"{v.host_path}:{v.container_path}:{mode}"])
        return result

    def _env_args(self) -> list[str]:
        """生成 -e 参数列表."""
        result = []
        for k, val in self.config.env.items():
            result.extend(["-e", f"{k}={val}"])
        return result

    def start(self) -> str:
        """启动后台容器, 返回 container_id.

        Returns:
            容器 ID 字符串

        Raises:
            ContainerRuntimeError: 容器启动失败
        """
        name = f"{self.config.name_prefix}_{uuid.uuid4().hex[:8]}"
        args = [
            "run",
            "-d",
            "--name",
            name,
            "-w",
            self.config.workdir,
            *self._volume_args(),
            *self._env_args(),
            self.config.image,
            "sleep",
            "infinity",
        ]
        proc = self._run(args)
        if proc.returncode != 0:
            raise ContainerRuntimeError(f"容器启动失败: {proc.stderr}")
        self.container_id = proc.stdout.strip()
        return self.container_id

    def exec(
        self,
        cmd: str,
        *,
        workdir: str | None = None,
        env: dict[str, str] | None = None,
        timeout: int = 1800,
    ) -> StepResult:
        """在容器内执行命令.

        Args:
            cmd: 要执行的 shell 命令
            workdir: 容器内工作目录 (可选)
            env: 额外环境变量 (可选)
            timeout: 超时时间 (秒)

        Returns:
            StepResult 实例, 包含执行结果和耗时
        """
        if not self.container_id:
            raise ContainerRuntimeError("容器未启动, 请先调用 start()")

        args = ["exec"]
        if workdir:
            args.extend(["-w", workdir])
        if env:
            for k, v in env.items():
                args.extend(["-e", f"{k}={v}"])
        args.extend([self.container_id, "bash", "-c", cmd])

        start_time = time.time()
        proc = self._run(args, timeout=timeout)
        duration = time.time() - start_time

        return StepResult(
            name=cmd[:60],
            success=(proc.returncode == 0),
            duration_seconds=duration,
            output=proc.stdout,
            error=proc.stderr,
        )

    def stop(self, remove: bool = True) -> None:
        """停止并可选删除容器.

        Args:
            remove: 是否同时删除容器, 默认 True
        """
        if self.container_id:
            self._run(["stop", self.container_id], timeout=30)
            if remove:
                self._run(["rm", "-f", self.container_id], timeout=30)
            self.container_id = None

    def logs(self, tail: int = 50) -> str:
        """获取容器日志.

        Args:
            tail: 返回最近 N 行日志

        Returns:
            日志内容字符串
        """
        if not self.container_id:
            return ""
        proc = self._run(["logs", "--tail", str(tail), self.container_id])
        return proc.stdout


def image_exists(name: str, engine: str | None = None) -> bool:
    """判断本地是否已存在指定镜像.

    Args:
        name: 镜像名称或 tag
        engine: 容器引擎 ("podman"/"docker"), None 表示自动检测

    Returns:
        镜像是否存在
    """
    if engine is None:
        engine = _detect_container_engine()
    check = subprocess.run(
        [engine, "image", "exists", name],
        capture_output=True,
    )
    return check.returncode == 0


def load_image_tar(tar_path: Path, engine: str | None = None) -> bool:
    """从 tar 加载镜像.

    Args:
        tar_path: tar 文件路径
        engine: 容器引擎, None 表示自动检测

    Returns:
        是否成功

    Raises:
        ContainerRuntimeError: 加载失败
        FileNotFoundError: tar 文件不存在
    """
    if not tar_path.exists():
        raise FileNotFoundError(f"镜像 tar 不存在: {tar_path}")

    if engine is None:
        engine = _detect_container_engine()

    proc = subprocess.run(
        [engine, "load", "-i", str(tar_path)],
        capture_output=True,
        text=True,
        timeout=600,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise ContainerRuntimeError(f"镜像加载失败: {proc.stderr}")
    return True


def load_image(config: ImageConfig, engine: str | None = None) -> bool:
    """加载基础镜像 tar (若已存在则跳过).

    Args:
        config: 镜像配置
        engine: 容器引擎, None 表示自动检测

    Returns:
        是否成功
    """
    if image_exists(config.base_name, engine):
        return True
    return load_image_tar(config.base_tar, engine)


def build_image(
    config: ImageConfig,
    context: Path,
    build_args: dict[str, str] | None = None,
    engine: str | None = None,
) -> bool:
    """构建中间镜像.

    使用容器引擎的 build 命令,从 Containerfile/Dockerfile 构建镜像.

    Args:
        config: 镜像配置
        context: 构建上下文目录 (包含 Containerfile)
        build_args: 构建参数 (如 {"PYTHON_VERSION": "3.13"})
        engine: 容器引擎, None 表示自动检测

    Returns:
        是否成功

    Raises:
        ContainerRuntimeError: 构建失败
    """
    if engine is None:
        engine = _detect_container_engine()

    containerfile_path = str(context / config.containerfile)
    cmd = [
        engine,
        "build",
        "-t",
        config.build_name,
        "-f",
        containerfile_path,
    ]
    for k, v in (build_args or {}).items():
        cmd.extend(["--build-arg", f"{k}={v}"])
    cmd.append(str(context))

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=1800,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise ContainerRuntimeError(f"镜像构建失败: {proc.stderr}")
    return True


def save_image(
    name: str,
    tar_path: Path,
    engine: str | None = None,
    generate_checksum: bool = True,
) -> bool:
    """将本地镜像导出为 tar.

    Args:
        name: 镜像名称或 tag
        tar_path: 输出 tar 文件路径
        engine: 容器引擎, None 表示自动检测
        generate_checksum: 是否生成 SHA256 校验文件

    Returns:
        是否成功

    Raises:
        ContainerRuntimeError: 导出失败
    """
    if engine is None:
        engine = _detect_container_engine()

    tar_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [engine, "save", "-o", str(tar_path), name],
        capture_output=True,
        text=True,
        timeout=600,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise ContainerRuntimeError(f"镜像导出失败: {proc.stderr}")

    if generate_checksum:
        sha256_hash = compute_sha256(tar_path)
        sha256_file = tar_path.with_suffix(tar_path.suffix + ".sha256")
        sha256_file.write_text(f"{sha256_hash}  {tar_path.name}\n", encoding="utf-8")
    return True


def cleanup_orphan_containers(
    name_prefix: str,
    *,
    max_age_hours: float = 4,
    engine: str | None = None,
) -> int:
    """清理名称匹配 name_prefix 且运行超过 max_age_hours 的孤儿容器.

    Args:
        name_prefix: 容器名称前缀
        max_age_hours: 最大存活时间 (小时)
        engine: 容器引擎, None 表示自动检测

    Returns:
        被清理的容器数量
    """
    if engine is None:
        engine = _detect_container_engine()

    # 列出所有匹配前缀的容器 (running + exited)
    proc = subprocess.run(
        [
            engine,
            "ps",
            "-a",
            "--filter",
            f"name={name_prefix}",
            "--format",
            "{{.ID}} {{.CreatedAt}}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return 0

    cleaned = 0
    for line in proc.stdout.strip().splitlines():
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        cid = parts[0]

        # 获取容器创建时间
        inspect = subprocess.run(
            [engine, "inspect", "--format", "{{.Created}}", cid],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )
        if inspect.returncode != 0:
            continue

        try:
            created_str = inspect.stdout.strip()
            # 解析 ISO 8601 格式时间戳
            created_dt = datetime.datetime.fromisoformat(
                created_str.replace("Z", "+00:00")
            )
            age_hours = (
                datetime.datetime.now(datetime.UTC) - created_dt
            ).total_seconds() / 3600
        except (ValueError, TypeError):
            continue

        if age_hours > max_age_hours:
            subprocess.run([engine, "rm", "-f", cid], capture_output=True, timeout=30)
            cleaned += 1

    return cleaned
