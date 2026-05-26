"""``world remove`` 子命令单元测试。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from taolib.cli._world_commands.remove import handle_remove, register_remove_parser

# ---------------------------------------------------------------------------
# 辅助工具
# ---------------------------------------------------------------------------

_WORLD_TOML_WITH_FRAGMENT = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"

[fragments.citations]
version = "1.2.0"
description = "Citations fragment"
optional = true
contents = ["rules/citations.md"]

[capabilities]
skills = "skills/"
"""

_WORLD_TOML_WITH_DEPENDENT = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"

[fragments.citations]
version = "1.2.0"
description = "Citations fragment"
optional = true
contents = ["rules/citations.md"]

[fragments.academic]
version = "1.0.0"
description = "Academic writing — depends on citations"
optional = true
contents = ["rules/academic.md"]

[capabilities]
skills = "skills/"
"""


def _setup_world(tmp_path: Path, content: str) -> Path:
    """创建 .agents/world.toml 并返回 world.toml 路径。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    world_toml = agents_dir / "world.toml"
    world_toml.write_text(content, encoding="utf-8")
    return world_toml


def _create_fragment_files(tmp_path: Path, rel_paths: list[str]) -> None:
    """在 .agents/ 目录下创建 fragment 对应文件。"""
    agents_dir = tmp_path / ".agents"
    for rel in rel_paths:
        f = agents_dir / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"# {rel}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------


def test_remove_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """正常卸载：文件被删除，world.toml 中该段已移除。"""
    _setup_world(tmp_path, _WORLD_TOML_WITH_FRAGMENT)
    _create_fragment_files(tmp_path, ["rules/citations.md"])
    monkeypatch.chdir(tmp_path)

    args = argparse.Namespace(name="citations", force=False, keep_files=False)
    rc = handle_remove(args)

    assert rc == 0

    # 验证文件已删除
    assert not (tmp_path / ".agents" / "rules" / "citations.md").exists()

    # 验证 world.toml 中段已移除
    text = (tmp_path / ".agents" / "world.toml").read_text(encoding="utf-8")
    assert "[fragments.citations]" not in text


def test_remove_not_installed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """目标未安装时返回 1。"""
    _setup_world(tmp_path, _WORLD_TOML_WITH_FRAGMENT)
    monkeypatch.chdir(tmp_path)

    args = argparse.Namespace(name="nonexistent", force=False, keep_files=False)
    rc = handle_remove(args)

    assert rc == 1


def test_remove_dependent_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """依赖者阻断：其他 Fragment 引用了目标名称时返回 2。"""
    _setup_world(tmp_path, _WORLD_TOML_WITH_DEPENDENT)
    _create_fragment_files(tmp_path, ["rules/citations.md", "rules/academic.md"])
    monkeypatch.chdir(tmp_path)

    args = argparse.Namespace(name="citations", force=False, keep_files=False)
    rc = handle_remove(args)

    assert rc == 2

    # 文件仍然存在
    assert (tmp_path / ".agents" / "rules" / "citations.md").exists()


def test_remove_force_skips_dependents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--force 跳过依赖者检查，返回 0。"""
    _setup_world(tmp_path, _WORLD_TOML_WITH_DEPENDENT)
    _create_fragment_files(tmp_path, ["rules/citations.md", "rules/academic.md"])
    monkeypatch.chdir(tmp_path)

    args = argparse.Namespace(name="citations", force=True, keep_files=False)
    rc = handle_remove(args)

    assert rc == 0

    # 文件已删除
    assert not (tmp_path / ".agents" / "rules" / "citations.md").exists()

    # world.toml 中段已移除
    text = (tmp_path / ".agents" / "world.toml").read_text(encoding="utf-8")
    assert "[fragments.citations]" not in text


def test_remove_keep_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--keep-files 仅注销，保留文件。"""
    _setup_world(tmp_path, _WORLD_TOML_WITH_FRAGMENT)
    _create_fragment_files(tmp_path, ["rules/citations.md"])
    monkeypatch.chdir(tmp_path)

    args = argparse.Namespace(name="citations", force=False, keep_files=True)
    rc = handle_remove(args)

    assert rc == 0

    # 文件仍然保留
    assert (tmp_path / ".agents" / "rules" / "citations.md").exists()

    # 但 world.toml 中段已注销
    text = (tmp_path / ".agents" / "world.toml").read_text(encoding="utf-8")
    assert "[fragments.citations]" not in text


# ---------------------------------------------------------------------------
# register_remove_parser
# ---------------------------------------------------------------------------


def test_register_remove_parser() -> None:
    """验证 parser 注册后包含 name, --force, --keep-files。"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_remove_parser(subparsers)

    args = parser.parse_args(["remove", "citations", "--force", "--keep-files"])
    assert args.name == "citations"
    assert args.force is True
    assert args.keep_files is True
