"""AuthConfig 测试。"""

from datetime import timedelta

import pytest

from taolib.testing.auth.config import AuthConfig


class TestAuthConfig:
    """测试 AuthConfig 配置。"""

    def test_create_with_required_secret(self):
        """测试使用必填密钥创建配置。"""
        config = AuthConfig(jwt_secret="my-secret")
        assert config.jwt_secret == "my-secret"

    def test_default_values(self):
        """测试默认配置值。"""
        config = AuthConfig(jwt_secret="my-secret")
        assert config.jwt_algorithm == "HS256"
        assert config.access_token_ttl == timedelta(hours=1)
        assert config.refresh_token_ttl == timedelta(days=30)
        assert config.token_issuer is None
        assert config.blacklist_key_prefix == "taolib:auth:blacklist:"

    def test_custom_values(self):
        """测试自定义配置值。"""
        config = AuthConfig(
            jwt_secret="custom-secret",
            jwt_algorithm="HS384",
            access_token_ttl=timedelta(minutes=30),
            refresh_token_ttl=timedelta(days=7),
            token_issuer="my-app",
            blacklist_key_prefix="app:bl:",
        )
        assert config.jwt_algorithm == "HS384"
        assert config.access_token_ttl == timedelta(minutes=30)
        assert config.refresh_token_ttl == timedelta(days=7)
        assert config.token_issuer == "my-app"
        assert config.blacklist_key_prefix == "app:bl:"

    def test_frozen_immutable(self):
        """测试配置不可变性。"""
        config = AuthConfig(jwt_secret="my-secret")
        with pytest.raises(AttributeError):
            config.jwt_secret = "changed"  # type: ignore[misc]

    def test_from_env(self, monkeypatch):
        """测试从环境变量创建配置。"""
        monkeypatch.setenv(
            "TAOLIB_AUTH_JWT_SECRET", "env-secret-key-that-is-long-enough-for-hs256"
        )
        monkeypatch.setenv("TAOLIB_AUTH_JWT_ALGORITHM", "HS384")
        monkeypatch.setenv("TAOLIB_AUTH_ACCESS_TOKEN_MINUTES", "30")
        monkeypatch.setenv("TAOLIB_AUTH_REFRESH_TOKEN_DAYS", "14")
        monkeypatch.setenv("TAOLIB_AUTH_TOKEN_ISSUER", "test-app")

        config = AuthConfig.from_env()
        assert config.jwt_secret == "env-secret-key-that-is-long-enough-for-hs256"
        assert config.jwt_algorithm == "HS384"
        assert config.access_token_ttl == timedelta(minutes=30)
        assert config.refresh_token_ttl == timedelta(days=14)
        assert config.token_issuer == "test-app"

    def test_from_env_custom_prefix(self, monkeypatch):
        """测试从自定义前缀环境变量创建配置。"""
        monkeypatch.setenv(
            "MY_APP_JWT_SECRET", "custom-env-secret-long-enough-for-hs256-validation"
        )
        config = AuthConfig.from_env(prefix="MY_APP_")
        assert config.jwt_secret == "custom-env-secret-long-enough-for-hs256-validation"

    def test_from_env_missing_secret_raises(self, monkeypatch):
        """测试缺少密钥环境变量时抛出 ValueError。"""
        monkeypatch.delenv("TAOLIB_AUTH_JWT_SECRET", raising=False)
        with pytest.raises(ValueError, match="JWT_SECRET"):
            AuthConfig.from_env()

    def test_from_env_defaults(self, monkeypatch):
        """测试从环境变量创建时使用默认值。"""
        monkeypatch.setenv(
            "TAOLIB_AUTH_JWT_SECRET", "a-secret-that-is-at-least-32-chars-long!"
        )
        config = AuthConfig.from_env()
        assert config.jwt_algorithm == "HS256"
        assert config.access_token_ttl == timedelta(hours=1)
        assert config.refresh_token_ttl == timedelta(days=30)

    def test_from_env_short_secret_raises(self, monkeypatch):
        """短密钥应抛出 ValueError。"""
        monkeypatch.setenv("TAOLIB_AUTH_JWT_SECRET", "too-short")
        with pytest.raises(ValueError, match="长度不足"):
            AuthConfig.from_env()



