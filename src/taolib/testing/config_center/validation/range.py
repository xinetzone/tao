"""范围验证器模块。

验证数值类型的配置值是否在指定范围内。
"""

from typing import Any

from ..validation.base import ConfigValidator, ValidationResult


class RangeValidator(ConfigValidator):
    """数值范围验证器。"""

    def __init__(
        self, min_value: int | float | None = None, max_value: int | float | None = None
    ) -> None:
        """初始化验证器。

        Args:
            min_value: 最小值（包含）
            max_value: 最大值（包含）
        """
        self._min_value = min_value
        self._max_value = max_value

    def validate(
        self, key: str, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """验证配置值是否在指定范围内。

        Args:
            key: 配置键
            value: 配置值
            context: 额外上下文

        Returns:
            验证结果
        """
        if not isinstance(value, (int, float)):
            return ValidationResult(valid=False, errors=[f"配置 '{key}' 的值不是数值"])

        errors: list[str] = []
        if self._min_value is not None and value < self._min_value:
            errors.append(f"值 {value} 小于最小值 {self._min_value}")
        if self._max_value is not None and value > self._max_value:
            errors.append(f"值 {value} 大于最大值 {self._max_value}")

        if errors:
            return ValidationResult(valid=False, errors=errors)
        return ValidationResult(valid=True)


