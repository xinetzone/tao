"""Redis Key 命名规范模块。

提供 Redis Key 生成函数，确保命名一致性。
"""


def config_key(environment: str, service: str, key: str) -> str:
    """生成配置值缓存 Key。

    Args:
        environment: 环境类型
        service: 服务名称
        key: 配置键

    Returns:
        Redis Key 字符串
    """
    return f"config:{environment}:{service}:{key}"


def config_meta_key(environment: str, service: str, key: str) -> str:
    """生成配置元数据缓存 Key。

    Args:
        environment: 环境类型
        service: 服务名称
        key: 配置键

    Returns:
        Redis Key 字符串
    """
    return f"config:meta:{environment}:{service}:{key}"


def config_list_key(environment: str, service: str) -> str:
    """生成服务配置列表缓存 Key。

    Args:
        environment: 环境类型
        service: 服务名称

    Returns:
        Redis Key 字符串
    """
    return f"config:list:{environment}:{service}"


def user_roles_key(user_id: str) -> str:
    """生成用户角色缓存 Key。

    Args:
        user_id: 用户 ID

    Returns:
        Redis Key 字符串
    """
    return f"user:roles:{user_id}"


def config_pattern(environment: str | None = None, service: str | None = None) -> str:
    """生成配置缓存 Key 模式（用于批量删除）。

    Args:
        environment: 环境类型（可选）
        service: 服务名称（可选）

    Returns:
        Redis Key 模式字符串
    """
    if environment and service:
        return f"config:{environment}:{service}:*"
    if environment:
        return f"config:{environment}:*"
    if service:
        return f"config:*:{service}:*"
    return "config:*"
