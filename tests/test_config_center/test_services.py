"""服务层测试 - 配置服务。"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.config_center.models.config import (
    ConfigCreate,
    ConfigDocument,
    ConfigUpdate,
)
from taolib.config_center.models.enums import ConfigStatus, ConfigValueType, Environment
from taolib.config_center.services.config_service import ConfigService


@pytest.fixture
def mock_config_repo() -> MagicMock:
    """创建模拟配置仓库。"""
    return AsyncMock()


@pytest.fixture
def mock_version_service() -> MagicMock:
    """创建模拟版本服务。"""
    return AsyncMock()


@pytest.fixture
def mock_audit_service() -> MagicMock:
    """创建模拟审计服务。"""
    return AsyncMock()


@pytest.fixture
def mock_cache() -> MagicMock:
    """创建模拟缓存。"""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    return cache


@pytest.fixture
def config_service(
    mock_config_repo: MagicMock,
    mock_version_service: MagicMock,
    mock_audit_service: MagicMock,
    mock_cache: MagicMock,
) -> ConfigService:
    """创建配置服务实例。"""
    return ConfigService(
        config_repo=mock_config_repo,
        version_service=mock_version_service,
        audit_service=mock_audit_service,
        cache=mock_cache,
    )


class TestConfigService:
    """测试 ConfigService。"""

    @pytest.mark.asyncio
    async def test_create_config_success(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
        mock_version_service: MagicMock,
        mock_audit_service: MagicMock,
    ) -> None:
        """测试成功创建配置。"""
        create_data = ConfigCreate(
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
        )

        # Mock repository create
        mock_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.create = AsyncMock(return_value=mock_config)

        result = await config_service.create_config(create_data, "user-1")

        assert result.id == "config-1"
        assert result.key == "database.host"
        assert result.value == "localhost:5432"

        # Verify version was created
        mock_version_service.create_version.assert_called_once()

        # Verify audit was logged
        mock_audit_service.log_action.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_config_success(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
    ) -> None:
        """测试成功获取配置。"""
        mock_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.get_by_id = AsyncMock(return_value=mock_config)

        result = await config_service.get_config("config-1")

        assert result is not None
        assert result.id == "config-1"
        assert result.key == "database.host"

    @pytest.mark.asyncio
    async def test_get_config_not_found(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
    ) -> None:
        """测试获取不存在的配置。"""
        mock_config_repo.get_by_id = AsyncMock(return_value=None)

        result = await config_service.get_config("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_config_with_cache(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """测试从缓存获取配置。"""
        cached_response = {
            "id": "config-1",
            "key": "database.host",
            "environment": "development",
            "service": "auth-service",
            "value": "cached-host",
            "value_type": "string",
            "version": 1,
            "created_by": "user-1",
            "updated_by": "user-1",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "status": "active",
            "description": "",
            "schema_id": None,
            "tags": [],
        }
        mock_cache.get = AsyncMock(return_value=cached_response)

        result = await config_service.get_config_by_key_env_service(
            "database.host", "development", "auth-service"
        )

        assert result is not None
        assert result.value == "cached-host"
        mock_config_repo.find_by_key_env_service.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_config_cache_miss_fallback_to_db(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """测试缓存未命中时从数据库获取。"""
        mock_cache.get = AsyncMock(return_value=None)

        mock_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="db-host",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.find_by_key_env_service = AsyncMock(return_value=mock_config)

        result = await config_service.get_config_by_key_env_service(
            "database.host", "development", "auth-service"
        )

        assert result is not None
        assert result.value == "db-host"
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_config_success(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
        mock_version_service: MagicMock,
        mock_audit_service: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """测试成功更新配置。"""
        old_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="old-host",
            value_type=ConfigValueType.STRING,
            version=1,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.get_by_id = AsyncMock(return_value=old_config)

        new_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="new-host",
            value_type=ConfigValueType.STRING,
            version=2,
            created_by="user-1",
            updated_by="user-2",
        )
        mock_config_repo.update = AsyncMock(return_value=new_config)

        update_data = ConfigUpdate(value="new-host")
        result = await config_service.update_config("config-1", update_data, "user-2")

        assert result is not None
        assert result.value == "new-host"
        assert result.version == 2

        # Verify cache was deleted
        mock_cache.delete.assert_called_once()

        # Verify version was created
        mock_version_service.create_version.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_config_not_found(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
    ) -> None:
        """测试更新不存在的配置。"""
        mock_config_repo.get_by_id = AsyncMock(return_value=None)

        update_data = ConfigUpdate(value="new-value")
        result = await config_service.update_config("nonexistent", update_data, "user-1")

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_config_success(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
        mock_audit_service: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """测试成功删除配置。"""
        mock_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.get_by_id = AsyncMock(return_value=mock_config)
        mock_config_repo.delete = AsyncMock(return_value=True)

        result = await config_service.delete_config("config-1", "user-1")

        assert result is True
        mock_cache.delete.assert_called_once()
        mock_audit_service.log_action.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_config_success(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
        mock_audit_service: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        """测试成功发布配置。"""
        mock_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost",
            value_type=ConfigValueType.STRING,
            status=ConfigStatus.DRAFT,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.get_by_id = AsyncMock(return_value=mock_config)

        published_config = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost",
            value_type=ConfigValueType.STRING,
            status=ConfigStatus.ACTIVE,
            created_by="user-1",
            updated_by="user-1",
        )
        mock_config_repo.update = AsyncMock(return_value=published_config)

        result = await config_service.publish_config("config-1", "user-1")

        assert result is not None
        mock_audit_service.log_action.assert_called_once()
        mock_cache.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_configs_with_filters(
        self,
        config_service: ConfigService,
        mock_config_repo: MagicMock,
    ) -> None:
        """测试按过滤条件列出配置。"""
        mock_configs = [
            ConfigDocument(
                id="config-1",
                key="database.host",
                environment=Environment.DEVELOPMENT,
                service="auth-service",
                value="localhost",
                value_type=ConfigValueType.STRING,
                status=ConfigStatus.ACTIVE,
                created_by="user-1",
                updated_by="user-1",
            ),
            ConfigDocument(
                id="config-2",
                key="database.port",
                environment=Environment.DEVELOPMENT,
                service="auth-service",
                value=5432,
                value_type=ConfigValueType.NUMBER,
                status=ConfigStatus.ACTIVE,
                created_by="user-1",
                updated_by="user-1",
            ),
        ]
        mock_config_repo.list = AsyncMock(return_value=mock_configs)

        results = await config_service.list_configs(
            environment="development",
            service="auth-service",
            status="active",
        )

        assert len(results) == 2
        mock_config_repo.list.assert_called_once()
