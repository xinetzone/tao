"""JWTService 测试。"""

from datetime import timedelta

import pytest
from jose import jwt

from taolib.auth.config import AuthConfig
from taolib.auth.errors import TokenExpiredError, TokenInvalidError
from taolib.auth.models import TokenPair, TokenPayload
from taolib.auth.tokens import JWTService


class TestJWTServiceCreateTokens:
    """测试 JWT 令牌创建。"""

    def test_create_access_token(
        self, jwt_service: JWTService, auth_config: AuthConfig
    ):
        """测试创建 access token。"""
        token = jwt_service.create_access_token("user-123", ["admin", "editor"])

        assert isinstance(token, str)
        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
        )
        assert payload["sub"] == "user-123"
        assert payload["roles"] == ["admin", "editor"]
        assert payload["type"] == "access"
        assert "jti" in payload
        assert "iat" in payload
        assert "exp" in payload
        assert payload["iss"] == "test-issuer"

    def test_create_access_token_extra_claims(
        self, jwt_service: JWTService, auth_config: AuthConfig
    ):
        """测试创建带额外声明的 access token。"""
        token = jwt_service.create_access_token(
            "user-123",
            ["admin"],
            extra_claims={"tenant": "acme"},
        )
        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
        )
        assert payload["tenant"] == "acme"

    def test_create_refresh_token(
        self, jwt_service: JWTService, auth_config: AuthConfig
    ):
        """测试创建 refresh token。"""
        token = jwt_service.create_refresh_token("user-456")

        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
        )
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"
        assert payload["roles"] == []
        assert "jti" in payload

    def test_create_token_pair(self, jwt_service: JWTService, auth_config: AuthConfig):
        """测试同时创建 access 和 refresh token。"""
        pair = jwt_service.create_token_pair("user-789", ["viewer"])

        assert isinstance(pair, TokenPair)
        assert pair.token_type == "bearer"
        assert pair.expires_in == 3600

        access_payload = jwt.decode(
            pair.access_token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
        )
        assert access_payload["type"] == "access"
        assert access_payload["roles"] == ["viewer"]

        refresh_payload = jwt.decode(
            pair.refresh_token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
        )
        assert refresh_payload["type"] == "refresh"

    def test_unique_jti_per_token(
        self, jwt_service: JWTService, auth_config: AuthConfig
    ):
        """测试每个令牌的 jti 唯一。"""
        t1 = jwt_service.create_access_token("user-1", ["admin"])
        t2 = jwt_service.create_access_token("user-1", ["admin"])

        p1 = jwt.decode(
            t1, auth_config.jwt_secret, algorithms=[auth_config.jwt_algorithm]
        )
        p2 = jwt.decode(
            t2, auth_config.jwt_secret, algorithms=[auth_config.jwt_algorithm]
        )

        assert p1["jti"] != p2["jti"]

    def test_no_issuer_when_not_configured(self):
        """测试未配置 issuer 时不包含 iss 声明。"""
        config = AuthConfig(jwt_secret="test-secret")
        service = JWTService(config)
        token = service.create_access_token("user-1", ["admin"])
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert "iss" not in payload


class TestJWTServiceDecodeTokens:
    """测试 JWT 令牌解码和验证。"""

    def test_decode_access_token(self, jwt_service: JWTService):
        """测试解码 access token。"""
        token = jwt_service.create_access_token("user-123", ["admin"])
        payload = jwt_service.decode_token(token)

        assert isinstance(payload, TokenPayload)
        assert payload.sub == "user-123"
        assert payload.roles == ["admin"]
        assert payload.type == "access"
        assert payload.jti != ""

    def test_decode_refresh_token(self, jwt_service: JWTService):
        """测试解码 refresh token。"""
        token = jwt_service.create_refresh_token("user-123")
        payload = jwt_service.decode_token(token)

        assert payload.sub == "user-123"
        assert payload.type == "refresh"
        assert payload.roles == []

    def test_verify_access_token(self, jwt_service: JWTService):
        """测试验证 access token 通过。"""
        token = jwt_service.create_access_token("user-123", ["admin"])
        payload = jwt_service.verify_access_token(token)

        assert payload.type == "access"
        assert payload.sub == "user-123"

    def test_verify_access_token_rejects_refresh(self, jwt_service: JWTService):
        """测试 access 验证拒绝 refresh token。"""
        token = jwt_service.create_refresh_token("user-123")

        with pytest.raises(TokenInvalidError, match="令牌类型不正确"):
            jwt_service.verify_access_token(token)

    def test_verify_refresh_token(self, jwt_service: JWTService):
        """测试验证 refresh token 通过。"""
        token = jwt_service.create_refresh_token("user-123")
        payload = jwt_service.verify_refresh_token(token)

        assert payload.type == "refresh"

    def test_verify_refresh_token_rejects_access(self, jwt_service: JWTService):
        """测试 refresh 验证拒绝 access token。"""
        token = jwt_service.create_access_token("user-123", ["admin"])

        with pytest.raises(TokenInvalidError, match="令牌类型不正确"):
            jwt_service.verify_refresh_token(token)

    def test_expired_token_raises(self):
        """测试过期令牌抛出 TokenExpiredError。"""
        config = AuthConfig(
            jwt_secret="test-secret",
            access_token_ttl=timedelta(seconds=-1),
        )
        service = JWTService(config)
        token = service.create_access_token("user-123", ["admin"])

        with pytest.raises(TokenExpiredError, match="令牌已过期"):
            service.verify_access_token(token)

    def test_invalid_token_raises(self, jwt_service: JWTService):
        """测试无效令牌抛出 TokenInvalidError。"""
        with pytest.raises(TokenInvalidError):
            jwt_service.decode_token("invalid.token.string")

    def test_wrong_secret_raises(self, jwt_service: JWTService):
        """测试错误密钥抛出 TokenInvalidError。"""
        token = jwt_service.create_access_token("user-123", ["admin"])

        other_config = AuthConfig(jwt_secret="wrong-secret")
        other_service = JWTService(other_config)

        with pytest.raises(TokenInvalidError):
            other_service.decode_token(token)

    def test_backward_compatible_token_without_jti(
        self, jwt_service: JWTService, auth_config: AuthConfig
    ):
        """测试兼容旧版令牌（无 jti 字段）。"""
        # 模拟旧版令牌（无 jti/iat）
        from datetime import UTC, datetime

        old_payload = {
            "sub": "old-user",
            "roles": ["viewer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(
            old_payload,
            auth_config.jwt_secret,
            algorithm=auth_config.jwt_algorithm,
        )

        payload = jwt_service.verify_access_token(token)
        assert payload.sub == "old-user"
        assert payload.jti == ""  # 旧版令牌无 jti

    def test_config_property(self, jwt_service: JWTService, auth_config: AuthConfig):
        """测试 config 属性。"""
        assert jwt_service.config is auth_config
