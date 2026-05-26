"""Redis key generation utilities for rate limiter."""


def make_window_key(identifier: str, path: str, method: str) -> str:
    """生成滑动窗口的 Redis 键。

    Args:
        identifier: 用户标识符（如 "user:abc123" 或 "ip:192.168.1.1"）
        path: 请求路径（如 "/api/v1/configs"）
        method: HTTP 方法（如 "GET"）

    Returns:
        Redis sorted set 键名
    """
    # Normalize path: remove trailing slashes, lowercase
    normalized_path = path.rstrip("/").lower()
    method_upper = method.upper()
    return f"ratelimit:window:{identifier}:{normalized_path}:{method_upper}"


def make_stats_top_users_key() -> str:
    """生成 Top Users 统计的 Redis 键。"""
    return "ratelimit:stats:top-users"


def make_stats_realtime_key() -> str:
    """生成实时请求统计的 Redis 键。"""
    return "ratelimit:stats:realtime"


def make_violation_counter_key(identifier: str) -> str:
    """生成违规计数器的 Redis 键。

    Args:
        identifier: 用户标识符

    Returns:
        Redis hash 键名
    """
    return f"ratelimit:violations:{identifier}"


def parse_identifier_type(identifier: str) -> str:
    """从标识符中提取类型。

    Args:
        identifier: 如 "user:abc123" 或 "ip:192.168.1.1"

    Returns:
        类型字符串："user" 或 "ip"
    """
    if ":" in identifier:
        return identifier.split(":", 1)[0]
    return "unknown"


