"""taolib.testing.auth 测试共享 fixtures。"""

from datetime import timedelta

import pytest

from taolib.testing.auth.blacklist import InMemoryTokenBlacklist
from taolib.testing.auth.config import AuthConfig
from taolib.testing.auth.models import AuthenticatedUser
from taolib.testing.auth.tokens import JWTService


@pytest.fixture
def auth_config() -> AuthConfig:
    """测试用认证配置。"""
    return AuthConfig(
        jwt_secret="test-secret-key-for-unit-tests",
        jwt_algorithm="HS256",
        access_token_ttl=timedelta(hours=1),
        refresh_token_ttl=timedelta(days=30),
        token_issuer="test-issuer",
        blacklist_key_prefix="test:auth:blacklist:",
    )


@pytest.fixture
def jwt_service(auth_config: AuthConfig) -> JWTService:
    """测试用 JWT 服务实例。"""
    return JWTService(auth_config)


@pytest.fixture
def memory_blacklist() -> InMemoryTokenBlacklist:
    """测试用内存黑名单。"""
    return InMemoryTokenBlacklist()


@pytest.fixture
def sample_user() -> AuthenticatedUser:
    """测试用已认证用户。"""
    return AuthenticatedUser(
        user_id="user-123",
        roles=["config_admin", "auditor"],
        auth_method="jwt",
        metadata={"jti": "test-jti-001"},
    )


@pytest.fixture
def api_key_user() -> AuthenticatedUser:
    """测试用 API Key 用户。"""
    return AuthenticatedUser(
        user_id="service-bot",
        roles=["config_viewer"],
        auth_method="api_key",
        metadata={"key_name": "ci-deploy-key"},
    )



