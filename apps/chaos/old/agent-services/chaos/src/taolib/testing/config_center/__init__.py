"""taolib.config_center - 中心化配置管理系统。

提供多环境配置管理、版本控制、审计日志和实时推送功能。

主要组件:
    - models: 数据模型（配置、版本、审计日志、用户/角色）
    - repository: 数据访问层（MongoDB）
    - cache: 缓存层（Redis）
    - services: 业务逻辑层
    - validation: 配置验证框架
    - server: Web 服务器（FastAPI）
    - events: 事件系统
    - client: 客户端 SDK
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore[import-not-found]

try:
    __version__ = version("taolib")
except Exception:
    import os

    __version__ = os.environ.get("TAOLIB_VERSION", "0.0.0")

# 公开 API 导出
from .client import ConfigCenterClient
from .models.audit import AuditLogResponse
from .models.config import ConfigCreate, ConfigResponse, ConfigUpdate
from .models.enums import (
    AuditAction,
    AuditStatus,
    ChangeType,
    ConfigStatus,
    ConfigValueType,
    Environment,
)
from .models.user import Permission, RoleCreate, RoleResponse, UserCreate, UserResponse
from .models.version import ConfigVersionResponse
from .validation.base import ConfigValidator, ValidationResult
from .validation.registry import ValidatorRegistry

__all__ = [
    "AuditAction",
    "AuditLogResponse",
    "AuditStatus",
    "ChangeType",
    "ConfigCenterClient",
    "ConfigCreate",
    "ConfigResponse",
    "ConfigStatus",
    "ConfigUpdate",
    "ConfigValidator",
    "ConfigValueType",
    "ConfigVersionResponse",
    "Environment",
    "Permission",
    "RoleCreate",
    "RoleResponse",
    "UserCreate",
    "UserResponse",
    "ValidationResult",
    "ValidatorRegistry",
    "__version__",
]
