"""FlowKit - 容器化构建工作流工具包.

提供可复用的构建系统基础设施,包括:
- 容器生命周期管理 (Podman/Docker 双引擎)
- Nuitka 编译器参数生成
- 构建产物完整性校验
- 构建报告生成

适用场景:
- 需要容器化编译 Python 项目
- 使用 Nuitka 进行 Python 代码编译
- 需要构建产物的完整性验证
- 需要标准化的构建报告

安装:
    ```bash
    pip install -e ./server/libs/flowkit
    ```

快速开始:
    ```python
    from taolib.flowkit import Container, ContainerConfig, NuitkaConfig

    # 配置容器
    config = ContainerConfig(
        image="python:3.13",
        name_prefix="my_build",
    )

    # 启动容器并执行命令
    container = Container(config)
    container.start()
    result = container.exec("python -c 'print(42)'")
    print(result.output)
    container.stop()

    # 配置 Nuitka 编译
    nuitka_config = NuitkaConfig(
        mode="module",
        include_packages=["mypackage"],
    )
    args = nuitka_config.to_args()
    ```

模块结构:
    - models: 核心数据模型 (BuildReport, ContainerConfig, etc.)
    - container: 容器生命周期管理
    - nuitka_config: Nuitka 编译器抽象
    - artifacts: 产物完整性校验

运行环境要求: Python 3.10+
"""

__version__ = "0.2.0"
__author__ = "AI Notebook Team"

# 核心数据模型
# 产物管理
# Podman Windows SDK 适配（仅 Windows 可用，Linux/macOS 用 Unix socket 直连即可）
import sys

from .artifacts import (
    ArtifactEntry,
    ArtifactManifest,
    generate_checksum_file,
    verify_checksum_file,
)

# 容器管理
from .container import (
    Container,
    ContainerNotFoundError,
    ContainerRuntimeError,
    build_image,
    cleanup_orphan_containers,
    image_exists,
    load_image,
    load_image_tar,
    save_image,
)
from .models import (
    BuildPaths,
    BuildReport,
    ContainerConfig,
    ImageConfig,
    StepResult,
    VolumeMount,
    compute_sha256,
)

if sys.platform == "win32":
    from .podman_win import PodmanSSHClient, quick_client
else:
    PodmanSSHClient = None  # type: ignore
    quick_client = None  # type: ignore

# Podman SDK 上下文工具（跨平台，Python SDK 风格容器操作）
# Nuitka 编译器
from .nuitka_config import (
    COMMON_PLUGINS,
    NUITKA_ACCELERATED,
    NUITKA_APP,
    # 预定义模板
    NUITKA_MODULE,
    NUITKA_ONEFILE,
    NUITKA_STANDALONE,
    # 常量
    STANDARD_PLUGINS,
    CacheConfig,
    CompilerConfig,
    DataConfig,
    MacOSConfig,
    # 主配置类
    NuitkaConfig,
    # 子配置类
    OutputConfig,
    VersionInfo,
    WindowsConfig,
    # 辅助函数
    build_nuitka_command,
    parse_nuitka_version,
)
from .podman_context import ContainerRun, ContainerRunError, ExecResult, PodmanContext

__all__ = [
    # 版本信息
    "__version__",
    # 数据模型
    "BuildPaths",
    "BuildReport",
    "ContainerConfig",
    "ImageConfig",
    "StepResult",
    "VolumeMount",
    "compute_sha256",
    # 容器管理
    "Container",
    "ContainerRuntimeError",
    "ContainerNotFoundError",
    "build_image",
    "cleanup_orphan_containers",
    "image_exists",
    "load_image",
    "load_image_tar",
    "save_image",
    # Nuitka 编译器
    "NuitkaConfig",
    "OutputConfig",
    "DataConfig",
    "CompilerConfig",
    "CacheConfig",
    "WindowsConfig",
    "MacOSConfig",
    "VersionInfo",
    "NUITKA_MODULE",
    "NUITKA_STANDALONE",
    "NUITKA_ONEFILE",
    "NUITKA_ACCELERATED",
    "NUITKA_APP",
    "STANDARD_PLUGINS",
    "COMMON_PLUGINS",
    "build_nuitka_command",
    "parse_nuitka_version",
    # 产物管理
    "ArtifactEntry",
    "ArtifactManifest",
    "generate_checksum_file",
    "verify_checksum_file",
    # Podman Windows SDK 适配（仅 Windows）
    *(["PodmanSSHClient", "quick_client"] if sys.platform == "win32" else []),
    # Podman SDK 上下文工具
    "PodmanContext",
    "ContainerRun",
    "ContainerRunError",
    "ExecResult",
]
