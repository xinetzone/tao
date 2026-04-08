"""客户端 SDK 测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from taolib.testing.config_center.client import ConfigCenterClient


class TestConfigCenterClient:
    """测试 ConfigCenterClient。"""

    @pytest.fixture
    def client(self) -> ConfigCenterClient:
        """创建客户端实例。"""
        return ConfigCenterClient(
            base_url="http://localhost:8000",
            token="test-token-123",
            cache_ttl=60,
        )

    def test_cache_key_generation(self, client: ConfigCenterClient) -> None:
        """测试缓存密钥生成。"""
        key = client._cache_key("development", "auth-service", "database.host")
        assert key == "development:auth-service:database.host"

    def test_local_cache_set_and_get(self, client: ConfigCenterClient) -> None:
        """测试本地缓存设置和获取。"""
        client._set_cached("test:key", "test-value")
        result = client._get_cached("test:key")
        assert result == "test-value"

    def test_local_cache_expiration(self, client: ConfigCenterClient) -> None:
        """测试本地缓存过期。"""
        import time

        # Set cache with 0 TTL (immediate expiration)
        client._cache_ttl = 0
        client._set_cached("test:key", "test-value")

        # Should be expired
        time.sleep(0.1)
        result = client._get_cached("test:key")
        assert result is None

    def test_local_cache_delete_on_miss(self, client: ConfigCenterClient) -> None:
        """测试缓存未命中时删除。"""
        client._set_cached("test:key", "old-value")

        # Manually expire
        import time
        time.sleep(client._cache_ttl + 0.1)

        result = client._get_cached("test:key")
        assert result is None
        assert "test:key" not in client._local_cache

    @patch("httpx.Client")
    def test_get_config_success(self, mock_client_cls: MagicMock, client: ConfigCenterClient) -> None:
        """测试成功获取配置。"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "config-1",
                "key": "database.host",
                "value": "localhost:5432",
                "environment": "development",
                "service": "auth-service",
            }
        ]

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = client.get_config("database.host", "development", "auth-service")

        assert result == "localhost:5432"
        # Verify cached
        assert client._get_cached("development:auth-service:database.host") == "localhost:5432"

    @patch("httpx.Client")
    def test_get_config_not_found(self, mock_client_cls: MagicMock, client: ConfigCenterClient) -> None:
        """测试获取配置不存在。"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = client.get_config("nonexistent.key", "development", "auth-service")

        assert result is None

    @patch("httpx.Client")
    def test_get_config_http_error(self, mock_client_cls: MagicMock, client: ConfigCenterClient) -> None:
        """测试获取配置 HTTP 错误。"""
        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = httpx.HTTPError("Connection error")
        mock_client_cls.return_value = mock_client

        result = client.get_config("database.host", "development", "auth-service")

        assert result is None

    @pytest.mark.asyncio
    async def test_aget_config_success(self, client: ConfigCenterClient) -> None:
        """测试异步成功获取配置。"""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "config-1",
                "key": "database.host",
                "value": "async-host:5432",
                "environment": "development",
                "service": "auth-service",
            }
        ]

        mock_client = httpx.AsyncClient()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await client.aget_config("database.host", "development", "auth-service")

        assert result == "async-host:5432"

    @pytest.mark.asyncio
    async def test_aget_config_cache_hit(self, client: ConfigCenterClient) -> None:
        """测试异步获取配置缓存命中。"""
        # Pre-populate cache
        client._set_cached("development:auth-service:cached.key", "cached-value")

        result = await client.aget_config("cached.key", "development", "auth-service")

        assert result == "cached-value"

    @patch("httpx.Client")
    def test_get_configs_success(self, mock_client_cls: MagicMock, client: ConfigCenterClient) -> None:
        """测试成功获取配置列表。"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"key": "database.host", "value": "localhost"},
            {"key": "database.port", "value": 5432},
        ]

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = client.get_configs("development", "auth-service")

        assert len(result) == 2
        assert result[0]["key"] == "database.host"

    @patch("httpx.Client")
    def test_get_configs_http_error(self, mock_client_cls: MagicMock, client: ConfigCenterClient) -> None:
        """测试获取配置列表 HTTP 错误。"""
        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get.side_effect = httpx.HTTPError("Connection error")
        mock_client_cls.return_value = mock_client

        result = client.get_configs("development", "auth-service")

        assert result == []

    def test_client_initialization_strips_base_url(self) -> None:
        """测试客户端初始化时去除 URL 尾部斜杠。"""
        client = ConfigCenterClient(
            base_url="http://localhost:8000/",
            token="test-token",
        )
        assert client._base_url == "http://localhost:8000"

    def test_client_auth_header(self) -> None:
        """测试客户端认证头。"""
        client = ConfigCenterClient(
            base_url="http://localhost:8000",
            token="my-token",
        )
        assert client._headers["Authorization"] == "Bearer my-token"



