"""正则表达式验证器模块。

验证字符串类型的配置值是否匹配指定的正则表达式。
"""

import re
from typing import Any

from ..validation.base import ConfigValidator, ValidationResult


class RegexValidator(ConfigValidator):
    """正则表达式验证器。"""

    def __init__(self, pattern: str, error_message: str | None = None) -> None:
        """初始化验证器。

        Args:
            pattern: 正则表达式模式
            error_message: 自定义错误消息
        """
        self._pattern = re.compile(pattern)
        self._error_message = error_message or f"值不匹配正则模式: {pattern}"

    def validate(
        self, key: str, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """验证配置值是否匹配正则表达式。

        Args:
            key: 配置键
            value: 配置值
            context: 额外上下文

        Returns:
            验证结果
        """
        if not isinstance(value, str):
            return ValidationResult(
                valid=False, errors=[f"配置 '{key}' 的值不是字符串"]
            )

        if self._pattern.match(value):
            return ValidationResult(valid=True)
        return ValidationResult(valid=False, errors=[self._error_message])


