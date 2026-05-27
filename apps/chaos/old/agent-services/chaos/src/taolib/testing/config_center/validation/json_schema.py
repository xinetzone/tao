"""JSON Schema 验证器模块。

使用 jsonschema 库验证配置值是否符合 JSON Schema。
"""

from typing import Any

import jsonschema

from ..validation.base import ConfigValidator, ValidationResult


class JsonSchemaValidator(ConfigValidator):
    """JSON Schema 验证器。"""

    def __init__(self, schema: dict[str, Any]) -> None:
        """初始化验证器。

        Args:
            schema: JSON Schema 定义
        """
        self._schema = schema

    def validate(
        self, key: str, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """验证配置值是否符合 JSON Schema。

        Args:
            key: 配置键
            value: 配置值
            context: 额外上下文

        Returns:
            验证结果
        """
        try:
            jsonschema.validate(instance=value, schema=self._schema)
            return ValidationResult(valid=True)
        except jsonschema.ValidationError as e:
            return ValidationResult(valid=False, errors=[e.message])
