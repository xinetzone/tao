"""验证器基类模块。

定义配置验证器的 Protocol 和验证结果数据类。
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """验证结果。

    Attributes:
        valid: 验证是否通过
        errors: 错误消息列表
    """

    valid: bool
    errors: list[str] = field(default_factory=list)


class ConfigValidator(Protocol):
    """配置验证器协议。

    所有验证器必须实现此协议。
    """

    def validate(
        self, key: str, value: Any, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """验证配置值。

        Args:
            key: 配置键
            value: 配置值
            context: 额外上下文信息

        Returns:
            验证结果
        """
        ...
