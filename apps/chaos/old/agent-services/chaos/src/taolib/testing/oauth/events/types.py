"""OAuth 事件类型模块。

定义 OAuth 系统中的事件数据类。
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class OAuthLoginEvent:
    """OAuth 登录事件。"""

    user_id: str
    provider: str
    connection_id: str
    is_new_user: bool
    ip_address: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "user_id": self.user_id,
            "provider": self.provider,
            "connection_id": self.connection_id,
            "is_new_user": self.is_new_user,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class OAuthLinkEvent:
    """OAuth 账户关联/解除关联事件。"""

    user_id: str
    provider: str
    connection_id: str
    action: str  # "link" 或 "unlink"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "user_id": self.user_id,
            "provider": self.provider,
            "connection_id": self.connection_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class OAuthTokenRefreshEvent:
    """OAuth Token 刷新事件。"""

    connection_id: str
    provider: str
    success: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "connection_id": self.connection_id,
            "provider": self.provider,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }
