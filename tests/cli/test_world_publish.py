"""``world publish`` 子命令单元测试。"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from taolib.cli._world_commands.publish import handle_publish, register_publish_parser

# ---------------------------------------------------------------------------
# 辅助工具
# ---------------------------------------------------------------------------

_WORLD_TOML = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"
"""

_REGISTRY_TOML_TEMPLATE = """\
[registries.local]
url = "{index_path}"
type = "git"
priority = 0
"""

_MANIFEST_VALID = """\
[fragment]
name = "my-fragment"
version = "1.0.0"
description = "A test fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "3.0.0"

[fragment.contents]
rules = ["rules/test.md"]
"""

_MANIFEST_NO_NAME = """\
[fragment]
version = "1.0.0"
description = "A test fragment"

[fragment.contents]
rules = []
"""

_INDEX_EXISTING = """\
[metadata]
name = "my-fragment"
description = "A test fragment"
category = "my"
type = "fragment"

[source]
repository = "https://github.com/org/repo"

[[versions]]
version = "1.0.0"
git_url = "https://github.com/org/repo"
git_ref = "v1.0.0"
manifest_path = "manifest.toml"
yanked = false

[latest]
stable = "1.0.0"
"""


def _setup_world(tmp_path: Path) -> Path:
    """创建 .agents/world.toml 并返回 agents_dir。"""
    agents_dir = tmp_path / "project" / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "world.toml").write_text(_WORLD_TOML, encoding="utf-8")
    return agents_dir


def _setup_registry(agents_dir: Path, index_path: Path) -> None:
    """创建 registry.toml。"""
    content = _REGISTRY_TOML_TEMPLATE.format(
        index_path=str(index_path).replace("\\", "/")
    )
    (agents_dir / "registry.toml").write_text(content, encoding="utf-8")


def _make_component(
    tmp_path: Path, manifest: str, files: dict[str, str] | None = None
) -> Path:
    """创建组件目录含 manifest.toml 和可选文件。"""
    comp_dir = tmp_path / "component"
    comp_dir.mkdir(parents=True, exist_ok=True)
    (comp_dir / "manifest.toml").write_text(manifest, encoding="utf-8")
    if files:
        for rel, content in files.items():
            p = comp_dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    return comp_dir


def _create_empty_index(tmp_path: Path) -> Path:
    """创建空 registry-index。"""
    index_root = tmp_path / "mock-index"
    (index_root / "fragments").mkdir(parents=True, exist_ok=True)
    return index_root


def _create_index_with_entry(tmp_path: Path) -> Path:
    """创建含已有条目的 registry-index。"""
    index_root = tmp_path / "mock-index"
    my_dir = index_root / "fragments" / "my"
    my_dir.mkdir(parents=True, exist_ok=True)
    (my_dir / "my-fragment.toml").write_text(_INDEX_EXISTING, encoding="utf-8")
    return index_root


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------


def test_publish_manifest_not_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """manifest 不存在时返回 1。"""
    agents_dir = _setup_world(tmp_path)
    monkeypatch.chdir(agents_dir.parent)

    # 空目录，无 manifest.toml
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    args = argparse.Namespace(
        path=str(empty_dir), registry=None, tag=None, dry_run=False
    )
    rc = handle_publish(args)
    assert rc == 1


def test_publish_manifest_missing_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """manifest 缺少 name 字段时返回 1。"""
    agents_dir = _setup_world(tmp_path)
    monkeypatch.chdir(agents_dir.parent)

    comp_dir = _make_component(tmp_path, _MANIFEST_NO_NAME)

    args = argparse.Namespace(
        path=str(comp_dir), registry=None, tag=None, dry_run=False
    )
    rc = handle_publish(args)
    assert rc == 1


def test_publish_contents_file_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """contents 声明的文件实际不存在时返回 1。"""
    agents_dir = _setup_world(tmp_path)
    index_path = _create_empty_index(tmp_path)
    _setup_registry(agents_dir, index_path)
    monkeypatch.chdir(agents_dir.parent)

    # manifest 声明 rules/test.md 但不创建该文件
    comp_dir = _make_component(tmp_path, _MANIFEST_VALID)
    # 不创建 rules/test.md

    args = argparse.Namespace(
        path=str(comp_dir), registry=None, tag=None, dry_run=False
    )
    rc = handle_publish(args)
    assert rc == 1


