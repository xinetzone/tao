"""验证器注册表模块。

实现按配置键模式注册验证器的注册表。
"""

import fnmatch
from typing import Any

from .base import ConfigValidator, ValidationResult


class ValidatorRegistry:
    """验证器注册表。

    按配置键模式注册验证器，支持通配符匹配。
    """

    def __init__(self) -> None:
        """初始化注册表。"""
        self._validators: list[tuple[str, ConfigValidator]] = []

    def register(self, pattern: str, validator: ConfigValidator) -> None:
        """注册验证器。

        Args:
            pattern: 配置键模式（支持通配符，如 `database.*`）
            validator: 验证器实例
        """
        self._validators.append((pattern, validator))

    def get_validators(self, key: str) -> list[ConfigValidator]:
        """获取匹配配置键的所有验证器。

        Args:
            key: 配置键

        Returns:
            验证器列表
        """
        return [v for pattern, v in self._validators if fnmatch.fnmatch(key, pattern)]

    def validate(
        self, key: str, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """执行验证链。

        Args:
            key: 配置键
            value: 配置值
            context: 额外上下文

        Returns:
            聚合的验证结果
        """
        validators = self.get_validators(key)
        if not validators:
            return ValidationResult(valid=True)

        all_errors: list[str] = []
        for validator in validators:
            result = validator.validate(key, value, context)
            if not result.valid:
                all_errors.extend(result.errors)

        if all_errors:
            return ValidationResult(valid=False, errors=all_errors)
        return ValidationResult(valid=True)


# 全局注册表实例
registry = ValidatorRegistry()
