"""仓库层测试 - 配置仓库。"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.config_center.models.config import ConfigDocument
from taolib.testing.config_center.models.enums import ConfigStatus, ConfigValueType, Environment
from taolib.testing.config_center.repository.config_repo import ConfigRepository


@pytest.fixture
def mock_collection() -> MagicMock:
    """创建模拟 MongoDB 集合。"""
    return AsyncMock()


@pytest.fixture
def config_repo(mock_collection: MagicMock) -> ConfigRepository:
    """创建配置仓库实例。"""
    return ConfigRepository(mock_collection)


class TestConfigRepository:
    """测试 ConfigRepository。"""

    @pytest.mark.asyncio
    async def test_find_by_key_env_service_success(self, config_repo: ConfigRepository, mock_collection: MagicMock) -> None:
        """测试按 key/environment/service 查找成功。"""
        mock_doc = {
            "_id": "config-1",
            "key": "database.host",
            "environment": "development",
            "service": "auth-service",
            "value": "localhost:5432",
            "value_type": "string",
            "created_by": "user-1",
            "updated_by": "user-1",
        }
        mock_collection.find_one.return_value = mock_doc

        result = await config_repo.find_by_key_env_service(
            "database.host", Environment.DEVELOPMENT, "auth-service"
        )

        assert result is not None
        assert result.id == "config-1"
        assert result.key == "database.host"
        mock_collection.find_one.assert_called_once_with({
            "key": "database.host",
            "environment": Environment.DEVELOPMENT,
            "service": "auth-service",
        })

    @pytest.mark.asyncio
    async def test_find_by_key_env_service_not_found(self, config_repo: ConfigRepository, mock_collection: MagicMock) -> None:
        """测试按 key/environment/service 查找不存在。"""
        mock_collection.find_one.return_value = None

        result = await config_repo.find_by_key_env_service(
            "nonexistent.key", Environment.DEVELOPMENT, "auth-service"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_tags_with_filters(self, config_repo: ConfigRepository, mock_collection: MagicMock) -> None:
        """测试按标签查找带过滤条件。"""
        mock_docs = [
            {
                "_id": "config-1",
                "key": "database.host",
                "environment": "development",
                "service": "auth-service",
                "value": "localhost",
                "value_type": "string",
                "tags": ["database", "production"],
                "created_by": "user-1",
                "updated_by": "user-1",
            },
            {
                "_id": "config-2",
                "key": "database.port",
                "environment": "development",
                "service": "auth-service",
                "value": 5432,
                "value_type": "number",
                "tags": ["database"],
                "created_by": "user-1",
                "updated_by": "user-1",
            },
        ]
        # Mock the list method
        config_repo.list = AsyncMock(return_value=[
            ConfigDocument(**doc) for doc in mock_docs
        ])

        result = await config_repo.find_by_tags(
            tags=["database"],
            environment=Environment.DEVELOPMENT,
            service="auth-service",
        )

        assert len(result) == 2
        config_repo.list.assert_called_once_with(
            filters={
                "tags": {"$in": ["database"]},
                "environment": Environment.DEVELOPMENT,
                "service": "auth-service",
            },
            skip=0,
            limit=100,
        )

    @pytest.mark.asyncio
    async def test_find_by_status_with_filters(self, config_repo: ConfigRepository, mock_collection: MagicMock) -> None:
        """测试按状态查找带过滤条件。"""
        mock_docs = [
            {
                "_id": "config-1",
                "key": "database.host",
                "environment": "production",
                "service": "auth-service",
                "value": "prod-db",
                "value_type": "string",
                "status": "active",
                "created_by": "user-1",
                "updated_by": "user-1",
            },
        ]
        config_repo.list = AsyncMock(return_value=[
            ConfigDocument(**doc) for doc in mock_docs
        ])

        result = await config_repo.find_by_status(
            status=ConfigStatus.ACTIVE,
            environment=Environment.PRODUCTION,
        )

        assert len(result) == 1
        config_repo.list.assert_called_once_with(
            filters={
                "status": ConfigStatus.ACTIVE,
                "environment": Environment.PRODUCTION,
            },
            skip=0,
            limit=100,
        )

    @pytest.mark.asyncio
    async def test_find_by_environment_and_service(self, config_repo: ConfigRepository, mock_collection: MagicMock) -> None:
        """测试按环境和服务查找。"""
        mock_docs = [
            {
                "_id": "config-1",
                "key": "database.host",
                "environment": "development",
                "service": "auth-service",
                "value": "localhost",
                "value_type": "string",
                "created_by": "user-1",
                "updated_by": "user-1",
            },
            {
                "_id": "config-2",
                "key": "database.port",
                "environment": "development",
                "service": "auth-service",
                "value": 5432,
                "value_type": "number",
                "created_by": "user-1",
                "updated_by": "user-1",
            },
        ]
        config_repo.list = AsyncMock(return_value=[
            ConfigDocument(**doc) for doc in mock_docs
        ])

        result = await config_repo.find_by_environment_and_service(
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            skip=0,
            limit=50,
        )

        assert len(result) == 2
        config_repo.list.assert_called_once_with(
            filters={
                "environment": Environment.DEVELOPMENT,
                "service": "auth-service",
            },
            skip=0,
            limit=50,
        )

    @pytest.mark.asyncio
    async def test_create_indexes(self, config_repo: ConfigRepository, mock_collection: MagicMock) -> None:
        """测试创建索引。"""
        mock_collection.create_index.return_value = "index_name"

        await config_repo.create_indexes()

        # Should create 4 indexes
        assert mock_collection.create_index.call_count == 4

        # Verify the unique composite index
        calls = [call[0] for call in mock_collection.create_index.call_args_list]
        unique_index = next(
            (call for call in calls if len(call[0]) == 3),
            None,
        )
        assert unique_index is not None
        assert unique_index[0] == [("key", 1), ("environment", 1), ("service", 1)]


class TestConfigRepositoryInMemory:
    """使用内存模拟的集成测试。"""

    @pytest.fixture
    def in_memory_collection(self) -> MagicMock:
        """创建内存中的模拟集合。"""
        from .conftest import MockMongoCollection
        return MockMongoCollection("configs")

    @pytest.fixture
    def in_memory_repo(self, in_memory_collection: MagicMock) -> ConfigRepository:
        """创建内存中的仓库实例。"""
        return ConfigRepository(in_memory_collection)

    @pytest.mark.asyncio
    async def test_create_and_find(
        self,
        in_memory_repo: ConfigRepository,
        in_memory_collection: MagicMock,
    ) -> None:
        """测试创建和查找配置。"""
        # Create a config document
        doc = ConfigDocument(
            id="config-1",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )

        # Insert into collection
        await in_memory_collection.insert_one(doc.model_dump(by_alias=True, exclude_unset=False))

        # Find by key/env/service
        result = await in_memory_repo.find_by_key_env_service(
            "database.host", Environment.DEVELOPMENT, "auth-service"
        )

        assert result is not None
        assert result.key == "database.host"
        assert result.value == "localhost:5432"

    @pytest.mark.asyncio
    async def test_update_config(
        self,
        in_memory_repo: ConfigRepository,
        in_memory_collection: MagicMock,
    ) -> None:
        """测试更新配置。"""
        # Create initial config
        doc_data = {
            "_id": "config-1",
            "key": "database.host",
            "environment": "development",
            "service": "auth-service",
            "value": "localhost:5432",
            "value_type": "string",
            "created_by": "user-1",
            "updated_by": "user-1",
        }
        await in_memory_collection.insert_one(doc_data)

        # Update the config
        await in_memory_collection.update_one(
            {"_id": "config-1"},
            {"$set": {"value": "new-host:5433", "updated_by": "user-2"}},
        )

        # Verify update
        result = await in_memory_repo.find_by_key_env_service(
            "database.host", Environment.DEVELOPMENT, "auth-service"
        )

        assert result is not None
        assert result.value == "new-host:5433"
        assert result.updated_by == "user-2"



