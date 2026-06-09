"""通用构建系统数据模型.

提供容器构建工作流的核心数据结构定义,包括:
- 容器镜像配置 (ImageConfig)
- 容器运行配置 (ContainerConfig, VolumeMount)
- 构建路径约定 (BuildPaths)
- 构建步骤结果 (StepResult)
- 构建报告 (BuildReport)

运行环境要求: Python 3.10+
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


def compute_sha256(file_path: Path, chunk_size: int = 8192) -> str:
    """计算文件的 SHA256 哈希值.

    Args:
        file_path: 要计算哈希的文件路径
        chunk_size: 分块读取大小 (字节), 默认 8KB

    Returns:
        十六进制 SHA256 哈希字符串

    Raises:
        FileNotFoundError: 文件不存在
        IsADirectoryError: 路径指向目录
    """
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class ImageConfig:
    """容器镜像配置.

    Attributes:
        base_tar: 基础镜像 tar 文件路径
        base_name: 基础镜像 tag (如 "miniconda3:llvm")
        build_name: 中间镜像 tag (如 "myproject-build:latest")
        containerfile: Containerfile/Dockerfile 文件名
        build_tar: 中间镜像导出/导入 tar 路径 (可选, 用于镜像迁移)
    """

    base_tar: Path
    base_name: str = "base:latest"
    build_name: str = "build:latest"
    containerfile: str = "Containerfile"
    build_tar: Path | None = None


@dataclass(frozen=True)
class VolumeMount:
    """容器卷挂载配置.

    Attributes:
        host_path: 宿主机路径
        container_path: 容器内挂载路径
        readonly: 是否只读挂载
    """

    host_path: Path
    container_path: str
    readonly: bool = False


@dataclass(frozen=True)
class ContainerConfig:
    """容器运行配置.

    Attributes:
        image: 容器镜像名称或 ID
        name_prefix: 容器名称前缀 (自动追加随机后缀)
        volumes: 卷挂载列表
        env: 环境变量映射
        workdir: 容器内工作目录
    """

    image: str
    name_prefix: str = "build_container"
    volumes: list[VolumeMount] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    workdir: str = "/work"


@dataclass(frozen=True)
class BuildPaths:
    """构建路径约定.

    定义构建过程中的标准目录结构,便于在不同环境间迁移.

    Attributes:
        source_dir: 源代码根目录
        output_dir: 构建输出根目录
        tvm_build_dir: 预编译 C++ 库目录 (可选, 特定项目使用)
        scripts_dir: 构建脚本目录

    Properties:
        tvm_output: TVM 输出目录
        vta_output: VTA 输出目录
        wheels_dir: wheel 包输出目录
        logs_dir: 构建日志目录
        reports_dir: 构建报告目录
    """

    source_dir: Path
    output_dir: Path
    tvm_build_dir: Path | None = None
    scripts_dir: Path | None = None

    @property
    def tvm_output(self) -> Path:
        """TVM 输出目录."""
        return self.output_dir / "tvm"

    @property
    def vta_output(self) -> Path:
        """VTA 输出目录."""
        return self.output_dir / "vta"

    @property
    def wheels_dir(self) -> Path:
        """wheel 包输出目录."""
        return self.output_dir / "wheels"

    @property
    def logs_dir(self) -> Path:
        """构建日志目录."""
        return self.output_dir / "logs"

    @property
    def reports_dir(self) -> Path:
        """构建报告目录."""
        return self.output_dir / "reports"


@dataclass
class StepResult:
    """单步执行结果.

    Attributes:
        name: 步骤名称或标识
        success: 是否成功
        duration_seconds: 执行耗时 (秒)
        output: 标准输出内容
        error: 标准错误内容
        artifacts: 产生的产物路径列表
    """

    name: str
    success: bool
    duration_seconds: float
    output: str = ""
    error: str = ""
    artifacts: list[str] = field(default_factory=list)


@dataclass
class BuildReport:
    """完整构建报告.

    聚合多个构建步骤的执行结果,提供序列化能力.

    Attributes:
        run_id: 构建运行唯一标识
        steps: 各步骤执行结果列表
        wheels: 生成的 wheel 包路径列表
        start_time: 构建开始时间 (ISO 8601)
        end_time: 构建结束时间 (ISO 8601)
        environment: 构建环境信息 (如 Python 版本、镜像 tag)

    Properties:
        success: 所有步骤是否全部成功
        total_duration: 总耗时 (秒)
    """

    run_id: str
    steps: list[StepResult] = field(default_factory=list)
    wheels: list[Path] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    environment: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """所有步骤是否全部成功."""
        return all(s.success for s in self.steps)

    @property
    def total_duration(self) -> float:
        """总耗时 (秒)."""
        return sum(s.duration_seconds for s in self.steps)

    def to_json(self, output_path: Path) -> Path:
        """将构建报告序列化为 JSON 文件.

        Args:
            output_path: 输出文件路径 (父目录会自动创建)

        Returns:
            实际写入的文件路径
        """
        data = {
            "run_id": self.run_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "environment": self.environment,
            "success": self.success,
            "total_duration": self.total_duration,
            "steps": [
                {
                    "name": s.name,
                    "success": s.success,
                    "duration_seconds": s.duration_seconds,
                    "artifacts": [str(a) for a in s.artifacts]
                    if hasattr(s, "artifacts")
                    else [],
                }
                for s in self.steps
            ],
            "wheels": [str(w) for w in self.wheels],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path

    @classmethod
    def from_json(cls, json_path: Path) -> BuildReport:
        """从 JSON 文件加载构建报告.

        Args:
            json_path: JSON 文件路径

        Returns:
            BuildReport 实例

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        data = json.loads(json_path.read_text(encoding="utf-8"))
        report = cls(
            run_id=data["run_id"],
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            environment=data.get("environment", {}),
        )
        for step_data in data.get("steps", []):
            report.steps.append(
                StepResult(
                    name=step_data["name"],
                    success=step_data["success"],
                    duration_seconds=step_data["duration_seconds"],
                    artifacts=step_data.get("artifacts", []),
                )
            )
        report.wheels = [Path(w) for w in data.get("wheels", [])]
        return report
