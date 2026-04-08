"""API 密钥认证测试。"""

import pytest

from taolib.testing.auth.api_key import APIKeyLookupProtocol, StaticAPIKeyLookup
from taolib.testing.auth.models import AuthenticatedUser


class TestStaticAPIKeyLookup:
    """测试静态 API 密钥查找。"""

    @pytest.fixture
    def api_keys(self) -> dict[str, AuthenticatedUser]:
        return {
            "key-abc-123": AuthenticatedUser(
                user_id="service-bot",
                roles=["config_viewer"],
                auth_method="api_key",
                metadata={"key_name": "ci-key"},
            ),
            "key-xyz-789": AuthenticatedUser(
                user_id="admin-bot",
                roles=["super_admin"],
                auth_method="api_key",
                metadata={"key_name": "admin-key"},
            ),
        }

    @pytest.fixture
    def lookup(self, api_keys) -> StaticAPIKeyLookup:
        return StaticAPIKeyLookup(api_keys)

    @pytest.mark.asyncio
    async def test_valid_key_returns_user(self, lookup: StaticAPIKeyLookup):
        """测试有效密钥返回用户。"""
        user = await lookup.lookup("key-abc-123")
        assert user is not None
        assert user.user_id == "service-bot"
        assert user.auth_method == "api_key"

    @pytest.mark.asyncio
    async def test_invalid_key_returns_none(self, lookup: StaticAPIKeyLookup):
        """测试无效密钥返回 None。"""
        user = await lookup.lookup("invalid-key")
        assert user is None

    @pytest.mark.asyncio
    async def test_empty_key_returns_none(self, lookup: StaticAPIKeyLookup):
        """测试空密钥返回 None。"""
        user = await lookup.lookup("")
        assert user is None

    @pytest.mark.asyncio
    async def test_multiple_keys(self, lookup: StaticAPIKeyLookup):
        """测试多个密钥。"""
        user1 = await lookup.lookup("key-abc-123")
        user2 = await lookup.lookup("key-xyz-789")

        assert user1 is not None
        assert user2 is not None
        assert user1.user_id == "service-bot"
        assert user2.user_id == "admin-bot"

    def test_implements_protocol(self, lookup: StaticAPIKeyLookup):
        """测试实现 Protocol。"""
        assert isinstance(lookup, APIKeyLookupProtocol)



