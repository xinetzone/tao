"""缓存层测试 - Redis 密钥和配置缓存。"""

import time
from unittest.mock import AsyncMock

import pytest

from taolib.testing.config_center.cache.config_cache import (
    InMemoryConfigCache,
    RedisConfigCache,
)
from taolib.testing.config_center.cache.keys import (
    config_key,
    config_list_key,
    config_meta_key,
    config_pattern,
    user_roles_key,
)


class TestCacheKeys:
    """测试 Redis 密钥生成函数。"""

    def test_config_key(self) -> None:
        """测试配置密钥生成。"""
        key = config_key("development", "auth-service", "database.host")
        assert key == "config:development:auth-service:database.host"

    def test_config_meta_key(self) -> None:
        """测试配置元数据密钥生成。"""
        key = config_meta_key("production", "api-gateway", "rate.limit")
        assert key == "config:meta:production:api-gateway:rate.limit"

    def test_config_list_key(self) -> None:
        """测试配置列表密钥生成。"""
        key = config_list_key("staging", "user-service")
        assert key == "config:list:staging:user-service"

    def test_user_roles_key(self) -> None:
        """测试用户角色密钥生成。"""
        key = user_roles_key("user-123")
        assert key == "user:roles:user-123"

    def test_config_pattern_specific(self) -> None:
        """测试特定配置模式生成。"""
        pattern = config_pattern("development", "auth-service")
        assert pattern == "config:development:auth-service:*"

    def test_config_pattern_environment_only(self) -> None:
        """测试仅环境的配置模式生成。"""
        pattern = config_pattern("production")
        assert pattern == "config:production:*"

    def test_config_pattern_global(self) -> None:
        """测试全局配置模式生成。"""
        pattern = config_pattern()
        assert pattern == "config:*"


class TestInMemoryConfigCache:
    """测试内存配置缓存。"""

    @pytest.fixture
    def cache(self) -> InMemoryConfigCache:
        """创建内存缓存实例。"""
        return InMemoryConfigCache()

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache: InMemoryConfigCache) -> None:
        """测试设置和获取缓存。"""
        await cache.set("development", "auth-service", "database.host", "localhost:5432")

        result = await cache.get("development", "auth-service", "database.host")

        assert result == "localhost:5432"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache: InMemoryConfigCache) -> None:
        """测试获取不存在的密钥返回 None。"""
        result = await cache.get("development", "auth-service", "nonexistent.key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, cache: InMemoryConfigCache) -> None:
        """测试设置自定义 TTL。"""
        await cache.set("development", "auth-service", "db.host", "localhost", ttl=60)

        result = await cache.get("development", "auth-service", "db.host")
        assert result == "localhost"

    @pytest.mark.asyncio
    async def test_delete_key(self, cache: InMemoryConfigCache) -> None:
        """测试删除密钥。"""
        await cache.set("development", "auth-service", "database.host", "localhost:5432")
        await cache.delete("development", "auth-service", "database.host")

        result = await cache.get("development", "auth-service", "database.host")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, cache: InMemoryConfigCache) -> None:
        """测试删除不存在的密钥不抛出异常。"""
        await cache.delete("development", "auth-service", "nonexistent.key")

    @pytest.mark.asyncio
    async def test_delete_pattern_by_environment(self, cache: InMemoryConfigCache) -> None:
        """测试按环境删除模式。"""
        # Set multiple keys
        await cache.set("development", "auth-service", "db.host", "dev-db")
        await cache.set("development", "api-gateway", "rate.limit", "100")
        await cache.set("production", "auth-service", "db.host", "prod-db")

        # Delete all development keys
        await cache.delete_pattern(environment="development")

        # Development keys should be gone
        assert await cache.get("development", "auth-service", "db.host") is None
        assert await cache.get("development", "api-gateway", "rate.limit") is None

        # Production keys should remain
        assert await cache.get("production", "auth-service", "db.host") == "prod-db"

    @pytest.mark.asyncio
    async def test_delete_pattern_by_service(self, cache: InMemoryConfigCache) -> None:
        """测试按服务删除模式。"""
        await cache.set("development", "auth-service", "db.host", "dev-db")
        await cache.set("production", "auth-service", "db.host", "prod-db")
        await cache.set("development", "api-gateway", "rate.limit", "100")

        await cache.delete_pattern(service="auth-service")

        # Auth-service keys should be gone
        assert await cache.get("development", "auth-service", "db.host") is None
        assert await cache.get("production", "auth-service", "db.host") is None

        # API-gateway keys should remain
        assert await cache.get("development", "api-gateway", "rate.limit") == "100"

    @pytest.mark.asyncio
    async def test_delete_pattern_global(self, cache: InMemoryConfigCache) -> None:
        """测试全局删除模式。"""
        await cache.set("development", "auth-service", "db.host", "dev-db")
        await cache.set("production", "api-gateway", "rate.limit", "100")

        await cache.delete_pattern()

        assert await cache.get("development", "auth-service", "db.host") is None
        assert await cache.get("production", "api-gateway", "rate.limit") is None

    @pytest.mark.asyncio
    async def test_cache_expiration(self, cache: InMemoryConfigCache) -> None:
        """测试缓存过期。"""
        # Set cache with 1 second TTL
        await cache.set("development", "auth-service", "db.host", "localhost", ttl=1)

        # Should be available immediately
        assert await cache.get("development", "auth-service", "db.host") == "localhost"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        result = await cache.get("development", "auth-service", "db.host")
        assert result is None

    @pytest.mark.asyncio
    async def test_complex_value_serialization(self, cache: InMemoryConfigCache) -> None:
        """测试复杂值序列化。"""
        complex_value = {
            "host": "localhost",
            "port": 5432,
            "options": {"ssl": True, "timeout": 30},
        }

        await cache.set("development", "auth-service", "database.config", complex_value)

        result = await cache.get("development", "auth-service", "database.config")
        assert result == complex_value

    @pytest.mark.asyncio
    async def test_different_environments_isolated(self, cache: InMemoryConfigCache) -> None:
        """测试不同环境的缓存隔离。"""
        await cache.set("development", "auth-service", "db.host", "dev-db")
        await cache.set("production", "auth-service", "db.host", "prod-db")

        dev_result = await cache.get("development", "auth-service", "db.host")
        prod_result = await cache.get("production", "auth-service", "db.host")

        assert dev_result == "dev-db"
        assert prod_result == "prod-db"


