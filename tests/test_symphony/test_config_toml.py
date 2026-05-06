"""TOML 配置加载器测试。"""

from pathlib import Path

import pytest

from taolib.symphony.config.toml_config import load_toml
from taolib.symphony.errors import ConfigError


class TestLoadToml:
    """测试 load_toml 加载行为。"""

    def test_load_defaults_section(self, tmp_path: Path) -> None:
        """正确提取 [defaults] 段内容。"""
        path = tmp_path / "symphony.toml"
        path.write_text(
            '[defaults.tracker]\n'
            'kind = "linear"\n'
            'project_slug = "from-toml"\n'
            '\n'
            '[defaults.polling]\n'
            'interval_ms = 10000\n',
            encoding="utf-8",
        )
        data = load_toml(path)
        assert data["tracker"]["kind"] == "linear"
        assert data["tracker"]["project_slug"] == "from-toml"
        assert data["polling"]["interval_ms"] == 10000

    def test_missing_defaults(self, tmp_path: Path) -> None:
        """无 [defaults] 段时返回空字典。"""
        path = tmp_path / "symphony.toml"
        path.write_text(
            '[other]\n'
            'key = "value"\n',
            encoding="utf-8",
        )
        data = load_toml(path)
        assert data == {}

    def test_file_not_found(self, tmp_path: Path) -> None:
        """文件不存在时抛出 ConfigError。"""
        path = tmp_path / "nonexistent.toml"
        with pytest.raises(ConfigError):
            load_toml(path)