def test_publish_version_not_incremented(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """版本未递增（已有 1.0.0，新发布 1.0.0）时返回 1。"""
    agents_dir = _setup_world(tmp_path)
    index_path = _create_index_with_entry(tmp_path)
    _setup_registry(agents_dir, index_path)
    monkeypatch.chdir(agents_dir.parent)

    comp_dir = _make_component(
        tmp_path, _MANIFEST_VALID, files={"rules/test.md": "# test\n"}
    )

    # mock resolve_index_path 返回本地 index
    monkeypatch.setattr(
        "taolib.cli._world_commands.publish.resolve_index_path",
        lambda source, force_update=False: index_path,
    )

    args = argparse.Namespace(
        path=str(comp_dir), registry=None, tag=None, dry_run=False
    )
    rc = handle_publish(args)
    assert rc == 1


def test_publish_dry_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """--dry-run 模式合法 manifest 返回 0 且不调用 git。"""
    agents_dir = _setup_world(tmp_path)
    index_path = _create_empty_index(tmp_path)
    _setup_registry(agents_dir, index_path)
    monkeypatch.chdir(agents_dir.parent)

    comp_dir = _make_component(
        tmp_path, _MANIFEST_VALID, files={"rules/test.md": "# test\n"}
    )

    monkeypatch.setattr(
        "taolib.cli._world_commands.publish.resolve_index_path",
        lambda source, force_update=False: index_path,
    )

    args = argparse.Namespace(
        path=str(comp_dir), registry=None, tag=None, dry_run=True
    )

    with patch("subprocess.run") as mock_run:
        rc = handle_publish(args)

    assert rc == 0
    # subprocess.run 不应被调用
    mock_run.assert_not_called()

    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert "my-fragment" in out


def test_publish_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """正常发布：mock git 命令 → index 文件被更新。"""
    agents_dir = _setup_world(tmp_path)
    index_path = _create_empty_index(tmp_path)
    _setup_registry(agents_dir, index_path)
    monkeypatch.chdir(agents_dir.parent)

    # 使用 version 2.0.0 避免与已有条目冲突
    manifest_v2 = _MANIFEST_VALID.replace('version = "1.0.0"', 'version = "2.0.0"')
    comp_dir = _make_component(
        tmp_path, manifest_v2, files={"rules/test.md": "# test\n"}
    )

    monkeypatch.setattr(
        "taolib.cli._world_commands.publish.resolve_index_path",
        lambda source, force_update=False: index_path,
    )

    # mock subprocess.run 对 git tag/push 返回 0
    def _fake_subprocess_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        class FakeResult:
            returncode = 0
            stdout = ""
            stderr = ""
        return FakeResult()

    with patch("subprocess.run", side_effect=_fake_subprocess_run):
        args = argparse.Namespace(
            path=str(comp_dir), registry=None, tag=None, dry_run=False
        )
        rc = handle_publish(args)

    assert rc == 0

    # 验证 index 文件被创建
    entry_file = index_path / "fragments" / "my" / "my-fragment.toml"
    assert entry_file.exists()

    content = entry_file.read_text(encoding="utf-8")
    assert 'name = "my-fragment"' in content
    assert 'version = "2.0.0"' in content
    assert 'git_ref = "v2.0.0"' in content

    out = capsys.readouterr().out
    assert "已发布" in out


def test_publish_appends_to_existing_index(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """已有 index 条目时追加新版本。"""
    agents_dir = _setup_world(tmp_path)
    index_path = _create_index_with_entry(tmp_path)
    _setup_registry(agents_dir, index_path)
    monkeypatch.chdir(agents_dir.parent)

    # version 2.0.0 > existing 1.0.0
    manifest_v2 = _MANIFEST_VALID.replace('version = "1.0.0"', 'version = "2.0.0"')
    comp_dir = _make_component(
        tmp_path, manifest_v2, files={"rules/test.md": "# test\n"}
    )

    monkeypatch.setattr(
        "taolib.cli._world_commands.publish.resolve_index_path",
        lambda source, force_update=False: index_path,
    )

    def _fake_subprocess_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        class FakeResult:
            returncode = 0
            stdout = ""
            stderr = ""
        return FakeResult()

    with patch("subprocess.run", side_effect=_fake_subprocess_run):
        args = argparse.Namespace(
            path=str(comp_dir), registry=None, tag=None, dry_run=False
        )
        rc = handle_publish(args)

    assert rc == 0

    entry_file = index_path / "fragments" / "my" / "my-fragment.toml"
    content = entry_file.read_text(encoding="utf-8")
    assert 'version = "2.0.0"' in content
    assert 'stable = "2.0.0"' in content


# ---------------------------------------------------------------------------
# register_publish_parser
# ---------------------------------------------------------------------------


def test_register_publish_parser() -> None:
    """验证 parser 注册后包含 path, --registry, --tag, --dry-run。"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_publish_parser(subparsers)

    args = parser.parse_args(["publish", "./my-comp", "--dry-run", "--tag", "v1.0.0"])
    assert args.path == "./my-comp"
    assert args.dry_run is True
    assert args.tag == "v1.0.0"
