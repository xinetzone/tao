"""``world install`` 子命令集成测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from taolib.cli.world import main

# ---------------------------------------------------------------------------
# 辅助：创建 .agents/world.toml
# ---------------------------------------------------------------------------

_WORLD_TOML = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"
min-alpha = 0.1

[fragments.my-fragment]
version = "1.0.0"
description = "An already-installed fragment"
optional = true

[capabilities]
skills = "skills/"
templates = "templates/"
"""

_WORLD_TOML_EMPTY_FRAGMENTS = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"
"""


def _write_world_toml(tmp_path: Path, content: str = _WORLD_TOML) -> Path:
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    toml_path = agents_dir / "world.toml"
    toml_path.write_text(content, encoding="utf-8")
    return toml_path


# ---------------------------------------------------------------------------
# 辅助：创建 fragment 源目录（含 manifest.toml）
# ---------------------------------------------------------------------------

_MANIFEST_PASS = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "3.0.0"

[fragment.dependencies]

[fragment.conflicts]

[fragment.contents]
rules = ["rules/new-rule.md"]
"""

_MANIFEST_KERNEL_FAIL = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "5.0.0"
max-version = "9.0.0"

[fragment.dependencies]

[fragment.conflicts]

[fragment.contents]
rules = []
"""

_MANIFEST_CONFLICT_FAIL = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "3.0.0"

[fragment.dependencies]

[fragment.conflicts]
my-fragment = "*"

[fragment.contents]
rules = []
"""

_MANIFEST_DEP_MISSING = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "3.0.0"

[fragment.dependencies]
missing-dep = "*"

[fragment.conflicts]

[fragment.contents]
rules = []
"""

_MANIFEST_FILE_CONFLICT = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "3.0.0"

[fragment.dependencies]

[fragment.conflicts]

[fragment.contents]
rules = ["rules/existing-file.md"]
"""


def _make_fragment_dir(tmp_path: Path, name: str, manifest_content: str) -> Path:
    """在 tmp_path/<name>/ 下创建含 manifest.toml 的 fragment 目录。"""
    frag_dir = tmp_path / name
    frag_dir.mkdir(parents=True, exist_ok=True)
    (frag_dir / "manifest.toml").write_text(manifest_content, encoding="utf-8")
    return frag_dir


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------


def test_install_dry_run_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """兼容的 manifest + world.toml，--dry-run 输出 PASS 并返回 0。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    frag_dir = _make_fragment_dir(tmp_path, "my-frag", _MANIFEST_PASS)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir), "--dry-run"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "PASS" in out


def test_install_dry_run_kernel_compat_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """manifest 要求 kernel >=5.0.0 但 world version=2.0.0，验证 L1 FAIL 返回 2。"""
    _write_world_toml(tmp_path)
    frag_dir = _make_fragment_dir(tmp_path, "my-frag", _MANIFEST_KERNEL_FAIL)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir), "--dry-run"])

    assert rc == 2
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "L1" in out


def test_install_dry_run_conflict_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """manifest conflicts 包含已安装 fragment，验证 L2 FAIL 返回 2。"""
    _write_world_toml(tmp_path)
    frag_dir = _make_fragment_dir(tmp_path, "my-frag", _MANIFEST_CONFLICT_FAIL)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir), "--dry-run"])

    assert rc == 2
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "L2" in out


def test_install_dry_run_dependency_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """manifest 依赖未安装的 fragment，验证 L3 FAIL 返回 2。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    frag_dir = _make_fragment_dir(tmp_path, "my-frag", _MANIFEST_DEP_MISSING)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir), "--dry-run"])

    assert rc == 2
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "L3" in out


def test_install_dry_run_file_conflict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """manifest contents 中的文件已存在于 .agents/，验证 L4 FAIL 返回 2。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    # 预先在 .agents/ 创建冲突文件
    conflict_file = tmp_path / ".agents" / "rules" / "existing-file.md"
    conflict_file.parent.mkdir(parents=True, exist_ok=True)
    conflict_file.write_text("existing content", encoding="utf-8")

    frag_dir = _make_fragment_dir(tmp_path, "my-frag", _MANIFEST_FILE_CONFLICT)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir), "--dry-run"])

    assert rc == 2
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "L4" in out


def test_install_without_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """不加 --dry-run 但校验失败时（这里使用 conflict_fail manifest），返回 2。"""
    _write_world_toml(tmp_path)
    frag_dir = _make_fragment_dir(tmp_path, "my-frag", _MANIFEST_CONFLICT_FAIL)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir)])

    assert rc == 2


def test_install_invalid_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """source 路径不存在，验证返回 1。"""
    _write_world_toml(tmp_path)
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(tmp_path / "nonexistent-dir"), "--dry-run"])

    assert rc == 1


# ---------------------------------------------------------------------------
# 实际安装流程测试（Task 14/15）
# ---------------------------------------------------------------------------

_MANIFEST_INSTALL_BASIC = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "5.0.0"

[fragment.contents]
rules = ["rules/test-rule.md"]
"""