class TestRedisConfigCache:
    """测试 Redis 配置缓存（使用 Mock）。"""

    @pytest.fixture
    def mock_redis(self) -> AsyncMock:
        """创建模拟 Redis 客户端。"""
        redis_mock = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock(return_value=True)
        redis_mock.delete = AsyncMock(return_value=1)
        redis_mock.keys = AsyncMock(return_value=[])
        return redis_mock

    @pytest.fixture
    def redis_cache(self, mock_redis: AsyncMock) -> RedisConfigCache:
        """创建 Redis 缓存实例。"""
        return RedisConfigCache(mock_redis)

    @pytest.mark.asyncio
    async def test_set_and_get(
        self,
        redis_cache: RedisConfigCache,
        mock_redis: AsyncMock,
    ) -> None:
        """测试设置和获取缓存。"""
        import json

        # Mock Redis get to return JSON string
        mock_redis.get.return_value = json.dumps("localhost:5432")

        await redis_cache.set("development", "auth-service", "database.host", "localhost:5432")
        result = await redis_cache.get("development", "auth-service", "database.host")

        assert result == "localhost:5432"
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_key(
        self,
        redis_cache: RedisConfigCache,
        mock_redis: AsyncMock,
    ) -> None:
        """测试缺失密钥返回 None。"""
        mock_redis.get.return_value = None

        result = await redis_cache.get("development", "auth-service", "nonexistent.key")

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_calls_redis_delete(
        self,
        redis_cache: RedisConfigCache,
        mock_redis: AsyncMock,
    ) -> None:
        """测试删除调用 Redis delete。"""
        await redis_cache.delete("development", "auth-service", "database.host")

        mock_redis.delete.assert_called_once_with("config:development:auth-service:database.host")

    @pytest.mark.asyncio
    async def test_delete_pattern_calls_redis_keys_and_delete(
        self,
        redis_cache: RedisConfigCache,
        mock_redis: AsyncMock,
    ) -> None:
        """测试模式删除调用 Redis keys 和 delete。"""
        mock_redis.keys.return_value = [
            "config:development:auth-service:db.host",
            "config:development:auth-service:db.port",
        ]

        await redis_cache.delete_pattern(environment="development", service="auth-service")

        mock_redis.keys.assert_called_once_with("config:development:auth-service:*")
        mock_redis.delete.assert_called_once()



