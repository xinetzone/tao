"""Tests for rate limiter configuration."""

import os
from unittest.mock import patch

from taolib.rate_limiter.config import (
    RateLimitConfig,
    _apply_env_overrides,
    load_rate_limit_config,
)
from taolib.rate_limiter.models import PathRule, WhitelistConfig


class TestRateLimitConfig:
    """Test RateLimitConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RateLimitConfig()
        assert config.enabled is True
        assert config.default_limit == 100
        assert config.window_seconds == 60
        assert config.redis_url == "redis://localhost:6379/1"
        assert config.mongo_violation_ttl_days == 90

    def test_custom_config(self):
        """Test custom configuration."""
        config = RateLimitConfig(
            enabled=False,
            default_limit=50,
            window_seconds=120,
        )
        assert config.enabled is False
        assert config.default_limit == 50
        assert config.window_seconds == 120

    def test_path_rules(self):
        """Test path-specific rules."""
        config = RateLimitConfig(
            path_rules={
                "/api/auth": PathRule(
                    limit=5,
                    window_seconds=60,
                    methods=["POST"],
                ),
            }
        )
        assert "/api/auth" in config.path_rules
        assert config.path_rules["/api/auth"].limit == 5

    def test_whitelist(self):
        """Test whitelist configuration."""
        config = RateLimitConfig(
            whitelist=WhitelistConfig(
                ips=["127.0.0.1", "10.0.0.0/8"],
                user_ids=["admin"],
                bypass_paths=["/health"],
            )
        )
        assert len(config.whitelist.ips) == 2
        assert len(config.whitelist.user_ids) == 1
        assert "/health" in config.whitelist.bypass_paths

    def test_from_toml_nonexistent_file(self):
        """Test loading from non-existent file returns default config."""
        config = RateLimitConfig.from_toml("/nonexistent/path.toml")
        assert config is not None
        assert isinstance(config, RateLimitConfig)

    def test_from_toml_valid_file(self, tmp_path):
        """Test loading from valid TOML file."""
        toml_content = """
[rate_limit]
enabled = true
default_limit = 200
window_seconds = 120
redis_url = "redis://localhost:6379/2"
"""
        config_file = tmp_path / "test_config.toml"
        config_file.write_text(toml_content)

        config = RateLimitConfig.from_toml(str(config_file))
        assert config.enabled is True
        assert config.default_limit == 200
        assert config.window_seconds == 120
        assert config.redis_url == "redis://localhost:6379/2"


class TestEnvOverrides:
    """Test environment variable overrides."""

    def test_apply_env_overrides_no_env(self):
        """Test no environment variables set."""
        config = RateLimitConfig(default_limit=100)
        result = _apply_env_overrides(config)
        assert result.default_limit == 100

    def test_apply_env_overrides_enabled(self):
        """Test TAOLIB_RATE_LIMIT_ENABLED override."""
        with patch.dict(os.environ, {"TAOLIB_RATE_LIMIT_ENABLED": "false"}):
            config = RateLimitConfig()
            result = _apply_env_overrides(config)
            assert result.enabled is False

    def test_apply_env_overrides_enabled_true(self):
        """Test TAOLIB_RATE_LIMIT_ENABLED with true value."""
        with patch.dict(os.environ, {"TAOLIB_RATE_LIMIT_ENABLED": "1"}):
            config = RateLimitConfig(enabled=False)
            result = _apply_env_overrides(config)
            assert result.enabled is True

    def test_apply_env_overrides_limit(self):
        """Test TAOLIB_RATE_LIMIT_DEFAULT_LIMIT override."""
        with patch.dict(os.environ, {"TAOLIB_RATE_LIMIT_DEFAULT_LIMIT": "500"}):
            config = RateLimitConfig()
            result = _apply_env_overrides(config)
            assert result.default_limit == 500

    def test_apply_env_overrides_window(self):
        """Test TAOLIB_RATE_LIMIT_WINDOW_SECONDS override."""
        with patch.dict(os.environ, {"TAOLIB_RATE_LIMIT_WINDOW_SECONDS": "300"}):
            config = RateLimitConfig()
            result = _apply_env_overrides(config)
            assert result.window_seconds == 300

    def test_apply_env_overrides_redis_url(self):
        """Test TAOLIB_RATE_LIMIT_REDIS_URL override."""
        with patch.dict(os.environ, {"TAOLIB_RATE_LIMIT_REDIS_URL": "redis://custom:6379/0"}):
            config = RateLimitConfig()
            result = _apply_env_overrides(config)
            assert result.redis_url == "redis://custom:6379/0"

    def test_apply_env_overrides_multiple(self):
        """Test multiple environment variables."""
        with patch.dict(os.environ, {
            "TAOLIB_RATE_LIMIT_ENABLED": "true",
            "TAOLIB_RATE_LIMIT_DEFAULT_LIMIT": "1000",
            "TAOLIB_RATE_LIMIT_WINDOW_SECONDS": "600",
        }):
            config = RateLimitConfig()
            result = _apply_env_overrides(config)
            assert result.enabled is True
            assert result.default_limit == 1000
            assert result.window_seconds == 600


class TestLoadRateLimitConfig:
    """Test load_rate_limit_config function."""

    def test_explicit_path(self, tmp_path):
        """Test loading from explicitly provided path."""
        toml_content = """
[rate_limit]
default_limit = 999
"""
        config_file = tmp_path / "explicit_config.toml"
        config_file.write_text(toml_content)

        config = load_rate_limit_config(config_path=str(config_file))
        assert config.default_limit == 999

    def test_env_variable_path(self, tmp_path):
        """Test loading from environment variable path."""
        toml_content = """
[rate_limit]
default_limit = 888
"""
        config_file = tmp_path / "env_config.toml"
        config_file.write_text(toml_content)

        with patch.dict(os.environ, {"TAOLIB_RATE_LIMIT_CONFIG": str(config_file)}):
            config = load_rate_limit_config()
            assert config.default_limit == 888

    def test_no_config_file_returns_defaults(self):
        """Test returning defaults when no config file exists."""
        # Ensure no env var is set
        env_copy = os.environ.copy()
        if "TAOLIB_RATE_LIMIT_CONFIG" in env_copy:
            del env_copy["TAOLIB_RATE_LIMIT_CONFIG"]

        with patch.dict(os.environ, env_copy, clear=True):
            # Mock Path.exists to return False for all default paths
            with patch("pathlib.Path.exists", return_value=False):
                config = load_rate_limit_config()
                assert config.default_limit == 100
                assert config.window_seconds == 60