_MANIFEST_INSTALL_WITH_HOOK = """\
[fragment]
name = "test-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "5.0.0"

[fragment.contents]
rules = ["rules/test-rule.md"]

[fragment.hooks]
post-install = "echo done"
"""


def _create_fragment_source(
    tmp_path: Path,
    manifest_content: str,
    files: dict[str, str] | None = None,
    name: str = "my-fragment",
) -> Path:
    """创建 fragment 源目录，含 manifest.toml 和可选的源文件。"""
    frag_dir = tmp_path / name
    frag_dir.mkdir()
    (frag_dir / "manifest.toml").write_text(manifest_content, encoding="utf-8")
    if files:
        for rel_path, content in files.items():
            p = frag_dir / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    return frag_dir


def test_install_actual_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """实际安装：文件被复制到 .agents/，world.toml 中新增 fragment 条目。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    frag_dir = _create_fragment_source(
        tmp_path,
        _MANIFEST_INSTALL_BASIC,
        files={"rules/test-rule.md": "# Test Rule\n"},
    )
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir)])

    assert rc == 0

    target = tmp_path / ".agents" / "rules" / "test-rule.md"
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "# Test Rule\n"

    world_toml = (tmp_path / ".agents" / "world.toml").read_text(encoding="utf-8")
    assert "[fragments.test-fragment]" in world_toml
    assert 'version = "1.0.0"' in world_toml


def test_install_actual_with_force(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """--force 模式下覆盖已存在的目标文件，返回 0。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    # 预先创建冲突文件
    conflict = tmp_path / ".agents" / "rules" / "test-rule.md"
    conflict.parent.mkdir(parents=True, exist_ok=True)
    conflict.write_text("OLD", encoding="utf-8")

    frag_dir = _create_fragment_source(
        tmp_path,
        _MANIFEST_INSTALL_BASIC,
        files={"rules/test-rule.md": "# Test Rule\n"},
    )
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir), "--force"])

    assert rc == 0
    assert conflict.read_text(encoding="utf-8") == "# Test Rule\n"


def test_install_rollback_on_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """register_fragment 抛异常时，已复制的文件被回滚清理。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    frag_dir = _create_fragment_source(
        tmp_path,
        _MANIFEST_INSTALL_BASIC,
        files={"rules/test-rule.md": "# Test Rule\n"},
    )
    monkeypatch.chdir(tmp_path)

    def _boom(*args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise RuntimeError("simulated registration failure")

    monkeypatch.setattr(
        "taolib.cli._world_commands.install.register_fragment",
        _boom,
    )

    rc = main(["install", str(frag_dir)])

    assert rc == 1
    target = tmp_path / ".agents" / "rules" / "test-rule.md"
    assert not target.exists(), "回滚后目标文件不应残留"


def test_install_hooks_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """manifest 中含 post-install hook，安装成功后 hook 被执行（不影响结果）。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    frag_dir = _create_fragment_source(
        tmp_path,
        _MANIFEST_INSTALL_WITH_HOOK,
        files={"rules/test-rule.md": "# Test Rule\n"},
    )
    monkeypatch.chdir(tmp_path)

    called: list[tuple[str, str]] = []

    def _fake_execute(manifest, agents_dir, phase, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        called.append((manifest.name, phase))
        return True

    monkeypatch.setattr(
        "taolib.cli._world_commands.install.execute_lifecycle_hooks",
        _fake_execute,
    )

    rc = main(["install", str(frag_dir)])

    assert rc == 0
    assert ("test-fragment", "post-install") in called


def test_install_registers_in_world_toml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """安装后 world.toml 包含 [fragments.test-fragment] 段且版本正确。"""
    _write_world_toml(tmp_path, _WORLD_TOML_EMPTY_FRAGMENTS)
    frag_dir = _create_fragment_source(
        tmp_path,
        _MANIFEST_INSTALL_BASIC,
        files={"rules/test-rule.md": "# Test Rule\n"},
    )
    monkeypatch.chdir(tmp_path)

    rc = main(["install", str(frag_dir)])

    assert rc == 0
    world_toml = (tmp_path / ".agents" / "world.toml").read_text(encoding="utf-8")
    assert "[fragments.test-fragment]" in world_toml
    assert 'version = "1.0.0"' in world_toml
    assert 'description = "A test fragment"' in world_toml
