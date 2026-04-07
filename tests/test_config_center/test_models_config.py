"""模型测试 - 配置数据模型。"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from taolib.config_center.models.config import (
    ConfigBase,
    ConfigCreate,
    ConfigDocument,
    ConfigResponse,
    ConfigUpdate,
)
from taolib.config_center.models.enums import ConfigStatus, ConfigValueType, Environment


class TestConfigBase:
    """测试 ConfigBase 模型。"""

    def test_create_valid_config(self, sample_config_data: dict) -> None:
        """测试创建有效的配置对象。"""
        config = ConfigBase(**sample_config_data)

        assert config.key == "database.host"
        assert config.environment == Environment.DEVELOPMENT
        assert config.service == "auth-service"
        assert config.value == "localhost:5432"
        assert config.value_type == ConfigValueType.STRING
        assert config.tags == ["database", "connection"]
        assert config.status == ConfigStatus.DRAFT

    def test_config_key_validation(self) -> None:
        """测试配置键长度验证。"""
        # Empty key should fail
        with pytest.raises(ValidationError):
            ConfigBase(
                key="",
                environment="development",
                service="test-service",
                value="test",
                value_type="string",
            )

        # Key too long (> 255 chars)
        with pytest.raises(ValidationError):
            ConfigBase(
                key="a" * 256,
                environment="development",
                service="test-service",
                value="test",
                value_type="string",
            )

    def test_config_service_validation(self) -> None:
        """测试服务名称验证。"""
        # Empty service should fail
        with pytest.raises(ValidationError):
            ConfigBase(
                key="test.key",
                environment="development",
                service="",
                value="test",
                value_type="string",
            )

        # Service too long (> 255 chars)
        with pytest.raises(ValidationError):
            ConfigBase(
                key="test.key",
                environment="development",
                service="a" * 256,
                value="test",
                value_type="string",
            )

    def test_environment_enum_accepts_string(self) -> None:
        """测试环境类型接受字符串。"""
        config = ConfigBase(
            key="test.key",
            environment="production",
            service="test-service",
            value="test",
            value_type="string",
        )
        assert config.environment == Environment.PRODUCTION

    def test_environment_invalid_raises(self) -> None:
        """测试无效环境类型抛出异常。"""
        with pytest.raises(ValidationError):
            ConfigBase(
                key="test.key",
                environment="invalid-env",
                service="test-service",
                value="test",
                value_type="string",
            )

    def test_default_values(self) -> None:
        """测试默认值设置。"""
        config = ConfigBase(
            key="test.key",
            environment="development",
            service="test-service",
            value="test",
            value_type="string",
        )

        assert config.description == ""
        assert config.schema_id is None
        assert config.tags == []
        assert config.status == ConfigStatus.DRAFT

    def test_description_max_length(self) -> None:
        """测试描述最大长度。"""
        with pytest.raises(ValidationError):
            ConfigBase(
                key="test.key",
                environment="development",
                service="test-service",
                value="test",
                value_type="string",
                description="a" * 1001,
            )


class TestConfigCreate:
    """测试 ConfigCreate 模型。"""

    def test_config_create_inherits_base(self, sample_config_data: dict) -> None:
        """测试 ConfigCreate 继承 ConfigBase 的所有字段。"""
        create_data = ConfigCreate(**sample_config_data)

        assert create_data.key == "database.host"
        assert create_data.value_type == ConfigValueType.STRING


class TestConfigUpdate:
    """测试 ConfigUpdate 模型。"""

    def test_update_all_fields_optional(self) -> None:
        """测试所有更新字段都是可选的。"""
        update = ConfigUpdate()

        assert update.value is None
        assert update.value_type is None
        assert update.description is None
        assert update.schema_id is None
        assert update.tags is None
        assert update.status is None

    def test_update_partial(self) -> None:
        """测试部分更新。"""
        update = ConfigUpdate(value="new-value")

        assert update.value == "new-value"
        assert update.value_type is None

    def test_update_with_tags(self) -> None:
        """测试更新标签。"""
        update = ConfigUpdate(tags=["tag1", "tag2"])

        assert update.tags == ["tag1", "tag2"]


class TestConfigResponse:
    """测试 ConfigResponse 模型。"""

    def test_response_model(self) -> None:
        """测试响应模型。"""
        now = datetime.now(tz=UTC)
        response = ConfigResponse(
            id="config-123",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            version=1,
            created_by="user-1",
            updated_by="user-1",
            created_at=now,
            updated_at=now,
        )

        assert response.id == "config-123"
        assert response.version == 1
        assert response.created_by == "user-1"
        assert response.updated_by == "user-1"

    def test_response_from_attributes(self) -> None:
        """测试 from_attributes 配置。"""
        now = datetime.now(tz=UTC)
        doc = ConfigDocument(
            id="config-123",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )

        response = ConfigResponse.model_validate(doc)
        assert response.id == "config-123"


class TestConfigDocument:
    """测试 ConfigDocument 模型。"""

    def test_document_creation_with_defaults(self) -> None:
        """测试文档创建时的默认值。"""
        doc = ConfigDocument(
            id="config-123",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )

        assert doc.version == 1
        assert doc.status == ConfigStatus.DRAFT
        assert doc.description == ""
        assert doc.schema_id is None
        assert doc.tags == []
        assert doc.created_at is not None
        assert doc.updated_at is not None

    def test_document_to_response(self) -> None:
        """测试转换为响应模型。"""
        now = datetime.now(tz=UTC)
        doc = ConfigDocument(
            id="config-123",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            version=5,
            created_by="user-1",
            updated_by="user-2",
            created_at=now,
            updated_at=now,
        )

        response = doc.to_response()

        assert response.id == "config-123"
        assert response.version == 5
        assert response.key == "database.host"
        assert response.created_by == "user-1"
        assert response.updated_by == "user-2"

    def test_document_alias_id(self) -> None:
        """测试 _id 别名。"""
        doc = ConfigDocument(
            _id="config-456",
            key="database.host",
            environment=Environment.DEVELOPMENT,
            service="auth-service",
            value="localhost:5432",
            value_type=ConfigValueType.STRING,
            created_by="user-1",
            updated_by="user-1",
        )

        assert doc.id == "config-456"

    def test_document_timestamps_auto_generated(self) -> None:
        """测试时间戳自动生成。"""
        doc = ConfigDocument(
            id="config-123",
            key="test.key",
            environment="development",
            service="test-service",
            value="test",
            value_type="string",
            created_by="user-1",
            updated_by="user-1",
        )

        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)
        assert doc.created_at.tzinfo is not None

    def test_all_value_types(self) -> None:
        """测试所有配置值类型。"""
        # String
        doc_str = ConfigDocument(
            id="1",
            key="test.string",
            environment="development",
            service="test",
            value="hello",
            value_type="string",
            created_by="u1",
            updated_by="u1",
        )
        assert doc_str.value == "hello"

        # Number
        doc_num = ConfigDocument(
            id="2",
            key="test.number",
            environment="development",
            service="test",
            value=42.5,
            value_type="number",
            created_by="u1",
            updated_by="u1",
        )
        assert doc_num.value == 42.5

        # Boolean
        doc_bool = ConfigDocument(
            id="3",
            key="test.boolean",
            environment="development",
            service="test",
            value=True,
            value_type="boolean",
            created_by="u1",
            updated_by="u1",
        )
        assert doc_bool.value is True

        # JSON
        doc_json = ConfigDocument(
            id="4",
            key="test.json",
            environment="development",
            service="test",
            value={"nested": "data"},
            value_type="json",
            created_by="u1",
            updated_by="u1",
        )
        assert doc_json.value == {"nested": "data"}

        # Secret
        doc_secret = ConfigDocument(
            id="5",
            key="test.secret",
            environment="development",
            service="test",
            value="super-secret",
            value_type="secret",
            created_by="u1",
            updated_by="u1",
        )
        assert doc_secret.value == "super-secret"
