"""配置合并与解析测试。"""

from pathlib import Path

import pytest

from taolib.symphony.config.resolver import (
    deep_merge,
    resolve_config,
    resolve_env_vars,
    resolve_paths,
)
from taolib.symphony.config.schema import SymphonyConfig


class TestDeepMerge:
    """测试 deep_merge 深度合并。"""

    def test_simple_merge(self) -> None:
        """基础合并：override 中的新键被加入。"""
        base = {"a": 1, "b": 2}
        override = {"c": 3}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_nested_merge(self) -> None:
        """嵌套字典递归合并。"""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}, "e": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}

    def test_override_scalar(self) -> None:
        """override 中的标量覆盖 base 中的同名键。"""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"c": 99}}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": {"c": 99}}

    def test_empty_override(self) -> None:
        """空 override 不影响 base。"""
        base = {"a": 1, "b": {"c": 2}}
        result = deep_merge(base, {})
        assert result == {"a": 1, "b": {"c": 2}}


class TestResolveEnvVars:
    """测试 resolve_env_vars 环境变量替换。"""

    def test_resolve_dollar_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """$VAR 形式的环境变量被正确替换。"""
        monkeypatch.setenv("TEST_SYM_KEY", "my-key-123")
        config = {"tracker": {"api_key": "$TEST_SYM_KEY", "kind": "linear"}}
        result = resolve_env_vars(config)
        assert result["tracker"]["api_key"] == "my-key-123"
        assert result["tracker"]["kind"] == "linear"

    def test_missing_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """缺失的环境变量保持原值。"""
        monkeypatch.delenv("MISSING_VAR", raising=False)
        config = {"tracker": {"api_key": "$MISSING_VAR"}}
        result = resolve_env_vars(config)
        assert result["tracker"]["api_key"] == "$MISSING_VAR"

    def test_nested_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """嵌套字典和列表中的 $VAR 均被替换。"""
        monkeypatch.setenv("NESTED_A", "value_a")
        monkeypatch.setenv("NESTED_B", "value_b")
        config = {
            "level1": {
                "level2": {
                    "key_a": "$NESTED_A",
                    "key_b": "$NESTED_B",
                },
                "list": ["$NESTED_A", "static"],
            },
        }
        result = resolve_env_vars(config)
        assert result["level1"]["level2"]["key_a"] == "value_a"
        assert result["level1"]["level2"]["key_b"] == "value_b"
        assert result["level1"]["list"] == ["value_a", "static"]


class TestResolvePaths:
    """测试 resolve_paths 路径解析。"""

    def test_tilde_expansion(self, tmp_path: Path) -> None:
        """~ 被展开为用户主目录。"""
        config = {"workspace": {"root": "~/symphony_tmp"}}
        result = resolve_paths(config, tmp_path)
        resolved = result["workspace"]["root"]
        assert isinstance(resolved, str)
        assert not resolved.startswith("~")
        assert Path(resolved).is_absolute()

    def test_relative_to_base(self, tmp_path: Path) -> None:
        """相对路径基于 base_dir 解析为绝对路径。"""
        config = {"workspace": {"root": "./workspaces"}}
        result = resolve_paths(config, tmp_path)
        resolved = result["workspace"]["root"]
        assert isinstance(resolved, str)
        assert Path(resolved).is_absolute()
        assert Path(resolved).name == "workspaces"


class TestResolveConfig:
    """测试 resolve_config 端到端组装。"""

    def test_full_resolution(
        self,
        tmp_path: Path,
        tmp_workflow_file: Path,
        tmp_toml_file: Path,
        env_vars: None,
    ) -> None:
        """CLI + env + workflow + toml 完整合并。"""
        cfg = resolve_config(
            cli_args={"port": 9090},
            toml_path=tmp_toml_file,
            workflow_path=tmp_workflow_file,
        )
        assert isinstance(cfg, SymphonyConfig)
        # env 变量替换
        assert cfg.tracker.api_key == "lin_api_xxx"
        # workflow 覆盖 toml
        assert cfg.tracker.project_slug == "test-proj"
        # CLI 覆盖
        assert cfg.server.port == 9090
        # toml 默认值
        assert cfg.tracker.kind == "linear"

    def test_cli_overrides(
        self,
        tmp_path: Path,
        tmp_workflow_file: Path,
        env_vars: None,
    ) -> None:
        """CLI 参数优先级最高。"""
        cfg = resolve_config(
            cli_args={"port": 8080},
            toml_path=None,
            workflow_path=tmp_workflow_file,
        )
        assert cfg.server.port == 8080

    def test_without_toml(
        self,
        tmp_path: Path,
        tmp_workflow_file: Path,
        env_vars: None,
    ) -> None:
        """无 toml 文件时正常工作。"""
        cfg = resolve_config(
            cli_args={},
            toml_path=None,
            workflow_path=tmp_workflow_file,
        )
        assert isinstance(cfg, SymphonyConfig)
        assert cfg.tracker.project_slug == "test-proj"
        assert cfg.polling.interval_ms == 5000
