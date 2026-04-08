"""邮件提供商协议和数据结构。

定义邮件发送提供商的统一接口和返回结果。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from taolib.testing.email_service.models.email import EmailDocument


@dataclass(frozen=True, slots=True)
class SendResult:
    """提供商发送结果。"""

    success: bool
    provider_name: str
    provider_message_id: str | None = None
    error_message: str | None = None
    latency_ms: float = 0.0


@dataclass(frozen=True, slots=True)
class ProviderHealthStatus:
    """提供商健康状态。"""

    provider_name: str
    is_healthy: bool
    consecutive_failures: int = 0
    last_check: datetime | None = None
    last_error: str | None = None


class EmailProviderProtocol(Protocol):
    """邮件提供商协议。

    所有邮件服务提供商必须实现此协议。
    """

    @property
    def name(self) -> str:
        """提供商名称。"""
        ...

    async def send(self, email: EmailDocument) -> SendResult:
        """发送单封邮件。

        Args:
            email: 邮件文档

        Returns:
            发送结果
        """
        ...

    async def send_bulk(self, emails: list[EmailDocument]) -> list[SendResult]:
        """批量发送邮件。

        Args:
            emails: 邮件文档列表

        Returns:
            发送结果列表
        """
        ...

    async def check_health(self) -> ProviderHealthStatus:
        """检查提供商健康状态。

        Returns:
            健康状态
        """
        ...


