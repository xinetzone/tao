"""验证框架测试。"""

import pytest

from taolib.testing.config_center.validation.base import ValidationResult
from taolib.testing.config_center.validation.json_schema import JsonSchemaValidator
from taolib.testing.config_center.validation.range import RangeValidator
from taolib.testing.config_center.validation.regex import RegexValidator
from taolib.testing.config_center.validation.registry import ValidatorRegistry


class TestValidationResult:
    """测试 ValidationResult。"""

    def test_valid_result(self) -> None:
        """测试有效结果。"""
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert result.errors == []

    def test_invalid_result_with_errors(self) -> None:
        """测试无效结果带错误。"""
        result = ValidationResult(valid=False, errors=["Error 1", "Error 2"])
        assert result.valid is False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors

    def test_frozen_dataclass(self) -> None:
        """测试冻结的数据类（不可变）。"""
        result = ValidationResult(valid=True)
        with pytest.raises(AttributeError):
            result.valid = False  # type: ignore[misc]


class TestValidatorRegistry:
    """测试 ValidatorRegistry。"""

    def test_register_and_get_validators(self) -> None:
        """测试注册和获取验证器。"""
        registry = ValidatorRegistry()
        mock_validator = MockValidator()

        registry.register("database.*", mock_validator)

        validators = registry.get_validators("database.host")
        assert len(validators) == 1
        assert validators[0] is mock_validator

    def test_get_validators_no_match(self) -> None:
        """测试获取不匹配的验证器返回空列表。"""
        registry = ValidatorRegistry()
        registry.register("database.*", MockValidator())

        validators = registry.get_validators("api.key")
        assert len(validators) == 0

    def test_get_validators_wildcard_match(self) -> None:
        """测试通配符匹配。"""
        registry = ValidatorRegistry()
        registry.register("database.*", MockValidator())
        registry.register("database.*.host", MockValidator())

        validators = registry.get_validators("database.primary.host")
        assert len(validators) == 2  # Both patterns match

    def test_validate_with_no_validators(self) -> None:
        """测试无验证器时返回有效结果。"""
        registry = ValidatorRegistry()

        result = registry.validate("unregistered.key", "any-value")
        assert result.valid is True
        assert result.errors == []

    def test_validate_with_passing_validators(self) -> None:
        """测试所有验证器通过。"""
        registry = ValidatorRegistry()
        registry.register("test.key", PassingValidator())

        result = registry.validate("test.key", "valid-value")
        assert result.valid is True
        assert result.errors == []

    def test_validate_with_failing_validator(self) -> None:
        """测试验证器失败。"""
        registry = ValidatorRegistry()
        registry.register("test.key", FailingValidator(["Error 1"]))

        result = registry.validate("test.key", "invalid-value")
        assert result.valid is False
        assert len(result.errors) == 1
        assert "Error 1" in result.errors

    def test_validate_aggregates_multiple_errors(self) -> None:
        """测试聚合多个错误。"""
        registry = ValidatorRegistry()
        registry.register("test.key", FailingValidator(["Error 1", "Error 2"]))
        registry.register("test.key", FailingValidator(["Error 3"]))

        result = registry.validate("test.key", "invalid-value")
        assert result.valid is False
        assert len(result.errors) == 3
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors
        assert "Error 3" in result.errors

    def test_register_multiple_validators_same_pattern(self) -> None:
        """测试同一模式注册多个验证器。"""
        registry = ValidatorRegistry()
        registry.register("database.*", PassingValidator())
        registry.register("database.*", FailingValidator(["Constraint violated"]))

        result = registry.validate("database.host", "value")
        assert result.valid is False
        assert len(result.errors) == 1


