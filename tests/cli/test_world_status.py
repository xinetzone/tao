"""``world status`` 子命令集成测试。"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from taolib.cli.world import main

_WORLD_TOML = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"
min-alpha = 0.1

[fragments.my-fragment]
version = "1.0.0"
description = "A test fragment"
optional = true
contents = ["rules/test.md"]

[capabilities]
skills = "skills/"
templates = "templates/"
"""


def _write_world_toml(tmp_path: Path, content: str = _WORLD_TOML) -> Path:
    """在 tmp_path/.agents/world.toml 写入 TOML 内容并返回路径。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    toml_path = agents_dir / "world.toml"
    toml_path.write_text(content, encoding="utf-8")
    return toml_path


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------


def test_status_finds_world_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """status 能找到 world.toml 并输出世界名称和版本。"""
    _write_world_toml(tmp_path)
    monkeypatch.chdir(tmp_path)

    rc = main(["status"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "test-world" in out
    assert "2.0.0" in out


def test_status_shows_fragments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """status 输出包含 fragment 名称和版本。"""
    _write_world_toml(tmp_path)
    monkeypatch.chdir(tmp_path)

    rc = main(["status"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "my-fragment" in out
    assert "1.0.0" in out


def test_status_shows_capabilities(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """status 输出包含 capabilities 信息。"""
    _write_world_toml(tmp_path)
    monkeypatch.chdir(tmp_path)

    rc = main(["status"])

    assert rc == 0
    out = capsys.readouterr().out
    # capabilities 部分应出现 skills 或 templates
    assert "skills" in out or "templates" in out


def test_status_missing_world_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """无 world.toml 时 status 退出码为 1。"""
    monkeypatch.chdir(tmp_path)

    rc = main(["status"])

    assert rc == 1


def test_status_no_args_returns_zero(capsys: pytest.CaptureFixture) -> None:
    """不传子命令时 main() 打印帮助并返回 0。"""
    rc = main([])
    assert rc == 0
