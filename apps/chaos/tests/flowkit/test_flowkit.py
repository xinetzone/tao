"""flowkit 包功能验证测试.

运行方式:
    python -m pytest tests/
    或直接运行: python tests/test_flowkit.py
"""
import json
from datetime import datetime
from pathlib import Path

import pytest

from taolib.flowkit import (
    NUITKA_ACCELERATED,
    NUITKA_MODULE,
    NUITKA_STANDALONE,
    STANDARD_PLUGINS,
    ArtifactEntry,
    ArtifactManifest,
    BuildPaths,
    BuildReport,
    CompilerConfig,
    ContainerConfig,
    NuitkaConfig,
    OutputConfig,
    StepResult,
    VolumeMount,
    build_nuitka_command,
    compute_sha256,
    generate_checksum_file,
    verify_checksum_file,
)


class TestModels:
    """测试数据模型."""

    def test_compute_sha256(self, tmp_path):
        """测试 SHA256 计算."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        hash_value = compute_sha256(test_file)
        assert len(hash_value) == 64
        assert hash_value == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_volume_mount(self):
        """测试卷挂载配置."""
        mount = VolumeMount(
            host_path=Path("/host/path"),
            container_path="/container/path",
            readonly=True,
        )
        assert mount.readonly is True
        # Use as_posix() for cross-platform compatibility
        assert mount.host_path.as_posix() == "/host/path"

    def test_container_config(self):
        """测试容器配置."""
        config = ContainerConfig(
            image="python:3.13",
            name_prefix="test_build",
            env={"DEBUG": "1"},
        )
        assert config.image == "python:3.13"
        assert config.env["DEBUG"] == "1"

    def test_build_paths(self, tmp_path):
        """测试构建路径."""
        paths = BuildPaths(
            source_dir=tmp_path / "src",
            output_dir=tmp_path / "output",
        )
        assert paths.wheels_dir == tmp_path / "output" / "wheels"
        assert paths.logs_dir == tmp_path / "output" / "logs"
        assert paths.tvm_output == tmp_path / "output" / "tvm"

    def test_step_result(self):
        """测试步骤结果."""
        result = StepResult(
            name="test_step",
            success=True,
            duration_seconds=10.5,
            output="Success",
        )
        assert result.success is True
        assert result.duration_seconds == 10.5

    def test_build_report(self, tmp_path):
        """测试构建报告."""
        report = BuildReport(run_id="test_123")
        report.steps.append(StepResult(
            name="step1",
            success=True,
            duration_seconds=5.0,
        ))
        report.steps.append(StepResult(
            name="step2",
            success=True,
            duration_seconds=10.0,
        ))

        assert report.success is True
        assert report.total_duration == 15.0

        # 测试 JSON 序列化
        json_path = tmp_path / "report.json"
        report.to_json(json_path)
        assert json_path.exists()

        data = json.loads(json_path.read_text())
        assert data["run_id"] == "test_123"
        assert len(data["steps"]) == 2

        # 测试从 JSON 加载
        loaded_report = BuildReport.from_json(json_path)
        assert loaded_report.run_id == "test_123"
        assert len(loaded_report.steps) == 2


class TestNuitka:
    """测试 Nuitka 编译器配置."""

    def test_nuitka_config_basic(self):
        """测试基本配置."""
        config = NuitkaConfig(
            mode="module",
            compiler="clang",
            include_packages=["mypackage"],
        )
        args = config.to_args()

        assert "--mode=module" in args
        assert "--clang" in args
        assert "--include-package=mypackage" in args
        assert "--include-package-data=mypackage" in args

    def test_nuitka_config_complex(self):
        """测试复杂配置."""
        config = NuitkaConfig(
            mode="standalone",
            compiler="gcc",
            enabled_plugins=["dill-compat", "numpy"],
            follow_imports=["mypackage", "mylib"],
            nofollow_imports=["tests"],
            include_packages=["mypackage"],
            include_modules=["mypackage.dynamic"],
            compiler_config=CompilerConfig(jobs=4),
        )
        args = config.to_args()

        assert "--mode=standalone" in args
        # gcc 不需要显式标志
        assert "--clang" not in args
        assert "--enable-plugin=dill-compat" in args
        assert "--enable-plugin=numpy" in args
        assert "--follow-import-to=mypackage" in args
        assert "--nofollow-import-to=tests" in args
        assert "--include-module=mypackage.dynamic" in args
        assert "--jobs=4" in args

    def test_nuitka_config_output(self):
        """测试输出配置."""
        config = NuitkaConfig(
            mode="standalone",
            output=OutputConfig(
                output_dir="./dist",
                output_filename="myapp",
                remove_build=True,
            ),
        )
        args = config.to_args()

        assert "--output-dir=./dist" in args
        assert "--output-filename=myapp" in args
        assert "--remove-output" in args

    def test_nuitka_config_compilers(self):
        """测试不同编译器."""
        # Clang
        args = NuitkaConfig(compiler="clang").to_args()
        assert "--clang" in args

        # MSVC
        args = NuitkaConfig(compiler="msvc").to_args()
        assert "--msvc=latest" in args

        # MinGW
        args = NuitkaConfig(compiler="mingw64").to_args()
        assert "--mingw64" in args

        # Zig
        args = NuitkaConfig(compiler="zig").to_args()
        assert "--zig" in args

    def test_nuitka_config_with_helpers(self):
        """测试辅助方法."""
        config = NUITKA_MODULE

        # with_output
        new_config = config.with_output("./output")
        assert new_config.output.output_dir == "./output"

        # with_jobs
        new_config = config.with_jobs(8)
        assert new_config.compiler_config.jobs == 8

    def test_backward_compat_properties(self):
        """测试向后兼容属性."""
        config = NuitkaConfig(
            enabled_plugins=["dill-compat", "numpy"],
            compiler_config=CompilerConfig(jobs=4),
        )

        # plugins 属性返回 enabled_plugins
        assert config.plugins == ["dill-compat", "numpy"]
        # jobs 属性返回 compiler_config.jobs
        assert config.jobs == 4

    def test_build_nuitka_command(self):
        """测试命令构建辅助函数."""
        config = NuitkaConfig(
            mode="standalone",
            include_packages=["tvm"],
        )
        cmd = build_nuitka_command(config, "tvm")

        assert cmd[0] == "python"
        assert cmd[1] == "-m"
        assert cmd[2] == "nuitka"
        assert "--mode=standalone" in cmd
        assert cmd[-1] == "tvm"

    def test_predefined_templates(self):
        """测试预定义模板."""
        assert NUITKA_MODULE.mode == "module"
        assert NUITKA_STANDALONE.mode == "standalone"
        assert NUITKA_ACCELERATED.mode == "accelerated"

    def test_standard_plugins(self):
        """测试标准插件列表."""
        assert "dill-compat" in STANDARD_PLUGINS
        assert "numpy" in STANDARD_PLUGINS
        assert "torch" in STANDARD_PLUGINS


class TestArtifacts:
    """测试产物管理."""

    def test_artifact_entry_from_file(self, tmp_path):
        """测试从文件创建产物条目."""
        test_file = tmp_path / "test.whl"
        test_file.write_text("fake wheel content")

        entry = ArtifactEntry.from_file(test_file, base_dir=tmp_path)
        assert entry.path == "test.whl"
        assert entry.size_bytes == len("fake wheel content")
        assert len(entry.sha256) == 64

    def test_artifact_manifest(self, tmp_path):
        """测试产物清单."""
        manifest = ArtifactManifest(
            created_at=datetime.now().isoformat(),
            run_id="build_123",
        )

        # 添加产物
        file1 = tmp_path / "file1.txt"
        file1.write_text("content1")
        file2 = tmp_path / "file2.txt"
        file2.write_text("content2")

        manifest.add_artifact(file1, base_dir=tmp_path)
        manifest.add_artifact(file2, base_dir=tmp_path)

        assert len(manifest.artifacts) == 2

        # 保存清单
        manifest_path = tmp_path / "manifest.json"
        manifest.to_json(manifest_path)
        assert manifest_path.exists()

        # 从 JSON 加载
        loaded = ArtifactManifest.from_json(manifest_path)
        assert loaded.run_id == "build_123"
        assert len(loaded.artifacts) == 2

        # 验证产物
        success, errors = ArtifactManifest.verify(manifest_path)
        assert success is True
        assert len(errors) == 0

    def test_artifact_manifest_verify_failure(self, tmp_path):
        """测试产物验证失败场景."""
        manifest = ArtifactManifest(
            created_at=datetime.now().isoformat(),
            run_id="build_456",
        )

        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")
        manifest.add_artifact(test_file, base_dir=tmp_path)

        manifest_path = tmp_path / "manifest.json"
        manifest.to_json(manifest_path)

        # 修改文件内容
        test_file.write_text("modified content")

        # 验证应该失败
        success, errors = ArtifactManifest.verify(manifest_path)
        assert success is False
        assert len(errors) > 0

    def test_checksum_file(self, tmp_path):
        """测试校验文件生成和验证."""
        test_file = tmp_path / "data.bin"
        test_file.write_bytes(b"binary data")

        # 生成校验文件
        checksum_path = generate_checksum_file(test_file)
        assert checksum_path.exists()
        assert checksum_path.suffix == ".sha256"

        # 验证校验文件
        success, message = verify_checksum_file(checksum_path)
        assert success is True

        # 修改文件后验证失败
        test_file.write_bytes(b"modified data")
        success, message = verify_checksum_file(checksum_path)
        assert success is False


class TestIntegration:
    """集成测试."""

    def test_complete_build_workflow(self, tmp_path):
        """测试完整的构建工作流."""
        # 1. 创建构建路径
        paths = BuildPaths(
            source_dir=tmp_path / "src",
            output_dir=tmp_path / "output",
        )
        paths.output_dir.mkdir(parents=True, exist_ok=True)

        # 2. 配置 Nuitka
        nuitka_config = NuitkaConfig(
            mode="module",
            include_packages=["mypackage"],
            compiler_config=CompilerConfig(jobs=4),
        )
        args = nuitka_config.to_args()
        assert len(args) > 0

        # 3. 创建构建报告
        report = BuildReport(run_id="integration_test")

        # 4. 模拟编译步骤
        report.steps.append(StepResult(
            name="compile",
            success=True,
            duration_seconds=120.0,
            output="Compilation successful",
        ))

        # 5. 创建产物
        wheel_file = paths.wheels_dir / "mypackage-1.0.0-py3-none-any.whl"
        wheel_file.parent.mkdir(parents=True, exist_ok=True)
        wheel_file.write_text("fake wheel")
        report.wheels.append(wheel_file)

        # 6. 创建产物清单
        manifest = ArtifactManifest(
            created_at=datetime.now().isoformat(),
            run_id=report.run_id,
        )
        manifest.add_artifact(wheel_file, base_dir=paths.output_dir)
        manifest_path = manifest.to_json(paths.output_dir / "manifest.json")

        # 7. 保存构建报告
        report.end_time = datetime.now().isoformat()
        report.environment = {"python_version": "3.13"}
        report.to_json(paths.reports_dir / "report.json")

        # 8. 验证产物
        success, errors = ArtifactManifest.verify(manifest_path)
        assert success is True

        # 9. 验证报告
        assert report.success is True
        assert report.total_duration == 120.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
