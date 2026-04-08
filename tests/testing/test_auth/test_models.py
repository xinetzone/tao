"""领域模型测试。"""

from datetime import UTC, datetime

import pytest

from taolib.testing.auth.models import AuthenticatedUser, TokenPair, TokenPayload


class TestTokenPayload:
    """测试 TokenPayload。"""

    def test_create(self):
        """测试创建实例。"""
        now = datetime.now(UTC)
        payload = TokenPayload(
            sub="user-123",
            roles=["admin"],
            exp=now,
            iat=now,
            type="access",
            jti="jti-001",
        )
        assert payload.sub == "user-123"
        assert payload.roles == ["admin"]
        assert payload.type == "access"
        assert payload.jti == "jti-001"

    def test_frozen(self):
        """测试不可变性。"""
        now = datetime.now(UTC)
        payload = TokenPayload(
            sub="user-123",
            roles=["admin"],
            exp=now,
            iat=now,
            type="access",
            jti="jti-001",
        )
        with pytest.raises(AttributeError):
            payload.sub = "changed"  # type: ignore[misc]


class TestAuthenticatedUser:
    """测试 AuthenticatedUser。"""

    def test_create_with_defaults(self):
        """测试使用默认值创建。"""
        user = AuthenticatedUser(
            user_id="user-123",
            roles=["admin"],
            auth_method="jwt",
        )
        assert user.metadata == {}

    def test_create_with_metadata(self):
        """测试带元数据创建。"""
        user = AuthenticatedUser(
            user_id="user-123",
            roles=["admin"],
            auth_method="api_key",
            metadata={"key_name": "deploy-key"},
        )
        assert user.metadata["key_name"] == "deploy-key"

    def test_frozen(self):
        """测试不可变性。"""
        user = AuthenticatedUser(
            user_id="user-123",
            roles=["admin"],
            auth_method="jwt",
        )
        with pytest.raises(AttributeError):
            user.user_id = "changed"  # type: ignore[misc]


class TestTokenPair:
    """测试 TokenPair。"""

    def test_create_with_defaults(self):
        """测试使用默认值创建。"""
        pair = TokenPair(
            access_token="access-xxx",
            refresh_token="refresh-xxx",
        )
        assert pair.token_type == "bearer"
        assert pair.expires_in == 3600

    def test_custom_expires(self):
        """测试自定义过期时间。"""
        pair = TokenPair(
            access_token="access-xxx",
            refresh_token="refresh-xxx",
            expires_in=1800,
        )
        assert pair.expires_in == 1800



