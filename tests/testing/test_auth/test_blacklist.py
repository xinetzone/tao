"""令牌黑名单测试。"""

import pytest

from taolib.testing.auth.blacklist import (
    InMemoryTokenBlacklist,
    NullTokenBlacklist,
    RedisTokenBlacklist,
)


class TestInMemoryTokenBlacklist:
    """测试内存黑名单。"""

    @pytest.fixture
    def blacklist(self) -> InMemoryTokenBlacklist:
        return InMemoryTokenBlacklist()

    @pytest.mark.asyncio
    async def test_add_and_check(self, blacklist: InMemoryTokenBlacklist):
        """测试添加后可查询到。"""
        await blacklist.add("jti-001", ttl_seconds=3600)
        assert await blacklist.is_blacklisted("jti-001") is True

    @pytest.mark.asyncio
    async def test_not_blacklisted(self, blacklist: InMemoryTokenBlacklist):
        """测试未添加的 jti 不在黑名单。"""
        assert await blacklist.is_blacklisted("jti-unknown") is False

    @pytest.mark.asyncio
    async def test_empty_jti_not_blacklisted(self, blacklist: InMemoryTokenBlacklist):
        """测试空 jti 不在黑名单。"""
        assert await blacklist.is_blacklisted("") is False

    @pytest.mark.asyncio
    async def test_zero_ttl_not_added(self, blacklist: InMemoryTokenBlacklist):
        """测试 TTL 为 0 时不添加。"""
        await blacklist.add("jti-zero", ttl_seconds=0)
        assert await blacklist.is_blacklisted("jti-zero") is False

    @pytest.mark.asyncio
    async def test_negative_ttl_not_added(self, blacklist: InMemoryTokenBlacklist):
        """测试负 TTL 不添加。"""
        await blacklist.add("jti-neg", ttl_seconds=-1)
        assert await blacklist.is_blacklisted("jti-neg") is False

    @pytest.mark.asyncio
    async def test_multiple_entries(self, blacklist: InMemoryTokenBlacklist):
        """测试多个条目。"""
        await blacklist.add("jti-1", ttl_seconds=3600)
        await blacklist.add("jti-2", ttl_seconds=3600)

        assert await blacklist.is_blacklisted("jti-1") is True
        assert await blacklist.is_blacklisted("jti-2") is True
        assert await blacklist.is_blacklisted("jti-3") is False


class TestNullTokenBlacklist:
    """测试空操作黑名单。"""

    @pytest.mark.asyncio
    async def test_always_returns_false(self):
        """测试始终返回 False。"""
        blacklist = NullTokenBlacklist()
        await blacklist.add("jti-001", ttl_seconds=3600)
        assert await blacklist.is_blacklisted("jti-001") is False


class TestRedisTokenBlacklist:
    """测试 Redis 黑名单（使用 Mock）。"""

    @pytest.fixture
    def mock_redis(self):
        """创建 Mock Redis 客户端。"""

        class MockRedis:
            def __init__(self):
                self._store: dict[str, tuple[str, int | None]] = {}

            async def set(self, key: str, value: str, ex: int | None = None):
                self._store[key] = (value, ex)

            async def get(self, key: str) -> str | None:
                if key in self._store:
                    return self._store[key][0]
                return None

        return MockRedis()

    @pytest.fixture
    def blacklist(self, mock_redis) -> RedisTokenBlacklist:
        return RedisTokenBlacklist(mock_redis, key_prefix="test:bl:")

    @pytest.mark.asyncio
    async def test_add_and_check(self, blacklist: RedisTokenBlacklist, mock_redis):
        """测试添加和查询。"""
        await blacklist.add("jti-redis-001", ttl_seconds=3600)
        assert await blacklist.is_blacklisted("jti-redis-001") is True

        # 验证 Redis 键格式
        assert "test:bl:jti-redis-001" in mock_redis._store

    @pytest.mark.asyncio
    async def test_not_blacklisted(self, blacklist: RedisTokenBlacklist):
        """测试未添加的 jti。"""
        assert await blacklist.is_blacklisted("jti-unknown") is False

    @pytest.mark.asyncio
    async def test_empty_jti(self, blacklist: RedisTokenBlacklist):
        """测试空 jti 不查询 Redis。"""
        assert await blacklist.is_blacklisted("") is False

    @pytest.mark.asyncio
    async def test_zero_ttl_skipped(self, blacklist: RedisTokenBlacklist, mock_redis):
        """测试 TTL 为 0 时跳过。"""
        await blacklist.add("jti-skip", ttl_seconds=0)
        assert "test:bl:jti-skip" not in mock_redis._store



