"""枚举定义模块。

定义配置管理系统中使用的所有枚举类型。
"""

from enum import StrEnum


class Environment(StrEnum):
    """环境类型枚举。"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRE_PRODUCTION = "pre-production"
    PRODUCTION = "production"


class ConfigValueType(StrEnum):
    """配置值类型枚举。"""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


class ConfigStatus(StrEnum):
    """配置状态枚举。"""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ChangeType(StrEnum):
    """配置变更类型枚举。"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


class AuditAction(StrEnum):
    """审计操作类型枚举。"""

    CONFIG_CREATE = "config.create"
    CONFIG_UPDATE = "config.update"
    CONFIG_DELETE = "config.delete"
    CONFIG_PUBLISH = "config.publish"
    CONFIG_ROLLBACK = "config.rollback"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    ROLE_ASSIGN = "role.assign"


class AuditStatus(StrEnum):
    """审计操作状态枚举。"""

    SUCCESS = "success"
    FAILED = "failed"


