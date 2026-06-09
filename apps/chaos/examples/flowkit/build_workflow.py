"""flowkit 使用示例 - 完整的构建工作流演示.

本示例展示如何使用 flowkit 构建一个完整的容器化编译流程:
1. 配置构建路径和 Nuitka 编译参数
2. 创建构建报告
3. 管理构建产物
4. 生成完整性清单

运行方式:
    python examples/build_workflow.py
"""

from datetime import datetime
from pathlib import Path

from taolib.flowkit import (
    NUITKA_MODULE,
    ArtifactManifest,
    BuildPaths,
    BuildReport,
    ContainerConfig,
    NuitkaConfig,
    StepResult,
    VolumeMount,
    compute_sha256,
)


def example_build_workflow() -> bool:
    """完整构建工作流示例."""
    print("=" * 60)
    print("FlowKit 构建工作流示例")
    print("=" * 60)

    # 1. 配置构建路径
    print("\n1️⃣  配置构建路径...")
    workspace = Path("./workspace")
    paths = BuildPaths(
        source_dir=workspace / "src",
        output_dir=workspace / "output",
    )

    # 创建必要的目录
    paths.source_dir.mkdir(parents=True, exist_ok=True)
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    paths.wheels_dir.mkdir(parents=True, exist_ok=True)

    print(f"   源码目录: {paths.source_dir}")
    print(f"   输出目录: {paths.output_dir}")
    print(f"   Wheel 目录: {paths.wheels_dir}")

    # 2. 配置 Nuitka 编译参数
    print("\n2️⃣  配置 Nuitka 编译参数...")

    # 使用预定义模板并自定义
    nuitka_config = NUITKA_MODULE.with_output(str(paths.output_dir)).with_jobs(8)
    nuitka_config = NuitkaConfig(
        mode=nuitka_config.mode,
        compiler=nuitka_config.compiler,
        include_packages=["mypackage"],
        include_modules=["mypackage.dynamic_module"],
        follow_imports=["mypackage"],
        nofollow_imports=["tests", "docs"],
        output=nuitka_config.output,
        compiler_config=nuitka_config.compiler_config,
    )

    args = nuitka_config.to_args()
    print(f"   编译模式: {nuitka_config.mode}")
    print(f"   编译器: {nuitka_config.compiler}")
    print(f"   并行任务: {nuitka_config.jobs}")
    print(f"   命令参数: {' '.join(args[:5])}...")

    # 3. 创建构建报告
    print("\n3️⃣  创建构建报告...")
    report = BuildReport(run_id=f"build_{int(datetime.now().timestamp())}")

    # 模拟编译步骤
    print("   执行编译步骤...")
    report.steps.append(
        StepResult(
            name="compile_mypackage",
            success=True,
            duration_seconds=45.3,
            output="Nuitka compilation successful",
            artifacts=["mypackage.cpython-313-x86_64-linux-gnu.so"],
        )
    )

    # 模拟打包步骤
    print("   执行打包步骤...")
    report.steps.append(
        StepResult(
            name="package_wheel",
            success=True,
            duration_seconds=12.7,
            output="Wheel package created",
            artifacts=["mypackage-1.0.0-py3-none-any.whl"],
        )
    )

    # 4. 创建模拟产物
    print("\n4️⃣  创建构建产物...")
    wheel_file = paths.wheels_dir / "mypackage-1.0.0-py3-none-any.whl"
    wheel_file.write_text("fake wheel content for demonstration")
    report.wheels.append(wheel_file)

    print(f"   产物: {wheel_file.name}")
    print(f"   大小: {wheel_file.stat().st_size} bytes")
    print(f"   SHA256: {compute_sha256(wheel_file)[:16]}...")

    # 5. 创建产物清单
    print("\n5️⃣  创建产物清单...")
    manifest = ArtifactManifest(
        created_at=datetime.now().isoformat(),
        run_id=report.run_id,
    )

    manifest.add_artifact(wheel_file, base_dir=paths.output_dir)
    manifest_path = manifest.to_json(paths.output_dir / "manifest.json")

    print(f"   清单路径: {manifest_path}")
    print(f"   产物数量: {len(manifest.artifacts)}")

    # 6. 验证产物完整性
    print("\n6️⃣  验证产物完整性...")
    success, errors = ArtifactManifest.verify(manifest_path)

    if success:
        print("   ✅ 所有产物校验通过")
    else:
        print("   ❌ 校验失败:")
        for err in errors:
            print(f"      - {err}")

    # 7. 保存构建报告
    print("\n7️⃣  保存构建报告...")
    report.end_time = datetime.now().isoformat()
    report.environment = {
        "python_version": "3.13",
        "nuitka_version": "2.0",
        "platform": "linux-x86_64",
    }

    report_path = paths.reports_dir / "report.json"
    report.to_json(report_path)

    print(f"   报告路径: {report_path}")
    print(f"   构建状态: {'SUCCESS' if report.success else 'FAILED'}")
    print(f"   总耗时: {report.total_duration:.1f}s")

    # 8. 从报告加载并分析
    print("\n8️⃣  加载并分析报告...")
    loaded_report = BuildReport.from_json(report_path)

    print(f"   运行 ID: {loaded_report.run_id}")
    print(f"   步骤数: {len(loaded_report.steps)}")
    for step in loaded_report.steps:
        status = "✅" if step.success else "❌"
        print(f"      {status} {step.name}: {step.duration_seconds:.1f}s")

    print("\n" + "=" * 60)
    print("构建工作流完成!")
    print("=" * 60)

    return report.success


