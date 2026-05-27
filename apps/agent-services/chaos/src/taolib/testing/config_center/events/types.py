"""事件类型定义模块。

定义配置管理系统中的事件类型和数据类。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class ConfigChangedEvent:
    """配置变更事件。

    Attributes:
        config_id: 配置 ID
        config_key: 配置键
        environment: 环境类型
        service: 服务名称
        change_type: 变更类型 (create/update/delete/rollback)
        version: 新版本号
        changed_by: 变更人用户 ID
        timestamp: 变更时间
        new_value: 新配置值（可选）
    """

    config_id: str
    config_key: str
    environment: str
    service: str
    change_type: str
    version: int
    changed_by: str
    timestamp: datetime
    new_value: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "config_id": self.config_id,
            "config_key": self.config_key,
            "environment": self.environment,
            "service": self.service,
            "change_type": self.change_type,
            "version": self.version,
            "changed_by": self.changed_by,
            "timestamp": self.timestamp.isoformat(),
            "new_value": self.new_value,
        }