class TestJsonSchemaValidator:
    """测试 JsonSchemaValidator。"""

    def test_valid_object(self) -> None:
        """测试有效对象。"""
        schema = {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
            },
            "required": ["host", "port"],
        }
        validator = JsonSchemaValidator(schema)
        value = {"host": "localhost", "port": 5432}

        result = validator.validate("database.config", value)
        assert result.valid is True

    def test_invalid_object_missing_required(self) -> None:
        """测试无效对象缺少必需字段。"""
        schema = {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
            },
            "required": ["host", "port"],
        }
        validator = JsonSchemaValidator(schema)
        value = {"host": "localhost"}  # Missing port

        result = validator.validate("database.config", value)
        assert result.valid is False
        assert len(result.errors) == 1
        assert "port" in result.errors[0]

    def test_invalid_object_wrong_type(self) -> None:
        """测试无效对象类型错误。"""
        schema = {
            "type": "object",
            "properties": {
                "port": {"type": "integer"},
            },
        }
        validator = JsonSchemaValidator(schema)
        value = {"port": "not-a-number"}

        result = validator.validate("database.config", value)
        assert result.valid is False

    def test_valid_string(self) -> None:
        """测试有效字符串。"""
        schema = {"type": "string", "minLength": 1}
        validator = JsonSchemaValidator(schema)

        result = validator.validate("api.key", "valid-key")
        assert result.valid is True

    def test_valid_array(self) -> None:
        """测试有效数组。"""
        schema = {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        }
        validator = JsonSchemaValidator(schema)
        value = ["tag1", "tag2", "tag3"]

        result = validator.validate("config.tags", value)
        assert result.valid is True


class TestRegexValidator:
    """测试 RegexValidator。"""

    def test_valid_email(self) -> None:
        """测试有效邮箱。"""
        validator = RegexValidator(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

        result = validator.validate("admin.email", "user@example.com")
        assert result.valid is True

    def test_invalid_email(self) -> None:
        """测试无效邮箱。"""
        validator = RegexValidator(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

        result = validator.validate("admin.email", "not-an-email")
        assert result.valid is False

    def test_custom_error_message(self) -> None:
        """测试自定义错误消息。"""
        validator = RegexValidator(
            r"^[A-Z][a-z]+$",
            error_message="Must start with capital letter",
        )

        result = validator.validate("user.name", "invalidName")
        assert result.valid is False
        assert "Must start with capital letter" in result.errors[0]

    def test_hostname_pattern(self) -> None:
        """测试主机名模式。"""
        validator = RegexValidator(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$")

        result = validator.validate("database.host", "db.example.com")
        assert result.valid is True

        result = validator.validate("database.host", "-invalid-host.com")
        assert result.valid is False


class TestRangeValidator:
    """测试 RangeValidator。"""

    def test_valid_number_in_range(self) -> None:
        """测试数字在范围内。"""
        validator = RangeValidator(min_value=1, max_value=65535)

        result = validator.validate("network.port", 8080)
        assert result.valid is True

    def test_number_below_min(self) -> None:
        """测试数字低于最小值。"""
        validator = RangeValidator(min_value=1, max_value=65535)

        result = validator.validate("network.port", 0)
        assert result.valid is False

    def test_number_above_max(self) -> None:
        """测试数字高于最大值。"""
        validator = RangeValidator(min_value=1, max_value=65535)

        result = validator.validate("network.port", 70000)
        assert result.valid is False

    def test_only_min_specified(self) -> None:
        """测试仅指定最小值。"""
        validator = RangeValidator(min_value=0)

        result = validator.validate("count.value", 100)
        assert result.valid is True

        result = validator.validate("count.value", -1)
        assert result.valid is False

    def test_only_max_specified(self) -> None:
        """测试仅指定最大值。"""
        validator = RangeValidator(max_value=100)

        result = validator.validate("percentage.value", 50)
        assert result.valid is True

        result = validator.validate("percentage.value", 150)
        assert result.valid is False

    def test_float_range(self) -> None:
        """测试浮点数范围。"""
        validator = RangeValidator(min_value=0.0, max_value=1.0)

        result = validator.validate("probability.value", 0.5)
        assert result.valid is True

        result = validator.validate("probability.value", 1.5)
        assert result.valid is False

    def test_custom_error_message(self) -> None:
        """测试错误消息格式。"""
        validator = RangeValidator(min_value=1, max_value=100)

        result = validator.validate("ttl.seconds", 200)
        assert result.valid is False
        assert "大于最大值" in result.errors[0]


# ---------------------------------------------------------------------------
# Helper validators for testing
# ---------------------------------------------------------------------------


class MockValidator:
    """模拟验证器（总是通过）。"""

    def validate(self, key: str, value: object, context: dict | None = None) -> ValidationResult:
        return ValidationResult(valid=True)


class PassingValidator:
    """总是通过的验证器。"""

    def validate(self, key: str, value: object, context: dict | None = None) -> ValidationResult:
        return ValidationResult(valid=True)


class FailingValidator:
    """总是失败的验证器。"""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors

    def validate(self, key: str, value: object, context: dict | None = None) -> ValidationResult:
        return ValidationResult(valid=False, errors=self.errors)