def example_container_config() -> None:
    """容器配置示例."""
    print("\n" + "=" * 60)
    print("容器配置示例")
    print("=" * 60)

    workspace = Path("./workspace")

    # 配置容器
    config = ContainerConfig(
        image="python:3.13-slim",
        name_prefix="build_container",
        volumes=[
            VolumeMount(workspace / "src", "/work/src", readonly=True),
            VolumeMount(workspace / "output", "/work/output"),
            VolumeMount(workspace / "ccache", "/root/.ccache"),
        ],
        env={
            "DEBUG": "1",
            "CCACHE_DIR": "/root/.ccache",
            "TVM_FFI": "ctypes",
        },
        workdir="/work",
    )

    print(f"\n镜像: {config.image}")
    print(f"容器名前缀: {config.name_prefix}")
    print(f"工作目录: {config.workdir}")
    print(f"卷挂载: {len(config.volumes)} 个")
    for vol in config.volumes:
        mode = "只读" if vol.readonly else "读写"
        print(f"  - {vol.host_path} -> {vol.container_path} ({mode})")
    print(f"环境变量: {len(config.env)} 个")
    for key, value in config.env.items():
        print(f"  - {key}={value}")

    print("\n注意: 实际容器操作需要 Podman 或 Docker 环境")
    print("=" * 60)


def example_nuitka_configs() -> None:
    """Nuitka 配置示例."""
    print("\n" + "=" * 60)
    print("Nuitka 配置示例")
    print("=" * 60)

    # 示例 1: 模块编译
    print("\n1️⃣  模块编译 (Module):")
    module_config = NuitkaConfig(
        mode="module",
        compiler="clang",
        include_packages=["mylib"],
        enabled_plugins=["dill-compat"],
    )
    print(f"   命令: python -m nuitka {' '.join(module_config.to_args())}")

    # 示例 2: 独立应用
    print("\n2️⃣  独立应用 (Standalone):")
    standalone_config = NuitkaConfig(
        mode="standalone",
        compiler="gcc",
        include_packages=["myapp", "mylib"],
        follow_imports=["myapp", "mylib"],
        nofollow_imports=["tests"],
        extra_flags=["--remove-output", "--include-data-dir=./data=data"],
    )
    print(f"   命令: python -m nuitka {' '.join(standalone_config.to_args()[:8])}...")

    # 示例 3: 单文件应用
    print("\n3️⃣  单文件应用 (Onefile):")
    onefile_config = NuitkaConfig(
        mode="onefile",
        compiler="clang",
        include_packages=["myapp"],
        extra_flags=[
            "--remove-output",
            "--windows-icon-from-ico=icon.ico",
            "--windows-company-name=MyCompany",
        ],
    )
    print(f"   命令: python -m nuitka {' '.join(onefile_config.to_args()[:8])}...")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 运行所有示例
    example_build_workflow()
    example_container_config()
    example_nuitka_configs()

    print("\n✨ 所有示例运行完成!\n")
